from typing import Iterable, cast

import bpy
from bpy.types import (
    Context,
    DisplaceModifier,
    Event,
    Image,
    ImageTexture,
    MaterialSlot,
    Mesh,
    ShaderNode,
    NodeSocketFloat,
    Object,
    ShaderNodeTexImage,
    ShapeKey,
)

from ..utils.wrappers import CBPOperator
from ..utils import blender_utils, render_utils
from .properties import MMProperties


class MMOperator(BADKitOperator):
    """Prepare materials for glTF export."""

    bl_label = "Marshall Materials"
    bl_idname = "object.material_marshall"
    FRAME_NAME = "MM-FRAME"
    target_stucture: str
    tex_size: int
    overwrite: bool

    @classmethod
    def poll(cls, context: Context):
        obj = context.view_layer.objects.active
        return obj and obj.mode == "OBJECT" and obj.type == "MESH"

    def invoke(self, context: Context, _event: Event) -> set[str]:
        # Get active object
        obj = context.view_layer.objects.active

        # Check that object can be worked with
        try:
            blender_utils.check_obj(obj)
        except RuntimeError as e:
            return self.cancel(e)

        # Read operator properties
        props: MMProperties = getattr(context.scene, MMProperties.bl_idname)
        self.target_stucture = props.target_stucture
        self.tex_size = pow(2, int(props.tex_size))
        self.overwrite = props.overwrite

        try:
            return self.execute(context)
        except RuntimeError as e:
            return self.error(e)

    def execute(self, context: Context) -> set[str]:
        # Configure baking settings
        reset_cb = render_utils.get_config_resetter(context)
        render_utils.configure_cycles(context=context, samples=1, denoise=False)
        context.scene.render.image_settings.file_format = "PNG"
        context.scene.render.image_settings.color_depth = "16"

        # Inspect active material of current object
        mat_tree = context.view_layer.objects.active.active_material.node_tree
        output_node = blender_utils.get_node_of_type(mat_tree, "OUTPUT_MATERIAL")

        # Remove old frame if necessary
        if self.overwrite:
            frame: ShaderNode = None
            for node in cast(Iterable[ShaderNode], mat_tree.nodes):
                if node.name == self.FRAME_NAME:
                    frame = node
                    break
            if frame:
                for node in cast(Iterable[ShaderNode], mat_tree.nodes):
                    if node.parent == frame:
                        mat_tree.nodes.remove(node)
                mat_tree.nodes.remove(frame)

        # Reset node selection
        mat_tree.nodes.active = None
        for node in cast(Iterable[ShaderNode], mat_tree.nodes):
            node.select = False

        # Calculate lowest y point
        y = 100000  # max y value
        for node in cast(Iterable[ShaderNode], mat_tree.nodes):
            _y = node.location[1] - node.height
            if _y < y:
                y = _y

        bake_name = f"{self.target_stucture}-BAKE"
        frame = mat_tree.nodes.new("NodeFrame")
        frame.name = self.FRAME_NAME

        uv: ShaderNode = mat_tree.nodes.new("ShaderNodeUVMap")
        uv.parent = frame

        if self.target_stucture == "SD":
            frame.label = "(Marshalled) Shadeless Diffuse"

            # Create Lightpath node
            lightpath: ShaderNode = mat_tree.nodes.new("ShaderNodeLightPath")
            lightpath.parent = frame

            # Create Transparent BSDF node
            transparent: ShaderNode = mat_tree.nodes.new("ShaderNodeBsdfTransparent")
            transparent.parent = frame

            # Create image texture node referencing image texture
            img_node = blender_utils.new_img_node(
                mat_tree.nodes, bake_name, self.tex_size
            )
            img_node.label = "DIFFUSE"
            img_node.select = True
            img_node.parent = frame
            mat_tree.nodes.active = img_node
            bpy.ops.object.bake()

            # Create Mix Shader node
            mix: ShaderNode = mat_tree.nodes.new("ShaderNodeMixShader")
            mix.parent = frame
            mix.hide = True
            mix.label = "SD Output"

            # Arrange nodes
            mix.location = ((output_node.location[0] - mix.width) - 20, y)
            lightpath.location = blender_utils.get_rel_loc(mix, -500, 250)
            img_node.location = blender_utils.get_rel_loc(mix, -500, -90)
            transparent.location = blender_utils.get_rel_loc(mix, -275, 25)
            uv.location = blender_utils.get_rel_loc(
                img_node, -(uv.width + 25), -img_node.height
            )

            # Connect nodes
            mat_tree.links.new(uv.outputs["UV"], img_node.inputs["Vector"])
            mat_tree.links.new(lightpath.outputs["Is Camera Ray"], mix.inputs["Fac"])
            mat_tree.links.new(transparent.outputs["BSDF"], mix.inputs[1])
            mat_tree.links.new(img_node.outputs["Color"], mix.inputs[2])
            mat_tree.links.new(mix.outputs["Shader"], output_node.inputs["Surface"])
        elif self.target_stucture == "MRPBR":
            frame.label = "(Marshalled) Metallic/Roughness PBR"

            # TODO: how to bake the different maps
            # TODO: clearcoat, transmisson, etc

            # Create emissive map image node
            emmisive = blender_utils.new_img_node(
                mat_tree.nodes, f"{bake_name}-EMISSIVE", self.tex_size
            )
            emmisive.label = "EMISSIVE"
            emmisive.select = True
            emmisive.parent = frame
            mat_tree.nodes.active = emmisive
            bpy.ops.object.bake()

            # Create Emission shader node
            emission = mat_tree.nodes.new("ShaderNodeEmission")
            emission.parent = frame

            # Create base color map image node
            base_color = blender_utils.new_img_node(
                mat_tree.nodes, f"{bake_name}-BASE_COLOR", self.tex_size, alpha=True
            )
            base_color.label = "BASE COLOR"
            base_color.select = True
            base_color.parent = frame
            mat_tree.nodes.active = base_color
            bpy.ops.object.bake()

            # Create Occlusion Roughness Metallic map image node
            orm = blender_utils.new_img_node(
                mat_tree.nodes, f"{bake_name}-ORM", self.tex_size, is_data=True
            )
            orm.label = "ORM"
            orm.select = True
            orm.parent = frame
            mat_tree.nodes.active = orm
            bpy.ops.object.bake()

            # Create SeparateRGB node for ORM map
            orm_split = mat_tree.nodes.new("ShaderNodeSeparateRGB")
            orm_split.parent = frame

            # Create glTF settings node for AO map
            settings = mat_tree.nodes.new("glTF Settings")
            settings.parent = frame

            # Create normal map image node
            normal = blender_utils.new_img_node(
                mat_tree.nodes, f"{bake_name}-NORMAL", self.tex_size, is_data=True
            )
            normal.label = "NORMAL"
            normal.select = True
            normal.parent = frame
            mat_tree.nodes.active = normal
            bpy.ops.object.bake()

            # Create Normal Map node
            normal_map = mat_tree.nodes.new("ShaderNodeNormalMap")
            normal_map.parent = frame

            # Create Principled BSDF node
            pbsdf = mat_tree.nodes.new("ShaderNodeBsdfPrincipled")
            pbsdf.parent = frame

            # Create Add Shader node
            add = mat_tree.nodes.new("ShaderNodeAddShader")
            add.parent = frame
            add.hide = True

            # Connect UV node
            mat_tree.links.new(uv.outputs["UV"], emmisive.inputs["Vector"])
            mat_tree.links.new(uv.outputs["UV"], base_color.inputs["Vector"])
            mat_tree.links.new(uv.outputs["UV"], orm.inputs["Vector"])
            mat_tree.links.new(uv.outputs["UV"], normal.inputs["Vector"])

            mat_tree.links.new(emmisive.outputs["Color"], emission.inputs["Color"])
            mat_tree.links.new(orm.outputs["Color"], orm_split.inputs["Image"])
            mat_tree.links.new(normal.outputs["Color"], normal_map.inputs["Color"])

            mat_tree.links.new(orm_split.outputs["R"], settings.inputs["Occlusion"])
            mat_tree.links.new(orm_split.outputs["G"], pbsdf.inputs["Roughness"])
            mat_tree.links.new(orm_split.outputs["B"], pbsdf.inputs["Metallic"])

            mat_tree.links.new(emission.outputs["Emission"], add.inputs[0])
            mat_tree.links.new(pbsdf.outputs["BSDF"], add.inputs[1])
            mat_tree.links.new(add.outputs["Shader"], output_node.inputs["Surface"])

        reset_cb(context)
        return {"FINISHED"}

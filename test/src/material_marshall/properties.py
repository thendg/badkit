from bpy.props import BoolProperty, EnumProperty

from ..utils.wrappers import CBPPropertyGroup

TARGET_STRUCTURE_ITEMS = [
    (
        "MRPBR",
        "Metallic/Roughness PBR Material",
        "Marhsall the current material into a Metallic/Roughness PBR Material.",
    ),
    (
        "SD",
        "Shadeless (unlit) Diffuse Material",
        "Marhsall the current material into a Shadeless (unlit) Diffuse Material.",
    ),
]


class MMProperties(CBPPropertyGroup):
    """
    A class holding the properties used by the Material Marshall operator.
    """

    bl_label = "Material Marshall Properties"
    bl_idname = "material_marshall_properties"

    target_stucture: EnumProperty(
        name="Target Material Structure",
        description="The desired material structure to marshall the material into.",
        items=TARGET_STRUCTURE_ITEMS,
        default=TARGET_STRUCTURE_ITEMS[0][0],
    )
    tex_size: EnumProperty(
        name="Texture Size",
        description="The size (in pixels) of textures if texture baking is required.",
        items=CBPPropertyGroup.get_map_sizes(map_type="material"),
        default=str(CBPPropertyGroup.MAP_SIZE_PWR_MIN),
    )
    overwrite: BoolProperty(
        name="Overwrite",
        description="Overwrite previously marshalled materials.",
        default=True,
    )

    @classmethod
    def get_props(cls) -> tuple[str]:
        return super().get_props(__file__)

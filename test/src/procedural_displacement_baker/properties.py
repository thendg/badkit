from bpy.props import BoolProperty, EnumProperty

from ..utils.wrappers import CBPPropertyGroup


class PDBProperties(CBPPropertyGroup):
    """
    A class holding the properties used by the Displacement Baker operator.
    """

    bl_label = "Displacement Baker Properties"
    bl_idname = "displacement_baker_properties"

    is_animated: BoolProperty(
        name="Animated",
        description="Should be selected only if the object has animated displacement. If the object is animated but the displacement is not, or object is completely static, this options should be left unchecked.",
        default=False,
    )
    disp_size: EnumProperty(
        name="Displacement Map Size",
        description="The size (in pixels) of intermediate displacement maps for prodedural displacement baking.",
        items=CBPPropertyGroup.get_map_sizes(map_type="displacement map"),
        default=str(CBPPropertyGroup.MAP_SIZE_PWR_MIN),
    )
    keep_original: BoolProperty(
        name="Keep Original", description="Keep the original object.", default=True
    )

    @classmethod
    def get_props(cls) -> tuple[str]:
        return super().get_props(__file__)

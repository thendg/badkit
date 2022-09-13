from typing import Type
import bpy.types as bpyt

from . import registerable
from .badkit_property_group import BADKitPropertyGroup


class BADKitPanel(bpyt.Panel, registerable.Registerable):
    """
    A wrapper for `bpy.types.Panel` implementing the Registerable base class and some helper methods.
    """

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    operator_idname: str
    props: Type[BADKitPropertyGroup]

    def draw(self, context: bpyt.Context):
        props = getattr(context.scene, self.props.bl_idname)
        col = self.layout.column()
        for propname in self.props.get_props():
            col.prop(props, propname)

        self.layout.operator(self.operator_idname)

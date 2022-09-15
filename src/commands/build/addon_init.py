from typing import Callable, Type

import bpy
from bpy.props import PointerProperty
from bpy.types import Context, Menu, PropertyGroup, Scene

from ...wrappers import registerable

# dictionary of operators to their draw functions
menu_funcs: dict[Type[registerable.Registerable], Callable[[Menu, Context], None]] = {}


def get_addon_classes() -> tuple[Type[registerable.Registerable]]:
    # TODO: load and return classes.pkl
    pass


# TODO: append blend data into Blender env on registration, remove un unregister


def register():
    "Register classes and append them to their associated menus."

    for cls in get_addon_classes():
        bpy.utils.register_class(cls)
        if issubclass(cls, PropertyGroup):
            setattr(Scene, cls.bl_idname, PointerProperty(type=cls))
        if cls.menu_target:
            menu_funcs[cls] = lambda caller, _context: caller.layout.operator(
                cls.bl_idname, text=cls.bl_label
            )
            cls.menu_target.append(menu_funcs[cls])
        print(f"[[CBP]] - Registered: {cls}")


def unregister():
    "Unregister classes and remove them from their associated menus."

    for cls in get_addon_classes():
        bpy.utils.unregister_class(cls)
        if issubclass(cls, PropertyGroup):
            delattr(Scene, cls.bl_idname)
        if cls.menu_target:
            cls.menu_target.remove(menu_funcs[cls])
        print(f"[[CBP]] - Unregistered: {cls}")


if __name__ == "__main__":
    register()

from typing import Any, Callable, Type
import pickle

import bpy
from bpy.props import PointerProperty
from bpy.types import Context, Menu, PropertyGroup, Scene

from badkit.wrappers import registerable


def unpickle(filename: str) -> Any:
    pkl = None
    with open(f"{filename}.pkl") as file:
        pkl = pickle.loads(file.read())
    return pkl


CLASSES: tuple[Type[registerable.Registerable]] = unpickle("classes")
# dictionary of operators to their draw functions
menu_funcs: dict[Type[registerable.Registerable], Callable[[Menu, Context], None]] = {}


def register():
    "Register classes and append them to their associated menus."

    for blend in unpickle("blend"):
        # TODO: append blend data into current file
        ...

    for cls in CLASSES:
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

    # TODO delete appended blend libraries to remove added blend data

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)
        if issubclass(cls, PropertyGroup):
            delattr(Scene, cls.bl_idname)
        if cls.menu_target:
            cls.menu_target.remove(menu_funcs[cls])
        print(f"[[CBP]] - Unregistered: {cls}")


if __name__ == "__main__":
    register()

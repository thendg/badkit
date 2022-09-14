import importlib
import os
import re
from typing import Optional, cast

from . import serializable
from .... import wrappers

# TODO: use dataclasses
# TODO: use privacy
# TODO: use tuple instead of list


def import_class(package: str, module: str):
    # TODO: this function currently assumes to be running in src dir
    mod_path = os.path.abspath(os.path.join(package, module + ".py"))
    if not os.path.exists(mod_path):
        raise FileNotFoundError(f"Failed to locate {package}.{module} at {mod_path}")
    cls: str = None
    with open(mod_path, "r") as mod_file:
        super_class = "BADKit" + module.capitalize()
        match = re.search(f"(?<=class )\w*(?=\({super_class}\):)", mod_file.read())
        if not match:
            raise ImportError(
                f"Failed to locate a subclass of {super_class} in {package}.{module} at {mod_path}"
            )
        cls = match.group()
    return importlib.import_module(f"{package}.{module}.{cls}")


class PanelData(serializable.Serializable):
    yaml_tag = "!Panel"

    def __init__(self, space: str, category: str) -> None:
        self.space = space
        self.category = category

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "space", "category"


class BlendData(serializable.Serializable):
    yaml_tag = "!Blend"

    def __init__(self, name: str, node_groups: list[str]) -> None:
        self.name = name
        self.node_groups = tuple(node_groups)

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "name", "node_groups"


class OperatorPackage(serializable.Serializable):
    yaml_tag = "!OperatorPackage"

    """A class representing the Python package containing classes of an operator to submit for registration in Blender."""

    def __init__(
        self,
        name: str,
        panel: Optional[PanelData] = None,
        blend: tuple[BlendData] = None,
    ) -> None:
        """
        Construct a Package object.

        :param operator: The operator class of the addon.
        :param properties: A custom property group class defined by the addon.
        :param panel: A panel class defined by the addon or a `PanelData` object.
        """

        self.name = name
        # TODO: currently Assumes to be running in src
        self.operator = cast(wrappers.BADKitOperator, import_class(name, "operator"))
        self.properties = cast(
            wrappers.BADKitPropertyGroup, import_class(name, "properties")
        )
        if panel:
            self.panel = type(
                self.operator.__name__ + "Panel",
                (wrappers.BADKitPanel,),
                {
                    "bl_label": self.operator.bl_label,
                    "bl_idname": f"{panel.space}_PT_{name}",
                    "bl_category": panel.category,
                    "bl_description": f"Panel for running the {self.operator.bl_label} operator.",
                    "operator_idname": self.operator.bl_idname,
                    "props": self.properties,
                },
            )
        else:
            self.panel = panel
        self.blend = blend

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "name", "panel", "blend"

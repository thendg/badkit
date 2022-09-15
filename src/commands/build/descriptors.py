from genericpath import exists
import importlib
import os
import re
from typing import Literal, Optional, Type, cast

import yaml

from ... import wrappers

# TODO: use dataclasses
# TODO: use privacy
# TODO: use tuple instead of list


def import_class(package: str, module: str, super_name: str):
    # TODO: this function currently assumes to be running in src dir
    mod_path = os.path.abspath(os.path.join(package, module + ".py"))
    if not os.path.exists(mod_path):
        raise FileNotFoundError(f"Failed to locate {package}.{module} at {mod_path}")
    cls: str = None
    with open(mod_path, "r") as mod_file:
        match = re.search(
            f"(?<=class )\w*(?=\((\w\.?)*\.?({super_name})\):)", mod_file.read()
        )
        if not match:
            raise ImportError(
                f"Failed to locate a subclass of {super_name} in {package}.{module} at {mod_path}"
            )
        cls = match.group()
    module = importlib.import_module(f"{package}.{module}")
    return getattr(module, cls)


class Serializable(yaml.YAMLObject):
    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        pass

    @classmethod
    def from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Serializable":
        # Set attributes to None if not in file
        values = loader.construct_mapping(node, deep=True)
        attr = cls.get_attrs()
        result = {}
        for val in attr:
            try:
                result[val] = values[val]
            except KeyError:
                result[val] = None
        return cls(**result)


class BLInfo(Serializable):
    yaml_tag = "!BLInfo"

    """A class to represent the metadata for a Blender addon."""

    def __init__(
        self,
        name: str,
        description: str,
        author: str,
        addon_version: list[int],
        blender_version: list[int],
        warning: str,
        doc_url: str,
        tracker_url: str,
        support: Literal["OFFICIAL", "COMMUNITY"],
    ) -> None:
        self.name = name
        self.description = description
        self.author = author
        self.addon_version = tuple(addon_version)
        self.blender_version = tuple(blender_version)
        self.warning = warning
        self.doc_url = doc_url
        self.tracker_url = tracker_url
        self.support = support

    def get_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "version": self.addon_version,
            "blender": self.blender_version,
            "warning": self.warning,
            "doc_url": self.doc_url,
            "tracker_url": self.tracker_url,
            "support": self.support,
        }

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return (
            "name",
            "description",
            "author",
            "addon_version",
            "blender_version",
            "warning",
            "doc_url",
            "tracker_url",
            "support",
        )


class Panel(Serializable):
    yaml_tag = "!Panel"

    def __init__(self, space: str, category: str) -> None:
        self.space = space
        self.category = category

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "space", "category"


class Operator(Serializable):
    yaml_tag = "!Operator"

    """A class representing the Python package containing classes of an operator to submit for registration in Blender."""

    def __init__(
        self,
        name: str,
        panel: Optional[Panel | str] = None,
    ) -> None:
        """
        Construct a Package object.

        :param operator: The operator class of the addon.
        :param properties: A custom property group class defined by the addon.
        :param panel: A panel class defined by the addon or a `PanelData` object.
        """

        self.name = name
        # TODO: currently Assumes to be running in src
        self.operator = cast(
            wrappers.BADKitOperator, import_class(name, "operator", "BADKitOperator")
        )
        try:
            self.properties = cast(
                wrappers.BADKitPropertyGroup,
                import_class(name, "properties", "BADKitPropertyGroup"),
            )
        except FileNotFoundError:
            self.properties = None

        if panel and isinstance(panel, Panel):
            if not self.properties:
                raise FileNotFoundError(
                    f"Panel generation was attempted but there are no properties defined for the operator {self.operator.bl_idname}."
                )
            self.panel: wrappers.BADKitPanel = type(
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

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "name", "panel"


class Blend(Serializable):
    yaml_tag = "!Blend"

    def __init__(self, name: str, node_groups: list[str]) -> None:
        self.name = name
        self.node_groups = tuple(node_groups)

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "name", "node_groups"


class Addon(Serializable):
    """A class representing an entire Blender addon."""

    yaml_tag = "!Addon"

    def __init__(
        self, bl_info: BLInfo, operators: list[Operator], blend: list[Blend]
    ) -> None:
        self.bl_info = bl_info
        self.operators = operators
        self.blend = blend

    def get_classes(self):
        return tuple(
            cls
            for operator in self.operators
            for cls in (operator.operator, operator.properties, operator.panel)
            if cls is not None
        )

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "bl_info", "operator_packages", "blend"


DESCRIPTOR_CLASSES: set[Type[yaml.YAMLObject]] = {
    BLInfo,
    Panel,
    Operator,
    Blend,
    Addon,
}

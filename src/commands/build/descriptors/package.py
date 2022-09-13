from typing import Type, Optional

import yaml

from .... import wrappers

# TODO: use dataclasses
# TODO: use privacy
# TODO: use tuple instead of list


class PanelData(yaml.YAMLObject):
    yaml_tag = "!Panel"

    def __init__(self, space: str, category: str) -> None:
        self.space = space
        self.category = category


class BlendData(yaml.YAMLObject):
    yaml_tag = "!Blend"

    def __init__(self, name: str, node_groups: list[str]) -> None:
        self.name = name
        self.node_groups = tuple(node_groups)


class Package(yaml.YAMLObject):
    yaml_tag = "!Package"

    """A class representing the Python package containing classes of an operator to submit for registration in Blender."""

    operator: Type[wrappers.BADKitOperator]
    properties: Optional[Type[wrappers.BADKitPropertyGroup]] = None
    panel: Optional[Type[wrappers.BADKitPanel]] = None

    def __init__(
        self,
        name: str,
        operator: Type[wrappers.BADKitOperator],
        properties: Optional[Type[wrappers.BADKitPropertyGroup]],
        panel: Optional[PanelData],
        blend: tuple[BlendData],
    ) -> None:
        """
        Construct a Package object.

        :param operator: The operator class of the addon.
        :param properties: A custom property group class defined by the addon.
        :param panel: A panel class defined by the addon or a `PanelData` object.
        """

        self.operator = operator
        self.properties = properties
        if panel:
            self.panel = type(
                operator.__name__ + "Panel",
                (wrappers.BADKitPanel,),
                {
                    "bl_label": operator.bl_label,
                    "bl_idname": f"{panel.space}_PT_{name}",
                    "bl_category": panel.category,
                    "bl_description": f"Panel for running the {operator.bl_label} operator.",
                    "operator_idname": operator.bl_idname,
                    "props": properties,
                },
            )
        else:
            self.panel = panel
        self.blend = blend

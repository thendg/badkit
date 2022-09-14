from typing import Literal

from . import operator_package, serializable


class BLInfo(serializable.Serializable):
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


class Addon(serializable.Serializable):
    yaml_tag = "!Addon"

    """A class representing an entire Blender addon."""

    def __init__(
        self,
        bl_info: BLInfo,
        operator_packagess: list[operator_package.OperatorPackage],
    ) -> None:
        self.bl_info = bl_info
        self.operator_packagess = operator_packagess

    @classmethod
    def get_attrs(cls) -> tuple[str, ...]:
        return "bl_info", "operator_packagess"

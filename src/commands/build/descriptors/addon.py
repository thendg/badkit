from typing import Literal

import yaml

from . import package


class BLInfo(yaml.YAMLObject):
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


class Addon(yaml.YAMLObject):
    yaml_tag = "!Addon"

    """A class representing an entire Blender addon."""

    def __init__(self, bl_info: BLInfo, packages: list[package.Package]) -> None:
        self.bl_info = bl_info
        self.packages = packages

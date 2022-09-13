import re
from bpy.types import PropertyGroup
from .registerable import Registerable


class BADKitPropertyGroup(PropertyGroup, Registerable):
    """
    A wrapper for `bpy.types.PropertyGroup` implementing the Registerable base class and some helper methods.
    """

    MAP_SIZE_PWR_MIN = 7
    MAP_SIZE_PWR_MAX = 13

    @staticmethod
    def get_map_sizes(map_type: str = "map") -> list[tuple[str]]:
        """
        Get a list of tuples with each tuple describing a texture size. Useful for creating size options with bpy.props.EnumProperty().

        :param map_type: The name used to describe the type of texture.
        """
        sizes = []

        for i in range(
            BADKitPropertyGroup.MAP_SIZE_PWR_MIN,
            BADKitPropertyGroup.MAP_SIZE_PWR_MAX + 1,
        ):
            px = pow(2, i)
            kpx = px / 1024
            sizes.append(
                (
                    str(i),
                    f"{px}px x {px}px",
                    f"Use {f'{int(kpx)}k' if (kpx) % 1 == 0 else f'{px}px'} {map_type} textures.",
                )
            )

        return sizes

    @classmethod  # classmethod instead of staticmethod so it can be overriden
    def get_props(cls, path: str) -> tuple[str]:
        """
        Get property names of a class from it's source file.

        :param path: The path to the source file.
        """

        with open(path) as file:
            # iterate file.readlines() so we don't have to read the whole file at once
            return tuple(
                [
                    match
                    for line in file.readlines()
                    for match in re.findall(r"\w+(?=:\ \w*)", line)
                ]
            )

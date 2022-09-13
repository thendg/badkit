from typing import Type

import yaml

from .addon import Addon, BLInfo
from .package import PanelData, BlendData, Package

CLASSES: set[Type[yaml.YAMLObject]] = {
    Addon,
    BLInfo,
    Package,
    PanelData,
    BlendData,
    Package,
}

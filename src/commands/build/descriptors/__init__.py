from typing import Type

import yaml

from .addon import Addon, BLInfo
from .operator_package import PanelData, BlendData, OperatorPackage

CLASSES: set[Type[yaml.YAMLObject]] = {
    Addon,
    BLInfo,
    OperatorPackage,
    PanelData,
    BlendData,
    OperatorPackage,
}

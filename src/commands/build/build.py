import os
import pickle
from typing import Callable, TypeVar
import zipfile

import click
import yaml

from .. import utils as cmd_utils
from . import descriptors
from ... import utils as badkit_utils, wrappers as badkit_wrappers

T = TypeVar("T")

SRC = "src"
BLEND = "blend"
ADDON = "addon.yaml"
BUILD = "build"


if False:  # Test switch
    SRC = os.path.join("test", SRC)
    ADDON = os.path.join("test", ADDON)
    BUILD = os.path.join("test", BUILD)

for descriptor in descriptors.DESCRIPTOR_CLASSES:
    yaml.SafeLoader.add_constructor(descriptor.yaml_tag, descriptor.from_yaml)


def run_in_dir(dir: str, func: Callable[[], T]) -> T:
    cwd = os.getcwd()
    os.chdir(dir)
    ret = func()
    os.chdir(cwd)
    return ret


def copy_to_zipf(zipf: zipfile.ZipFile, path: str, prefix: str = "") -> None:
    for root, _, files in os.walk(path):
        for file in files:
            zipf.write(
                os.path.join(root, file),
                arcname=os.path.join(prefix, root, file),
            )


@click.command()
def build() -> None:
    """Build an addon bundle from a specified source directory."""

    addon_path = os.path.abspath(ADDON)
    if not os.path.exists(addon_path):
        raise FileNotFoundError(f"Failed to find {ADDON}.")

    addon: descriptors.Addon = None
    with open(ADDON, "r") as addon_file:
        addon = run_in_dir(SRC, lambda: yaml.safe_load(addon_file))

    # Prepare names/paths
    build_dir = os.path.abspath(BUILD)
    build_path = f"{build_dir}{os.path.sep}{addon.bl_info.name}.zip".replace(
        " ", "-"
    ).lower()
    if os.path.exists(build_path):
        os.remove(build_path)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir, exist_ok=True)

    # Create archive
    with zipfile.ZipFile(build_path, "w") as bundle:
        bundle.write(
            os.path.join(
                os.path.dirname(__file__),
                "addon_init.py",
            ),
            arcname="__init__.py",
        )

        run_in_dir(SRC, lambda: copy_to_zipf(bundle, BLEND))
        copy_badkit_module_to_bundle: Callable[
            [str], None
        ] = lambda filename: run_in_dir(
            os.path.dirname(os.path.dirname(filename)),
            lambda: copy_to_zipf(
                bundle, os.path.basename(os.path.dirname(filename)), prefix="badkit"
            ),
        )
        copy_badkit_module_to_bundle(badkit_utils.__file__)
        copy_badkit_module_to_bundle(badkit_wrappers.__file__)

        bundle.writestr("classes.pkl", pickle.dumps(addon.get_classes()))
        bundle.writestr("blend.pkl", pickle.dumps(addon.blend))

    cmd_utils.log(
        f'Bundle built to "{os.path.abspath(build_path)}"',
        fg="white",
        bold=True,
    )

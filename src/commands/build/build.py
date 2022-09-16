import os
import pickle
import zipfile

import click
import yaml

from .. import logger
from . import descriptors

SRC = "src"
BLEND = "blend"
ADDON = "addon.yaml"
BUILD = "build"

for descriptor in descriptors.DESCRIPTOR_CLASSES:
    yaml.SafeLoader.add_constructor(descriptor.yaml_tag, descriptor.from_yaml)


@click.command()
def build() -> None:
    """Build an addon bundle from a specified source directory."""

    src_dir = os.path.abspath("test/" + SRC)
    addon_path = os.path.abspath("test/" + ADDON)
    if not os.path.exists(addon_path):
        raise FileNotFoundError(f"Failed to find {ADDON}.")

    addon: descriptors.Addon = None
    with open(addon_path, "r") as addon_file:
        cwd = os.getcwd()
        os.chdir(src_dir)
        addon = yaml.safe_load(addon_file)
        os.chdir(cwd)

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
        for root, _, files in os.walk(os.path.join(src_dir, BLEND)):
            for file in files:
                bundle.write(
                    os.path.join(src_dir, BLEND, root, file),
                    arcname=os.path.join(root, file),
                )
        # TODO: Can't pickle <class 'src.commands.build.descriptors.MMOperatorPanel'>: attribute lookup MMOperatorPanel on src.commands.build.descriptors failed
        # the type() constructor used in src.build.descriptors:165 assigns the generated Panel type to the descriptors module, rather than the operator that the panel belongs to
        # this is why the error says it <class 'src.commands.build.descriptors.MMOperatorPanel'> instead of <class 'src.commands.build.descriptors.Operator.MMOperatorPanel'>
        # research here: https://stackoverflow.com/questions/4677012/python-cant-pickle-type-x-attribute-lookup-failed
        bundle.writestr("classes.pkl", pickle.dumps(addon.get_classes()))
        bundle.writestr("blend.pkl", pickle.dumps(addon.blend))

    logger.log(
        f'Bundle built to "{os.path.abspath(build_path)}"\n',
        fg="white",
        bold=True,
    )

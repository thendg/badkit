import os
import zipfile

import click
import yaml

from . import consts, descriptors

for descriptor in descriptors.CLASSES:
    yaml.SafeLoader.add_constructor(descriptor.yaml_tag, descriptor.from_yaml)


@click.command()
@click.option(
    "-a",
    "--addon-path",
    type=click.Path(exists=True, dir_okay=False),
    default="./src/addon.yaml",
    help="The path to the source directory of the addon.",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False),
    default="./build",
    help="The path of the containing directory to write the addon bundle to.",
    show_default=True,
)
def build(
    addon_path: click.Path,
    output: click.Path,
) -> None:
    """Build an addon bundle from a specified source directory."""

    addon_path = os.path.abspath(addon_path)
    addon_dir = os.path.dirname(addon_path)
    os.chdir(addon_dir)
    addon: descriptors.addon.Addon = None
    with open(addon_path, "r") as addon_file:
        os.chdir(os.path.join(addon_dir, consts.SRC))
        addon = yaml.safe_load(addon_file)

    # Prepare names/paths
    build_path = output + ".zip"
    print(os.path.abspath(build_path))
    # Delete old bundle
    if os.path.exists(build_path):
        os.remove(build_path)
    else:
        os.makedirs(os.path.dirname(output), exist_ok=True)

    # Create archive
    with zipfile.ZipFile(build_path, "w") as bundle:
        for operator_package in addon.operator_packagess:
            bundle_write = lambda name: bundle.write(
                os.path.join(addon_dir, consts.SRC, operator_package.name, name),
                arcname=os.path.join(operator_package.name, name),
            )
            bundle_write("operator.py")
            if operator_package.properties:
                bundle_write("properties.py")
            if operator_package.blend:
                for _, _, files in os.walk(
                    os.path.join(operator_package.name, "blend")
                ):
                    for blend in files:
                        bundle_write(blend)
        # TODO: copy __init__.py file into bundle
        # TODO: append blend data into Blender env on registration, remove un unregister

    print(f'Bundle built to "{build_path}".\n')

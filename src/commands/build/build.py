import os
import zipfile

import click
import yaml

from . import descriptors

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

    addon: descriptors.addon.Addon = None
    with open(addon_path, "r") as addon_file:
        addon = yaml.safe_load(addon_file)

    os.chdir(addon.name)

    # Prepare names/paths
    build_path = output + ".zip"

    # Delete old bundle
    if os.path.exists(build_path):
        os.remove(build_path)
    else:
        os.makedirs(os.path.dirname(output), exist_ok=True)

    # TODO: add custom __init__.py to addon bundle

    # Create archive
    with zipfile.ZipFile(build_path, "w") as bundle:
        for file in include:
            bundle.write(file, arcname=os.path.join(name, file))

    print(f'Bundle built to "{build_path}".\n')

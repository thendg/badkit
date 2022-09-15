import os
import pickle
import zipfile

import click
import yaml

from . import consts, descriptors

for descriptor in descriptors.DESCRIPTOR_CLASSES:
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
    addon: descriptors.Addon = None
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
        bundle.write(
            os.path.join(
                os.path.dirname(__file__),
                "addon_init.py",
            ),
            arcname="__init__.py",
        )
        for root, _, files in os.walk(
            os.path.join(addon_dir, consts.SRC, consts.BLEND)
        ):
            for file in files:
                bundle.write(
                    os.path.join(addon_dir, consts.BLEND, root, file),
                    arcname=os.path.join(root, file),
                )
        # TODO: Can't pickle <class 'src.commands.build.descriptors.MMOperatorPanel'>: attribute lookup MMOperatorPanel on src.commands.build.descriptors failed
        # the type() constructor used in src.build.descriptors:165 assigns the generated Panel type to the descriptors module, rather than the operator that the panel belongs to
        # this is why the error says it <class 'src.commands.build.descriptors.MMOperatorPanel'> instead of <class 'src.commands.build.descriptors.Operator.MMOperatorPanel'>
        # research here: https://stackoverflow.com/questions/4677012/python-cant-pickle-type-x-attribute-lookup-failed
        bundle.writestr("classes.pkl", pickle.dumps(addon.get_classes()))
        bundle.writestr("blend.pkl", pickle.dumps(addon.blend))

    print(f'Bundle built to "{build_path}".\n')

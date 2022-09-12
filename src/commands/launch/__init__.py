import subprocess

import click

from . import bootloader


@click.command()
@click.option(
    "--blender",
    type=click.Path(dir_okay=False, exists=True),
    default="blender",
    help="A path to the Blender executable (or an alias for it). If provided, a Blender environment will be launched using this exectuable, otherwise no Blender environment will be launched and the addon bundle will only be built.",
    show_default=True,
)
@click.option(
    "--file",
    type=click.Path(dir_okay=False, exists=True),
    help="A path to a file that should be opened on launch.",
)
@click.argument(
    "addons",
    type=click.Path(file_okay=False, exists=True),
    nargs=-1,
)
def launch(blender: str, file: click.Path, addons: list[click.Path]) -> None:
    """
    Launch a Blender environment with a set of custom addons (specified in ADDONS) installed and enabled. ADDONS should be specified last since all following tokens will be collected into it's value.
    """

    subprocess.run(
        [
            blender,
            file if file else "",
            "--python",
            bootloader.__file__,
            "--",
            *addons,
        ]
    )

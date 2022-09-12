import glob
import os
from typing import Callable
import zipfile

import click

SEPARATOR = ";"

splitter: Callable[[str], list[str]] = lambda s: s.split(SEPARATOR)


@click.command()
@click.option(
    "--build",
    type=click.Path(exists=True, file_okay=False),
    default="./src",
    help="The path to the source directory of the addon.",
    show_default=True,
)
@click.option(
    "--output",
    type=click.Path(file_okay=False),
    default="./build",
    help="The path of the containing directory to write the addon bundle to.",
    show_default=True,
)
@click.option(
    "--name",
    type=str,
    required=True,
    help="The name of the addon bundle.",
)
@click.option(
    "--file",
    type=click.Path(dir_okay=False, exists=True),
    help="A path to a file that should be opened on launch.",
)
@click.option(
    "--include",
    type=str,
    default="py",
    callback=splitter,
    help=f"A {SEPARATOR} separated list of file extensions to include in the addon bundle.",
    show_default=True,
)
@click.option(
    "--exclude",
    type=str,
    callback=splitter,
    help=f"A {SEPARATOR} separated list of glob patterns to ignore in the addon bundle.",
)
@click.option(
    "--blender",
    type=click.Path(exists=True, dir_okay=False),
    help="A path to the Blender executable (or an alias for it). If provided, a Blender environment will be launched using this exectuable, otherwise no Blender environment will be launched and the addon bundle will only be built.",
)
def build(
    src: click.Path,
    output: click.Path,
    name: str,
    file: click.Path,
    include: list[str],
    exclude: list[str],
) -> None:
    """Build an addon bundle from a specified source directory."""

    os.chdir(src)

    # Delete old bundle
    build_path = os.path.join(output, f"{name}.zip")
    if os.path.exists(build_path):
        os.remove(build_path)
    else:
        os.makedirs(output, exist_ok=True)

    # TODO: read from addon.yaml, this way we don't need include/exclude
    # TODO: add custom __init__.py to addon bundle

    # Get excluded files
    excluded = []
    for e in exclude:
        excluded += glob.glob(f"**/{e}", recursive=True)

    # Get included files
    included = []
    for ext in include:
        for file in glob.glob(f"**/*.{ext}", recursive=True):
            if file not in excluded:
                included.append(file)

    # Create archive
    with zipfile.ZipFile(build_path, "w") as bundle:
        for file in include:
            bundle.write(file, arcname=os.path.join(name, file))

    print(f'Bundle built to "{build_path}".\n')

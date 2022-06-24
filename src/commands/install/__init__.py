import subprocess
import os

import click


@click.command()
@click.argument("pkg-name", type=str)
def install(pkg_name: str) -> None:
    """Locally install a distribution package from PyPI."""
    subprocess.run(
        ["pip", "install", pkg_name, "-t", os.path.join("src", "vendor", pkg_name)]
    )

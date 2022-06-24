import click

from .commands import build, install, launch


@click.version_option("0.0.1")
@click.group()
def cli() -> None:
    """
    BADKit: The Blender Addon Development Kit. A proper framework for addon development in Blender.

    - 2022 NOIR Development Group
    """
    pass


def main() -> None:
    """Entry point function for the program."""

    cli.add_command(build)
    cli.add_command(install)
    cli.add_command(launch)
    cli(prog_name="badkit")


if __name__ == "__main__":
    main()

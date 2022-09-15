import click

from .commands import build, install, launch

# TODO: add fake-bpy-module install instructions to README. I would have liked to install it automatically but we don't know which version of blender they're using
# - maybe we could infer it from the Blender version in the addon.yaml file?
# Add a command to perform static type checks on the addon before each build
# - make sure the type check still uses their mypy config if the have one


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

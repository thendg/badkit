from typing import Any, Callable
import click
import datetime

# TODO: implement
log: Callable[[str, Any], None] = lambda message, **kwargs: click.secho(
    f'[{datetime.datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))}] BADKit: ' + message,
    **kwargs,
)

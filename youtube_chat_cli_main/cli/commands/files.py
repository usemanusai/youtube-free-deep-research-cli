"""File CLI commands."""

import click


@click.group()
def files():
    """File commands."""
    pass


__all__ = ["files"]


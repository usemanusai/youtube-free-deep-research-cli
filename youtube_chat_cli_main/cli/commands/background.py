"""Background service CLI commands."""

import click


@click.group()
def background():
    """Background service commands."""
    pass


__all__ = ["background"]


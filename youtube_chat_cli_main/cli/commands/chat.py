"""Chat CLI commands."""

import click


@click.group()
def chat():
    """Chat commands."""
    pass


__all__ = ["chat"]


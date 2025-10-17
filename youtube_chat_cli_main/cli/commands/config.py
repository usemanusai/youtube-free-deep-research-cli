"""Configuration CLI commands."""

import click


@click.group()
def config():
    """Configuration commands."""
    pass


__all__ = ["config"]


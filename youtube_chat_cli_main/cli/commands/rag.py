"""RAG CLI commands."""

import click


@click.group()
def rag():
    """RAG commands."""
    pass


@rag.command()
def chat():
    """Interactive RAG chat."""
    click.echo("Chat command")


__all__ = ["rag"]


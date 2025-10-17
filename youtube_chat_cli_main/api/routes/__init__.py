"""API route modules."""

from . import health
from . import chat
from . import files
from . import search
from . import config
from . import background

__all__ = [
    "health",
    "chat",
    "files",
    "search",
    "config",
    "background",
]


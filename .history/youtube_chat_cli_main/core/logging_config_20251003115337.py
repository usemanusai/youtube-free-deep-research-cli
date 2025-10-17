"""Structured logging configuration using structlog.

Provides JSON logs in production and pretty console logs in development.
Environment variables:
- LOG_LEVEL: logging level (default: INFO)
- LOG_FORMAT: json|pretty (default: json)
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any, Dict

import structlog


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, level_name, logging.INFO)
    log_format = os.getenv("LOG_FORMAT", "json").lower()

    # Reset basicConfig to avoid duplicate handlers
    root = logging.getLogger()
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    # Tame noisy loggers
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if log_format == "pretty":
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # JSON with orjson
        def _orjson_dumps(obj: Dict[str, Any], **kwargs):
            import orjson
            default = kwargs.get("default")
            return orjson.dumps(obj, default=default).decode()

        renderer = structlog.processors.JSONRenderer(serializer=_orjson_dumps)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Bridge stdlib logging to structlog
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    ))
    root.addHandler(handler)
    root.setLevel(log_level)

    # Add baseline context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(service="jaegis-api")


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name or __name__)


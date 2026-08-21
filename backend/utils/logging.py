"""Structured logging helpers used across the backend.

Every log message written through :func:`get_logger` is prefixed with the
``studysync`` logger name so that the ``LOGGING`` configuration in
``config/settings.py`` picks it up on both console and rotating file handlers.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

_LOGGER_NAME = 'studysync'


def get_logger(name: str = 'studysync') -> logging.Logger:
    """Return a logger instance for the given module name.

    Args:
        name: The module/component name to attach to the logger.

    Returns:
        A configured :class:`logging.Logger`.
    """
    return logging.getLogger(f'{_LOGGER_NAME}.{name}')


def log_event(
    name: str,
    event: str,
    level: str = 'info',
    **context: Any,
) -> None:
    """Emit a structured event log line.

    Args:
        name: Component name (e.g. ``authentication``, ``students``).
        event: Short event label (e.g. ``student_registered``).
        level: One of ``debug``, ``info``, ``warning``, ``error``, ``critical``.
        **context: Arbitrary key/value pairs attached to the message.
    """
    logger = get_logger(name)
    message = f'{event} :: {_format_context(context)}'
    getattr(logger, level, logger.info)(message)


def _format_context(context: Dict[str, Any]) -> str:
    """Render a context dict as a compact ``key=value`` string."""
    if not context:
        return ''
    return ' '.join(f'{key}={value!r}' for key, value in context.items())


__all__ = ['get_logger', 'log_event']

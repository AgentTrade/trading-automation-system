"""
Logging configuration for the trading automation system.

Provides consistent application logging without exposing
credentials or sensitive account information.
"""

import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide logging."""

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for a module."""

    return logging.getLogger(name)

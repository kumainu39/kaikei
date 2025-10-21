"""Configure project-wide logging."""
from __future__ import annotations

import logging
from logging.config import dictConfig


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


def setup_logging() -> None:
    dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).debug("Logging configured")

"""
Centralized Logging Configuration.

Configures application-wide logging with stream (console) and
rotating file handlers. Ensures secrets or sensitive tokens are not logged.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


class SecretRedactingFormatter(logging.Formatter):
    """Custom formatter that redacts sensitive keywords from log output."""

    SENSITIVE_KEYS = ("API_KEY", "SECRET", "PASSWORD", "TOKEN", "AUTH")

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        for key in self.SENSITIVE_KEYS:
            if key in formatted:
                # Redact potential key=value or key:value patterns
                import re

                formatted = re.sub(
                    rf"({key}[\s:=]+)[^\s,;&]+",
                    r"\1[REDACTED]",
                    formatted,
                    flags=re.IGNORECASE,
                )
        return formatted


def configure_logging(level: str | None = None) -> None:
    """
    Configure root logging with console and rotating file handlers.
    """
    log_level_str = level or settings.log_level
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    formatter = SecretRedactingFormatter(
        log_format, datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. Rotating File Handler
    try:
        settings.logs_dir.mkdir(parents=True, exist_ok=True)
        file_path = settings.log_file

        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not initialize log file handler: {e}")

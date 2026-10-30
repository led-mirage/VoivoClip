# VoivoClip
#
# Application logging configuration
#
# Copyright (c) 2024-2026 led-mirage
# This source code is licensed under the MIT License.

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys


LOGGER_NAME = "VoivoClip"
LOG_DIRECTORY_NAME = "logs"
LOG_FILE_NAME = "VoivoClip.log"
MAX_LOG_FILE_SIZE = 1024 * 1024
LOG_BACKUP_COUNT = 3


def get_application_directory() -> Path:
    """Return the directory containing the executable or project."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_log_file_path() -> Path:
    """Return the path of the application log file."""
    return get_application_directory() / LOG_DIRECTORY_NAME / LOG_FILE_NAME


def setup_logging(level: int = logging.INFO) -> Path | None:
    """Configure application logging and return the log file path.

    If the log file cannot be created, logging is disabled and None is
    returned so that a logging failure does not prevent application startup.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    log_file_path = get_log_file_path()

    for handler in logger.handlers:
        if (
            isinstance(handler, RotatingFileHandler)
            and Path(handler.baseFilename) == log_file_path
        ):
            handler.setLevel(level)
            return log_file_path

    try:
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            log_file_path,
            maxBytes=MAX_LOG_FILE_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError:
        if not logger.handlers:
            logger.addHandler(logging.NullHandler())
        return None

    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] [%(threadName)s] %(message)s"
        )
    )
    logger.addHandler(handler)
    return log_file_path


def get_logger(name: str) -> logging.Logger:
    """Return a child logger of the VoivoClip application logger."""
    if name == LOGGER_NAME or name.startswith(f"{LOGGER_NAME}."):
        logger_name = name
    else:
        logger_name = f"{LOGGER_NAME}.{name}"
    return logging.getLogger(logger_name)


def get_active_log_file_path() -> Path | None:
    """Return the active log file path, or None if file logging is unavailable."""
    logger = logging.getLogger(LOGGER_NAME)

    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            return Path(handler.baseFilename)

    return None

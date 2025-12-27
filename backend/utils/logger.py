import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

"""
This module sets up a logger that writes logs to both a rotating file and the console.
The log file is created in the parent directory of this script as 'log.log'.
"""

log_path = Path(__file__).parent.parent / "log.log"
log_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure log directory exists


def setup_logger(name: str = __name__):
    """
    Creates and configures a logger with both file and stream handlers.
    Uses rotating file handler to limit log file size and backups.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:  # Prevent adding handlers multiple times
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler = RotatingFileHandler(
            log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger


def get_logger(name):
    """this func ensures each file has its own logger name"""
    return setup_logger(name)

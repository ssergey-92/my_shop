"""Module for creation app logger."""

from os import path as os_path, getenv as os_getenv
from pathlib import Path
from logging import Formatter, Logger, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler


def get_logs_dir_path() -> str:
    """Get logs saving path."""

    log_path = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        os_getenv("BASE_LOGGER_DIR_NAME"),
    )

    return os_path.abspath(log_path)


def get_stream_handler() -> StreamHandler:
    """Create stream handler for logger."""

    stream_handler = StreamHandler()
    stream_handler.setLevel(os_getenv("BANK_LOGGER_CONSOLE_HANDLER_LEVEL"))
    formatter = Formatter(
        "*** "
        "%(asctime)s | %(name)s | %(funcName)s | %(levelname)s | %(message)s",
    )
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_rotating_file_handler() -> RotatingFileHandler:
    """Create rotating file handler for logger."""

    logs_path = get_logs_dir_path()
    create_directory(logs_path)
    logs_file_path = os_path.join(
        logs_path, os_getenv("BANK_LOGGER_FILE_NAME")
    )
    rotating_file_handler = RotatingFileHandler(
        filename=logs_file_path,
        mode="a",
        maxBytes=int(os_getenv("BASE_LOGGER_FILE_SIZE")),
        backupCount=int(os_getenv("BASE_LOGGER_BACKUP_COUNT")),
        encoding=os_getenv("ENCODING"),
    )
    rotating_file_handler.setLevel(os_getenv("BANK_LOGGER_FILE_HANDLER_LEVEL"))
    formatter = Formatter(
        "%(asctime)s|%(name)s|%(funcName)s|%(levelname)s|%(message)s",
    )
    rotating_file_handler.setFormatter(formatter)
    return rotating_file_handler


def create_directory(abs_path: str) -> None:
    """Create path if it is not existed."""

    Path(abs_path).mkdir(parents=True, exist_ok=True)


def get_app_logger(logger_name: str) -> Logger:
    """Create app logger."""

    logger = getLogger(logger_name)
    logger.handlers.clear()
    for i_handler in (get_stream_handler(), get_rotating_file_handler()):
        logger.addHandler(i_handler)
    logger.setLevel(os_getenv("BANK_LOGGER_LEVEL"))
    return logger


app_logger = get_app_logger("my_bank")
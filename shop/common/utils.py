from os import chmod as os_chmod, remove as os_remove

from .custom_logger import app_logger

server_error = {"error": "Internal server error!"}


def delete_file_from_sys(file_path: str) -> None:
    try:
        os_chmod(file_path, 0o777)
        os_remove(file_path)
        app_logger.debug(f"File {file_path=} was deleted!")
    except FileNotFoundError:
        app_logger.error(f"{file_path=} is not existed in sys!")
    except PermissionError:
        app_logger.error(f"Permission error for {file_path=}!")
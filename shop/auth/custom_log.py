from os import getenv as os_getenv
from logging import getLogger

from .apps import AuthConfig

app_logger_name = "{}_{}".format(
    os_getenv("DC_SHOP_SERVICE_NAME"), AuthConfig.name,
)
app_logger = getLogger(app_logger_name)
app_logger.info(f"Logger {app_logger_name} is created.")

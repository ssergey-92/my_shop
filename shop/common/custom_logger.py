from os import getenv as os_getenv
from logging import getLogger


app_logger_name = "{}_logger".format(os_getenv("DC_SHOP_SERVICE_NAME"))
app_logger = getLogger(app_logger_name)
app_logger.info(f"Logger {app_logger_name} is created.")

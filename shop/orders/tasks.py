"""Module with tasks for Celery."""

from cryptography.fernet import Fernet
from json import dumps as json_dumps, loads as json_loads
from os import getenv as os_getenv
from redis import StrictRedis
from requests import post
from requests.exceptions import Timeout
from traceback import print_exception

from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger

from .constants import ORDER_STATUSES, ORDER_PAYMENT_CHANNEL

celery_logger = get_task_logger("celery_logger")
redis_client = StrictRedis(
    username=os_getenv("REDIS_USERNAME"),
    password=os_getenv("REDIS_PASSWORD"),
    host=settings.REDIS_HOST,
    port=os_getenv("REDIS_PORT"),
    db=os_getenv("REDIS_BROKER_DB"),
)

bank_url = "http://{host}:{port}/users/payment".format(
    host=os_getenv("DC_BANK_SERVICE_NAME"), port=os_getenv("BANK_PORT")
)
fernet = Fernet(bytes(os_getenv("PAYMENT_KEY"), os_getenv("ENCODING")))


@shared_task(ignore_result=True)
def conduct_order_payment(order_id: int, payment_details: dict) -> None:
    """Conduct payment for order.

    Encrypt card details and sent payment request to bank. Decrypt response
    data and publish payment details in redis channel.

    """
    celery_logger.info(f"{order_id=}, {payment_details=}")
    order_status = ORDER_STATUSES["payment_rejected"]
    details = {}
    try:
        data = json_dumps(payment_details).encode(os_getenv("ENCODING"))
        encrypted_data = fernet.encrypt(data)
        response = post(url=bank_url, data=encrypted_data, timeout=7)
        if response.status_code == 200:
            order_status = ORDER_STATUSES["payed"]
        decrypted_data = fernet.decrypt(response.text)
        details = json_loads(decrypted_data)
    except Timeout:
        details = {"msg": f"Bank is not responding!"}
    except Exception as exc:
        celery_logger.error(f"{print_exception(exc)}")
        details = {"msg": "Internal Server Error"}
    finally:
        msg = json_dumps(
            {
                "order_id": order_id,
                "order_status": order_status,
                "details": details,
            }
        )
        redis_client.publish(channel=ORDER_PAYMENT_CHANNEL, message=msg)

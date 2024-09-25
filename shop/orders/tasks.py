from cryptography.fernet import Fernet
from json import dumps as json_dumps
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


@shared_task(ignore_result=True)
def conduct_order_payment(order_id: int, card_details: dict) -> None:
    """Conduct payment for order.

    Encrypt card details and sent payment request to bank. Decrypt response
    data and publish payment details in redis.

    """
    celery_logger.info(f"{order_id=}, {card_details=}")
    order_status = ORDER_STATUSES["payment_rejected"]
    details = {}
    try:
        # fernet = Fernet(bytes(os_getenv("PAYMENT_KEY"), os_getenv("ENCODING")))
        # data = fernet.encrypt(
        #     json_dumps(card_details).encode(os_getenv("ENCODING")),
        # )
        # response = post(os_getenv("BANK_URL"), data=data, timeout=7)
        # if response.status_code == 200:
        #     order_status = ORDER_STATUSES["payed"]
        #
        # response_data = fernet.decrypt(response.text)
        # details = {"msg": response_data}

        details = {"msg": "TODO"}
    except Timeout:
        details = {"msg": f"Bank is not responding!"}
    except Exception as exc:
        celery_logger.error(f"{print_exception(exc)}")
        details = {"msg": "Internal Server Error"}
    finally:
        celery_logger.info(f"{order_id=}, {order_status=}, {details=}")
        msg = json_dumps(
            {"order_id": order_id, "order_status": order_status, "details": details}
        )
        redis_client.publish(channel=ORDER_PAYMENT_CHANNEL, message=msg)

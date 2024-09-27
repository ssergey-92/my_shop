from json import loads as json_loads
from traceback import print_exception

from .constants import ORDER_PAYMENT_CHANNEL
from .tasks import redis_client
from common.custom_logger import app_logger


def listen_order_payment_status() -> None:
    """Listen signals from Redis channel 'order_payment_channel'.

    If received msg 'message' then decode and dumps channel msg and change
    order status.

    """
    from .services import PaymentHandler

    pubsub = redis_client.pubsub()
    pubsub.subscribe(ORDER_PAYMENT_CHANNEL)
    app_logger.debug(f"Subscribe to channel: {ORDER_PAYMENT_CHANNEL=}")
    try:
        for msg in pubsub.listen():
            app_logger.debug(f"Received {msg=} from {ORDER_PAYMENT_CHANNEL=}")
            if msg['type'] == 'message':
                data = json_loads(msg["data"])
                PaymentHandler.update_order_payment_details(data)
    except Exception as exc:
        app_logger.error(print_exception(exc))

"""Module with constants for app 'Orders'."""

ORDER_STATUSES = {
    "created": "created",
    "confirmed": "confirmed",
    "payment_in_progress": "payment in progress",
    "payment_rejected": "payment rejected",
    "payed": "payed",
}

ORDER_PAYMENT_CHANNEL = "order_payment_channel"
CARD_NUMBER_LENGTH = 16
CARD_CODE_LENGTH = 3

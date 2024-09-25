import traceback

from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .order import unexsist_order_error
from common.custom_logger import app_logger
from common.utils import server_error
from orders.exceptions import OrderException
from orders.models import Order, OrderStatus
from orders.serializers import PaymentCardSerializer
from orders.tasks import conduct_order_payment


class PaymentHandler:
    _payment_in_progress_status = (
        OrderStatus.objects.get(name='payment in progress')
    )
    _payed_status = OrderStatus.objects.get(name="payed")
    _rejected_payment_status = OrderStatus.objects.get(name="payment rejected")

    @classmethod
    def pay_order(cls, request: Request, order_id: int) -> Response:
        try:
            card_details = PaymentCardSerializer(data=request.data)
            if not card_details.is_valid():
                raise ValidationError(card_details.errors)

            cls._update_order_satus(order_id, cls._payment_in_progress_status)
            conduct_order_payment.delay(
                order_id=order_id, card_details=card_details.data,
            )
            return Response({"msg": "Processing payment"}, HTTP_200_OK)
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def update_order_status(cls, payment_result: dict, ):
        try:
            if payment_result['order_status'] == "payed":
                order_status = cls._payed_status
            else:
                order_status = cls._rejected_payment_status

            cls._update_order_satus(payment_result['order_id'], order_status)
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))

    @staticmethod
    def _update_order_satus(order_id: int, order_status: OrderStatus) -> None:
        with transaction.atomic():
            order = (
                Order.objects.select_for_update().
                filter(pk=order_id).
                first()
            )
            if not order:
                raise OrderException(
                    unexsist_order_error.format(id=order_id)
                )

            order.status = order_status
            order.save()



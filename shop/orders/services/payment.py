import traceback

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from common.custom_logger import app_logger
from common.utils import server_error
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
        """Handle logic to pay user's order by card.

        Validate user card details. If valid update order status and call
        func to conduct payment with bank. Return corresponding response.

        """
        try:
            card_details = PaymentCardSerializer(data=request.data)
            if not card_details.is_valid():
                raise ValidationError(card_details.errors)

            payment_details = card_details.data
            payment_details["charge_price"] = float(
                Order.objects.filter(id=order_id)
                .values_list("total_cost", flat=True)[0]
            )
            (
                Order.objects.filter(id=order_id).
                update(status=cls._payment_in_progress_status)
            )
            conduct_order_payment.delay(order_id, payment_details)
            return Response({"msg": "Processing payment"}, HTTP_200_OK)
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def update_order_payment_details(cls, payment_result: dict):
        """Update order payment details bases of payment result."""

        try:
            payment_comment = None
            if payment_result['order_status'] == "payed":
                order_status = cls._payed_status
            else:
                order_status = cls._rejected_payment_status
                payment_comment = payment_result["details"].get("msg", None)
            (
                Order.objects.filter(id=payment_result['order_id']).
                update(status=order_status, payment_comment=payment_comment)
            )
        except Exception as exc:
            app_logger.error(traceback.print_exception(exc))

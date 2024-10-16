"""Module contains endpoints for app."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from .services import BasketHandler, OrderHandler, PaymentHandler


class BasketView(APIView):

    def get(self, request: Request) -> Response:
        """Get products from user's bucket."""

        return BasketHandler.get_basket(request)

    def post(self, request: Request) -> Response:
        """Add or increase quantity of product in user's bucket."""

        return BasketHandler.add_product(request)

    def delete(self, request: Request) -> Response:
        """Delete or reduce quantity of product in user's bucket."""

        return BasketHandler.remove_product(request)


class OrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, id: int = None) -> Response:
        """Get order by id if set else get active user's orders."""

        if id:
            return OrderHandler.get_order_by_id(id)

        return OrderHandler.get_user_orders(request.user)

    def post(self, request: Request, id: int = None) -> Response:
        """Confirm order if id is set else create order."""

        if id:
            return OrderHandler.confirm_order(request.data, id)

        return OrderHandler.create_init_order(
            request.data, request.user, request.session,
        )


class PaymentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, id: int) -> Response:
        """Pay order by id."""

        return PaymentHandler.pay_order(request.data, id)

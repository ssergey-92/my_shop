"""Module contains endpoints for app."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from orders.services import BasketHandler


class BasketAPIView(APIView):

    def get(self, request: Request) -> Response:
        """Get products from user's bucket."""

        return BasketHandler.get_basket(request)


    def post(self, request: Request) -> Response:
        """Add or increase quantity of product in user's bucket."""

        return BasketHandler.add_product(request)

    def delete(self, request: Request) -> Response:
        """Delete or reduce quantity of product in user's bucket."""

        return BasketHandler.remove_product(request)

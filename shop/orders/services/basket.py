from traceback import format_exc as tb_format_exc

from django.core.cache import cache
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
from orders.serializers import BasketAddItemSerializer, BucketProductSerializer
from products.models import Product


class BasketHandler:
    """Class for handling business logic bucket related endpoints."""

    @classmethod
    def add_product(cls, request: Request) -> Response:
        """Handle logic to add or increase quantity of product in bucket.

        Steps:
        - remove cashed response
        - validate request body
        - add or increase quantity of product in bucket
        - cached succeed response
        - return corresponding response

        """
        try:
            cache.delete(request.session.get("basket"))
            product = BasketAddItemSerializer(data=request.data)
            product.is_valid(raise_exception=True)
            cls._add_product_to_user(product.data, request)
            user_basket = cls._get_user_basket(request)
            response = (user_basket, HTTP_200_OK)
            cache.set(request.session["basket"], response, 360)
            return Response(*response)
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def get_basket(cls, request: Request) -> Response:
        """Handle logic to get bucket products.

        Return cached response if found. Else get bucket products, cached
        and return response.

        """
        try:
            cached_response = cache.get(request.session.get("basket"))
            if cached_response:
                app_logger.debug(f"{cached_response=}")
                return Response(*cached_response)

            user_basket = cls._get_user_basket(request)
            response = (user_basket, HTTP_200_OK)
            cache.set(request.session["basket"], response, 360)
            return Response(*response)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def remove_product(cls, request: Request) -> Response:
        """Handle logic to remove or reduce quantity of product in bucket.

        Steps:
        - remove cashed response
        - validate request body
        - remove or reduce quantity of product in bucket
        - cached succeed response
        - return corresponding response

        """
        try:
            cache.delete(request.session.get("basket"))
            product = BasketAddItemSerializer(data=request.data)
            product.is_valid(raise_exception=True)
            cls._remove_product_from_user(product.data, request)
            user_basket = cls._get_user_basket(request)
            response = (user_basket, HTTP_200_OK)
            cache.set(request.session["basket"], response, 360)
            return Response(*response)
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def _add_product_to_user(product_data: dict, request: Request) -> None:
        """Add or increase quantity of product in bucket(session)."""

        if not request.session.get("basket"):
            request.session["basket"] = {}

        if not request.session["basket"].get(str(product_data["id"])):
            request.session["basket"][str(product_data["id"])] = product_data
        else:
            request.session["basket"][str(product_data["id"])]["count"] += (
                product_data["count"]
            )

        request.session.save()

    @staticmethod
    def _remove_product_from_user(
            product_data: dict, request: Request,
    ) -> None:
        """Remove or reduce quantity of product in bucket(session)."""

        if (
                not request.session.get("basket") or
                not request.session["basket"].get(str(product_data["id"]))
        ):
            request.session["basket"] = {}
            return
        request.session["basket"][str(product_data["id"])]["count"] -= (
            product_data["count"]
        )
        if request.session["basket"][str(product_data["id"])]["count"] <= 0:
            request.session["basket"].pop(str(product_data["id"]), None)
        request.session.save()

    @staticmethod
    def _get_user_basket(request: Request) -> list:
        """Get product data from user bucket."""

        basket_data = []
        if not request.session.get("basket"):
            request.session["basket"] = {}
            return basket_data

        products_ids = [
            int(product_id) for product_id in request.session["basket"].keys()
        ]
        basket_products = (
            Product.objects.prefetch_related("images", "tags", "reviews").
            filter(id__in=products_ids, is_active=True)
        )
        for i_product in basket_products:
            i_product.required_amount = (
                request.session["basket"][str(i_product.id)]["count"]
            )
            basket_data.append(BucketProductSerializer(i_product).data)
        return basket_data

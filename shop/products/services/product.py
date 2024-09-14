"""Handle business logi for products related endpoints"""

from random import sample

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from common.custom_logger import app_logger
from common.utils import server_error

from products.models import Product
from products.serializers import (
    OutSpecialProductSerializer,
    OutProductFullSerializer,
)

product_id_error = {"error": "Product id is not existed!"}
min_sorting_index = 0
max_sorting_index = 10
total_popular_products = 8
total_limited_products = 16
total_banners_products = 3


class ProductHandler:
    """Class for handling business logic Product related endpoints"""

    @staticmethod
    def get_popular_products() -> Response:
        """Get popular products."""

        try:
            popular_products_qs = Product.get_popular_products(
                total_popular_products,
            )
            if not popular_products_qs:
                return Response(status=HTTP_204_NO_CONTENT)

            popular_products = OutSpecialProductSerializer(
                popular_products_qs, many=True,
            )
            return Response(popular_products.data, HTTP_200_OK)
        except Exception as exc:
            app_logger.error(exc)
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_limited_products() -> Response:
        """Get limited products."""

        try:
            limited_products_qs = Product.get_limited_products(
                total_limited_products,
            )
            if not limited_products_qs:
                return Response(status=HTTP_204_NO_CONTENT)

            limited_products = OutSpecialProductSerializer(
                limited_products_qs, many=True,
            )
            return Response(limited_products.data, HTTP_200_OK)
        except Exception as exc:
            app_logger.error(exc)
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)


    @staticmethod
    def get_banners_products() -> Response:
        """Get banners products (3 random active products)."""

        try:
            products_ids = list(
                Product.objects.
                filter(is_active=True).
                values_list("id", flat=True)
            )
            if not products_ids:
                return Response(status=HTTP_204_NO_CONTENT)

            random_products_ids = sample(products_ids, total_banners_products)
            banners_products_qs = Product.get_banners_products(
                random_products_ids,
            )
            banners_products = OutSpecialProductSerializer(
                banners_products_qs, many=True,
            )
            return Response(banners_products.data, HTTP_200_OK)
        except Exception as exc:
            app_logger.error(exc)
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_product_by_id(product_id: int) -> Response:
        """Get product by id."""

        try:
            product = Product.objects.get(pk=product_id)
            if not product:
                return Response(product_id_error,HTTP_404_NOT_FOUND,)

            product_data = OutProductFullSerializer(product)
            return Response(product_data.data,HTTP_200_OK)
        except Exception as exc:
            app_logger.error(exc)
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

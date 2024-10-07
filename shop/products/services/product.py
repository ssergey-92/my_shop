"""Handle business logi for products related endpoints"""

from traceback import format_exc as tb_format_exc

from random import sample

from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST,
)

from .common import apply_pagination_to_qs, get_pagination_last_page
from common.custom_logger import app_logger
from common.utils import server_error
from products.constants import DEFAULT_PAGINATION_LIMIT
from products.models import Product
from products.serializers import (
    InSalesProductSerializer,
    OutSalesProductSerializer,
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
    def get_popular_products_response() -> Response:
        """Get popular products."""

        try:
            popular_products_qs = Product.get_popular_products(
                total_popular_products,
            )
            popular_products = OutSpecialProductSerializer(
                popular_products_qs, many=True,
            )
            return Response(popular_products.data, HTTP_200_OK)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get_limited_products_response() -> Response:
        """Get limited products."""

        try:
            limited_products_qs = Product.get_limited_products(
                total_limited_products,
            )
            limited_products = OutSpecialProductSerializer(
                limited_products_qs, many=True,
            )
            return Response(limited_products.data, HTTP_200_OK)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)


    @staticmethod
    def get_banners_products_response() -> Response:
        """Get banners products (3 random active products)."""

        try:
            products_ids = Product.get_products_ids()
            if not products_ids:
                return Response([], HTTP_200_OK)
            elif total_banners_products > len(products_ids):
                maxl_banners_products = len(products_ids)
            else:
                maxl_banners_products = total_banners_products

            random_products_ids = sample(products_ids, maxl_banners_products)
            banners_products_qs = Product.get_banners_products(
                random_products_ids,
            )
            banners_products = OutSpecialProductSerializer(
                banners_products_qs, many=True,
            )
            return Response(banners_products.data, HTTP_200_OK)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    def get_sales_products_response(cls, query_params: dict) -> Response:
        try:
            response_data = cache.get(query_params)
            app_logger.debug(f"GET CACHE {query_params=} {response_data=}")
            if response_data:
                return Response(*response_data)

            query_data = InSalesProductSerializer(data=query_params)
            query_data.is_valid(raise_exception=True)
            current_page = query_data.data["current_page"]
            sales_products_details = {
                "items": cls._get_sales_products_data(current_page),
                "currentPage": current_page,
                "lastPage": get_pagination_last_page(
                        Product.get_sales_products().count()
                    )
            }
            response_data = (sales_products_details, HTTP_200_OK)
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            app_logger.debug(f"SET CACHE {query_params=}: {response_data=}")
            cache.set(query_params, response_data, 5)
            return Response(*response_data)

    @staticmethod
    def get_product_by_id_response(product_id: int) -> Response:
        """Get product by id."""

        try:
            product = Product.get_by_id_with_prefetch(product_id)
            product_details = OutProductFullSerializer(product)
            return Response(product_details.data,HTTP_200_OK)
        except Product.DoesNotExist:
            app_logger.info(f"Product with id {product_id} does not exist!")
            return Response(product_id_error, HTTP_404_NOT_FOUND)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)


    @staticmethod
    def _get_sales_products_data(
            current_page: int, limit: int = DEFAULT_PAGINATION_LIMIT,
    ) -> dict:
        """Get sales Products data."""
        sales_products_qs = Product.get_sales_products()
        sales_products_qs = apply_pagination_to_qs(
            sales_products_qs, current_page, limit,
        )
        return OutSalesProductSerializer(sales_products_qs, many=True).data



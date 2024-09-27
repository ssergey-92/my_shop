"""Handle business logi for product review related endpoints"""

from traceback import print_exception as tb_print_exception

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from common.custom_logger import app_logger
from common.utils import server_error
from products.models import Product, ProductReview
from products.serializers import ProductReviewSerializer
from .product import product_id_error

min_review_rate = 0
max_review_rate = 5


class ProductReviewHandler:
    """Class for handling business logic of product review related endpoints."""

    @staticmethod
    def add_review(product_id: int, request: Request) -> Response:
        """Add new review to product.

        Validate product id and review data then add review if data is valid.
        Return all product related reviews.

        """
        try:
            product = (
                Product.objects.prefetch_related("reviews").get(pk=product_id)
            )
            if not product:
                return Response(product_id_error, HTTP_400_BAD_REQUEST)

            review_data = ProductReviewSerializer(data=request.data)
            if not review_data.is_valid():
                return Response(
                    {"error": review_data.errors}, HTTP_400_BAD_REQUEST,
                )

            product.add_new_review(review_data.data)
            product_reviews = ProductReviewSerializer(
                product.reviews, many=True,
            )
            return Response(product_reviews.data, HTTP_200_OK)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

"""Handle business logi for product review related endpoints"""

from traceback import print_exception as tb_print_exception

from django.db import IntegrityError
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
from products.models import Product, ProductReview
from products.serializers import ProductReviewSerializer
from .product import product_id_error

min_review_rate = 0
max_review_rate = 5


class ProductReviewHandler:
    """Class to handle logic of product review related endpoints."""

    _review_duplication_error = (
            "User with email '{email}' has already published the review!"
    )

    @classmethod
    def add_review_response(cls, product_id: int, request: Request) -> Response:
        """Add new review to product.

        Validate product id and review data then add review if data is valid.
        Return all product related reviews.

        """
        try:
            review_data = ProductReviewSerializer(data=request.data)
            review_data.is_valid(raise_exception=True)
            product = (
                Product.objects.prefetch_related("reviews").get(pk=product_id)
            )
            product.add_new_review(review_data.data)
            product_reviews = ProductReviewSerializer(
                product.reviews, many=True,
            )
            return Response(product_reviews.data, HTTP_200_OK)
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({
                "error": cls._review_duplication_error.format(
                    email=review_data.data["email"]
                    ),
                },
                HTTP_400_BAD_REQUEST,
            )
        except Product.DoesNotExist:
            return Response(product_id_error, HTTP_400_BAD_REQUEST)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

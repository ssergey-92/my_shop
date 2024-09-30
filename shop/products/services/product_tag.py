"""Handle business logi for product tags related endpoints"""

from traceback import print_exception as tb_print_exception

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from .category import category_unexist_error
from common.custom_logger import app_logger
from common.utils import server_error
from products.models import Category, ProductTag
from products.serializers import  (
    InCategoryIdSerializer,
    ProductTagSerializer,
)


class ProductTagHandler:
    """Class for handling business logic of product tags related endpoints."""

    @staticmethod
    def get_tags_for_category_response(category_id: dict) -> Response:
        """Get Product tags related to category.

        Validate category and take tags which belongs to category and
        its subcategories.

        """
        try:
            category_id = InCategoryIdSerializer(data=category_id)
            category_id.is_valid(raise_exception=True)
            if category_id.data["id"]:
                tags = Category.get_category_related_tags(
                    category_id.data["id"],
                )
            else:
                tags = ProductTag.objects.all()
            return Response(
                ProductTagSerializer(tags, many=True).data, HTTP_200_OK,
            )
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response(category_unexist_error, HTTP_400_BAD_REQUEST)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

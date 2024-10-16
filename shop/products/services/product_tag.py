"""Handle business logi for product tags related endpoints"""

from traceback import format_exc as tb_format_exc

from rest_framework.exceptions import ValidationError
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
from products.serializers import (
    InCategoryIdSerializer,
    ProductTagSerializer,
)


class ProductTagHandler:
    """Class for handling business logic of product tags related endpoints."""

    @staticmethod
    def get_tags_for_category_response(category_details: dict) -> Response:
        """Get Product tags related to category.

        Validate category and take tags which belongs to category and
        its subcategories.

        """
        try:
            if not category_details or not category_details.get("category"):
                tags = ProductTag.objects.all()
            else:
                category = InCategoryIdSerializer(data=category_details)
                category.is_valid(raise_exception=True)
                tags = Category.get_category_related_tags(category.data["id"])
            return Response(
                ProductTagSerializer(tags, many=True).data, HTTP_200_OK,
            )
        except ValidationError as exc:
            return Response({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response(category_unexist_error, HTTP_400_BAD_REQUEST)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

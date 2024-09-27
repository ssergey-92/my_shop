"""Handle business logi for category related endpoints"""

from traceback import print_exception as tb_print_exception

from rest_framework.response import Response
from rest_framework import status

from common.custom_logger import app_logger
from common.utils import server_error
from products.models import Category
from products.serializers import OutCategoriesTreeSerializer

category_max_nesting_level = 1
category_unexist_error = {"error": "Category id is not existed!"}
category_id_unset_error = {"error": "Category id is not set!"}


class CategoryHandler:
    """Class for handling business logic of category related endpoints."""

    @staticmethod
    def get_categories() -> Response:
        """Get all categories.

        Create categories tree with subcategories. Include only active
        categories. (Image field can not be None!)

        """
        try:
            categories_qs = (
                Category.objects.
                filter(is_active=True, parent__isnull=True).
                select_related("image").
                prefetch_related("subcategories").
                order_by("title")
            )
            if categories_qs:
                categories_tree = OutCategoriesTreeSerializer(
                    categories_qs, many=True,
                )
                return Response(categories_tree.data, status.HTTP_200_OK)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(
                server_error, status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

"""Handle business logi for category related endpoints"""

from traceback import format_exc as tb_format_exc

from django.core.cache import cache
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

    _category_tree_cache_key = "Category tree"

    @classmethod
    def get_categories_response(cls) -> Response:
        """Get all categories.

        Create categories tree with subcategories. Include only active
        categories. (Image field can not be None!)

        """
        try:
            response_data = cache.get(cls._category_tree_cache_key)
            app_logger.debug(
                f"GET CACHE {cls._category_tree_cache_key=} {response_data=}"
            )
            if response_data:
                return Response(*response_data)

            categories_qs = Category.get_root_categories_with_prefetch()
            categories_tree_data = OutCategoriesTreeSerializer(
                categories_qs, many=True,
            ).data
            response_data = (categories_tree_data, status.HTTP_200_OK)
        except Exception:
            app_logger.error(tb_format_exc())
            return Response(
                server_error, status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        else:
            app_logger.debug(
                f"SET CACHE {cls._category_tree_cache_key=}: {response_data=}"
            )
            cache.set(cls._category_tree_cache_key, response_data, 60)
            return Response(*response_data)

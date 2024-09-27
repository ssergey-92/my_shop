"""Handle business logi for product tags related endpoints"""

from traceback import print_exception as tb_print_exception

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from common.custom_logger import app_logger
from common.utils import server_error
from products.models import Category, ProductTag
from products.serializers import ProductTagSerializer
from .category import category_unexist_error


class ProductTagHandler:
    """Class for handling business logic of product tags related endpoints."""

    @staticmethod
    def get_tags_for_category(request: Request) -> Response:
        """Get Product tags related to category.

        Validate category and take tags which belongs to category and
        its subcategories.

        """
        try:
            category_id = request.query_params.get("category", None)
            if category_id:
                category = (
                    Category.objects.
                    prefetch_related("subcategories").
                    get(id=int(category_id))
                )
                if not category:
                    return Response(
                        category_unexist_error, HTTP_400_BAD_REQUEST
                    )

                tags = category.get_category_related_tags()
            else:
                tags = ProductTag.objects.all()

            if not tags:
                return Response(status=HTTP_204_NO_CONTENT)

            return Response(
                ProductTagSerializer(tags, many=True).data, HTTP_200_OK,
            )
        except Exception as exc:
            app_logger.error(tb_print_exception(exc))
            return Response(server_error, HTTP_500_INTERNAL_SERVER_ERROR)

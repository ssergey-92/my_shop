"""Handle business logi for catalog related endpoints"""
from traceback import print_exception as tb_print_exception
from typing import Optional

from django.core.cache import cache
from django.db.models import QuerySet, Q, Count, Sum
from django.http import QueryDict

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from .common import apply_pagination_to_qs, get_pagination_last_page
from common.custom_logger import app_logger
from common.utils import server_error
from products.models import Product, Category
from products.serializers import (
    CatalogQueryParamsSerializer,
    OutSpecialProductSerializer,
)


class CatalogHandler:
    """Class for handling business logic of catalog related endpoints."""

    _base_query_set = Product.objects.distinct()

    @classmethod
    def get_catalog(cls, request: Request) -> Response:
        """Handle logic for getting products as per request query params.

        If request.query_params is cached as key then use cached response.
        Else:
            - Validate query params.
            - Select Products as per Category id and its subcategories.
              Filter and sort products as per query params and filter
              is_active=True for Product and Category and apply pagination.
            -Cache response data for 60sec.

        """
        try:
            response_data = cache.get(request.query_params.dict())
            app_logger.debug(
                f"GET CACHE {request.query_params.dict()=} {response_data=}"
            )
            if response_data:
                return Response(*response_data)

            query_params = cls._get_query_params(request.query_params)
            products_data = cls._get_products_data(query_params)
            catalog_data = {
                "items": products_data,
                "currentPage": query_params["pagination"]["current_page"],
                "lastPage": cls._get_catalog_last_page(query_params),
            }
            response_data = (catalog_data, HTTP_200_OK)
        except ValidationError as exc:
            response_data = ({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception as exc:
            app_logger.error(f"{tb_print_exception(exc)}")
            response_data = (server_error, HTTP_500_INTERNAL_SERVER_ERROR)

        app_logger.debug(
            f"SET CACHE {request.query_params.dict()}: {response_data=}"
        )
        cache.set(request.query_params.dict(), response_data, 60)
        return Response(*response_data)

    @staticmethod
    def _get_query_params(query_params: QueryDict) -> dict:
        """Validate and sort request query params."""

        query_params = CatalogQueryParamsSerializer(data={
           "name": query_params.get("filter[name]"),
            "minPrice": query_params.get("filter[minPrice]"),
            "maxPrice": query_params.get("filter[maxPrice]"),
            "freeDelivery": query_params.get("filter[freeDelivery]"),
            "available": query_params.get("filter[available]"),
            "category": query_params.get("category", None),
            "currentPage": query_params.get("currentPage"),
            "limit": query_params.get("limit"),
            "sort": query_params.get("sort"),
            "sortType": query_params.get("sortType"),
            "tags": query_params.getlist("tags[]"),
            },
        )
        if not query_params.is_valid():
            app_logger.debug(f"{query_params.errors=}")
            raise ValidationError(query_params.errors)

        app_logger.debug(f"{query_params.data=}")
        return query_params.data

    @staticmethod
    def _add_filters_to_qs(
            query_set: QuerySet, category_id: Optional[int], filters: dict,
    ) -> QuerySet:
        """Add filters to catalog query set"""
        query_set = query_set.filter(Q(is_active=True))
        if category_id:
            query_set = query_set.filter(
                Q(category_id=category_id) | Q(category__parent_id=category_id)
            )
        if filters:
            query_set = query_set.filter(**filters)
        return query_set

    @staticmethod
    def _add_sort_to_qs(query_set: QuerySet, sort: str) -> QuerySet:
        """Add order by field to query set and annotate it if required."""

        if not sort:
            return query_set

        if sort.endswith("total_reviews"):
            query_set = query_set.annotate(total_reviews=Count("reviews__id"))
        elif sort.endswith("total_sailed"):
            query_set = query_set.annotate(
                total_sailed=Sum("orderandproduct__total_quantity")
            )

        query_set = query_set.order_by(sort)
        return query_set

    @classmethod
    def _get_products_data(cls, query_params: dict) -> dict:
        """Get Products data as per validated request query params."""

        catalog_qs = cls._add_filters_to_qs(
            cls._base_query_set,
            query_params["category_id"],
            query_params["filters"],
        )
        catalog_qs = cls._add_sort_to_qs(catalog_qs, query_params["sort"])
        catalog_qs = apply_pagination_to_qs(
            catalog_qs,
            query_params["pagination"]["current_page"],
            query_params["pagination"]["limit"],
        )
        app_logger.debug(f"{catalog_qs=}")
        catalog_data = OutSpecialProductSerializer(catalog_qs, many=True)
        app_logger.debug(f"{catalog_data.data=}")
        return catalog_data.data

    @classmethod
    def _get_catalog_last_page(cls, query_params: dict) -> int:
        """Get last page for catalog pagination.

        Use validated request query params to do define total matched products
        and then count last page.
        """

        catalog_qs = cls._add_filters_to_qs(
            cls._base_query_set,
            query_params["category_id"],
            query_params["filters"],
        )
        return get_pagination_last_page(
            catalog_qs.count(), query_params["pagination"]["limit"],
        )

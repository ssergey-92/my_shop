"""Handle business logi for catalog related endpoints"""

from traceback import format_exc as tb_format_exc
from typing import Optional

from django.core.cache import cache
from django.db import models
from django.db.models import Case, Count, F, Sum, QuerySet, Q, When
from django.http import QueryDict
from django.utils.timezone import now

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.exceptions import ValidationError
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

    _base_query_set = (
        Product.objects.select_related("category").
        prefetch_related("images", "reviews", "tags").
        distinct()
    )

    @classmethod
    def get_catalog_response(cls, search_details: QueryDict) -> Response:
        """Handle logic to get Products as per catalog search details.

        If search_details is cached then return cached response.
        Else:
            - Validate search details.
            - Select Products as per Category id and its subcategories.
              Filter and sort products as per query params and filter
              is_active=True for Product and Category and apply pagination.
            -Cache response data for 60sec.

        """
        try:
            response_data = cache.get(str(search_details))
            app_logger.debug(f"GET CACHE {search_details=} {response_data=}")
            if response_data:
                return Response(*response_data)

            validated_search_details = cls._get_validated_search_details(
                search_details,
            )
            catalog_data = {
                "items": cls._get_products_data(validated_search_details),
                "currentPage":
                    validated_search_details["pagination"]["current_page"],
                "lastPage":
                    cls._get_catalog_last_page(validated_search_details),
            }
            response_data = (catalog_data, HTTP_200_OK)
        except ValidationError as exc:
            response_data = ({"error": str(exc)}, HTTP_400_BAD_REQUEST)
        except Exception:
            app_logger.error(f"{tb_format_exc()}")
            response_data = (server_error, HTTP_500_INTERNAL_SERVER_ERROR)

        app_logger.debug(f"SET CACHE {search_details=}: {response_data=}")
        cache.set(str(search_details), response_data, 60)
        return Response(*response_data)

    @staticmethod
    def _get_validated_search_details(query_params: QueryDict) -> dict:
        """Validate and sort request query params."""

        query_params = CatalogQueryParamsSerializer(
            data={
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
        query_params.is_valid(raise_exception=True)
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
            query_set = (
                query_set.annotate(total_reviews=Count("reviews__id")).
                order_by(sort)
            )
        elif sort.endswith("total_sailed"):
            query_set = (
                query_set.annotate(
                    total_sailed=Sum("orderandproduct__total_quantity")
                ).order_by(sort)
            )
        elif sort.endswith("price"):
            sort = sort.replace("price", "final_price")
            query_set = (
                query_set.annotate(final_price=Case(
                    When(
                        Q(is_sales=True) &
                        Q(sales_price__isnull=False) &
                        (Q(sales_from__lte=now()) | Q(sales_from__isnull=True)) &
                        (Q(sales_to__gte=now()) | Q(sales_to__isnull=True)),
                        then=F("sales_price")
                    ),
                    default=F("price"),
                    output_field=models.DecimalField()
                    )
                ).order_by(sort)
            )
        else:
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

"""Module contains endpoints for app."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from .services import (
    CatalogHandler,
    CategoryHandler,
    ProductHandler,
    ProductReviewHandler,
    ProductTagHandler,
)


class CatalogView(APIView):


    def get(self, request: Request) -> Response:
        """Get Category and subcategories products as per query params."""

        return CatalogHandler.get_catalog_response(request.query_params)


class CategoryView(APIView):
    def get(self, request: Request) -> Response:
        """Get all Categories with subcategories."""

        return CategoryHandler.get_categories_response()


class ProductView(APIView):

    def get(self, request: Request, id: int) -> Response:
        """Get Product details as per Product.id. """

        return ProductHandler.get_product_by_id_response(id)


class ProductBannerView(APIView):

    def get(self, request: Request) -> Response:
        """Get 'banners' Products."""

        return ProductHandler.get_banners_products_response()


class ProductPopularView(APIView):

    def get(self, request: Request) -> Response:
        """Get 'popular' Products."""

        return ProductHandler.get_popular_products_response()


class ProductLimitedView(APIView):

    def get(self, request: Request) -> Response:
        """Get 'limited' Products."""

        return ProductHandler.get_limited_products_response()


class ProductReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, id: int) -> Response:
        """Add new Product Review to Product."""

        return ProductReviewHandler.add_review_response(id, request)


class ProductSalesView(APIView):

    def get(self, request: Request) -> Response:
        """Get 'sales' Products."""

        return ProductHandler.get_sales_products_response(
            request.query_params.dict()
        )


class TagView(APIView):

    def get(self, request: Request) -> Response:
        """Get product tags as per category id."""

        return ProductTagHandler.get_tags_for_category_response(
            request.query_params.dict(),
        )

"""URL configuration for 'Products' app."""

from django.urls import path

from .apps import ProductsConfig
from .views import (
    CatalogView,
    CategoryView,
    ProductView,
    ProductBannerView,
    ProductPopularView,
    ProductLimitedView,
    ProductReviewView,
    ProductSalesView,
    TagView,
)

app_name = ProductsConfig.name

urlpatterns = [
    path(
        "catalog",
        CatalogView.as_view(),
        name="catalog_details",
    ),
    path(
        "categories",
        CategoryView.as_view(),
        name="categories_details",
    ),
    path(
        "product/<int:id>",
        ProductView.as_view(),
        name="product_details",
    ),
    path(
        "product/<int:id>/reviews",
        ProductReviewView.as_view(),
        name="product_review",
    ),
    path(
        "products/popular",
        ProductPopularView.as_view(),
        name="products_popular"),
    path(
        "products/limited",
        ProductLimitedView.as_view(),
        name="products_limited",
    ),
    path(
        "sales",
        ProductSalesView.as_view(),
        name="products_sales",
    ),
    path(
        "banners",
        ProductBannerView.as_view(),
        name="products_banners",
    ),
    path(
        "tags",
        TagView.as_view(),
        name="products_tags"
    ),
]

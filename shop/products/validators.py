"""Module with extra common app validators."""

from typing import Optional

from .models import Category
from common.custom_logger import app_logger
from .services import (
    category_max_nesting_level,
    min_review_rate,
    max_review_rate,
    min_sorting_index,
    max_sorting_index ,
)


parent_category_max_nesting_error = (
    f"Parent category has max nesting level = {category_max_nesting_level}"
)
parent_category_exceeded_nesting_error = (
    f"Parent category has exceeded max nesting level: "
    f"{category_max_nesting_level}"
)
price_error = "Product price should bigger then 0"
review_rate_error = (
    f"Review rate should be between {min_review_rate} and {max_review_rate}"
)
subcategories_nesting_error = (
    f"Subcategories will exceed max nesting level: "
    f"{category_max_nesting_level}"
)
sorting_index_error = (
    f"Sorting index should be between "
    f"{min_sorting_index} and {max_sorting_index}"
)


def validate_product_price(price: int) -> Optional[str]:
    """Extra validation of Product.price."""

    if price < 0:
        return price_error


def validate_product_review_rate(review_rate: int) -> Optional[str]:
    """Extra validation of ProductReview.rate."""

    if  (max_review_rate < review_rate) or (review_rate <  min_review_rate):
        return review_rate_error


def validate_product_sorting_index(sorting_index: int) -> Optional[str]:
    """Extra validation of Product.sorting_index."""

    if  (
            (max_sorting_index < sorting_index) or
            (sorting_index <  min_sorting_index)
    ):
        return sorting_index_error


def check_parent_nesting_level(parent_nesting_level: int) -> Optional[str]:
    """Check nesting level of parent category."""

    if parent_nesting_level == category_max_nesting_level:
        return parent_category_max_nesting_error
    elif parent_nesting_level > category_max_nesting_level:
        return parent_category_exceeded_nesting_error


def validate_parent_category_nesting(parent_category_id: int) -> Optional[str]:
    """Extra validation of nesting level.

    Validation is used to check if category(parent_category) can have
    subcategory.

    """
    nesting_level = Category.get_nesting_level(parent_category_id)
    return check_parent_nesting_level(nesting_level)


def validate_new_parent_category(
        category_id: int, parent_category_id: int,
) -> Optional[str]:
    """Extra validation to check if category can have selected parent category.

    Check that parent category and category is not violated max nesting level.

    """
    parent_nesting = Category.get_nesting_level(parent_category_id)
    app_logger.debug(f"{parent_category_id=} {parent_nesting=}")
    validation_error = check_parent_nesting_level(parent_nesting)
    if validation_error:
        return validation_error

    subcategories_nesting = Category.get_subcategories_rel_nesting_level(
        category_id,
    )
    full_nesting = parent_nesting + 1 + subcategories_nesting
    app_logger.debug(
        f"{category_id=} {subcategories_nesting=}, {full_nesting=}",
    )
    if full_nesting > category_max_nesting_level:
        return subcategories_nesting_error

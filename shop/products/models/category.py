"""App db model Category."""

from typing import Optional

from django.db import models, connection
from django.db.models import QuerySet

from .product_tag import ProductTag
from common.custom_logger import app_logger

unavailable_image = "Image is currently unavailable!"
sql_get_active_root_category = """
    WITH RECURSIVE RootCategory AS (
    SELECT id, parent_id, is_active
    FROM products_category AS pc
    WHERE id = %s

    UNION ALL

    SELECT pc.id, pc.parent_id, pc.is_active
    FROM products_category AS pc
    INNER JOIN RootCategory AS rc ON pc.id = rc.parent_id
    WHERE pc.is_active is TRUE
    )
    SELECT rc.id
    FROM RootCategory AS rc
    WHERE parent_id is NULL;
"""
sql_get_active_nesting_level ="""
    WITH RECURSIVE NestingLevel AS (
    SELECT id, parent_id, is_active, 0 AS depth
    FROM products_category AS pc
    WHERE id = %s

    UNION ALL

    SELECT pc.id, pc.parent_id, pc.is_active, depth + 1
    FROM products_category AS pc
    INNER JOIN NestingLevel AS nl ON nl.parent_id = pc.id
    WHERE pc.is_active is TRUE
    )
    SELECT MAX(depth)
    FROM NestingLevel;
"""
sql_get_subcategories_max_nesting_level ="""
    WITH RECURSIVE NestingLevel AS (
    SELECT id, parent_id, is_active, 0 AS depth
    FROM products_category AS pc
    WHERE id = %s

    UNION ALL

    SELECT pc.id, pc.parent_id, pc.is_active, depth + 1
    FROM products_category AS pc
    INNER JOIN NestingLevel AS nl ON nl.id = pc.parent_id
    WHERE pc.is_active is TRUE
    )
    SELECT MAX(depth)
    FROM NestingLevel;
"""


class Category(models.Model):
    title = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False,
    )
    parent= models.ForeignKey(
        to="Category",
        to_field="id",
        related_name="subcategories",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    image = models.ForeignKey(
        to="CategoryImage",
        to_field="id",
        on_delete=models.SET_NULL,
        related_name="categories",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Category: full details"
        verbose_name_plural = "Categories: full details"

    def __str__(self) -> str:
        """String representation of Category object."""

        return f"Category id: {self.id} title: {self.title}"

    @staticmethod
    def get_nesting_level(category_id: int) -> int:
        """Get category nesting level (root category nesting level = 0). """

        with connection.cursor() as cursor:
            cursor.execute(sql_get_active_nesting_level, [category_id])
            nesting_level = cursor.fetchone()
        return nesting_level[0] if nesting_level else 0

    @staticmethod
    def get_subcategories_rel_nesting_level(category_id: int) -> int:
        """Get max relative nesting level of subcategories from category.

        Count relative nesting level from category_id.

        """
        with connection.cursor() as cursor:
            cursor.execute(
                sql_get_subcategories_max_nesting_level, [category_id],
            )
            max_sub_nesting = cursor.fetchone()
            app_logger.debug(f"{category_id=} {max_sub_nesting=}")
        return max_sub_nesting[0] if max_sub_nesting else 0


    def get_root_category_id(self) -> Optional[int]:
        """Get root category id."""

        if self.parent is None:
            return None

        with connection.cursor() as cursor:
            cursor.execute(sql_get_active_root_category, [self.id])
            root_category_id = cursor.fetchone()
        return root_category_id[0] if root_category_id else None

    def get_category_related_tags(self) -> QuerySet:
        """Get tags related to category and its subcategories."""

        related_categories_ids = [self.id]
        if self.subcategories:
            for i_category in self.subcategories.filter(is_active=True).all():
                related_categories_ids.append(i_category.id)
        return (
            ProductTag.objects.
            filter(products__category_id__in=related_categories_ids).
            distinct()
        )

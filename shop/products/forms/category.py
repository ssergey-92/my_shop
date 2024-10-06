"""Module with form related to Category"""

from typing import Optional

from django import forms
from django.core.exceptions import ValidationError
from rest_framework.fields import ImageField

from common.custom_logger import app_logger
from common.validators import validate_image_src
from products.models import Category, CategoryImage
from products.validators import (
    validate_new_parent_category,
    validate_parent_category_nesting,
)

parent_field_internal_error = "Parent field is not set! Internal error!"
select_other_parent_category = "Select another parent category! "
can_not_add_subcategories = "Can not add subcategory for this category! "


class CategoryImageForm(forms.ModelForm):
    class Meta:
        model = CategoryImage
        fields = ["src", "alt"]

    def clean_src(self) -> ImageField:
        """Add extra checks for image file of 'src' field.

        Returns:
            ImageField: src field

        """
        src = self.cleaned_data.get("src")

        validation_error = validate_image_src(src)
        if not validation_error:
            return src

        app_logger.debug(f"error: {validation_error}")
        raise ValidationError(validation_error)


class CategoryForm(forms.ModelForm):
    """Class CategoryForm. Custom form for django admin panel.

     Class is used for Category(admin.ModelAdmin).

     """

    class Meta:
        model = Category
        fields = ["id", "title", "parent", "image", "is_active"]

    def clean_parent(self) -> Optional[Category]:
        """Extra validation for 'parent' field.

        If new instance is created check parent category nesting level if set.
        If parent field is changed, check additionally subcategories nesting

        Returns:
            str: parent object

        """

        parent_category = self.cleaned_data.get("parent")
        validation_error = ""
        app_logger.debug(f"{self.instance=} {parent_category=}")
        if not parent_category: # root Category
            return None

        if not self.instance.id: # new Category created
            validation_error = validate_parent_category_nesting(
                parent_category.id,
            )
        elif (
                not self.instance.parent or
                (parent_category.id != self.instance.parent.id)
        ): # Changing parent category
            validation_error = validate_new_parent_category(
                self.instance.id, parent_category.id,
            )

        if not validation_error:
            return parent_category

        app_logger.debug(f"error: {validation_error}")
        error_msg = select_other_parent_category + validation_error
        app_logger.debug(f"error: {error_msg}")
        raise ValidationError(error_msg)


class CategoryInlineForm(forms.ModelForm):
    """Class CategoryInlineForm. Custom form for django admin panel.

     Class is used for Category.subcategories (InlineModelAdmin).

     """
    class Meta:
        model = Category
        fields = ["title", "parent", "image", "is_active"]

    def clean(self) -> dict:
        """Extra validation for 'parent' field.

        Parent field is required as this form is used to add subcategory.
        Check that 'parent' field is set and nesting level of parent category.

        Returns:
            str: cleaned data

        """

        cleaned_data = super().clean()
        if cleaned_data.get("parent"):
            validation_error = validate_parent_category_nesting(
                cleaned_data.get("parent").id,
            )
            if not validation_error:
                return cleaned_data

            error_msg = can_not_add_subcategories + validation_error
            app_logger.debug(error_msg)
            raise ValidationError(error_msg)

        app_logger.error(parent_field_internal_error)
        raise ValidationError(parent_field_internal_error)

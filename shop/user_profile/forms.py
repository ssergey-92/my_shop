"""App forms for django admin panel."""

from typing import Optional

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Profile
from common.validators import (
    validate_image_src,
    validate_full_name,
    validate_phone_number,
)


class ProfileForm(forms.ModelForm):
    """Custom Profile Form for django admin panel."""

    avatar_src = forms.ImageField(required=False, label="Upload New Avatar")

    class Meta:
        model = Profile
        fields = ["full_name", "unique_email", "unique_phone"]

    def clean_avatar_src(self) -> Optional[InMemoryUploadedFile]:
        """Extra validation for avatar_src field."""

        avatar_src = self.cleaned_data.get("avatar_src", None)
        # Require extra check as 'avatar_src' field is optional
        if not avatar_src:
            return

        validation_error = validate_image_src(avatar_src)
        if not validation_error:
            return avatar_src

        raise ValidationError(validation_error)

    def clean_full_name(self) -> str:
        """Extra validation for full_name field."""

        full_name = self.cleaned_data.get("full_name").strip(" ")
        validation_error = validate_full_name(full_name)
        if not validation_error:
            return full_name

        raise ValidationError(validation_error)

    def clean_unique_phone(self) -> str:
        """Extra validation for unique_phone field."""

        phone = self.cleaned_data.get("unique_phone").strip(" ")
        validation_error = validate_phone_number(phone)
        if not validation_error:
            return phone

        raise ValidationError(validation_error)

    def save(self, commit=True) -> Profile:
        """Save updated profile."""

        avatar_src = self.cleaned_data.pop("avatar_src", None)
        profile = super(ProfileForm, self).save()
        if avatar_src:
            profile.set_new_avatar(avatar_src)

        return profile

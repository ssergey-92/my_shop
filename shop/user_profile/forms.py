from django import forms
from django.core.exceptions import ValidationError

from .models import Avatar, Profile
from .validators import (
    validate_avatar_src,
    validate_profile_full_name,
    validate_profile_unique_phone,
)
from common.utils import delete_file_from_sys


class ProfileForm(forms.ModelForm):
    avatar_src = forms.ImageField(required=False, label="Upload New Avatar")

    class Meta:
        model = Profile
        fields = ["full_name", "unique_email", "unique_phone"]

    def clean_avatar_src(self):
        avatar_src = self.cleaned_data.get("avatar_src", None)
        # Require extra check as 'avatar_src' field is optional
        if not avatar_src:
            return

        validation_error = validate_avatar_src(avatar_src)
        if not validation_error:
            return avatar_src

        raise ValidationError(validation_error)

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name").strip(" ")
        validation_error = validate_profile_full_name(full_name)
        if not validation_error:
            return full_name

        raise ValidationError(validation_error)

    def clean_unique_phone(self):
        phone = self.cleaned_data.get("unique_phone").strip(" ")
        validation_error = validate_profile_unique_phone(phone)
        if not validation_error:
            return phone

        raise ValidationError(validation_error)

    def save(self, commit=True):
        avatar_src = self.cleaned_data.pop("avatar_src", None)
        profile = super(ProfileForm, self).save()
        if avatar_src:
            if hasattr(profile, "avatar"):
                delete_file_from_sys(profile.avatar.src.path)
            profile.set_new_avatar(avatar_src)


        return profile
from typing import Optional

from django.contrib.auth.models import User
from django.db import IntegrityError

from common.custom_logger import app_logger


def create_new_user(user_details: dict) -> Optional[User]:
    try:
        return User.objects.create_user(**user_details)
    except IntegrityError as exc:
        app_logger.debug(f"Username is existed in table 'auth_user' : {exc}")
    except TypeError as exc:
        app_logger.error(f"Inexistent field in table 'auth_user': {exc}")
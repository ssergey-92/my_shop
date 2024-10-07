"""Django settings for 'shop' project."""

from pathlib import Path
from os import (
    getenv as os_getenv,
    makedirs as os_makedirs,
    path as os_path,
)

if os_getenv("SHOP_DEV_SERVER", "True") == "True":
    from dotenv import load_dotenv
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os_getenv("SHOP_SECRET_KEY")

DEBUG = os_getenv("SHOP_DEBUG") == "True"

ALLOWED_HOSTS = os_getenv("SHOP_ALLOWED_HOSTS").split(" ")
INTERNAL_IPS = []


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.messages',
    "rest_framework",
    "frontend",
    "authorization.apps.AuthorizationConfig",
    "user_profile.apps.UserProfileConfig",
    "products.apps.ProductsConfig",
    "orders.apps.OrdersConfig",
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


if os_getenv("SHOP_TESTING", None) != "True" and DEBUG:
    INTERNAL_IPS.extend(
        os_getenv("SHOP_INTERNAL_IPS").split(" ")
    )
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = 'shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'shop.wsgi.application'

# Database
if os_getenv("SHOP_DEV_SERVER") == "True":
    DB_HOST = os_getenv("SHOP_DB_DEV_HOST")
    REDIS_HOST = os_getenv("REDIS_DEV_HOST")
else:
    REDIS_HOST = os_getenv("DC_REDIS_SERVICE_NAME")
    DB_HOST = os_getenv("DC_DB_SERVICE_NAME")

DATABASES = {
    "default": {
        "ENGINE": os_getenv("SHOP_DB_ENGINE"),
        "NAME": os_getenv("MYSQL_DATABASE"),
        "USER": os_getenv("MYSQL_USER"),
        "PASSWORD": os_getenv("MYSQL_PASSWORD"),
        "HOST": DB_HOST,
        "PORT": os_getenv("MYSQL_PORT"),
        "OPTIONS": {
            "charset":  os_getenv("SHOP_DB_CHARSET"),
        },
    }
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cashing
if os_getenv("SHOP_DUMMY_CACHE") == "True":
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": (
                f"redis://{os_getenv("REDIS_USERNAME")}:"
                f"{os_getenv("REDIS_PASSWORD")}@{REDIS_HOST}:"
                f"{os_getenv("REDIS_PORT")}/{os_getenv("REDIS_CACHES_DB")}"
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_TIMEOUT": int(os_getenv("REDIS_TIMEOUT")),
            "TIMEOUT": int(os_getenv("REDIS_CASH_EXPIRY")),
            }
        }
    }


# Celery configs
CELERY_BROKER_URL = (
    f"redis://{os_getenv("REDIS_USERNAME")}:{os_getenv("REDIS_PASSWORD")}"
    f"@{REDIS_HOST}:{os_getenv("REDIS_PORT")}/{os_getenv("REDIS_BROKER_DB")}"
)
CELERY_RESULT_BACKEND = (
    f"redis://{os_getenv("REDIS_USERNAME")}:{os_getenv("REDIS_PASSWORD")}"
    f"@{REDIS_HOST}:{os_getenv("REDIS_PORT")}/{os_getenv("REDIS_BROKER_DB")}"
)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images) and Media files
STATIC_URL = 'static/'
MEDIA_ROOT = os_path.join(BASE_DIR, "media")
MEDIA_URL = "media/"
if os_getenv("SHOP_DEV_SERVER") == "True":
    STATIC_ROOT = os_path.join(BASE_DIR, 'frontend/static/')
else:
    STATIC_ROOT = os_path.join(BASE_DIR, "static")


# Logger setting for project
LOGDIR_PATH = os_path.join(BASE_DIR, os_getenv("BASE_LOGGER_DIR_NAME"))
os_makedirs(LOGDIR_PATH, exist_ok=True)
LOGFILE_PATH = os_path.join(LOGDIR_PATH, os_getenv("SHOP_LOGGER_FILE_NAME"))
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format":
                "%(name)s|%(pathname)s|%(message)s"
        },
        "for_file": {
            "format":
                "%(levelname)s|%(asctime)s|%(name)s|%(pathname)s|%(message)s",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": os_getenv("SHOP_LOGGER_CONSOLE_HANDLER_LEVEL"),
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "logfile": {
            "level": os_getenv("SHOP_LOGGER_FILE_HANDLER_LEVEL"),
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "for_file",
            "filename": LOGFILE_PATH,
            "maxBytes": int(os_getenv("BASE_LOGGER_FILE_SIZE")),
            "backupCount": int(os_getenv("BASE_LOGGER_BACKUP_COUNT")),
        },
    },
    "root": {
        "handlers": ["console", "logfile"],
        "level": os_getenv("SHOP_LOGGER_LEVEL"),
        "propagate": False,
    },
}
if DEBUG:
    LOGGING["loggers"] = {
        "django.db.backends": {
            "handlers": ["console", "logfile"],
            "level": "DEBUG",
            "propagate": False,
        },
        'django.request': {
            "handlers": ["console", "logfile"],
            "level": os_getenv("SHOP_LOGGER_LEVEL"),
            "propagate": False,
        },
    }


# Rest framework settings
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_PAGINATION_CLASS":
        "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


SUPPORTED_IMAGE_EXTENSIONS = os_getenv("SHOP_SUPPORTED_IMAGE_EXTENSIONS").split(' ')
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os_getenv("SHOP_DATA_UPLOAD_MAX_MEMORY_SIZE"))
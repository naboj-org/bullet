import os

import dj_database_url

from .base import *  # noqa

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = False

DATABASES = {"default": dj_database_url.config(default="postgres://localhost")}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 3600

ADMINS = [("Bullet Team", "bullet-notifications.group@trojsten.sk")]
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "root": {
        "handlers": ["console", "mail_admins"],
        "level": "WARNING",
    },
}

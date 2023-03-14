import os

import dj_database_url

import bullet

from .base import *  # noqa

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = False

DATABASES = {"default": dj_database_url.config(default="postgres://localhost")}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 3600

SERVER_EMAIL = "server@naboj.online"

dsn = os.environ.get("SENTRY_DSN", None)
if dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        auto_session_tracking=False,
        traces_sample_rate=0,
        send_default_pii=True,
        release=bullet.VERSION,
    )

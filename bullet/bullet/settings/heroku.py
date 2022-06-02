import dj_database_url

from .development import *  # noqa
from .development import MIDDLEWARE

MIDDLEWARE = ("whitenoise.middleware.WhiteNoiseMiddleware",) + MIDDLEWARE

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

ADMINS = [("Matus Zelenak", "matus.zelenak@trojsten.com")]

DATABASES = {"default": dj_database_url.config(default="postgres://localhost")}

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 3600

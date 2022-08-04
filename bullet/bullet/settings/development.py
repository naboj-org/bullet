import socket

from .base import *  # noqa
from .base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

PRODUCTION = False

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1"]

MIDDLEWARE.append(
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)

INSTALLED_APPS += ["debug_toolbar"]
SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

from .base import *

DEBUG = True

PRODUCTION = False

INTERNAL_IPS = [
    '127.0.0.1',
]

ALLOWED_HOSTS += ['bullet.top']

MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('django_hosts.middleware.HostsRequestMiddleware')
MIDDLEWARE = tuple(MIDDLEWARE)

MIDDLEWARE = (
    'django_hosts.middleware.HostsRequestMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE

INSTALLED_APPS += ['debug_toolbar']

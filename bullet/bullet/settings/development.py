from .base import *

DEBUG = True

PRODUCTION = False

INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE = list(MIDDLEWARE)
MIDDLEWARE.remove('django_hosts.middleware.HostsRequestMiddleware')
MIDDLEWARE = tuple(MIDDLEWARE)

PARENT_HOST = 'localhost'
HOST_PORT = os.environ.get('HOST_PORT', '8000')

MIDDLEWARE = (
    'django_hosts.middleware.HostsRequestMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE

INSTALLED_APPS += ['debug_toolbar']

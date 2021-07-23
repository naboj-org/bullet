import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# This will be overwritten by prod ENV
SECRET_KEY = '3qj^lv&gv&rq&6ef5f1xuvu(s-7++e)b0x0#&qq0uy&dx^!d7^'
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", 'localhost math.localhost physics.localhost junior.localhost').split(" ")

INSTALLED_APPS = [
    'address',
    'django_hosts',
    'phonenumber_field',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'competitions',
    'web'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'bullet'),
        'USER': os.environ.get('POSTGRES_USER', 'bullet'),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "bullet"),
        'HOST': os.environ.get('POSTGRES_HOST', 'bullet-db'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432)
    }
}

INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware'
]

DEFAULT_HOST = 'math'
PARENT_HOST = os.environ.get("PARENT_HOST")
ROOT_URLCONF = 'web.urls_shared'
ROOT_HOSTCONF = 'bullet.hosts'

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

WSGI_APPLICATION = 'bullet.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher'
]


AUTH_USER_MODEL = 'users.User'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

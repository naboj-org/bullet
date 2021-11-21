import os
from pathlib import Path

import django.conf.locale
from django.conf import global_settings

from bullet.constants import Languages

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# This will be overwritten by prod ENV
SECRET_KEY = "3qj^lv&gv&rq&6ef5f1xuvu(s-7++e)b0x0#&qq0uy&dx^!d7^"
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "localhost math.localhost physics.localhost junior.localhost",
).split(" ")

INSTALLED_APPS = [
    "address",
    "django_hosts",
    "phonenumber_field",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "competitions",
    "web",
    "education",
    "django.forms",
    "captcha",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "bullet"),
        "USER": os.environ.get("POSTGRES_USER", "bullet"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "bullet"),
        "HOST": os.environ.get("POSTGRES_HOST", "bullet-db"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = [
    "django_hosts.middleware.HostsRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_hosts.middleware.HostsResponseMiddleware",
]

DEFAULT_HOST = "math"
PARENT_HOST = os.environ.get("PARENT_HOST")
HOST_PORT = os.environ.get("HOST_PORT", "")
ROOT_URLCONF = "web.urls_shared"
ROOT_HOSTCONF = "bullet.hosts"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "bullet.wsgi.application"

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

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


AUTH_USER_MODEL = "users.User"

LANGUAGE_CODE = "en-GB"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)
LANGUAGES = Languages.choices

EXTRA_LANG_INFO = {
    "de-de": {
        "bidi": False,
        "code": "de-de",
        "name": "German",
        "name_local": u"Deutsch",
    },
    "de-ch": {
        "bidi": False,
        "code": "de-ch",
        "name": "Swiss German",
        "name_local": u"Schweizerdeutsch",
    },
}

LANG_INFO = dict(django.conf.locale.LANG_INFO, **EXTRA_LANG_INFO)
django.conf.locale.LANG_INFO = LANG_INFO
global_settings.LANGUAGES = LANGUAGES

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# This will be overwritten by prod ENV
SECRET_KEY = "3qj^lv&gv&rq&6ef5f1xuvu(s-7++e)b0x0#&qq0uy&dx^!d7^"
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "localhost math.localhost physics.localhost junior.localhost "
    "chemistry.localhost admin.localhost",
).split(" ")

INSTALLED_APPS = [
    "address",
    "phonenumber_field",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "users",
    "competitions",
    "web",
    "bullet_admin",
    "education",
    "countries",
    "problems",
    "django_countries",
    "captcha",
    "django_minify_html",
    "fontawesomefree",
    "django_htmx",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "bullet"),
        "USER": os.environ.get("POSTGRES_USER", "bullet"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "bullet"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "web.middleware.AdminDomainMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "competitions.middleware.BranchMiddleware",
    "countries.middleware.CountryLanguageMiddleware",
    "django_minify_html.middleware.MinifyHtmlMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

PARENT_HOST = os.environ.get("PARENT_HOST")
ROOT_URLCONF = "web.urls"

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
                "web.context_processors.menu_context",
                "web.context_processors.branch_context",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "bullet.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
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
]


AUTH_USER_MODEL = "users.User"
LOGIN_URL = "badmin:login"
LOGIN_REDIRECT_URL = "badmin:home"
SESSION_COOKIE_NAME = "bullet_session"
CSRF_COOKIE_NAME = "bullet_csrf_token"

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

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
MEDIA_ROOT = BASE_DIR / "uploads"
MEDIA_URL = "/uploads/"
GEOIP_PATH = "/geoip/"

MEILISEARCH_URL = os.environ.get("MEILISEARCH_URL", "http://meilisearch:7700/")
MEILISEARCH_KEY = os.environ.get("MEILISEARCH_KEY", None)

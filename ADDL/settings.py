import os
from pathlib import Path

import dj_database_url
from django.test.runner import DiscoverRunner

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

IS_HEROKU = "DYNO" in os.environ
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if "SECRET_KEY" in os.environ:
    SECRET_KEY = os.environ["SECRET_KEY"]

# Generally avoid wildcards(*). However since Heroku router provides hostname validation it is ok
if IS_HEROKU:
    ALLOWED_HOSTS = ["*"]
    CSRF_TRUSTED_ORIGINS = ["https://*.addl.app", "https://addl-portal.herokuapp.com"]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# SECURITY WARNING: don't run with debug turned on in production!
if not IS_HEROKU:
    DEBUG = True

# Application definition
INSTALLED_APPS = [
    # Django included packages
    #"debug_toolbar",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.postgres",
    # Installed packages
    "rest_framework",
    "django_extensions",
    "phonenumber_field",
    "smart_selects",
    # Created packages
    "Members.apps.MembersConfig",
    "Scores.apps.ScoresConfig",
    "Locations.apps.LocationsConfig",
    "Schedule.apps.ScheduleConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    #"debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ADDL.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "Common.context_processors.latest_season",
            ],
        },
    },
]

WSGI_APPLICATION = "ADDL.wsgi.application"

MAX_CONN_AGE = 600

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "addl",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


if "DATABASE_URL" in os.environ:
    # Configure Django for DATABASE_URL environment variable.
    DATABASES["default"] = dj_database_url.config(
        conn_max_age=MAX_CONN_AGE, ssl_require=True
    )

    # Enable test database if found in CI environment.
    if "CI" in os.environ:
        DATABASES["default"]["TEST"] = DATABASES["default"]


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
if IS_HEROKU:
    STATIC_URL = "static/"
else:
    STATIC_URL = "src/"
STATICFILES_DIRS = [
    BASE_DIR / "src/",
    BASE_DIR / "node_modules/",
]
STATIC_ROOT = BASE_DIR / "static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Phonenumber_Field Settings

PHONENUMBER_DB_FORMAT = "NATIONAL"
PHONENUMBER_DEFAULT_REGION = "US"


# Test Runner Config


class HerokuDiscoverRunner(DiscoverRunner):
    """Test Runner for Heroku CI, which provides a database for you.
    This requires you to set the TEST database (done for you by settings().)"""

    def setup_databases(self, **kwargs):
        self.keepdb = True
        return super(HerokuDiscoverRunner, self).setup_databases(**kwargs)


# Use HerokuDiscoverRunner on Heroku CI

if "CI" in os.environ:
    TEST_RUNNER = "ADDL.settings.HerokuDiscoverRunner"

# Custom User Model

AUTH_USER_MODEL = "Members.Player"


# Email Settings

if IS_HEROKU:
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_PORT = os.environ.get("EMAIL_PORT")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_USE_SSL = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "ADDL Support <support@addl.app>"
EMAIL_SUBJECT_PREFIX = "[ADDL] "


# Login Redirects

LOGIN_URL = "/members/login"
LOGIN_REDIRECT_URL = "/members/profile"
LOGOUT_REDIRECT_URL = "/"

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if IS_HEROKU:
    os.environ["ENVIRONMENT"] = "production"
else:
    os.environ["ENVIRONMENT"] = "development"
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        DjangoIntegration(
            transaction_style="url",
        ),
    ],
    _experiments={
        "profiles_sample_rate": 0.2,
    },
    max_breadcrumbs=10,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.2,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    environment=os.environ.get("ENVIRONMENT"),
    release=os.environ.get("GIT_SHA"),
)


# Smart Selects Settings
USE_DJANGO_JQUERY = True


# INTERNAL_IPS = [
#     "127.0.0.1",
# ]
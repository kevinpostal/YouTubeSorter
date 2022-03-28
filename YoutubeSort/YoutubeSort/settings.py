"""django settings."""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "jw!4z-0kh8975dgrh&t2ko2pmi4mk6u2!$3x+heth&f1n"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", ".ngrok.io", "127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd Party
    "channels",
    "rest_framework",
    "django_celery_results",
    # Custom
    "YoutubeSort",
    "YoutubeAuth",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "YoutubeAuth.middleware.ValidateYoutubeToken",
]

ROOT_URLCONF = "YoutubeSort.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS":
            {
                "context_processors":
                    [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
            },
    },
]

ASGI_APPLICATION = "YoutubeSort.asgi.application"

DATABASES = {
    "default":
        {
            "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
            "NAME": os.environ.get("SQL_DATABASE", "django"),
            "USER": os.environ.get("SQL_USER", "django"),
            "PASSWORD": os.environ.get("SQL_PASSWORD", "django"),
            "HOST": os.environ.get("SQL_HOST", "localhost"),
            "PORT": os.environ.get("SQL_PORT", "5432"),
        },
}

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

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
#STATICFILES_DIRS = [(os.path.join(BASE_DIR, 'static'))]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES":
        ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"],
}

CHANNEL_LAYERS = {
    "default":
        {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG":
                {
                    "hosts": [(os.environ.get("REDIS_HOST", "localhost"), 6379)],
                    "capacity": 1500,
                    "expiry": 10,
                },
        },
}

# CELERY STUFF

broker_url = os.environ.get("BROKER_URL", "redis://localhost:6379")
result_persistent = True
task_send_sent_event = True
#accept_content = ['application/json']\
accept_content = ['application/x-msgpack']

task_serializer = 'msgpack'
result_serializer = 'msgpack'
result_backend = 'django-db'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_TIME_LIMIT = 20 * 60  # set a max task time of 20 minutes
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_EXPIRES = 60 * 60 * 24 * 5  # seconds in 5 days
task_acks_late = False
worker_prefetch_multiplier = 128

###
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

AUTH_USER_MODEL = "YoutubeAuth.Credentials"
AUTHENTICATION_BACKENDS = ["YoutubeAuth.backends.EmailorUsernameModelBackend"]

DATA_UPLOAD_MAX_NUMBER_FIELDS = 99999

if DEBUG:
    import django_stubs_ext
    django_stubs_ext.monkeypatch()

    INSTALLED_APPS = [
        # Dev extensions
        "django_extensions",
        "debug_toolbar",
    ] + INSTALLED_APPS

    MIDDLEWARE = [
        # Dev extensions
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
    ]

    INTERNAL_IPS = [
        # ...
        "127.0.0.1",
        # ...
    ]

    if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
        import debugpy
        debugpy.listen(("0.0.0.0", 3000))
        debugpy.wait_for_client()
        print('Attached!')

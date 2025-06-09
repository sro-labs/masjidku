from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^=6-_k)oh!n9-fpcd1qd0rf(!8y2!!8cc*so1if(!*ydv@*_dc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    '9000-idx-masjidku-1745924443148.cluster-bg6uurscprhn6qxr6xwtrhvkf6.cloudworkstations.dev',
]

CORS_ALLOWED_ORIGINS = ["*"]
CORS_ORIGIN_WHITELIST = (
    '*',
)

CSRF_TRUSTED_ORIGINS = [
    'https://9000-idx-masjidku-1745924443148.cluster-bg6uurscprhn6qxr6xwtrhvkf6.cloudworkstations.dev'
]

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
        "level": "DEBUG",
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}


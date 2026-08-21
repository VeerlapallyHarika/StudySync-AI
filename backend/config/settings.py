"""Django settings for the StudySync AI backend.

Configuration is environment driven via a ``.env`` file (see ``.env.example``).
"""
from datetime import timedelta
from pathlib import Path

from django.conf import settings as _  # noqa: F401  (unused import guard for linters)

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-study-sync-ai')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'authentication',
    'students',
    'groups',
    'reports',
    'notifications',
    'insights',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv('SQLITE_PATH') or (BASE_DIR / 'db.sqlite3'),
    }
}

# Enable WAL mode for concurrent reads during CSV imports / group generation.
if os.getenv('SQLITE_WAL', 'True').lower() in ('true', '1', 'yes'):
    DATABASES['default']['OPTIONS'] = {'timeout': 20}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Transport security (auto-enabled in production, i.e. when DEBUG is off).
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173',
    ).split(',')
    if origin.strip()
]
# Production safety: must be explicitly enabled (defaults to off).
CORS_ALLOW_ALL_ORIGINS = bool(os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 'yes'))
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
]

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authentication.jwt.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'utils.exceptions.studysync_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.getenv('THROTTLE_RATE_ANON', '120/hour'),
        'user': os.getenv('THROTTLE_RATE_USER', '1200/hour'),
        'login': os.getenv('THROTTLE_RATE_LOGIN', '10/minute'),
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50,
}

# ---------------------------------------------------------------------------
# Application settings (secrets kept in the environment)
# ---------------------------------------------------------------------------
JWT = {
    'SECRET': os.getenv('JWT_SECRET', SECRET_KEY),
    'ACCESS_MINUTES': int(os.getenv('JWT_ACCESS_MINUTES', '30')),
    'REFRESH_DAYS': int(os.getenv('JWT_REFRESH_DAYS', '7')),
    'ALGORITHM': 'HS256',
}

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@studysync.ai')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
DEFAULT_STUDENT_PASSWORD = os.getenv('DEFAULT_STUDENT_PASSWORD', 'studysync')

# Fail fast in production when placeholder secrets would be used.
if not DEBUG:
    _PLACEHOLDER_SECRETS = {
        'django-insecure-study-sync-ai',
        'django-insecure-study-sync-ai-production',
        'change-me-in-production-with-a-long-random-string',
        'change-me-in-production-with-a-long-random-jwt-secret',
        'replace-with-a-long-random-secret-key',
        'replace-with-a-long-random-jwt-secret',
    }
    if SECRET_KEY in _PLACEHOLDER_SECRETS or JWT['SECRET'] in _PLACEHOLDER_SECRETS:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(
            'Production requires a real SECRET_KEY and JWT_SECRET. '
            'See backend/.env.example for guidance.'
        )
    if not os.getenv('ADMIN_PASSWORD'):
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured('Production requires ADMIN_PASSWORD to be set.')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} :: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {'handlers': ['console', 'file'], 'level': 'INFO'},
    'loggers': {
        'studysync': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': False},
    },
}

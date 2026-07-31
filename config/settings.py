"""
Django settings for Viskotu backend.
Uses python-decouple to read from .env
"""

from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

# Application definition
DJANGO_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    'storages',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.spaces',
    'apps.campaigns',
    'apps.placements',
    'apps.jobs',
    'apps.messages',
    'apps.notifications',
    'apps.payments',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Database — SQLite for local dev default, or PostgreSQL if configured
USE_SQLITE = config('USE_SQLITE', default=True, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='viskotu'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & media files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / config('MEDIA_ROOT', default='media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Django REST Framework ─────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'PAGE_SIZE': 20,
}

# ─── Simple JWT ───────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('REFRESH_TOKEN_LIFETIME_DAYS', default=30, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ─── CORS ─────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True

# Frontend base URL — used in emails (password reset, etc.)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

# ─── DRF Spectacular (OpenAPI docs) ───────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'Viskotu API',
    'DESCRIPTION': 'AdManager platform API — connects advertisers, space owners, and printers.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ─── Email ────────────────────────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='apps.core.utils.bird_backend.BirdEmailBackend')
BIRD_API_KEY = config('BIRD_API_KEY', default='bk_eu1_NBO3HzkXBGbq3t4U0fDbdkf0EYURs')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='onboarding@messagebird.dev')

EMAIL_HOST = config('EMAIL_HOST', default='smtp.bird.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ─── Paddle Checkout ──────────────────────────────────────────────────────
PADDLE_API_KEY = config('PADDLE_API_KEY', default='')
PADDLE_PRODUCT_ID = config('PADDLE_PRODUCT_ID', default='')

# ─── PayHere Checkout ─────────────────────────────────────────────────────
PAYHERE_MERCHANT_ID = config('PAYHERE_MERCHANT_ID', default='4OVyvZtlthI4JH5FFruf2e3PQ' if DEBUG else 'dummy_app_id')
PAYHERE_SECRET = config('PAYHERE_SECRET', default='8LTmg28x5Xz4KGzxt65OHQ8bStYZULLPi8goCdNrw6ap' if DEBUG else 'dummy_app_secret')

# ─── AWS S3 Media Storage ──────────────────────────────────────────────────
# If AWS_ACCESS_KEY_ID is provided in the environment, use S3 for media.
# Otherwise, fall back to local disk storage (useful for local dev without keys).
if config('AWS_ACCESS_KEY_ID', default=None):
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_DEFAULT_REGION', default='us-east-1')
    
    # Use Amazon S3 for storage
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # Generate URLs pointing to the S3 bucket
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    
    # Optional but recommended settings
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'



GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')

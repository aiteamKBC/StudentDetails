import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('DJANGO_SECRET_KEY is required in .env')

DEBUG = env_bool('DJANGO_DEBUG', False)
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]
IS_RUNSERVER = any(arg.startswith('runserver') for arg in sys.argv)
if IS_RUNSERVER:
    # Ensure local development works over plain HTTP even if production env vars are loaded.
    for host in ('127.0.0.1', 'localhost'):
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'authapp',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'email_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'email_project.wsgi.application'
ASGI_APPLICATION = 'email_project.asgi.application'

USE_SQLITE = env_bool('USE_SQLITE', False)
if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL is required in .env when USE_SQLITE is False')
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG),
    }

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security defaults: safe in production, easy to override via environment.
SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', not DEBUG)
SESSION_COOKIE_SECURE = env_bool('DJANGO_SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('DJANGO_CSRF_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv('DJANGO_SECURE_REFERRER_POLICY', 'same-origin')
X_FRAME_OPTIONS = os.getenv('DJANGO_X_FRAME_OPTIONS', 'DENY')

_default_hsts = 0 if DEBUG else 31536000
SECURE_HSTS_SECONDS = env_int('DJANGO_SECURE_HSTS_SECONDS', _default_hsts)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', not DEBUG)
SECURE_HSTS_PRELOAD = env_bool('DJANGO_SECURE_HSTS_PRELOAD', not DEBUG)

if env_bool('DJANGO_TRUST_X_FORWARDED_PROTO', False):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if IS_RUNSERVER:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# Simple in-memory throttling cache.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'auth-rate-limit',
    }
}

LOGIN_RATE_LIMIT_WINDOW_SECONDS = env_int('LOGIN_RATE_LIMIT_WINDOW_SECONDS', 300)
LOGIN_RATE_LIMIT_PER_IP = env_int('LOGIN_RATE_LIMIT_PER_IP', 30)
LOGIN_RATE_LIMIT_PER_EMAIL = env_int('LOGIN_RATE_LIMIT_PER_EMAIL', 8)
LOGIN_BLOCK_SECONDS = env_int('LOGIN_BLOCK_SECONDS', 900)

KBC_TABLE_SCHEMA = os.getenv('KBC_TABLE_SCHEMA', 'public')
KBC_TABLE_NAME = os.getenv('KBC_TABLE_NAME', 'kbc_users_data')
KBC_ID_COLUMN = os.getenv('KBC_ID_COLUMN', 'ID')
KBC_EMAIL_COLUMN = os.getenv('KBC_EMAIL_COLUMN', 'Email')
KBC_NAME_COLUMN = os.getenv('KBC_NAME_COLUMN', 'FullName')
KBC_GROUP_COLUMN = os.getenv('KBC_GROUP_COLUMN', 'Group')

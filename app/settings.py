import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# Project Basic Configuration
# ------------------------------------------------------------------------------
PROJECT_NAME = "PANDA MEDICINES STORE"
BASE_DIR = Path(__file__).resolve().parent.parent

# Step 1: Loading base .env file (for ENV_TYPE)
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Step 2: Getting environment type
ENV_TYPE = os.getenv("ENV_TYPE", "local").lower()

# Step 3: Loading respective credentials
SECRETS_FILE_MAP = {
    "local": "secrets/.env.local.secrets",
    "preproduction": "secrets/.env.preproduction.secrets",
    "production": "secrets/.env.production.secrets"
}

secret_file = SECRETS_FILE_MAP.get(ENV_TYPE)
print("Secreate File Loaded as : ", secret_file)
if secret_file:
    load_dotenv(dotenv_path=BASE_DIR / secret_file, override=True)
else:
    raise Exception(f"Unknown ENV_TYPE: {ENV_TYPE}")

DEBUG = os.getenv('DEBUG', default=True)
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in environment variables")

ALLOWED_HOSTS = ['*']

# ------------------------------------------------------------------------------
# Installed Apps
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'apps',
    'core',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt'
]

INSTALLED_APPS += LOCAL_APPS + THIRD_PARTY_APPS

# ------------------------------------------------------------------------------
# Caching (Redis)
# ------------------------------------------------------------------------------
# cache_redis_db = 1 if ENV_TYPE == "production" else 2 if ENV_TYPE == "preproduction" else 0

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': f'redis://127.0.0.1:6379/{cache_redis_db}',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'SOCKET_CONNECT_TIMEOUT': 5,
#             'SOCKET_TIMEOUT': 5,
#             'THREAD_LOCAL': True,
#         },
#         'TIMEOUT': 3600,
#     }
# }

# ------------------------------------------------------------------------------
# REST Framework Settings
# ------------------------------------------------------------------------------
REST_FRAMEWORK_ENV_TYPE = os.getenv("REST_FRAMEWORK_ENV_TYPE", "").lower()
if REST_FRAMEWORK_ENV_TYPE == 'local':
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'apps.helpers.simpleJWT_helper.CustomUserAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.AllowAny',
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'EXCEPTION_HANDLER': 'apps.helpers.exception_handler.custom_exception_handler',
    }
else:
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'apps.helpers.simpleJWT_helper.CustomUserAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.AllowAny',
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'EXCEPTION_HANDLER': 'apps.helpers.exception_handler.custom_exception_handler',
    }

# ------------------------------------------------------------------------------
# JWT Settings
# ------------------------------------------------------------------------------

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------------------------------------------------------
# URL & WSGI
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'app.urls'
WSGI_APPLICATION = 'app.wsgi.application'


# ------------------------------------------------------------------------------
# Templates
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# ------------------------------------------------------------------------------
# Database Settings
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': "medicine_store_db",
            'USER': 'root',
            'PASSWORD': "",
            'HOST': 'localhost',
            'PORT': '3307',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
            }
        },
}


# ------------------------------------------------------------------------------
# Password Validators
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Time - Localization
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = False


# # ------------------------------------------------------------------------------
# # Static & Media Files
# # ------------------------------------------------------------------------------
# CONTENT_DIR = os.path.join(BASE_DIR, 'content')
# STATIC_ROOT = os.path.join(CONTENT_DIR, "static")

# MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# STATIC_URL = '/static/'
# MEDIA_URL = '/media/'
# STATICFILES_DIRS = [CONTENT_DIR]

# # STATIC_URL = '/static/'
# # STATICFILES_DIRS = [
# #     BASE_DIR / "static",
# # ]
# # STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------------------------------------------------------------
# Static & Media Files
# ------------------------------------------------------------------------------

CONTENT_DIR = BASE_DIR / "content"

STATICFILES_DIRS = [
    CONTENT_DIR,   # <-- Correct root folder
]

STATIC_ROOT = BASE_DIR / "static_root"

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"




# ------------------------------------------------------------------------------
# Default Auto Field
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

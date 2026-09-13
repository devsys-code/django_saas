import os
import warnings
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

try:
  from jwt import InsecureKeyLengthWarning
  warnings.filterwarnings('ignore', category=InsecureKeyLengthWarning)
except ImportError:
  pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-g-x1@*#sd_i(*@u+z4qap+=7=)*ht19a@crutwm61aq+)k$z9h')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()] or ['*']

# Application definition
INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',

  # Librerías de terceros
  'corsheaders',
  'rest_framework',
  'django_filters',

  # Módulos internos
  'utl',
  'mod.sed.apps.SedConfig',
  'mod.uth.apps.UthConfig',
  'mod.org.apps.OrgConfig',
  'mod.usr.apps.UsrConfig',
  'mod.tsk.apps.TskConfig',
]

AUTH_USER_MODEL = 'usr.User'
SILENCED_SYSTEM_CHECKS = ['auth.E003']
APPEND_SLASH = False

MIDDLEWARE = [
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

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

WSGI_APPLICATION = 'api.wsgi.application'

# Database configuration
db_url = os.getenv('DATABASE_URL')
if db_url:
  parsed = urlparse(db_url)
  DATABASES = {
    'default': {
      'ENGINE': 'django.db.backends.postgresql',
      'NAME': parsed.path.lstrip('/'),
      'USER': parsed.username,
      'PASSWORD': parsed.password,
      'HOST': parsed.hostname or 'localhost',
      'PORT': parsed.port or 5432,
      'CONN_MAX_AGE': int(os.getenv('CONN_MAX_AGE', '600')),
    }
  }
else:
  DATABASES = {
    'default': {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME': BASE_DIR / 'db.sqlite3',
    }
  }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
  {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

# REST Framework
REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': [
    'utl.authentication.JWTAuthentication',
  ],
  'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.AllowAny',
  ],
  'DEFAULT_FILTER_BACKENDS': [
    'django_filters.rest_framework.DjangoFilterBackend',
    'rest_framework.filters.OrderingFilter',
  ],
  'DEFAULT_PAGINATION_CLASS': 'utl.pagination.CustomPageNumberPagination',
  'PAGE_SIZE': 10,
  'EXCEPTION_HANDLER': 'utl.exceptions.custom_exception_handler',
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
allowed_origins_env = os.getenv('ALLOWED_ORIGINS', '')
if allowed_origins_env:
  CORS_ALLOWED_ORIGINS = [o.strip() for o in allowed_origins_env.split(',') if o.strip()]

# JWT Settings
JWT_SECRET = os.getenv('JWT_SECRET', 'super-secret-jwt-key-2026')
JWT_EXPIRES_IN = os.getenv('JWT_EXPIRES_IN', '15m')

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

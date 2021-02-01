import os
import djmail

from datetime import timedelta
from celery.schedules import crontab


var_prefix = 'CRAWLER_'


def get_site_var(var_name, default=None):
    full_var_name = f'{var_prefix}{var_name}'
    var = os.getenv(full_var_name, default)
    if var is None:
        raise ValueError(
            f'"{full_var_name}" undefined.'
        )
    return var

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = get_site_var('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    'api.eshop-index.app',
]


# Global variables

VOTE_ALIKE_UPPERBOUND = int(get_site_var('VOTE_ALIKE_UPPERBOUND'))
VOTE_ALIKE_LOWERBOUND = int(get_site_var('VOTE_ALIKE_LOWERBOUND'))

VOTE_TAG_UPPERBOUND = int(get_site_var('VOTE_TAG_UPPERBOUND'))
VOTE_TAG_LOWERBOUND = int(get_site_var('VOTE_TAG_LOWERBOUND'))

VOTE_RECOMENDATION_UPPERBOUND = int(
    get_site_var('VOTE_RECOMENDATION_UPPERBOUND'))
VOTE_RECOMENDATION_LOWERBOUND = int(
    get_site_var('VOTE_RECOMENDATION_LOWERBOUND'))


# Email
WEBSITE_URL = get_site_var('WEBSITE_URL')

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = get_site_var('EMAIL_ADDRESS')
EMAIL_HOST_PASSWORD = get_site_var('EMAIL_PASSWORD')
EMAIL_PORT = 587

EMAIL_BACKEND = "djmail.backends.celery.EmailBackend"
DJMAIL_REAL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# reCAPTCHA
RECAPTCHA_SECRET_KEY = get_site_var('RECAPTCHA_SECRET_KEY')


# Application definition
AUTH_USER_MODEL = 'users.EshopIndexUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Rest Framework apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # djmail app
    'djmail',

    'classification',
    'games',
    'users',
]

MIDDLEWARE = [
    # Middleware for django-cors-headers
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eshop_crawler.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'eshop_crawler.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_site_var('DB_NAME'),
        'USER': get_site_var('DB_USER'),
        'PASSWORD': get_site_var('DB_PASSWORD'),
        'HOST': get_site_var('DB_HOST'),
        'PORT': 5432,
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    # {'NAME': 'django.contrib.auth.password_validation'
    #     '.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation'
        '.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation'
        '.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation'
        '.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Rest Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    )
}


# JWT Tokens auth

JWT_AUTH = {
    # Security vars
    # 'JWT_SECRET_KEY': settings.SECRET_KEY,
    # 'JWT_GET_USER_SECRET_KEY': None,
    # 'JWT_PUBLIC_KEY': None,
    # 'JWT_PRIVATE_KEY': None,
    # 'JWT_ALGORITHM': 'HS256',
    # 'JWT_VERIFY': True,
    # 'JWT_VERIFY_EXPIRATION': True,

    # Token expiration vars
    'JWT_EXPIRATION_DELTA': timedelta(days=2),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=14),
}


# CORS
CORS_ORIGIN_REGEX_WHITELIST = (
    r'(http(s)?://)?localhost(.)*(/)?',
    r'(http(s)?://)?(.)*eshop-index\.app(/)?',
)


# Celery
CELERY_BROKER_URL = get_site_var('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = get_site_var('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

CELERY_BEAT_SCHEDULE = {
    'update_switch_us': {
        'task': 'games.tasks.update_switch_us.update_switch_us',
        'schedule': crontab(hour='6', minute='0'),
        # 'args': (*args),
    },
    'update_switch_eu': {
        'task': 'games.tasks.update_switch_eu.update_switch_eu',
        'schedule': crontab(hour='6', minute='15'),
        # 'args': (*args),
    },
    'update_switch_price': {
        'task': 'games.tasks.update_switch_price.update_switch_price',
        'schedule': crontab(hour='6', minute='30'),
        # 'args': (*args),
    },
    'djmail_retry_send_messages': {
        'task': 'djmail.tasks.retry_send_messages',
        'schedule': crontab(hour='*'),
    },
}

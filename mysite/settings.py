"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

SESSION_EXPIRE_AT_BROWSER_CLOSE = config('SESSION_EXPIRE_AT_BROWSER_CLOSE')

#PROD
# ALLOWED_HOSTS = ['3.137.63.181', 'localhost', "goebookbuddy.org", "www.goebookbuddy.org", "semester.goebookbuddy.org"]

#DEV
ALLOWED_HOSTS = ['localhost','*', '192.168.1.3', '192.168.1.4', '10.0.0.124', 'goebookbuddy.org', 'www.goebookbuddy.org', 'semester.goebookbuddy.org']

WSGI_APPLICATION = f'{config("PROJECT_NAME")}.wsgi.application'

ASGI_APPLICATION = f'{config("PROJECT_NAME")}.routing.application'




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #Django Rest
    'rest_framework',
    'rest_framework.authtoken',
    "rest_framework_api_key",
    #My Apps
    'buddy_program_data',
    'users',
    'site_admin',
    'pages',
    'testing',
    'registration',
    'jitsi_data',
    'messaging',
    'matches',
    'reading_sessions',
    'evaluations',
    'staff_chat',
    'sub_requests',
    'private_chat',
    #Channels,
    'channels',
    #Localflavor
    'localflavor',
    # packages
    'compressor',
    'django_countries',
    'phonenumber_field',
    'cropperjs',
]

#ADMINS
MANAGERS=[('Buddy_Admin', 'admin@ebookbuddy.org'),]
ADMINS=[('Buddy_Admin', 'admin@ebookbuddy.org'),]

LOCAL_MIDDLEWARE = f'{config("PROJECT_NAME")}.middleware.ThreadLocalMiddleware'

MIDDLEWARE = [
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'mysite.middleware.ThreadLocalMiddleware',
]

AUTH_USER_MODEL = 'users.CustomUser'
ROOT_URLCONF = f'{config("PROJECT_NAME")}.urls'


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

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.EmailModelBackend'
]

API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"

# REST_FRAMEWORK = {
#     "DEFAULT_PERMISSION_CLASSES": [
#         'rest_framework.permissions.AllowAny',
#         # "rest_framework_api_key.permissions.HasAPIKey",


#     ],
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.BasicAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ]

# }

# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         # 'rest_framework.authentication.TokenAuthentication',  # <-- And here
#         'rest_framework.authentication.BasicAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',  #both are mentioned 
#         'rest_framework.permissions.AllowAny',
#         # "rest_framework_api_key.permissions.HasAPIKey",
#     ]
# }



# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

#PRODUCTION DATABASE
# DATABASES = {
#     'default': {
#         'ENGINE': config('DB_ENGINE'),
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': config('DB_PORT'),
#     }
# }

#DEV DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '___spring2022',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#Jitsi Meet
APP_ID= config('APP_ID')
APP_SUB= config('APP_SUB')
APP_SECRET= config('APP_SECRET')

# Email info
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
SERVER_EMAIL=config('SERVER_EMAIL')

STU_REG_EMAIL_HOST = config('STU_REG_EMAIL_HOST')
STU_REG_EMAIL_HOST_USER = config('STU_REG_EMAIL_HOST_USER')
STU_REG_EMAIL_HOST_PASSWORD = config('STU_REG_EMAIL_HOST_PASSWORD')
STU_REG_EMAIL_PORT = config('STU_REG_EMAIL_PORT')
STU_REG_EMAIL_USE_TLS = config('STU_REG_EMAIL_USE_TLS')
STU_REG_DEFAULT_FROM_EMAIL = config('STU_REG_DEFAULT_FROM_EMAIL')

VOL_REG_EMAIL_HOST = config('VOL_REG_EMAIL_HOST')
VOL_REG_EMAIL_HOST_USER = config('VOL_REG_EMAIL_HOST_USER')
VOL_REG_EMAIL_HOST_PASSWORD = config('VOL_REG_EMAIL_HOST_PASSWORD')
VOL_REG_EMAIL_PORT = config('VOL_REG_EMAIL_PORT')
VOL_REG_EMAIL_USE_TLS = config('VOL_REG_EMAIL_USE_TLS')
VOL_REG_DEFAULT_FROM_EMAIL = config('VOL_REG_DEFAULT_FROM_EMAIL')

TWILIO_ACCOUNT_SID=config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=config('TWILIO_AUTH_TOKEN')
TWILIO_SMS_NUMBER=config('TWILIO_SMS_NUMBER')



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

#file storage
CSV_DIRECTORY = BASE_DIR / 'csv' # Define the directory where csv are exported
TEX_DIRECTORY = BASE_DIR / 'tex' # Define the directory where tex files and pdf are exported

#DEV STATIC FILES
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_cdn'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media_cdn'
TEMP = BASE_DIR / 'media_cdn/temp'

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

COMPRESS_ROOT = 'static/'

COMPRESS_ENABLED = False

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


# Production AWS STATIC
# AWS_S3_SIGNATURE_VERSION = config('AWS_S3_SIGNATURE_VERSION')
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY =config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# AWS_DEFAULT_ACL = config('AWS_DEFAULT_ACL')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
# AWS_LOCATION = config('AWS_LOCATION')

# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]

# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
PHONENUMBER_DEFAULT_REGION = 'US'

#Base URL
# BASE_URL = "https://goebookbuddy.org"
BASE_URL ="http://127.0.0.1:8000"

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

GEOIP_PATH = BASE_DIR / 'static/locator'


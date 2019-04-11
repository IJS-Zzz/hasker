from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']
SECRET_KEY = os.environ.get('SECRET_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/hasker-emails'
EMAIL_HOST_USER = 'noreply@hasker.com'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media/'

from .base import *


DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SECRET_KEY = '^y9@e&sx_xb)++hgkxu6%55ina@rh8%a3kpz9*=i&awof1@)po'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = 'noreply@hasker.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': root('db.sqlite3'),
    }
}

if DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        INTERNAL_IPS = ('127.0.0.1',)
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(
            MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        )
        DEBUG_TOOLBAR_CONFIG = {
            'INTERCEPT_REDIRECTS': False,
        }

STATIC_ROOT = root('public/static/')
MEDIA_ROOT = root('public/media/')


# Questions

PAGINATE_QUESTIONS = 10
PAGINATE_ANSWERS = 10
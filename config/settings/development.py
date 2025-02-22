from .._base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEBUG = True

ALLOWED_HOSTS = []

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

SECRET_KEY = 'hwpzhsFzLuzWRlLs8Tj8X2ow5Im9Kn5eFlKLupTmNKjz_4scF1CbaFlq9tyt5F4'

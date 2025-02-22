import os

from .._base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

DEBUG = False

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = []

CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'

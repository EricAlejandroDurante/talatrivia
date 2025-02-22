from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer la configuración predeterminada de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Crear la instancia de Celery
app = Celery('config')

# Cargar configuración desde settings.py (usa el prefijo CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en tus aplicaciones Django
app.autodiscover_tasks()
"""Ajustes usados automáticamente por `manage.py test`.

Evita que las pruebas toquen la base de datos de producción (Supabase) y
desactiva integraciones externas.
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# WhiteNoise necesita el directorio de staticfiles, que no se genera en tests.
MIDDLEWARE = [
    middleware
    for middleware in MIDDLEWARE
    if middleware != 'whitenoise.middleware.WhiteNoiseMiddleware'
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SUPABASE_URL = ''
SUPABASE_KEY = ''

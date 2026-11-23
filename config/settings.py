import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables desde .env.local (vercel env pull) y .env (local).
# load_dotenv no sobrescribe variables ya definidas, así que .env.local manda.
load_dotenv(BASE_DIR / '.env.local')
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('SECRET_KEY debe estar definida en el entorno')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,0.0.0.0,.vercel.app',
    ).split(',')
    if host.strip()
]

# Credenciales de Supabase (Storage / SDK)
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
SUPABASE_STORAGE_BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', 'product-images')
SUPABASE_RECEIPTS_BUCKET = os.environ.get('SUPABASE_RECEIPTS_BUCKET', 'payment-receipts')
SUPABASE_DESIGNS_BUCKET = os.environ.get('SUPABASE_DESIGNS_BUCKET', 'custom-designs')

# En Vercel el disco es efímero: nunca se debe caer al guardado local.
# En desarrollo/tests se mantiene el fallback para poder trabajar sin Supabase.
ALLOW_LOCAL_STORAGE_FALLBACK = os.environ.get(
    'ALLOW_LOCAL_STORAGE_FALLBACK', str(DEBUG)
).lower() in ('1', 'true', 'yes', 'on')

# Datos públicos del negocio (configurables sin tocar el código).
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '')
BUSINESS_ADDRESS = os.environ.get(
    'BUSINESS_ADDRESS', 'Calle Groenlandia 2350, Cerrillos'
)
BANK_NAME = os.environ.get('BANK_NAME', 'Banco Estado')
BANK_ACCOUNT_TYPE = os.environ.get('BANK_ACCOUNT_TYPE', 'Cuenta Vista')
BANK_RUT = os.environ.get('BANK_RUT', '')
BANK_ACCOUNT = os.environ.get('BANK_ACCOUNT', '')

# Correo (Gmail SMTP).
# EMAIL_BACKEND se puede forzar desde el entorno; si no se define, se usa SMTP
# cuando hay credenciales y consola en local cuando no las hay.
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in (
    '1', 'true', 'yes', 'on'
)
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() in (
    '1', 'true', 'yes', 'on'
)
if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured(
        'EMAIL_USE_TLS y EMAIL_USE_SSL no pueden estar activos a la vez'
    )
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '').strip()
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '15'))

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '').strip() or 'ctorresj@utem.cl'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', '').strip() or (
    f'Volantines Strong <{EMAIL_HOST_USER}>'
    if EMAIL_HOST_USER
    else 'Volantines Strong <webmaster@localhost>'
)

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', '').strip() or (
    'django.core.mail.backends.smtp.EmailBackend'
    if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
    else 'django.core.mail.backends.console.EmailBackend'
)

SEND_CUSTOMER_CONFIRMATION = os.environ.get(
    'SEND_CUSTOMER_CONFIRMATION', 'True'
).lower() in ('1', 'true', 'yes', 'on')
LOGIN_URL = 'admin_panel:login'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom apps
    'products',
    'cart',
    'orders',
    'admin_panel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.business',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Usa DATABASE_URL de Supabase si está definida; de lo contrario usa SQLite local.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=0,
            ssl_require=True,
        )
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

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
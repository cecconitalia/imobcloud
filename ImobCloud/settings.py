# ImobCloud/settings.py

import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-chave-padrao-apenas-para-dev')

# SECURITY WARNING: don't run with debug turned on in production!
# Lê do .env. Se não tiver, assume False por segurança.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# =============================================================
# HOSTS E ORIGENS DINÂMICOS
# =============================================================
# Permite definir múltiplos hosts no .env separados por vírgula
allowed_hosts_env = os.getenv('ALLOWED_HOSTS')
if allowed_hosts_env:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',')]
else:
    # Fallback seguro
    ALLOWED_HOSTS = ['*', 'imobhome.com.br', 'www.imobhome.com.br', 'teste.imobhome.com.br', 'localhost', '127.0.0.1']


# Application definition
INSTALLED_APPS = [
    'jazzmin', # Tema do Admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Necessário para o Whitenoise
    'django.contrib.sites',

    'rest_framework',               
    'corsheaders',                  
    'rest_framework_simplejwt',     
    'django_celery_beat',           
    'simple_history',               

    # Apps Locais
    'core',
    'app_imoveis.apps.AppImoveisConfig',
    'app_clientes.apps.AppClientesConfig',
    'app_contratos.apps.AppContratosConfig',
    'app_financeiro.apps.AppFinanceiroConfig',
    'app_publicacoes',
    'app_config_ia',
    'app_alugueis',
    'app_boletos',
    'app_vistorias',
]

AUTH_USER_MODEL = 'core.PerfilUsuario' 

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise: Serve arquivos estáticos e o Frontend Vue diretamente
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', 
    'simple_history.middleware.HistoryRequestMiddleware', 
    'ImobCloud.middleware.TenantIdentificationMiddleware',     
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ImobCloud.urls'

FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Adiciona a pasta do build do Vue aos templates
        'DIRS': [os.path.join(FRONTEND_DIR, 'dist')],
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

WSGI_APPLICATION = 'ImobCloud.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'imobcloud_db'),
        'USER': os.getenv('POSTGRES_USER', 'imobcloud_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'D8h5..2025@'),
        'HOST': os.getenv('DB_HOST', 'db'), 
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# =============================================================
# ARQUIVOS ESTÁTICOS
# =============================================================
STATIC_URL = '/static/' 
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend', 'dist'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SITE_ID = 1

# =============================================================
# Django REST Framework Settings (CORRIGIDO)
# =============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        # ATENÇÃO: Comentado para evitar bloqueio 403 em ambiente local/sem assinatura
        # 'core.permissions.IsSubscriptionActive', 
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# =============================================================
# CONFIGURAÇÃO DO JWT
# =============================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# =============================================================
# CORS Headers Settings
# =============================================================
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

# =============================================================
# Jazzmin Admin Theme Settings
# =============================================================
JAZZMIN_SETTINGS = {
    "site_title": "ImobHome Admin",
    "site_header": "ImobHome",
    "site_brand": "ImobHome",
    "site_logo": None,
    "login_logo": None,
    "search_model": ["auth.User", "core.Imobiliaria", "app_imoveis.Imovel"],
    "topbar_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
    ],
    "order_with_respect_to": ["core", "app_imoveis", "app_clientes", "app_contratos", "auth"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "theme": "united",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-navy",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_unfold": False,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "theme": "united",
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

BRADESCO_CERT_PATH = os.path.join(BASE_DIR, 'media', 'bradesco_certs', 'Cert_b64.cer') 
BRADESCO_KEY_PATH = os.path.join(BASE_DIR, 'media', 'bradesco_certs', 'openapi.bradesco.com.br.key')

# =============================================================
# SEGURANÇA HÍBRIDA (LOCAL vs PRODUÇÃO)
# =============================================================
csrf_trusted_env = os.getenv('CSRF_TRUSTED_ORIGINS')
if csrf_trusted_env:
    CSRF_TRUSTED_ORIGINS = [url.strip() for url in csrf_trusted_env.split(',')]
else:
    if DEBUG:
        CSRF_TRUSTED_ORIGINS = [
            'http://localhost:8001',
            'http://127.0.0.1:8001',
            'http://localhost:5173',
            'http://127.0.0.1:5173'
        ]
    else:
        CSRF_TRUSTED_ORIGINS = [
            'https://imobhome.com.br',
            'https://www.imobhome.com.br',
            'https://teste.imobhome.com.br'
        ]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_PROXY_SSL_HEADER = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'

CELERY_BEAT_SCHEDULE = {
    'verificar-posts-agendados': {
        'task': 'app_publicacoes.tasks.verificar_publicacoes_agendadas',
        'schedule': 60.0,
    },
}

LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'imobcloud.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

SITE_URL = os.getenv('SITE_URL', "https://imobhome.com.br")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'ImobHome <no-reply@imobhome.com.br>')

if DEBUG:
    SECURE_SSL_REDIRECT = False
else:
    # Em produção, o Nginx geralmente cuida do redirect
    pass

X_FRAME_OPTIONS = 'SAMEORIGIN'
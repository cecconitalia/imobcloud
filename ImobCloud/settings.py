import os
import platform
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# DETECÇÃO AUTOMÁTICA DE AMBIENTE (WINDOWS vs LINUX)
# ==============================================================================
# Se for Windows, assume que é desenvolvimento local do Cristiano
IS_LOCAL_DEV = platform.system() == 'Windows'

if IS_LOCAL_DEV:
    print("🖥️  MODO LOCAL DETECTADO (WINDOWS) - Forçando configurações de Dev")
    DEBUG = True
    DB_HOST_DEFAULT = '127.0.0.1' 
    DB_PORT_DEFAULT = '5433' # Sua porta customizada local
else:
    # Produção (Linux/Vultr)
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    DB_HOST_DEFAULT = '127.0.0.1'
    DB_PORT_DEFAULT = '5432'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-chave-padrao-apenas-para-dev')

# =============================================================
# HOSTS E ORIGENS DINÂMICOS
# =============================================================
if IS_LOCAL_DEV:
    ALLOWED_HOSTS = ['*']
else:
    allowed_hosts_env = os.getenv('ALLOWED_HOSTS')
    if allowed_hosts_env:
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',')]
    else:
        # O ponto antes do domínio permite todos os subdomínios (Essencial para SaaS)
        ALLOWED_HOSTS = [
            'imobhome.com.br', 
            '.imobhome.com.br', 
            'www.imobhome.com.br', 
            '155.138.233.124', 
            'localhost', 
            '127.0.0.1'
        ]

# Application definition
INSTALLED_APPS = [
    'jazzmin', # Tema do Admin (Deve vir antes do admin)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', 
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
    'whitenoise.middleware.WhiteNoiseMiddleware', # Serve o Vue.js e Estáticos
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

# Configuração do Frontend Vue.js
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'ImobCloud2025'),
        'HOST': os.getenv('DB_HOST', DB_HOST_DEFAULT), 
        'PORT': os.getenv('DB_PORT', DB_PORT_DEFAULT),
        'ATOMIC_REQUESTS': True,
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
# ARQUIVOS ESTÁTICOS E FRONTEND
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
# Django REST Framework Settings
# =============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

# =============================================================
# JAZZMIN ADMIN
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
# SEGURANÇA HÍBRIDA E CSRF (CORREÇÃO TOKEN MISSING)
# =============================================================
csrf_trusted_env = os.getenv('CSRF_TRUSTED_ORIGINS')

if csrf_trusted_env:
    CSRF_TRUSTED_ORIGINS = [url.strip() for url in csrf_trusted_env.split(',')]
else:
    if IS_LOCAL_DEV:
        CSRF_TRUSTED_ORIGINS = [
            'http://localhost:8001',
            'http://127.0.0.1:8001',
            'http://localhost:5173',
            'http://127.0.0.1:5173'
        ]
        SECURE_PROXY_SSL_HEADER = None
        SESSION_COOKIE_SECURE = False
        CSRF_COOKIE_SECURE = False
    else:
        # Produção: Garantir suporte a subdomínios no CSRF
        CSRF_TRUSTED_ORIGINS = [
            'https://imobhome.com.br',
            'https://www.imobhome.com.br',
            'https://*.imobhome.com.br' # Permite CSRF em qualquer subdomínio
        ]
        # Essencial para Gunicorn + Nginx HTTPS
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True

# Redis / Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
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

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'imobcloud.log') if not IS_LOCAL_DEV else 'imobcloud.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
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

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'ImobHome <no-reply@imobhome.com.br>')

# Segurança Adicional
SECURE_SSL_REDIRECT = False # Deixe o Nginx gerenciar o redirect para evitar loops
X_FRAME_OPTIONS = 'SAMEORIGIN'
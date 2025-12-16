# ImobCloud/settings.py

import os
from datetime import timedelta
from dotenv import load_dotenv # Adicionado para carregar variáveis de ambiente

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# A SECRET_KEY agora é lida a partir das variáveis de ambiente
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Permitimos o acesso de localhost e qualquer subdomínio de localhost
ALLOWED_HOSTS = ['*', 'localhost', '.localhost', '.ngrok-free.app']


# Application definition

INSTALLED_APPS = [
    #'jazzmin', # ADICIONE ESTA LINHA AQUI E MANTENHA-A ANTES DE 'django.contrib.admin'
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    #'sslserver',


    'rest_framework', # Django REST Framework
    'corsheaders',    # CORS Headers for cross-origin requests
    'rest_framework_simplejwt', # Adicione esta linha para JWT
    'django_celery_beat', # Adicionado para agendamento de tarefas

    'core', # Nosso app que conterá o modelo Imobiliaria
    'app_imoveis.apps.AppImoveisConfig',
    'app_clientes.apps.AppClientesConfig',
    'app_contratos.apps.AppContratosConfig',
    'app_financeiro.apps.AppFinanceiroConfig',
    'app_publicacoes',
    'app_config_ia',
    'app_alugueis',
    'app_boletos',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # ORDEM CORRIGIDA: AuthenticationMiddleware DEVE VIR ANTES do seu middleware de Tenant
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <<< ESTA LINHA DEVE VIR ANTES
    'ImobCloud.middleware.TenantIdentificationMiddleware',     # <<< ESTA LINHA DEVE VIR DEPOIS
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ImobCloud.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'imobcloud_db',
        'USER': 'imobcloud_user',
        'PASSWORD': os.getenv('DB_PASSWORD'), # <--- ALTERADO para usar variável de ambiente
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo' # Ajuste para o fuso horário correto no Brasil

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

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
        'rest_framework.permissions.AllowAny', # Permite acesso sem autenticação
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
    # Tempo de vida do token de acesso
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    # Tempo de vida do token de refresh (para renovar o token de acesso)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # Rotaciona o token de refresh a cada uso, aumentando a segurança.
    'ROTATE_REFRESH_TOKENS': True,
    # Habilita o refresh do token no cookie, opcional mas útil para algumas setups.
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
# =============================================================


# =============================================================
# CORS Headers Settings (para requisições entre origens diferentes)
# =============================================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# =============================================================
# Jazzmin Admin Theme Settings
# =============================================================
JAZZMIN_SETTINGS = {
    "site_title": "ImobCloud Admin",
    "site_header": "ImobCloud",
    "site_brand": "ImobCloud",
    "site_logo": "img/logo.png",
    "site_logo_classes": "img-circle",
    "login_logo": None,
    "login_logo_dark": None,
    "search_model": ["auth.User", "core.Imobiliaria", "app_imoveis.Imovel"],
    "topbar_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Suporte", "url": "#", "new_window": True},
        {"model": "auth.User"},
    ],
    "order_with_respect_to": ["core", "app_imoveis", "app_clientes", "app_contratos", "auth"],
    "navigation_expanded": True,
    "show_sidebar": True,
    "sidebar_nav_compact_mode": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_icons": True,
    "actions_dropdown_urls": True,
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",
    "usermenu_links": [
        {"model": "auth.user"}
    ],
    "show_ui_builder": False,
    "theme": "united",
    "dark_mode_theme": None,
    "custom_css": None,
    "custom_js": None,
    "show_language_chooser": True,
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
    "sidebar_nav_item_indent": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "united",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success"
    },
    "sidebar_nav_colorize_icon": False,
    "sidebar_nav_filter_tree": False,
    "sidebar_nav_top_level_style": "tabs",
    "sidebar_nav_top_level_color": "navbar-light",
}

# =============================================================
# Configurações de Média (Upload de Arquivos)
# =============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# =============================================================
# CONFIGURAÇÕES DO BRADESCO (para certificado mTLS)
# ATENÇÃO: Substitua pelos caminhos corretos dos seus arquivos!
# =============================================================
# Caminho para o certificado público (.crt ou .pem)
BRADESCO_CERT_PATH = os.path.join(BASE_DIR, 'caminho', 'para', 'seu_certificado.crt')
# Caminho para a chave privada (.key)
BRADESCO_KEY_PATH = os.path.join(BASE_DIR, 'caminho', 'para', 'sua_chave_privada.key')

# =============================================================
# Configurações CSRF
# =============================================================
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://*.ngrok-free.app', # Permitir Ngrok para Webhooks/Callback
]

# =============================================================
# Configurações de E-mail
# =============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.ofertacobrasil.com.br'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER')

# ===================================================================
# CONFIGURAÇÕES DO CELERY E REDIS
# ===================================================================
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo' # Ajuste para o seu fuso horário

# Configuração do Celery Beat (Agendador de Tarefas Periódicas)
CELERY_BEAT_SCHEDULE = {
    'verificar-posts-agendados': {
        'task': 'app_publicacoes.tasks.verificar_publicacoes_agendadas', # NOME CORRIGIDO AQUI
        'schedule': 60.0,  # Executar a cada 60 segundos
    },
}

# ===================================================================
# URL BASE DO SITE (Importante para Instagram/Facebook API)
# ===================================================================
# Em produção, coloque o domínio real (ex: https://imobcloud.com.br)
# Para testes locais com Instagram, use a URL do Ngrok atual.
# ATUALIZE ESTA LINHA SEMPRE QUE REINICIAR O NGROK
SITE_URL = "https://6595c62c5f39.ngrok-free.app"
# ImobCloud/settings.py

import os
from datetime import timedelta # Importado para as configurações JWT

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@e^z-v*796s^86^!%5)2k(4z&h!j09c1(m%c@7s9n%w7g&^m9n' # ALtere isso em produção!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Permitimos o acesso de localhost e qualquer subdomínio de localhost
ALLOWED_HOSTS = ['*', 'localhost', '.localhost']


# Application definition

INSTALLED_APPS = [
    'jazzmin', # ADICIONE ESTA LINHA AQUI E MANTENHA-A ANTES DE 'django.contrib.admin'
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'sslserver',

    'rest_framework', # Django REST Framework
    'corsheaders',    # CORS Headers for cross-origin requests
    'rest_framework_simplejwt', # Adicione esta linha para JWT

    'core', # Nosso app que conterá o modelo Imobiliaria
    'app_imoveis.apps.AppImoveisConfig',
    'app_clientes.apps.AppClientesConfig',
    'app_contratos.apps.AppContratosConfig',
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
        'PASSWORD': 'D8h5..12', # <--- COLOQUE SUA SENHA REAL AQUI!
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
# Configurações CSRF
# =============================================================
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    # Se você estiver usando subdomínios, adicione-os também para CSRF
    # Ex: 'http://sol.localhost:5173',
    # Para produção, você listaria os domínios reais:
    # 'https://seusistema.com',
    # 'https://*.seusistema.com',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.ofertacobrasil.com.br'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'estilomusical@ofertacobrasil.com.br'
EMAIL_HOST_PASSWORD = 'P5jNfHUWb@K#$R9'
DEFAULT_FROM_EMAIL = 'estilomusical@ofertacobrasil.com.br'

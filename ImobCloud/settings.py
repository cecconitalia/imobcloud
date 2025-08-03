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

    'rest_framework', # Django REST Framework
    'corsheaders',    # CORS Headers for cross-origin requests
    'rest_framework_simplejwt', # Adicione esta linha para JWT

    'core', # Nosso app que conterá o modelo Imobiliaria
    'app_imoveis.apps.AppImoveisConfig',
    'app_clientes.apps.AppClientesConfig',
    'app_contratos.apps.AppContratosConfig',
]


MIDDLEWARE = [
    # Nosso custom middleware para identificar o tenant pelo subdomínio
    'ImobCloud.middleware.TenantIdentificationMiddleware', # DEVE VIR ANTES DE OUTROS MIDDLEWARE QUE PRECISAM DO TENANT
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # DEVE VIR ANTES DE CommonMiddleware, SessionMiddleware etc.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
        'rest_framework_simplejwt.authentication.JWTAuthentication', # Adicionado para usar JWT
        'rest_framework.authentication.SessionAuthentication',       # Opcional: útil para browsable API
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # Por padrão, vamos permitir acesso irrestrito para facilitar o desenvolvimento
        # e aplicar IsAuthenticated nas views específicas do painel da imobiliária.
        'rest_framework.permissions.AllowAny', # Permite acesso sem autenticação
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer', # Fornece a interface navegável no navegador
    ],
}

# =============================================================
# CORS Headers Settings (para requisições entre origens diferentes)
# =============================================================
# Para desenvolvimento, permitir todas as origens é conveniente.
# Em produção, você deve mudar para False e listar explicitamente as origens permitidas.
CORS_ALLOW_ALL_ORIGINS = True

# Se CORS_ALLOW_ALL_ORIGINS for False, você listaria as origens permitidas assim:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
#     "http://sol.localhost:5173", # Adicione todos os seus subdomínios .localhost aqui
#     # Ex: "http://imobiliaria_teste.localhost:5173",
#     # Para produção: "https://seusistema.com", "https://*.seusistema.com"
# ]

# Importante para lidar com credenciais (cookies, cabeçalhos de autorização) entre origens
CORS_ALLOW_CREDENTIALS = True

# =============================================================
# Jazzmin Admin Theme Settings
# Mais informações: https://jazzmin.netlify.app/pages/configuration.html
# =============================================================
JAZZMIN_SETTINGS = {
    # Título que aparece na aba do navegador
    "site_title": "ImobCloud Admin",

    # Título que aparece no cabeçalho do painel
    "site_header": "ImobCloud",

    # Nome da marca no sidebar (pequeno)
    "site_brand": "ImobCloud",

    # Logo opcional (caminho para um arquivo estático)
    "site_logo": "img/logo.png", # Você precisaria criar este arquivo static/img/logo.png
    "site_logo_classes": "img-circle", # Ex: "img-circle", "img-square"

    # URL para onde o logo aponta
    "login_logo": None,
    "login_logo_dark": None,

    # Barra de pesquisa no admin
    "search_model": ["auth.User", "core.Imobiliaria", "app_imoveis.Imovel"],

    # Links no cabeçalho (ex: link para o site público)
    "topbar_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Suporte", "url": "#", "new_window": True}, # Exemplo de link de suporte
        {"model": "auth.User"}, # Link para o modelo de usuário
    ],

    # Navegação no sidebar (modelo de itens do menu)
    "order_with_respect_to": ["core", "app_imoveis", "app_clientes", "app_contratos", "auth"],

    # Configurações de UI do sidebar
    "navigation_expanded": True, # Sidebar expandido por padrão
    "show_sidebar": True,
    "sidebar_nav_compact_mode": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_icons": True,
    "actions_dropdown_urls": True, # Mostrar URLs para ações dropdown

    # Estilos de tema (escolha um)
    # Veja as opções em: https://jazzmin.netlify.app/pages/themes.html
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",
    "usermenu_links": [
        # {"name": "Seu Perfil", "url": "/admin/auth/user/change/"}, # Exemplo
        {"model": "auth.user"}
    ],
    "show_ui_builder": False, # Mude para True se quiser experimentar temas visuais (apenas em dev)
    "theme": "united", # Tema padrão
    "dark_mode_theme": None, # Tema para modo escuro (ex: "darkly", "slate", "superhero")
    "custom_css": None, # Caminho para seu CSS customizado
    "custom_js": None,  # Caminho para seu JS customizado
    "show_language_chooser": True,
}

# =============================================================
# Jazzmin UI Tweaks (Para ajustes finos de UI)
# Mais informações: https://jazzmin.netlify.app/pages/ui_tweaks.html
# =============================================================
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-navy", # Cor da marca na barra de navegação
    "accent": "accent-primary", # Cor de destaque para elementos interativos
    "navbar": "navbar-dark", # Estilo da barra de navegação
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
    "theme": "united", # Deve ser o mesmo de JAZZMIN_SETTINGS.theme
    "dark_mode_theme": None, # Deve ser o mesmo de JAZZMIN_SETTINGS.dark_mode_theme
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
    "sidebar_nav_top_level_style": "tabs", # ou "cards" ou None
    "sidebar_nav_top_level_color": "navbar-light",
}

# =============================================================
# Configurações de Mídia (Upload de Arquivos)
# https://docs.djangoproject.com/en/5.0/ref/settings/#media-root
# https://docs.djangoproject.com/en/5.0/ref/settings/#media-url
# =============================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
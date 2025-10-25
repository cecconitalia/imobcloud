# C:\wamp64\www\Imobcloud\ImobCloud\urls_public.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adicione aqui futuras URLs que serão acessíveis globalmente,
    # como uma página de registro para novas imobiliárias ou a página inicial do sistema.
]
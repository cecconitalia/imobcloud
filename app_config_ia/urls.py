from django.urls import path
from .views import ListarVozesDaMarcaView, ConfiguracaoImobiliariaView

urlpatterns = [
    path('opcoes-voz/', ListarVozesDaMarcaView.as_view(), name='listar-vozes-marca'),
    path('configuracao/', ConfiguracaoImobiliariaView.as_view(), name='configuracao-imobiliaria'),
]
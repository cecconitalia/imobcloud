# C:\wamp64\www\ImobCloud\app_clientes\urls.py

from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    ClienteViewSet, 
    VisitaViewSet, 
    AtividadeViewSet, 
    OportunidadeViewSet,
    TarefaViewSet,
    MinhasTarefasView,
    GoogleCalendarAuthView,
    GoogleCalendarAuthCallbackView,
    RelatoriosView,
    FunilEtapaViewSet, # ADICIONADO AQUI
)

# Roteador principal
router = routers.DefaultRouter()

router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'oportunidades', OportunidadeViewSet, basename='oportunidade')
router.register(r'tarefas', TarefaViewSet, basename='tarefa')
router.register(r'minhas-tarefas', MinhasTarefasView, basename='minhas-tarefas')
router.register(r'relatorios', RelatoriosView, basename='relatorios')

# ADICIONADO AQUI: Rota para as etapas do funil dinâmico
router.register(r'funil-etapas', FunilEtapaViewSet, basename='funil-etapas')

# Roteador aninhado
oportunidades_router = routers.NestedSimpleRouter(router, r'oportunidades', lookup='oportunidade')
oportunidades_router.register(r'tarefas', TarefaViewSet, basename='oportunidade-tarefas')

urlpatterns = [
    # Incluímos as URLs de ambos os roteadores
    path('', include(router.urls)),
    path('', include(oportunidades_router.urls)),
    
    # URLs específicas
    path('google-calendar-auth/', GoogleCalendarAuthView.as_view(), name='google-calendar-auth'),
    path('google-calendar-auth/callback/', GoogleCalendarAuthCallbackView.as_view(), name='google-calendar-auth-callback'),
]
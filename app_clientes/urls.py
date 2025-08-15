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
    RelatoriosView
)

# Roteador principal e unificado
# CORREÇÃO: Removemos os roteadores múltiplos e consolidamos tudo em um só.
router = routers.DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'oportunidades', OportunidadeViewSet, basename='oportunidade')
router.register(r'tarefas', TarefaViewSet, basename='tarefa')

# CORREÇÃO: A URL para 'Minhas Tarefas' é registrada no roteador principal.
# Isso cria o endpoint: /api/v1/minhas-tarefas/
router.register(r'minhas-tarefas', MinhasTarefasView, basename='minhas-tarefas')

# Roteador aninhado para tarefas de oportunidades (esta parte está correta e é mantida)
# Cria o endpoint: /api/v1/oportunidades/{oportunidade_pk}/tarefas/
oportunidades_router = routers.NestedSimpleRouter(router, r'oportunidades', lookup='oportunidade')
oportunidades_router.register(r'tarefas', TarefaViewSet, basename='oportunidade-tarefas')

urlpatterns = [
    # Incluímos as URLs do roteador principal e do aninhado
    path('', include(router.urls)),
    path('', include(oportunidades_router.urls)),
    
    # Mantemos as URLs específicas que não usam o roteador
    path('google-calendar-auth/', GoogleCalendarAuthView.as_view(), name='google-calendar-auth'),
    path('google-calendar-auth/callback/', GoogleCalendarAuthCallbackView.as_view(), name='google-calendar-auth-callback'),
    
    path('relatorios/', RelatoriosView.as_view({'get': 'list'}), name='relatorios'),
]
# C:\wamp64\www\ImobCloud\app_clientes\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

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
    FunilEtapaViewSet,
    GerarRelatorioVisitaPDFView
)

# Roteador principal
router = DefaultRouter()

# --- ROTAS PRINCIPAIS ---
# Estas rotas ficam disponíveis em /api/v1/...
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'oportunidades', OportunidadeViewSet, basename='oportunidade')
router.register(r'fases-funil', FunilEtapaViewSet, basename='fases-funil')

# REGISTRO DAS TAREFAS
router.register(r'tarefas', TarefaViewSet, basename='tarefa')

router.register(r'minhas-tarefas', MinhasTarefasView, basename='minhas-tarefas')
router.register(r'relatorios', RelatoriosView, basename='relatorios')

# --- ROTEADOR ANINHADO (Opcional, mas mantido para compatibilidade) ---
# Permite acessar /api/v1/oportunidades/{id}/tarefas/
oportunidades_router = NestedSimpleRouter(router, r'oportunidades', lookup='oportunidade')
oportunidades_router.register(r'tarefas', TarefaViewSet, basename='oportunidade-tarefas')

urlpatterns = [
    # Inclui as rotas do roteador principal
    path('', include(router.urls)),
    
    # Inclui as rotas aninhadas
    path('', include(oportunidades_router.urls)),
    
    # URLs específicas (Auth Google, PDF, etc)
    path('google-calendar-auth/', GoogleCalendarAuthView.as_view(), name='google-calendar-auth'),
    path('google-calendar-auth/callback/', GoogleCalendarAuthCallbackView.as_view(), name='google-calendar-auth-callback'),
    path('visitas/<int:pk>/pdf/', GerarRelatorioVisitaPDFView.as_view(), name='visita-pdf'),
]
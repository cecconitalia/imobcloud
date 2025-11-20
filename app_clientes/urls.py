# C:\wamp64\www\ImobCloud\app_clientes\urls.py

from django.urls import path, include
# Importamos o DefaultRouter nativo para evitar conflitos com prefixos complexos
from rest_framework.routers import DefaultRouter
# Importamos apenas o NestedSimpleRouter da biblioteca nested
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
    GerarRelatorioVisitaPDFView # NOVO IMPORT
)

# Roteador principal (Usa o nativo para maior compatibilidade com prefixos '/')
router = DefaultRouter()

# --- ROTAS ESPECÍFICAS (Registrar ANTES de 'clientes' para evitar conflitos de URL) ---
# O frontend chama: /api/v1/clientes/oportunidades/
router.register(r'clientes/oportunidades', OportunidadeViewSet, basename='oportunidade')

# O frontend chama: /api/v1/clientes/fases-funil/
router.register(r'clientes/fases-funil', FunilEtapaViewSet, basename='fases-funil')

# --- ROTAS GERAIS ---
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'tarefas', TarefaViewSet, basename='tarefa')
router.register(r'minhas-tarefas', MinhasTarefasView, basename='minhas-tarefas')
router.register(r'relatorios', RelatoriosView, basename='relatorios')

# --- ROTEADOR ANINHADO (Para tarefas dentro de oportunidades) ---
# Atenção: O prefixo aqui DEVE ser idêntico ao registado acima (clientes/oportunidades)
oportunidades_router = NestedSimpleRouter(router, r'clientes/oportunidades', lookup='oportunidade')
oportunidades_router.register(r'tarefas', TarefaViewSet, basename='oportunidade-tarefas')

urlpatterns = [
    # Incluímos as URLs de ambos os roteadores
    path('', include(router.urls)),
    path('', include(oportunidades_router.urls)),
    
    # URLs específicas fora do router
    path('google-calendar-auth/', GoogleCalendarAuthView.as_view(), name='google-calendar-auth'),
    path('google-calendar-auth/callback/', GoogleCalendarAuthCallbackView.as_view(), name='google-calendar-auth-callback'),

    # NOVO: Rota para PDF da Visita
    path('visitas/<int:pk>/pdf/', GerarRelatorioVisitaPDFView.as_view(), name='visita-pdf'),
]
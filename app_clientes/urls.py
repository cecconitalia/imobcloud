# C:\wamp64\www\ImobCloud\app_clientes\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    EtapaFunilViewSet,  # <-- IMPORTADO
    ClienteViewSet, 
    VisitaViewSet, 
    AtividadeViewSet, 
    OportunidadeViewSet,
    TarefaViewSet,
    MinhasTarefasView,
    GoogleCalendarAuthView,
    GoogleCalendarAuthCallbackView,
    RelatoriosView,
    FunilVendasDataView
)

# Roteador principal
router = DefaultRouter()
# --- NOVA ROTA ADICIONADA AQUI ---
router.register(r'etapas-funil', EtapaFunilViewSet, basename='etapa-funil')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'oportunidades', OportunidadeViewSet, basename='oportunidade')

# Roteador aninhado para tarefas de oportunidades (inalterado)
oportunidades_router = routers.NestedSimpleRouter(router, r'oportunidades', lookup='oportunidade')
oportunidades_router.register(r'tarefas', TarefaViewSet, basename='oportunidade-tarefas')

# Router para Minhas Tarefas (inalterado)
router_minhas_tarefas = DefaultRouter()
router_minhas_tarefas.register(r'minhas-tarefas', MinhasTarefasView, basename='minhas-tarefas')

# O TarefaViewSet de nível superior precisa ser configurado manualmente
# para evitar conflitos com o roteador aninhado. (inalterado)
tarefas_list = TarefaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
tarefas_detail = TarefaViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

# Lista de URLs (inalterada, exceto pela adição do router)
urlpatterns = [
    # Inclui as rotas dos roteadores (agora com 'etapas-funil')
    path('', include(router.urls)),
    path('', include(oportunidades_router.urls)),
    path('', include(router_minhas_tarefas.urls)),
    
    # Rota para a visualização do Funil de Vendas com Vue Flow
    path('funil-vendas/', FunilVendasDataView.as_view(), name='funil-vendas-data'),
    
    # Rotas explícitas para tarefas de nível superior
    path('tarefas/', tarefas_list, name='tarefa-list'),
    path('tarefas/<int:pk>/', tarefas_detail, name='tarefa-detail'),
    
    # Rotas para autenticação com Google Calendar
    path('google-calendar-auth/', GoogleCalendarAuthView.as_view(), name='google-calendar-auth'),
    path('google-calendar-auth/callback/', GoogleCalendarAuthCallbackView.as_view(), name='google-calendar-auth-callback'),
    
    # Rota para Relatórios
    path('relatorios/', RelatoriosView.as_view({'get': 'list'}), name='relatorios'),
]
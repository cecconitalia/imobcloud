# C:\wamp64\www\ImobCloud\app_clientes\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
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

# Roteador principal
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'visitas', VisitaViewSet)
router.register(r'atividades', AtividadeViewSet)
router.register(r'oportunidades', OportunidadeViewSet)

# Roteador aninhado para tarefas de oportunidades
oportunidades_router = routers.NestedSimpleRouter(router, r'oportunidades', lookup='oportunidade')
oportunidades_router.register(r'tarefas', TarefaViewSet, basename='oportunidade-tarefas')

# Router para Minhas Tarefas
router_minhas_tarefas = DefaultRouter()
router_minhas_tarefas.register(r'minhas-tarefas', MinhasTarefasView, basename='minhas-tarefas')

# O TarefaViewSet de nível superior precisa ser configurado manualmente
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

urlpatterns = [
    path('', include(router.urls)),
    path('', include(oportunidades_router.urls)),
    path('', include(router_minhas_tarefas.urls)),
    
    # CORREÇÃO: Rotas explícitas para tarefas de nível superior
    path('tarefas/', tarefas_list, name='tarefa-list'),
    path('tarefas/<int:pk>/', tarefas_detail, name='tarefa-detail'),
    
    path('google-calendar-auth/', GoogleCalendarAuthView.as_view(), name='google-calendar-auth'),
    path('google-calendar-auth/callback/', GoogleCalendarAuthCallbackView.as_view(), name='google-calendar-auth-callback'),
    
    path('relatorios/', RelatoriosView.as_view({'get': 'list'}), name='relatorios'),
]
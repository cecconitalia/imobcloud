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

# Roteador principal
router = routers.DefaultRouter()

# CORREÇÃO APLICADA AQUI:
# Com base no seu urls.py principal, o correto é registrar o ClienteViewSet
# sob o prefixo 'clientes'. Isto irá gerar a URL final correta: /api/v1/clientes/
router.register(r'clientes', ClienteViewSet, basename='cliente')

# As outras rotas serão aninhadas sob /api/v1/, como por exemplo:
# /api/v1/visitas/, /api/v1/oportunidades/, etc.
router.register(r'visitas', VisitaViewSet, basename='visita')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'oportunidades', OportunidadeViewSet, basename='oportunidade')
router.register(r'tarefas', TarefaViewSet, basename='tarefa')
router.register(r'minhas-tarefas', MinhasTarefasView, basename='minhas-tarefas')

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
    path('relatorios/', RelatoriosView.as_view({'get': 'list'}), name='relatorios'),
]
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
    RelatoriosView # <-- View importada
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

urlpatterns = [
    path('', include(router.urls)),
    path('', include(oportunidades_router.urls)),
    path('minhas_tarefas/', MinhasTarefasView.as_view(), name='minhas-tarefas'),
    
    path('google-calendar-auth/', GoogleCalendarAuthView.as_view(), name='google-calendar-auth'),
    path('google-calendar-auth/callback/', GoogleCalendarAuthCallbackView.as_view(), name='google-calendar-auth-callback'),
    
    # NOVA URL PARA OS RELATÓRIOS
    path('relatorios/', RelatoriosView.as_view(), name='relatorios'),
]
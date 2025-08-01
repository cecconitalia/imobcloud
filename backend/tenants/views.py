# tenants/views.py
from rest_framework import viewsets, permissions
from .models import Tenant
from .serializers import TenantSerializer

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    # AQUI ESTÁ A SEGURANÇA:
    # Apenas usuários que são administradores (is_staff=True) podem acessar.
    permission_classes = [permissions.IsAdminUser]
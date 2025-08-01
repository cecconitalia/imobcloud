# tenants/serializers.py
from rest_framework import serializers
from .models import Tenant, Domain

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('id', 'domain', 'is_primary')

class TenantSerializer(serializers.ModelSerializer):
    # Usamos o DomainSerializer para aninhar os domínios dentro de cada tenant
    domains = DomainSerializer(many=True, read_only=True, source='domains')

    class Meta:
        model = Tenant
        fields = ('id', 'schema_name', 'name', 'created_on', 'domains')
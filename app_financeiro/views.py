from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, ContaBancaria, Transacao
from .serializers import CategoriaSerializer, ContaBancariaSerializer, TransacaoSerializer
from core.permissions import IsCorretorOrReadOnly
from core.models import PerfilUsuario

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Categoria.objects.all()
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil:
            return Categoria.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria)
        return Categoria.objects.none()

class ContaBancariaViewSet(viewsets.ModelViewSet):
    queryset = ContaBancaria.objects.all()
    serializer_class = ContaBancariaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ContaBancaria.objects.all()
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil:
            return ContaBancaria.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria)
        return ContaBancaria.objects.none()

class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsCorretorOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transacao.objects.all()
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil:
            return Transacao.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria)
        return Transacao.objects.none()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        if not hasattr(request.user, 'perfil') or not request.user.perfil:
            return Response({"error": "Usuário sem perfil associado."}, status=status.HTTP_400_BAD_REQUEST)
        
        hoje = timezone.now().date()
        inicio_do_mes = hoje.replace(day=1)

        transacoes_mes = Transacao.objects.filter(
            imobiliaria=request.user.perfil.imobiliaria,
            data__gte=inicio_do_mes,
            data__lte=hoje
        )

        total_receitas = transacoes_mes.filter(tipo='RECEITA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        total_despesas = transacoes_mes.filter(tipo='DESPESA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        saldo_mes = total_receitas - total_despesas

        return Response({
            "receitas_mes": total_receitas,
            "despesas_mes": total_despesas,
            "saldo_mes": saldo_mes
        })
    
    @action(detail=False, methods=['get'])
    def dre(self, request):
        if not hasattr(request.user, 'perfil') or not request.user.perfil:
            return Response({"error": "Usuário sem perfil associado."}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        transacoes = Transacao.objects.filter(imobiliaria=request.user.perfil.imobiliaria)
        if start_date:
            transacoes = transacoes.filter(data__gte=start_date)
        if end_date:
            transacoes = transacoes.filter(data__lte=end_date)
            
        receitas_brutas = transacoes.filter(tipo='RECEITA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        despesas_operacionais = transacoes.filter(tipo='DESPESA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']

        dre_data = {
            "receita_bruta_servicos": {
                "titulo": "Receita Bruta",
                "valor": receitas_brutas,
                "subcategorias": []
            },
            "deducoes_receita": {
                "titulo": "Deduções da Receita Bruta",
                "valor": 0,
                "subcategorias": []
            },
            "custo_servicos": {
                "titulo": "Custo dos Serviços Prestados",
                "valor": 0,
                "subcategorias": []
            },
            "lucro_bruto": {
                "titulo": "Lucro Bruto",
                "valor": receitas_brutas,
            },
            "despesas_operacionais": {
                "titulo": "Despesas Operacionais",
                "valor": despesas_operacionais,
                "subcategorias": []
            },
            "lucro_liquido_antes_impostos": {
                "titulo": "Lucro Líquido Antes dos Impostos",
                "valor": receitas_brutas - despesas_operacionais,
            },
        }

        for categoria in Categoria.objects.filter(imobiliaria=request.user.perfil.imobiliaria, pai__isnull=True):
            subcategorias_data = []
            for subcategoria in categoria.subcategorias.all():
                subtotal = transacoes.filter(categoria=subcategoria).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
                subcategorias_data.append({
                    "titulo": subcategoria.nome,
                    "valor": subtotal
                })
            
            total_categoria = transacoes.filter(categoria=categoria).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
            
            if categoria.tipo == 'RECEITA':
                dre_data["receita_bruta_servicos"]["subcategorias"].append({
                    "titulo": categoria.nome,
                    "valor": total_categoria,
                    "subcategorias": subcategorias_data
                })
            elif categoria.tipo == 'DESPESA':
                dre_data["despesas_operacionais"]["subcategorias"].append({
                    "titulo": categoria.nome,
                    "valor": total_categoria,
                    "subcategorias": subcategorias_data
                })

        return Response(dre_data)
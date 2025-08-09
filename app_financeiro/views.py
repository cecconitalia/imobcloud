from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, ContaBancaria, Transacao
from .serializers import CategoriaSerializer, ContaBancariaSerializer, TransacaoSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class ContaBancariaViewSet(viewsets.ModelViewSet):
    queryset = ContaBancaria.objects.all()
    serializer_class = ContaBancariaSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Correção para o erro 'perfilusuario'
        if not hasattr(request.user, 'perfilusuario'):
            return Response({"error": "O utilizador não tem um perfil associado."}, status=status.HTTP_400_BAD_REQUEST)

        transacoes_mes = Transacao.objects.filter(imobiliaria=request.user.perfilusuario.imobiliaria, data__gte=start_of_month, data__lte=today)
        
        receitas_mes = transacoes_mes.filter(tipo='RECEITA').aggregate(total=Sum('valor'))['total'] or 0
        despesas_mes = transacoes_mes.filter(tipo='DESPESA').aggregate(total=Sum('valor'))['total'] or 0
        
        saldo_mes = receitas_mes - despesas_mes
        
        data = {
            'receitas_mes': receitas_mes,
            'despesas_mes': despesas_mes,
            'saldo_mes': saldo_mes,
        }
        
        return Response(data)

    @action(detail=False, methods=['get'])
    def dre(self, request):
        # Correção para o erro 'perfilusuario'
        if not hasattr(request.user, 'perfilusuario'):
            return Response({"error": "O utilizador não tem um perfil associado."}, status=status.HTTP_400_BAD_REQUEST)
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        transacoes = Transacao.objects.filter(imobiliaria=request.user.perfilusuario.imobiliaria)
        if start_date:
            transacoes = transacoes.filter(data__gte=start_date)
        if end_date:
            transacoes = transacoes.filter(data__lte=end_date)
            
        receitas = transacoes.filter(tipo='RECEITA').aggregate(total=Sum('valor'))['total'] or 0
        despesas = transacoes.filter(tipo='DESPESA').aggregate(total=Sum('valor'))['total'] or 0
        
        dre_data = {
            "receita_bruta_servicos": {
                "titulo": "Receita Bruta",
                "valor": receitas,
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
                "valor": receitas - 0,
            },
            "despesas_operacionais": {
                "titulo": "Despesas Operacionais",
                "valor": despesas,
                "subcategorias": []
            },
            "lucro_liquido_antes_impostos": {
                "titulo": "Lucro Líquido Antes dos Impostos",
                "valor": receitas - despesas,
            },
        }
        
        for categoria in Categoria.objects.filter(imobiliaria=request.user.perfilusuario.imobiliaria, pai__isnull=True):
            subcategorias_data = []
            for subcategoria in categoria.subcategorias.all():
                subtotal = transacoes.filter(categoria=subcategoria).aggregate(total=Sum('valor'))['total'] or 0
                subcategorias_data.append({
                    "titulo": subcategoria.nome,
                    "valor": subtotal
                })
            
            total_categoria = transacoes.filter(categoria=categoria).aggregate(total=Sum('valor'))['total'] or 0
            
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
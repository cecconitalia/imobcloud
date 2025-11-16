# C:\wamp64\www\ImobCloud\app_contratos\views.py

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Contrato, Pagamento
from .serializers import ContratoSerializer, PagamentoSerializer, ContratoCriacaoSerializer 
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from django.conf import settings
import os
from django.utils.dateparse import parse_date
from django.db import transaction
from django.db.models import Exists, OuterRef
from app_financeiro.models import Transacao 
from rest_framework.views import APIView # Importação necessária para a classe
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import re # Importar a biblioteca de Expressões Regulares (RegEx)

# Importar a função de valor por extenso
from ImobCloud.utils.formatacao_util import valor_por_extenso


# =================================================================
# === Função helper 'get_contrato_context' (movida para fora)    ===
# =================================================================
def get_contrato_context(contrato):
    """
    Função helper para montar o CONTEXTO (agora fora da classe)
    """
    
    # Preparar valores por extenso
    valor_total_extenso = "(Valor total não definido)"
    if contrato.valor_total:
        try:
            # Usa a função importada
            valor_total_extenso = valor_por_extenso(contrato.valor_total)
        except Exception:
            pass # Mantém o default

    aluguel_extenso = "(Valor do aluguel não definido)"
    if contrato.aluguel:
        try:
            # Usa a função importada
            aluguel_extenso = valor_por_extenso(contrato.aluguel)
        except Exception:
            pass # Mantém o default

    valor_comissao_extenso = "(Valor de comissão não definido)"
    if contrato.valor_comissao_acordado:
        try:
            # Usa a função importada
            valor_comissao_extenso = valor_por_extenso(contrato.valor_comissao_acordado)
        except Exception:
            pass # Mantém o default

    context = {
        'contrato': contrato,
        'proprietario': contrato.proprietario,
        'inquilino': contrato.inquilino,
        'imovel': contrato.imovel,
        'fiadores': contrato.fiadores.all(),
        'imobiliaria': contrato.imobiliaria,
        'data_hoje': timezone.now(),
        
        # Adicionando os valores por extenso que faltavam
        'valor_total_extenso': valor_total_extenso,
        'aluguel_extenso': aluguel_extenso,
        'valor_comissao_extenso': valor_comissao_extenso,
    }
    return context


class ContratoViewSet(viewsets.ModelViewSet):
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.imobiliaria:
            
            # CORREÇÃO: O nome do campo é 'status', não 'status_pagamento'
            pagamento_exists_subquery = Pagamento.objects.filter(
                contrato=OuterRef('pk'),
                status='PAGO' # <-- CORRIGIDO
            ).values('pk')
            
            transacao_exists_subquery = Transacao.objects.filter(
                contrato=OuterRef('pk'),
                tipo='RECEITA',
                status='PAGO'
            ).values('pk')

            return Contrato.objects.filter(
                imobiliaria=self.request.user.perfil.imobiliaria
            ).annotate(
                # Verifica se existe algum pagamento PAGO para este contrato
                possui_pagamento_pago=Exists(pagamento_exists_subquery),
                # Verifica se existe alguma transação de RECEITA PAGA para este contrato
                possui_transacao_paga=Exists(transacao_exists_subquery)
            ).order_by('-data_assinatura')
        return Contrato.objects.none()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return ContratoCriacaoSerializer
        return ContratoSerializer

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.imobiliaria:
            serializer.save(imobiliaria=self.request.user.perfil.imobiliaria)
        else:
            raise ValidationError("Usuário não tem imobiliária associada.")
            
    def perform_update(self, serializer):
        # A lógica de atualização (sinais) cuidará do financeiro
        serializer.save()

    @action(detail=True, methods=['get'])
    def pagamentos(self, request, pk=None):
        contrato = self.get_object()
        pagamentos = Pagamento.objects.filter(contrato=contrato).order_by('data_vencimento')
        serializer = PagamentoSerializer(pagamentos, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def transacoes(self, request, pk=None):
        contrato = self.get_object()
        
        # Tenta buscar transações de aluguel (Pagamentos)
        pagamentos = Pagamento.objects.filter(contrato=contrato).order_by('data_vencimento')
        
        # Tenta buscar transações de comissão de venda (Transações)
        transacoes_comissao = Transacao.objects.filter(
            contrato=contrato,
            tipo='RECEITA' # Assumindo que a comissão é uma RECEITA
        ).order_by('data_vencimento')

        # Serializa os dois tipos
        pagamentos_data = PagamentoSerializer(pagamentos, many=True).data
        transacoes_data = [] # Precisamos de um TransacaoSerializer aqui
        
        # Por enquanto, vamos focar nos pagamentos de aluguel se existirem
        if pagamentos.exists():
             serializer = PagamentoSerializer(pagamentos, many=True)
             return Response(serializer.data)
        
        return Response(pagamentos_data)


    # (Correção anterior)
    @action(detail=True, methods=['get'], url_path='get-html')
    def get_html_content(self, request, pk=None):
        contrato = get_object_or_404(Contrato, pk=pk)
        
        # 1. Se o contrato JÁ TEM conteúdo personalizado, use-o
        #    (Isto carrega as suas edições salvas)
        if contrato.conteudo_personalizado:
            return Response(contrato.conteudo_personalizado)
            
        # 2. Se não tiver, GERE o conteúdo pela primeira vez
        context = get_contrato_context(contrato) # Chamando a função standalone
        
        template_name = 'contrato_aluguel_template.html'
        if contrato.tipo_contrato == 'VENDA':
            template_name = 'contrato_venda_template.html'
            
        html_string = render_to_string(template_name, context)
        
        # 3. Salve o HTML (recém-gerado) no banco
        contrato.conteudo_personalizado = html_string
        contrato.save()
        
        # 4. Retorne o HTML
        return Response(html_string)


    # (Correção anterior)
    @action(detail=True, methods=['post'], url_path='salvar-html-editado')
    def salvar_html_editado(self, request, pk=None):
        contrato = get_object_or_404(Contrato, pk=pk)
        html_content = request.data.get('html_content', '')
        
        if not html_content:
            return Response({"error": "Nenhum conteúdo HTML fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
        contrato.conteudo_personalizado = html_content
        contrato.save()
        
        return Response({"success": "Documento atualizado com sucesso."})


    # =================================================================
    # === CORREÇÃO: Adicionar url_path='visualizar-pdf'            ===
    # === para corrigir o erro 404 Not Found ao visualizar.         ===
    # =================================================================
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny], url_path='visualizar-pdf') # Cuidado: AllowAny
    def generate_pdf_contrato(self, request, pk=None):
        try:
            contrato = get_object_or_404(Contrato, pk=pk)
            
            # 1. Pega o HTML (prioriza o editado)
            html_content = contrato.conteudo_personalizado
            
            # 2. Se não houver HTML editado, gera a partir do template
            if not html_content:
                # Chamando a função standalone
                context = get_contrato_context(contrato)
                
                template_name = 'contrato_aluguel_template.html'
                if contrato.tipo_contrato == 'VENDA':
                    template_name = 'contrato_venda_template.html'
                
                html_content = render_to_string(template_name, context)

            # ==========================================================
            # LIMPEZA DE ESTILOS INCOMPATÍVEIS com xhtml2pdf
            # ==========================================================
            html_content = re.sub(r'font-size:[^;\"]*', '', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'font-family:[^;\"]*', '', html_content, flags=re.IGNORECASE)
            
            html_content = re.sub(r'<p style=\"text-align:\\s*center;\">', r'<p align=\"center\">', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<p style=\"text-align:\\s*right;\">', r'<p align=\"right\">', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<p style=\"text-align:\\s*left;\">', r'<p align=\"left\">', html_content, flags=re.IGNORECASE)
            
            html_content = re.sub(r'text-align:[^;\"]*', '', html_content, flags=re.IGNORECASE) 
            
            html_content = re.sub(r'<span style=\"\\s*\">\\s*</span>', '', html_content, flags=re.IGNORECASE)
            # ==========================================================

            # Adicionar meta charset UTF-8
            html_string_with_meta = f'<html><head><meta charset=\"UTF-8\"></head><body>{html_content}</body></html>'

            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html_string_with_meta.encode("UTF-8")), result)
            
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'filename="contrato_{pk}.pdf"'
                return response
            else:
                return HttpResponse(f'Erro ao gerar PDF: {pdf.err}', status=500)

        except Contrato.DoesNotExist:
            return Response({"error": "Contrato não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Classe PagamentoViewSet (Adicionada na correção anterior)
class PagamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Pagamentos (Criada para corrigir o ImportError).
    """
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Garante que o usuário só veja pagamentos da sua imobiliária
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.imobiliaria:
            return Pagamento.objects.filter(
                contrato__imobiliaria=self.request.user.perfil.imobiliaria
            ).order_by('-data_vencimento')
        
        # Se não tiver imobiliária, não retorna nada
        return Pagamento.objects.none()

    def perform_create(self, serializer):
        serializer.save()


# Classe GerarReciboView (Adicionada na correção anterior)
class GerarReciboView(APIView):
    """
    View baseada em classe para gerar o PDF do recibo.
    Substitui a antiga função 'gerar_recibo_pdf'.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pagamento_id):
        pagamento = get_object_or_404(Pagamento, pk=pagamento_id, contrato__imobiliaria=request.user.perfil.imobiliaria)

        if pagamento.status != 'PAGO': # <-- CORRIGIDO
            return HttpResponse("Este pagamento ainda não foi baixado.", status=400)

        # Lógica para gerar o recibo (exemplo simples)
        context = {
            'pagamento': pagamento,
            'contrato': pagamento.contrato,
            'imobiliaria': pagamento.contrato.imobiliaria,
            'locatario': pagamento.contrato.inquilino,
            'locador': pagamento.contrato.proprietario,
            'imovel': pagamento.contrato.imovel,
            'data_pagamento': pagamento.data_pagamento or timezone.now(), # Usa a data do pagamento se houver
        }
        
        html_string = render_to_string('recibo_template.html', context)
        
        # Limpeza de estilos
        html_string = re.sub(r'font-size:[^;\"]*', '', html_string, flags=re.IGNORECASE)
        html_string = re.sub(r'font-family:[^;\"]*', '', html_string, flags=re.IGNORECASE)
        html_string = re.sub(r'<p style=\"text-align:\\s*center;\">', r'<p align=\"center\">', html_string, flags=re.IGNORECASE)
        html_string = re.sub(r'<p style=\"text-align:\\s*right;\">', r'<p align=\"right\">', html_content, flags=re.IGNORECASE)
        html_string = re.sub(r'<p style=\"text-align:\\s*left;\">', r'<p align=\"left\">', html_content, flags=re.IGNORECASE)
        html_string = re.sub(r'text-align:[^;\"]*', '', html_string, flags=re.IGNORECASE) 
        html_string = re.sub(r'<span style=\"\\s*\">\\s*</span>', '', html_string, flags=re.IGNORECASE)

        html_string_with_meta = f'<html><head><meta charset=\"UTF-8\"></head><body>{html_string}</body></html>'

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string_with_meta.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'filename="recibo_{pagamento_id}.pdf"'
            return response
        
        return HttpResponse(f'Erro ao gerar recibo: {pdf.err}', status=500)


# Função 'gerar_contrato_pdf_editado' (Adicionada na correção anterior)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gerar_contrato_pdf_editado(request, pk=None):
    """
    View standalone para gerar o PDF (usada pelo urls.py).
    A lógica é idêntica à action 'generate_pdf_contrato'.
    """
    try:
        # Garante que o contrato pertença à imobiliária do usuário
        if not (hasattr(request.user, 'perfil') and request.user.perfil.imobiliaria):
             return HttpResponse("Usuário não tem imobiliária associada.", status=403)
             
        contrato = get_object_or_404(Contrato, pk=pk, imobiliaria=request.user.perfil.imobiliaria)
        
        # 1. Pega o HTML (prioriza o editado)
        html_content = contrato.conteudo_personalizado
        
        # 2. Se não houver HTML editado, gera a partir do template
        if not html_content:
            # Chama a função standalone
            context = get_contrato_context(contrato)
            
            template_name = 'contrato_aluguel_template.html'
            if contrato.tipo_contrato == 'VENDA':
                template_name = 'contrato_venda_template.html'
            
            html_content = render_to_string(template_name, context)

        # ==========================================================
        # LIMPEZA DE ESTILOS INCOMPATÍVEIS com xhtml2pdf
        # ==========================================================
        html_content = re.sub(r'font-size:[^;\"]*', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'font-family:[^;\"]*', '', html_content, flags=re.IGNORECASE)
        
        html_content = re.sub(r'<p style=\"text-align:\\s*center;\">', r'<p align=\"center\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p style=\"text-align:\\s*right;\">', r'<p align=\"right\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p style=\"text-align:\\s*left;\">', r'<p align=\"left\">', html_content, flags=re.IGNORECASE)
        
        html_content = re.sub(r'text-align:[^;\"]*', '', html_content, flags=re.IGNORECASE) 
        
        html_content = re.sub(r'<span style=\"\\s*\">\\s*</span>', '', html_content, flags=re.IGNORECASE)
        # ==========================================================

        # Adicionar meta charset UTF-8
        html_string_with_meta = f'<html><head><meta charset=\"UTF-8\"></head><body>{html_content}</body></html>'

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string_with_meta.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'filename="contrato_editado_{pk}.pdf"'
            return response
        else:
            return HttpResponse(f'Erro ao gerar PDF: {pdf.err}', status=500)

    except Contrato.DoesNotExist:
        return Response({"error": "Contrato não encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def limpar_estilos_view(request, pk):
    try:
        contrato = get_object_or_404(Contrato, pk=pk, imobiliaria=request.user.perfil.imobiliaria)
        
        if not contrato.conteudo_personalizado:
            return Response({"message": "Contrato não possui conteúdo personalizado."}, status=status.HTTP_400_BAD_REQUEST)

        html_content = contrato.conteudo_personalizado

        # ==========================================================
        # Aplicar a mesma limpeza aqui por segurança
        # ==========================================================
        html_content = re.sub(r'font-size:[^;\"]*', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'font-family:[^;\"]*', '', html_content, flags=re.IGNORECASE)
        
        # Converter alinhamento
        html_content = re.sub(r'<p style=\"text-align:\\s*center;\">', r'<p align=\"center\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p style=\"text-align:\\s*right;\">', r'<p align=\"right\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p style=\"text-align:\\s*left;\">', r'<p align=\"left\">', html_content, flags=re.IGNORECASE)
        
        html_content = re.sub(r'text-align:[^;\"]*', '', html_content, flags=re.IGNORECASE) # Limpa o que sobrou

        html_content = re.sub(r'<span style=\"\\s*\">\\s*</span>', '', html_content, flags=re.IGNORECASE)
        # ==========================================================

        html_string_with_meta = f'<html><head><meta charset=\"UTF-8\"></head><body>{html_content}</body></html>'

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string_with_meta.encode("UTF-8")), result)
        
        if not pdf.err:
            # Salvar o conteúdo limpo de volta no banco
            contrato.conteudo_personalizado = html_content
            contrato.save()
            return Response({"success": "Estilos limpos e documento salvo."})
        else:
            return Response({"error": f"Erro ao validar PDF após limpeza: {pdf.err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Contrato.DoesNotExist:
        return Response({"error": "Contrato não encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# C:\wamp64\www\ImobCloud\app_contratos\views.py

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Contrato, Pagamento, ModeloContrato
from .serializers import (
    ContratoSerializer, PagamentoSerializer, ContratoCriacaoSerializer, 
    ContratoListSerializer, ModeloContratoSerializer
)

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.template.loader import render_to_string

from django.template import Template, Context

from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from django.conf import settings
import os
from django.utils.dateparse import parse_date
from django.db import transaction
from django.db.models import Exists, OuterRef, Q, Count, Sum
from app_financeiro.models import Transacao 
from app_financeiro.serializers import TransacaoListSerializer 
from app_vistorias.models import Vistoria
from rest_framework.views import APIView 
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import re 

# === SEGURANÇA: Importação do Bleach ===
try:
    import bleach
except ImportError:
    bleach = None 

from ImobCloud.utils.formatacao_util import valor_por_extenso

def get_contrato_context(contrato):
    valor_total_extenso = "(Valor total não definido)"
    if contrato.valor_total:
        try:
            valor_total_extenso = valor_por_extenso(contrato.valor_total)
        except Exception:
            pass 

    aluguel_extenso = "(Valor do aluguel não definido)"
    if contrato.aluguel:
        try:
            aluguel_extenso = valor_por_extenso(contrato.aluguel)
        except Exception:
            pass 

    valor_comissao_extenso = "(Valor de comissão não definido)"
    if contrato.valor_comissao_acordado:
        try:
            valor_comissao_extenso = valor_por_extenso(contrato.valor_comissao_acordado)
        except Exception:
            pass
    
    proprietario = contrato.proprietario
    proprietario_pf = None
    proprietario_pj = None
    if proprietario:
        if proprietario.tipo_pessoa == 'FISICA': 
            proprietario_pf = proprietario 
        elif proprietario.tipo_pessoa == 'JURIDICA':
            proprietario_pj = proprietario 

    inquilino = contrato.inquilino
    inquilino_pf = None
    inquilino_pj = None
    if inquilino:
        if inquilino.tipo_pessoa == 'FISICA':
            inquilino_pf = inquilino
        elif inquilino.tipo_pessoa == 'JURIDICA':
            inquilino_pj = inquilino
    
    fiadores_list = []
    for fiador_cliente in contrato.fiadores.all():
        fiador_pf = None
        fiador_pj = None
        if fiador_cliente:
            if fiador_cliente.tipo_pessoa == 'FISICA':
                fiador_pf = fiador_cliente
            elif fiador_cliente.tipo_pessoa == 'JURIDICA':
                fiador_pj = fiador_cliente
        
        fiadores_list.append({
            'cliente': fiador_cliente, 
            'pf': fiador_pf,           
            'pj': fiador_pj            
        })
    
    context = {
        'contrato': contrato,
        'proprietario': proprietario,
        'inquilino': inquilino,
        'imovel': contrato.imovel,
        'imobiliaria': contrato.imobiliaria,
        'data_hoje': timezone.now(),
        
        'locador_pf': proprietario_pf,
        'locador_pj': proprietario_pj,
        'locatario_pf': inquilino_pf,
        'locatario_pj': inquilino_pj,
        'fiadores_list': fiadores_list,
        
        'fiadores': contrato.fiadores.all(), 

        'valor_total_extenso': valor_total_extenso,
        'aluguel_extenso': aluguel_extenso,
        'valor_comissao_extenso': valor_comissao_extenso,
    }
    return context


class ModeloContratoViewSet(viewsets.ModelViewSet):
    serializer_class = ModeloContratoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria
            
        if imobiliaria:
            queryset = ModeloContrato.objects.filter(
                imobiliaria=imobiliaria
            )
            tipo_contrato = self.request.query_params.get('tipo_contrato', None)
            if tipo_contrato:
                queryset = queryset.filter(tipo_contrato=tipo_contrato)
            return queryset.order_by('-padrao', 'nome')
        return ModeloContrato.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria

        if imobiliaria:
            serializer.save(imobiliaria=imobiliaria)
        else:
            raise ValidationError("Usuário não tem imobiliária associada.")

class ContratoViewSet(viewsets.ModelViewSet):
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria
            
        if imobiliaria:
            pagamento_exists_subquery = Pagamento.objects.filter(
                contrato=OuterRef('pk'),
                status='PAGO'
            ).values('pk')
            transacao_paga_exists_subquery = Transacao.objects.filter(
                contrato=OuterRef('pk'),
                tipo='RECEITA',
                status='PAGO'
            ).values('pk')
            transacao_financeira_exists = Transacao.objects.filter(
                contrato=OuterRef('pk')
            ).values('pk')

            return Contrato.objects.filter(
                imobiliaria=imobiliaria,
                excluido=False 
            ).annotate(
                possui_pagamento_pago=Exists(pagamento_exists_subquery),
                possui_transacao_paga=Exists(transacao_paga_exists_subquery),
                financeiro_gerado=Exists(transacao_financeira_exists)
            ).order_by('-data_cadastro') 
            
        return Contrato.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return ContratoListSerializer
        
        if self.action in ['create', 'update', 'partial_update', 'ativar']:
            return ContratoCriacaoSerializer
            
        return ContratoSerializer

    def perform_create(self, serializer):
        user = self.request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria

        if imobiliaria:
            serializer.save(imobiliaria=imobiliaria)
        else:
            raise ValidationError("Usuário não tem imobiliária associada.")
            
    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete() 
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contrato.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_contratos=Count('id'),
            total_ativos=Count('id', filter=Q(status_contrato=Contrato.Status.ATIVO)),
            total_rascunho=Count('id', filter=Q(status_contrato=Contrato.Status.RASCUNHO)),
            total_concluidos=Count('id', filter=Q(status_contrato=Contrato.Status.CONCLUIDO)),
            valor_total_alugueis_ativos=Sum(
                'aluguel',
                filter=Q(
                    tipo_contrato=Contrato.TipoContrato.ALUGUEL, 
                    status_contrato=Contrato.Status.ATIVO
                )
            ),
            valor_total_vendas_ativas=Sum(
                'valor_total', 
                filter=Q(
                    tipo_contrato=Contrato.TipoContrato.VENDA, 
                    status_contrato=Contrato.Status.ATIVO
                )
            )
        )
        stats['valor_total_vendas_ativas'] = stats['valor_total_vendas_ativas'] or 0
        stats['valor_total_alugueis_ativos'] = stats['valor_total_alugueis_ativos'] or 0

        return Response(stats)

    @action(detail=True, methods=['post'], url_path='ativar')
    def ativar(self, request, pk=None):
        try:
            contrato = self.get_object() 
            
            if contrato.status_contrato == Contrato.Status.ATIVO:
                return Response(
                    {"warning": "O contrato já está ativo."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            data_patch = {'status_contrato': Contrato.Status.ATIVO}
            if not contrato.data_assinatura:
                 data_patch['data_assinatura'] = timezone.now().date()

            serializer = self.get_serializer(
                contrato, 
                data=data_patch, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            
            self.perform_update(serializer)
            
            read_serializer = ContratoSerializer(serializer.instance, context={'request': request})
            return Response(read_serializer.data, status=status.HTTP_200_OK)

        except Contrato.DoesNotExist:
            return Response({"error": "Contrato não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            if isinstance(e, ValidationError):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def pagamentos(self, request, pk=None):
        contrato = self.get_object()
        
        # 1. Busca as Transações reais
        transacoes = Transacao.objects.filter(
            contrato=contrato, 
            tipo='RECEITA'
        ).order_by('data_vencimento')
        
        if transacoes.exists():
            serializer = TransacaoListSerializer(transacoes, many=True)
            return Response(serializer.data)
        
        # 2. Fallback
        if contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
             pagamentos = Pagamento.objects.filter(contrato=contrato).order_by('data_vencimento')
             serializer = PagamentoSerializer(pagamentos, many=True)
             return Response(serializer.data)
        
        return Response([]) 
        
    @action(detail=True, methods=['get'])
    def transacoes(self, request, pk=None):
        contrato = self.get_object()
        pagamentos = Pagamento.objects.filter(contrato=contrato).order_by('data_vencimento')
        pagamentos_data = PagamentoSerializer(pagamentos, many=True).data
        if pagamentos.exists():
             return Response(pagamentos_data)
        return Response(pagamentos_data)

    @action(detail=True, methods=['get'], url_path='get-html')
    def get_html_content(self, request, pk=None):
        contrato = get_object_or_404(Contrato, pk=pk)
        
        if contrato.conteudo_personalizado and len(contrato.conteudo_personalizado) > 50:
            return Response(contrato.conteudo_personalizado)
            
        context = get_contrato_context(contrato)
        html_string = ""
        
        modelo = contrato.modelo_utilizado
        
        if not modelo:
            modelo = ModeloContrato.objects.filter(
                imobiliaria=contrato.imobiliaria,
                tipo_contrato=contrato.tipo_contrato,
                padrao=True
            ).first()

        if modelo and modelo.conteudo and len(modelo.conteudo) > 50:
            try:
                template = Template(modelo.conteudo)
                context_obj = Context(context)
                html_string = template.render(context_obj)
            except Exception as e:
                print(f"Erro ao renderizar template do BD (ID: {modelo.id}): {e}")
                html_string = ""
        
        if not html_string:
            template_name = 'contrato_aluguel_template.html'
            if contrato.tipo_contrato == 'VENDA':
                template_name = 'contrato_venda_template.html'
            
            html_string = render_to_string(template_name, context)
        
        contrato.conteudo_personalizado = html_string
        contrato.save()
        
        return Response(html_string)

    @action(detail=True, methods=['post'], url_path='salvar-html-editado')
    def salvar_html_editado(self, request, pk=None):
        contrato = get_object_or_404(Contrato, pk=pk)
        html_content = request.data.get('html_content', '')
        
        if not html_content:
            return Response({"error": "Nenhum conteúdo HTML fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
        if bleach:
            allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
                'p', 'br', 'strong', 'b', 'i', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'span', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                'img', 'hr', 'blockquote'
            ]
            allowed_attributes = {
                '*': ['style', 'class', 'align'],
                'img': ['src', 'alt', 'width', 'height'],
                'a': ['href', 'target']
            }
            allowed_styles = [
                'color', 'background-color', 'text-align', 'font-size', 'font-weight', 
                'margin', 'padding', 'border', 'width', 'height', 'text-decoration'
            ]
            
            try:
                html_content = bleach.clean(
                    html_content,
                    tags=allowed_tags,
                    attributes=allowed_attributes,
                    styles=allowed_styles,
                    strip=True 
                )
            except Exception as e:
                print(f"Erro ao sanitizar HTML: {e}")
        
        contrato.conteudo_personalizado = html_content
        contrato.save()
        
        return Response({"success": "Documento atualizado com sucesso."})

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny], url_path='visualizar-pdf')
    def generate_pdf_contrato(self, request, pk=None):
        try:
            contrato = get_object_or_404(Contrato, pk=pk)
            
            html_content = contrato.conteudo_personalizado
            
            if not html_content or len(html_content) < 50:
                context = get_contrato_context(contrato)
                modelo = contrato.modelo_utilizado
                
                if not modelo:
                    modelo = ModeloContrato.objects.filter(
                        imobiliaria=contrato.imobiliaria,
                        tipo_contrato=contrato.tipo_contrato,
                        padrao=True
                    ).first()
                
                if modelo and modelo.conteudo and len(modelo.conteudo) > 50:
                    try:
                        template = Template(modelo.conteudo)
                        context_obj = Context(context)
                        html_content = template.render(context_obj)
                    except Exception:
                        html_content = "" 
                
                if not html_content:
                    template_name = 'contrato_aluguel_template.html'
                    if contrato.tipo_contrato == 'VENDA':
                        template_name = 'contrato_venda_template.html'
                    html_content = render_to_string(template_name, context)

            html_content = re.sub(r'<p style=\"text-align:\\s*center;\">', r'<p align=\"center\">', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<p style=\"text-align:\\s*right;\">', r'<p align=\"right\">', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<p style=\"text-align:\\s*left;\">', r'<p align=\"left\">', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<p style=\"text-align:\\s*justify;\">', r'<p align=\"justify\">', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<span style=\"\\s*\">\\s*</span>', '', html_content, flags=re.IGNORECASE)

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

    # =========================================================================
    # ACTION CORRIGIDA: PENDENTES VISTORIA (Inclui RASCUNHO para ENTRADA)
    # =========================================================================
    @action(detail=False, methods=['get'])
    def pendentes_vistoria(self, request):
        """
        Lista contratos aptos para vistoria.
        Lógica:
        - ENTRADA: Contratos ATIVOS ou RASCUNHO (Aluguel) que NÃO têm vistoria de entrada CONCLUÍDA.
        - SAÍDA: Contratos ATIVOS (Aluguel) que NÃO têm vistoria de saída CONCLUÍDA.
        """
        tipo = request.query_params.get('tipo', 'ENTRADA')
        
        # 1. Recuperar Imobiliária explicitamente
        user = request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria
            
        if not imobiliaria:
            return Response([])

        # 2. Queryset Base Limpo e Seguro
        # Filtrando explicitamente: Apenas desta imobiliária, Apenas Aluguel e Não Excluídos.
        # REMOVIDO filtro status='ATIVO' daqui para aplicar logicamente abaixo.
        qs = Contrato.objects.filter(
            imobiliaria=imobiliaria,
            tipo_contrato='ALUGUEL',
            excluido=False
        )

        # 3. Subqueries de verificação (Vistoria CONCLUÍDA)
        has_entrada = Vistoria.objects.filter(
            contrato=OuterRef('pk'), 
            tipo='ENTRADA', 
            concluida=True
        )
        
        has_saida = Vistoria.objects.filter(
            contrato=OuterRef('pk'), 
            tipo='SAIDA', 
            concluida=True
        )

        if tipo == 'ENTRADA':
            # CORREÇÃO PRINCIPAL: Permite RASCUNHO ou ATIVO
            qs = qs.filter(status_contrato__in=[Contrato.Status.RASCUNHO, Contrato.Status.ATIVO])
            qs = qs.annotate(ja_tem_entrada=Exists(has_entrada)).filter(ja_tem_entrada=False)
            
        elif tipo == 'SAIDA':
            # Para saída, geralmente o contrato já deve estar rodando (ATIVO)
            qs = qs.filter(status_contrato=Contrato.Status.ATIVO)
            qs = qs.annotate(ja_tem_saida=Exists(has_saida)).filter(ja_tem_saida=False)
        
        elif tipo == 'PERIODICA':
            # Para periódica, listamos todos os ativos de aluguel
            qs = qs.filter(status_contrato=Contrato.Status.ATIVO)
            
        else:
            return Response(
                {"error": "Tipo inválido. Use ENTRADA, SAIDA ou PERIODICA."}, 
                status=400
            )

        # Ordenação por ID (mais recente primeiro)
        qs = qs.order_by('-id')

        # Serialização padrão
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

class PagamentoViewSet(viewsets.ModelViewSet):
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria

        if imobiliaria:
            return Pagamento.objects.filter(
                contrato__imobiliaria=imobiliaria
            ).order_by('-data_vencimento')
        return Pagamento.objects.none()
    
    def perform_create(self, serializer):
        serializer.save()

class GerarReciboView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pagamento_id):
        user = request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria
            
        pagamento = get_object_or_404(Pagamento, pk=pagamento_id, contrato__imobiliaria=imobiliaria)
        
        if pagamento.status != 'PAGO':
            return HttpResponse("Este pagamento ainda não foi baixado.", status=400)
        context = {
            'pagamento': pagamento,
            'contrato': pagamento.contrato,
            'imobiliaria': pagamento.contrato.imobiliaria,
            'locatario': pagamento.contrato.inquilino,
            'locador': pagamento.contrato.proprietario,
            'imovel': pagamento.contrato.imovel,
            'data_pagamento': pagamento.data_pagamento or timezone.now(),
        }
        html_string = render_to_string('recibo_template.html', context)
        html_string = re.sub(r'<p style=\"text-align:\\s*center;\">', r'<p align=\"center\">', html_string, flags=re.IGNORECASE)
        html_string = re.sub(r'<p style=\"text-align:\\s*right;\">', r'<p align=\"right\">', html_string, flags=re.IGNORECASE)
        html_string = re.sub(r'<p style=\"text-align:\\s*left;\">', r'<p align=\"left\">', html_string, flags=re.IGNORECASE)
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gerar_contrato_pdf_editado(request, pk=None):
    try:
        view = ContratoViewSet.as_view({'get': 'generate_pdf_contrato'})
        response = view(request, pk=pk)
        if response.status_code == 200:
             response['Content-Disposition'] = f'filename="contrato_editado_{pk}.pdf"'
        return response
    except Contrato.DoesNotExist:
        return Response({"error": "Contrato não encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def limpar_estilos_view(request, pk):
    try:
        user = request.user
        imobiliaria = getattr(user, 'imobiliaria', None)
        if hasattr(user, 'perfil') and user.perfil:
            imobiliaria = user.perfil.imobiliaria
            
        contrato = get_object_or_404(Contrato, pk=pk, contrato__imobiliaria=imobiliaria)
        
        if not contrato.conteudo_personalizado:
            return Response({"message": "Contrato não possui conteúdo personalizado."}, status=status.HTTP_400_BAD_REQUEST)
        html_content = contrato.conteudo_personalizado
        html_content = re.sub(r'<p style=\"text-align:\\s*center;\">', r'<p align=\"center\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p style=\"text-align:\\s*right;\">', r'<p align=\"right\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p style=\"text-align:\\s*left;\">', r'<p align=\"left\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p style=\"text-align:\\s*justify;\">', r'<p align=\"justify\">', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<span style=\"\\s*\">\\s*</span>', '', html_content, flags=re.IGNORECASE)
        html_string_with_meta = f'<html><head><meta charset=\"UTF-8\"></head><body>{html_content}</body></html>'
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string_with_meta.encode("UTF-8")), result)
        if not pdf.err:
            contrato.conteudo_personalizado = html_content
            contrato.save()
            return Response({"success": "Estilos limpos e documento salvo."})
        else:
            return Response({"error": f"Erro ao validar PDF após limpeza: {pdf.err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Contrato.DoesNotExist:
        return Response({"error": "Contrato não encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
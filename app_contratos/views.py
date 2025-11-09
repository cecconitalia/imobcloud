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
# Imports para a query otimizada
from django.db.models import Exists, OuterRef
# Imports para a action 'gerar_financeiro'
from app_financeiro.models import Transacao, Categoria, Conta
from datetime import date
from dateutil.relativedelta import relativedelta
from rest_framework.views import APIView
from django.utils import timezone

# Imports do Reportlab (necessárias para GerarReciboView)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class ContratoViewSet(viewsets.ModelViewSet):
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.imobiliaria:
            
            # Subquery para verificar a existência de pagamentos
            pagamento_exists_subquery = Pagamento.objects.filter(
                contrato_id=OuterRef('pk')
            )
            
            return Contrato.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria).annotate(
                financeiro_gerado=Exists(pagamento_exists_subquery)
            ).select_related(
                'imovel', 'inquilino', 'proprietario'
            ).prefetch_related('fiadores', 'pagamentos')
        return Contrato.objects.none()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ContratoCriacaoSerializer
        return ContratoSerializer

    def perform_create(self, serializer):
        # Cria o contrato sempre como PENDENTE
        serializer.save(
            imobiliaria=self.request.user.perfil.imobiliaria,
            status_contrato=Contrato.Status.PENDENTE 
        )

    def perform_update(self, serializer):
        serializer.save(imobiliaria=self.request.user.perfil.imobiliaria)

    # ==================================================================
    # NOVA ACTION: Ativar Contrato (Chamada pelo novo botão)
    # ==================================================================
    @action(detail=True, methods=['post'], url_path='ativar')
    @transaction.atomic
    def ativar_contrato(self, request, pk=None):
        contrato = self.get_object()

        # 1. Verifica se já está ativo
        if contrato.status_contrato == Contrato.Status.ATIVO:
            return Response(
                {"error": "Este contrato já está ativo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Validação (só para aluguel): 
        # Garante que os dados mínimos para o signal existem
        if contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
            if not contrato.aluguel or not contrato.duracao_meses:
                 return Response(
                    {"error": "Não é possível ativar. Defina o 'Valor do Aluguel' e a 'Duração (meses)' primeiro."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 3. Ativa o contrato
        contrato.status_contrato = Contrato.Status.ATIVO
        contrato.save() # <-- ISSO VAI DISPARAR O SIGNAL 'pre_save'

        # O signal (app_contratos/signals.py) vai cuidar da geração
        # automática do financeiro neste momento.

        return Response(
            {"status": "Contrato ativado com sucesso. O financeiro foi gerado automaticamente."},
            status=status.HTTP_200_OK
        )
    # ==================================================================
    # Fim da nova Action
    # ==================================================================


    @action(detail=True, methods=['get'])
    def pagamentos(self, request, pk=None):
        contrato = self.get_object()
        pagamentos = contrato.pagamentos.all().order_by('data_vencimento')
        serializer = PagamentoSerializer(pagamentos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='gerar-financeiro')
    @transaction.atomic
    def gerar_financeiro(self, request, pk=None):
        """
        Action manual para (Re)Gerar o financeiro. 
        Usada pelo botão 'Regerar' no frontend.
        """
        contrato = self.get_object()
        imobiliaria = contrato.imobiliaria
        
        if contrato.tipo_contrato != Contrato.TipoContrato.ALUGUEL:
            return Response(
                {"error": "Geração financeira manual disponível apenas para contratos de Aluguel."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not contrato.aluguel or not contrato.duracao_meses:
             return Response(
                {"error": "Contrato precisa ter 'Valor do Aluguel' e 'Duração (meses)' definidos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Limpa Lançamentos PENDENTES antigos para evitar duplicidade
        Pagamento.objects.filter(contrato=contrato, status='PENDENTE').delete()
        Transacao.objects.filter(contrato=contrato, status='PENDENTE').delete()
        
        data_parcela = contrato.data_inicio
        
        try:
            categoria_aluguel = Categoria.objects.get(imobiliaria=imobiliaria, nome='Receita de Aluguel')
        except Categoria.DoesNotExist:
            categoria_aluguel = Categoria.objects.create(imobiliaria=imobiliaria, nome='Receita de Aluguel', tipo='RECEITA')
            
        try:
            conta_padrao = Conta.objects.filter(imobiliaria=imobiliaria).first()
        except Conta.DoesNotExist:
            conta_padrao = None

        duracao = contrato.duracao_meses
        parcelas_criadas = 0

        for i in range(duracao):
            Pagamento.objects.create(
                contrato=contrato,
                data_vencimento=data_parcela,
                valor=contrato.aluguel, 
                status='PENDENTE'
            )
            
            Transacao.objects.create(
                imobiliaria=imobiliaria,
                descricao=f'Aluguel {i+1}/{duracao} - Imóvel: {contrato.imovel.titulo_anuncio}',
                valor=contrato.aluguel,
                data_transacao=date.today(), 
                data_vencimento=data_parcela,
                tipo='RECEITA',
                status='PENDENTE',
                categoria=categoria_aluguel,
                conta=conta_padrao,
                cliente=contrato.inquilino,
                imovel=contrato.imovel,
                contrato=contrato
            )
            
            data_parcela += relativedelta(months=1)
            parcelas_criadas += 1

        return Response(
            {"status": f"{parcelas_criadas} parcelas financeiras foram geradas com sucesso."},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'], url_path='get-html')
    def get_html(self, request, pk=None):
        contrato = self.get_object()
        if contrato.conteudo_personalizado:
            return HttpResponse(contrato.conteudo_personalizado, content_type='text/html; charset=utf-8')

        template_name = 'contrato_aluguel_template.html' if contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL else 'contrato_venda_template.html'
        context = {
            'contrato': contrato,
            'imovel': contrato.imovel,
            'proprietario': contrato.proprietario,
            'inquilino': contrato.inquilino,
            'imobiliaria': contrato.imobiliaria,
            'data_hoje': timezone.now().date(),
        }
        html_string = render_to_string(template_name, context)
        return HttpResponse(html_string, content_type='text/html; charset=utf-8')

    @action(detail=True, methods=['post'], url_path='salvar-html-editado')
    def salvar_html_editado(self, request, pk=None):
        contrato = self.get_object()
        html_content = request.data.get('html_content')
        if not html_content:
            return Response({"error": "Conteúdo HTML é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        contrato.conteudo_personalizado = html_content
        contrato.save()
        return Response({"status": "Conteúdo do contrato salvo com sucesso."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='visualizar-pdf')
    def visualizar_pdf(self, request, pk=None):
        contrato = self.get_object()
        
        if contrato.conteudo_personalizado:
            html_content = contrato.conteudo_personalizado
        else:
            template_name = 'contrato_aluguel_template.html' if contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL else 'contrato_venda_template.html'
            context = {
                'contrato': contrato,
                'imovel': contrato.imovel,
                'proprietario': contrato.proprietario,
                'inquilino': contrato.inquilino,
                'imobiliaria': contrato.imobiliaria,
                'data_hoje': timezone.now().date(),
            }
            html_content = render_to_string(template_name, context)
        
        html_string_with_meta = f'<html><head><meta charset="UTF-8"></head><body>{html_content}</body></html>'
        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string_with_meta.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"contrato_{contrato.tipo_contrato.lower()}_{contrato.id}.pdf"
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        
        return HttpResponse("Erro ao gerar o PDF.", status=500)


class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.imobiliaria:
            return Pagamento.objects.filter(contrato__imobiliaria=self.request.user.perfil.imobiliaria).order_by('-data_vencimento')
        return Pagamento.objects.none()
    
    @action(detail=True, methods=['post'], url_path='marcar-pago')
    @transaction.atomic
    def marcar_como_pago(self, request, pk=None):
        pagamento = self.get_object()
        
        data_pagamento_str = request.data.get('data_pagamento')
        if data_pagamento_str:
            data_pagamento = parse_date(data_pagamento_str)
            if not data_pagamento:
                raise ValidationError({"data_pagamento": "Formato de data inválido. Use AAAA-MM-DD."})
        else:
            data_pagamento = timezone.now().date()

        if pagamento.status == 'PAGO':
            return Response({'status': 'Pagamento já estava baixado.'}, status=status.HTTP_400_BAD_REQUEST)

        pagamento.status = 'PAGO'
        pagamento.data_pagamento = data_pagamento
        pagamento.save()

        transacao_correspondente = Transacao.objects.filter(
            contrato=pagamento.contrato,
            valor=pagamento.valor,
            data_vencimento=pagamento.data_vencimento,
            status__in=['PENDENTE', 'ATRASADO']
        ).first()

        if transacao_correspondente:
            transacao_correspondente.status = 'PAGO'
            transacao_correspondente.data_transacao = data_pagamento
            transacao_correspondente.save()
            return Response({'status': 'Pagamento e transação atualizados com sucesso.'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Pagamento atualizado, mas transação correspondente não foi encontrada ou já estava paga.'}, status=status.HTTP_200_OK)


class GerarReciboView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pagamento_id):
        imobiliaria = request.user.perfil.imobiliaria
        pagamento = get_object_or_404(Pagamento, pk=pagamento_id, contrato__imobiliaria=imobiliaria)
        contrato = pagamento.contrato
        cliente = contrato.inquilino
        imovel = contrato.imovel

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        y_position = height - 50

        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2.0, y_position, "Recibo de Pagamento de Aluguel")
        y_position -= 50

        p.setFont("Helvetica", 12)
        p.drawString(70, y_position, f"Recebemos de: {cliente.nome_completo}")
        y_position -= 20
        p.drawString(70, y_position, f"CPF/CNPJ: {cliente.cpf_cnpj}")
        y_position -= 40
        p.drawString(70, y_position, f"A importância de R$ {pagamento.valor:.2f}")
        y_position -= 20
        p.drawString(70, y_position, f"Referente ao aluguel do imóvel situado em: {imovel.logradouro}")
        y_position -= 20
        p.drawString(70, y_position, f"Vencimento original: {pagamento.data_vencimento.strftime('%d/%m/%Y')}")
        y_position -= 20
        p.drawString(70, y_position, f"Data do Pagamento: {pagamento.data_pagamento.strftime('%d/%m/%Y') if pagamento.data_pagamento else 'N/A'}")
        y_position -= 60

        p.drawString(70, y_position, f"_________________________________________")
        y_position -= 15
        p.drawString(70, y_position, imobiliaria.nome)
        y_position -= 30
        
        p.setFont("Helvetica-Oblique", 10)
        p.drawCentredString(width / 2.0, y_position, "Este recibo é válido como comprovante de quitação da parcela mencionada.")

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="recibo_{pagamento.id}.pdf"'
        return response
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gerar_contrato_pdf_editado(request, contrato_id):
    contrato = get_object_or_404(Contrato, pk=contrato_id)
    if not request.user.is_superuser and contrato.imobiliaria != request.tenant:
        return HttpResponse("Acesso negado.", status=403)
    
    html_content = request.data.get('html_content')
    if not html_content:
        return HttpResponse("Conteúdo HTML é obrigatório.", status=400)
    
    html_string_with_meta = f'<html><head><meta charset="UTF-8"></head><body>{html_content}</body></html>'

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string_with_meta.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"contrato_{contrato.tipo_contrato.lower()}_{contrato.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return HttpResponse("Erro ao gerar o PDF.", status=500)
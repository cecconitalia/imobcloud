# C:\wamp64\www\imobcloud\app_contratos\views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Contrato, Pagamento
from .serializers import ContratoSerializer, PagamentoSerializer, ContratoCriacaoSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from django.conf import settings
import os

from django.utils.dateparse import parse_date
from django.db import transaction
from app_financeiro.models import Transacao
from rest_framework.views import APIView
from django.utils import timezone

class ContratoViewSet(viewsets.ModelViewSet):
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contrato.objects.filter(imovel__imobiliaria=self.request.tenant).select_related('imovel', 'inquilino', 'proprietario')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ContratoCriacaoSerializer
        return ContratoSerializer

    def perform_create(self, serializer):
        serializer.save(imobiliaria=self.request.tenant)

    @action(detail=True, methods=['get'])
    def pagamentos(self, request, pk=None):
        contrato = self.get_object()
        pagamentos = contrato.pagamentos.all().order_by('data_vencimento')
        serializer = PagamentoSerializer(pagamentos, many=True)
        return Response(serializer.data)

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pagamento.objects.filter(contrato__imobiliaria=self.request.tenant).order_by('-data_vencimento')
    
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
        pagamento = get_object_or_404(Pagamento, pk=pagamento_id, contrato__imobiliaria=request.tenant)
        contrato = pagamento.contrato
        cliente = contrato.inquilino
        imovel = contrato.imovel
        imobiliaria = request.tenant

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        y_position = height - 50
        if imobiliaria.logo:
            logo_path = os.path.join(settings.MEDIA_ROOT, imobiliaria.logo.name)
            if os.path.exists(logo_path):
                try:
                    logo = ImageReader(logo_path)
                    p.drawImage(logo, 50, y_position - 40, width=120, height=60, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    print(f"Erro ao ler o logo: {e}")

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
        # CORREÇÃO: Usa o campo 'endereco' do modelo Imovel
        p.drawString(70, y_position, f"Referente ao aluguel do imóvel situado em: {imovel.endereco}")
        y_position -= 20
        p.drawString(70, y_position, f"Vencimento original: {pagamento.data_vencimento.strftime('%d/%m/%Y')}")
        y_position -= 20
        p.drawString(70, y_position, f"Data do Pagamento: {pagamento.data_pagamento.strftime('%d/%m/%Y') if pagamento.data_pagamento else 'N/A'}")
        y_position -= 60

        p.drawString(70, y_position, f"_________________________________________")
        y_position -= 15
        p.drawString(70, y_position, imobiliaria.nome)
        y_position -= 15
        p.drawString(70, y_position, f"CNPJ: {imobiliaria.cnpj}")
        y_position -= 30
        
        p.setFont("Helvetica-Oblique", 10)
        p.drawCentredString(width / 2.0, y_position, "Este recibo é válido como comprovante de quitação da parcela mencionada.")

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="recibo_{pagamento.id}.pdf"'
        return response
# C:\wamp64\www\imobcloud\app_contratos\views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import date
from io import BytesIO
from xhtml2pdf import pisa
import locale
from num2words import num2words
from decimal import Decimal

from .models import Contrato, Pagamento
from .serializers import (
    ContratoSerializer, 
    ContratoCriacaoSerializer, 
    ContratoListSerializer, # <--- Importado
    PagamentoSerializer
)
from app_financeiro.models import Transacao, Categoria, Conta
from app_imoveis.models import Imovel

# ==================================================================
# CORREÇÃO: O arquivo 'app_contratos/services.py' está faltando
# no seu projeto, causando o 'ModuleNotFoundError'.
#
# Comentei o import e as funções que dependem dele para
# permitir que o servidor inicie.
# ==================================================================
# from .services import (
#     gerar_financeiro_contrato_aluguel, 
#     gerar_financeiro_contrato_venda,
#     remover_financeiro_contrato
# )
# ==================================================================

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    # ==================================================================
    # CORREÇÃO 1: Otimizar a queryset da lista com select_related
    # ==================================================================
    def get_queryset(self):
        user = self.request.user
        
        # Otimiza a consulta principal, especialmente para a 'list' view
        queryset = Contrato.objects.filter(
            imobiliaria=self.request.tenant
        ).select_related(
            'imovel', 
            'inquilino', 
            'proprietario'
        )

        # (O resto da sua lógica de filtro, se houver, pode vir aqui)
        
        return queryset

    # ==================================================================
    # CORREÇÃO 2: Usar o Serializer correto para a ação 'list'
    # ==================================================================
    def get_serializer_class(self):
        """
        Define qual serializer usar com base na ação (action).
        - 'list':       Usa o ContratoListSerializer (leve, para a lista)
        - 'create'/'update': Usa o ContratoCriacaoSerializer (para escrita)
        - 'retrieve':   Usa o ContratoSerializer (pesado, para detalhes)
        """
        if self.action == 'list':
            return ContratoListSerializer
            
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return ContratoCriacaoSerializer
            
        return ContratoSerializer # Padrão para 'retrieve' e outras ações

    def perform_create(self, serializer):
        # Associa automaticamente a imobiliária do usuário ao contrato
        contrato = serializer.save(imobiliaria=self.request.tenant)
        
        # ==================================================================
        # CORREÇÃO: Lógica financeira comentada
        # (depende do 'services.py' que está faltando)
        # ==================================================================
        # Se o contrato for salvo como ATIVO, gera o financeiro
        # if contrato.status_contrato == Contrato.Status.ATIVO:
        #     try:
        #         if contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        #             gerar_financeiro_contrato_aluguel(contrato)
        #         elif contrato.tipo_contrato == Contrato.TipoContrato.VENDA:
        #             gerar_financeiro_contrato_venda(contrato)
        #     except Exception as e:
        #         # Se a geração financeira falhar, não reverte a criação do contrato,
        #         # mas registra o erro. A geração pode ser manual depois.
        #         print(f"Erro ao gerar financeiro na criação do Contrato {contrato.id}: {e}")
        # ==================================================================


    def perform_update(self, serializer):
        # Busca o estado anterior do contrato ANTES de salvar
        contrato_anterior = self.get_object()
        status_anterior = contrato_anterior.status_contrato

        # Salva o contrato com os novos dados
        contrato_atualizado = serializer.save()
        status_novo = contrato_atualizado.status_contrato

        # ==================================================================
        # CORREÇÃO: Lógica financeira comentada
        # (depende do 'services.py' que está faltando)
        # ==================================================================
        
        # # Caso 1: O contrato está sendo ATIVADO (era PENDENTE, agora é ATIVO)
        # if status_anterior != Contrato.Status.ATIVO and status_novo == Contrato.Status.ATIVO:
        #     # Verifica se já existe financeiro (talvez de uma ativação anterior)
        #     financeiro_existente = Transacao.objects.filter(contrato=contrato_atualizado).exists()
            
        #     if not financeiro_existente:
        #         try:
        #             if contrato_atualizado.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        #                 gerar_financeiro_contrato_aluguel(contrato_atualizado)
        #             elif contrato_atualizado.tipo_contrato == Contrato.TipoContrato.VENDA:
        #                 gerar_financeiro_contrato_venda(contrato_atualizado)
        #         except Exception as e:
        #             print(f"Erro ao gerar financeiro na ATIVAÇÃO do Contrato {contrato_atualizado.id}: {e}")
        
        #     # Se for aluguel, atualiza o status do imóvel para ALUGADO
        #     if contrato_atualizado.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        #         contrato_atualizado.imovel.status = Imovel.Status.ALUGADO
        #         contrato_atualizado.imovel.save()
        #     # Se for venda, atualiza para VENDIDO
        #     elif contrato_atualizado.tipo_contrato == Contrato.TipoContrato.VENDA:
        #         contrato_atualizado.imovel.status = Imovel.Status.VENDIDO
        #         contrato_atualizado.imovel.save()

        # # Caso 2: O contrato está sendo INATIVADO (era ATIVO, agora é PENDENTE/RESCINDIDO/INATIVO)
        # elif status_anterior == Contrato.Status.ATIVO and status_novo != Contrato.Status.ATIVO:
        #     try:
        #         # Remove o financeiro (parcelas pendentes, etc.)
        #         remover_financeiro_contrato(contrato_atualizado)
        #     except Exception as e:
        #         print(f"Erro ao remover financeiro na DESATIVAÇÃO do Contrato {contrato_atualizado.id}: {e}")

        #     # Se o contrato foi inativado (e não concluído),
        #     # o imóvel volta a ficar disponível para o tipo original
        #     if status_novo != Contrato.Status.CONCLUIDO:
        #         if contrato_atualizado.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        #             contrato_atualizado.imovel.status = Imovel.Status.PARA_ALUGAR
        #             contrato_atualizado.imovel.save()
        #         elif contrato_atualizado.tipo_contrato == Contrato.TipoContrato.VENDA:
        #             contrato_atualizado.imovel.status = Imovel.Status.A_VENDA
        #             contrato_atualizado.imovel.save()
        
        # elif status_anterior == Contrato.Status.ATIVO and status_novo == Contrato.Status.ATIVO:
        #     pass
        # ==================================================================


    @action(detail=True, methods=['get'], url_path='gerar-recibo')
    def gerar_recibo(self, request, pk=None):
        contrato = self.get_object()
        pagamento_id = request.query_params.get('pagamento_id')

        if not pagamento_id:
            return Response({"error": "O ID do pagamento é necessário."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pagamento = Pagamento.objects.get(id=pagamento_id, contrato=contrato)
        except Pagamento.DoesNotExist:
            return Response({"error": "Pagamento não encontrado para este contrato."}, status=status.HTTP_404_NOT_FOUND)

        if pagamento.status != 'PAGO':
            return Response({"error": "Só é possível gerar recibo para pagamentos com status 'PAGO'."}, status=status.HTTP_400_BAD_REQUEST)

        # Configura o locale para Português do Brasil
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
            try:
                 locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
            except locale.Error:
                 pass # Usa o padrão do sistema se pt_BR falhar

        today = date.today()
        
        try:
            valor_por_extenso = num2words(pagamento.valor, lang='pt_BR')
        except Exception:
            valor_por_extenso = "Valor não pôde ser escrito"

        context = {
            'imobiliaria': contrato.imobiliaria,
            'contrato': contrato,
            'pagamento': pagamento,
            'inquilino': contrato.inquilino,
            'proprietario': contrato.proprietario,
            'imovel': contrato.imovel,
            'valor_por_extenso': valor_por_extenso.capitalize(),
            'data_hoje': today.strftime("%d de %B de %Y"),
        }

        html_string = render_to_string('recibo_template.html', context)
        result = BytesIO()
        
        try:
            pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                filename = f"recibo_contrato_{contrato.id}_pagamento_{pagamento.id}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)
        except Exception as e:
            return HttpResponse(f"Erro inesperado ao gerar PDF: {e}", status=500)

    @action(detail=True, methods=['get'], url_path='gerar-documento')
    def gerar_documento_contrato(self, request, pk=None):
        contrato = self.get_object()

        # Configura o locale para Português do Brasil
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
             try:
                 locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
             except locale.Error:
                 pass # Usa o padrão do sistema se pt_BR falhar

        data_assinatura = contrato.data_assinatura or date.today()

        # Dados comuns
        context = {
            'imobiliaria': contrato.imobiliaria,
            'contrato': contrato,
            'imovel': contrato.imovel,
            'proprietario': contrato.proprietario,
            'inquilino': contrato.inquilino, # (Será o Comprador se for Venda)
            'fiadores': contrato.fiadores.all(),
            'data_extenso': data_assinatura.strftime("%d de %B de %Y"),
            # 'css_styles': settings.STATIC_ROOT + '/css/contrato_pdf.css' # (Se você tiver um)
        }
        
        template_name = None

        # Dados específicos
        if contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
            template_name = 'contrato_aluguel_template.html'
            try:
                valor_extenso = num2words(contrato.aluguel, lang='pt_BR')
                context['valor_aluguel_extenso'] = valor_extenso.capitalize()
            except Exception:
                context['valor_aluguel_extenso'] = "Valor não pôde ser escrito"
        
        elif contrato.tipo_contrato == Contrato.TipoContrato.VENDA:
            template_name = 'contrato_venda_template.html'
            try:
                valor_extenso = num2words(contrato.valor_total, lang='pt_BR')
                context['valor_total_extenso'] = valor_extenso.capitalize()
            except Exception:
                context['valor_total_extenso'] = "Valor não pôde ser escrito"

        else:
            return Response({"error": "Tipo de contrato não suportado para geração de PDF."}, status=status.HTTP_400_BAD_REQUEST)

        # Se houver conteúdo personalizado, usa-o
        if contrato.conteudo_personalizado:
             html_string = contrato.conteudo_personalizado
        else:
             html_string = render_to_string(template_name, context)
        
        result = BytesIO()
        
        try:
            pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                filename = f"contrato_{contrato.tipo_contrato.lower()}_{contrato.id}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)
        except Exception as e:
            return HttpResponse(f"Erro inesperado ao gerar PDF: {e}", status=500)


class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra pagamentos pela imobiliária do usuário
        return Pagamento.objects.filter(contrato__imobiliaria=self.request.tenant)

    @action(detail=True, methods=['post'], url_path='registrar-pagamento')
    def registrar_pagamento(self, request, pk=None):
        pagamento = self.get_object()
        
        if pagamento.status == 'PAGO':
            return Response({"message": "Este pagamento já foi registrado."}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Adicionar lógica de qual conta/forma de pagamento
        
        pagamento.status = 'PAGO'
        pagamento.data_pagamento = timezone.now().date()
        pagamento.save()
        
        # TODO: Lançar esta baixa no financeiro (Transação)
        
        return Response(PagamentoSerializer(pagamento).data, status=status.HTTP_200_OK)
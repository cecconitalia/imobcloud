# C:\wamp64\www\ImobCloud\app_boletos\views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from .serializers import ConfiguracaoBancoSerializer, BoletoSerializer
from .models import ConfiguracaoBanco, Boleto, ArquivoRemessa, ArquivoRetorno
from app_financeiro.models import Transacao
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

# A lógica de geração e processamento de arquivos CNAB é complexa.
# Aqui, vamos simular a funcionalidade. Em um projeto real, você usaria uma biblioteca como 'pycnab'.

def simular_geracao_cnab(imobiliaria, config_banco, boletos):
    """ Função placeholder para simular a criação de um arquivo de remessa. """
    conteudo = f"REMESSA CNAB240 - {config_banco.nome_banco}\n"
    conteudo += f"IMOBILIARIA: {imobiliaria.nome}\n"
    for boleto in boletos:
        transacao = boleto.transacao
        # Acessa o nome do cliente a partir da transação, que tem uma propriedade para isso
        conteudo += f"REGISTRO: {transacao.cliente_nome};{transacao.valor};{boleto.nosso_numero}\n"
    return conteudo.encode('utf-8')

def simular_processamento_retorno(arquivo_conteudo):
    """ Função placeholder para simular o processamento de um retorno. """
    log = "Iniciando processamento...\n"
    # Lógica para ler o arquivo e identificar pagamentos
    # Exemplo: nosso_numero;valor_pago;data_pagamento
    # "12345;150.00;2025-08-23"
    pagamentos_identificados = [
        {'nosso_numero': '12345', 'valor_pago': 150.00, 'data_pagamento': '2025-08-23'},
    ]
    log += f"{len(pagamentos_identificados)} pagamentos identificados no arquivo.\n"
    return log, pagamentos_identificados


class ConfiguracaoBancoViewSet(viewsets.ModelViewSet):
    """ ViewSet para gerir as configurações de banco (CRUD). """
    queryset = ConfiguracaoBanco.objects.all()
    serializer_class = ConfiguracaoBancoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConfiguracaoBanco.objects.filter(imobiliaria=self.request.tenant)

    # CORREÇÃO: Adicionando o método perform_create para associar a imobiliária
    def perform_create(self, serializer):
        """ Associa a imobiliária do usuário logado (tenant) ao criar uma nova configuração. """
        if not self.request.tenant:
            raise PermissionDenied("Não foi possível associar a configuração a uma imobiliária.")
        serializer.save(imobiliaria=self.request.tenant)


class BoletoViewSet(viewsets.ViewSet):
    """ ViewSet para gerenciar o ciclo de vida dos boletos via remessa/retorno. """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='pendentes-remessa')
    def pendentes_remessa(self, request):
        """ Lista todas as transações de receita pendentes que ainda não têm boleto. """
        transacoes = Transacao.objects.filter(
            imobiliaria=request.tenant,
            tipo='RECEITA',
            status__in=['PENDENTE', 'ATRASADO'],
            boleto__isnull=True
        )
        # Para simplificar, não estamos usando um serializer aqui
        data = [{
            'id': t.id,
            'descricao': t.descricao,
            'valor': t.valor,
            'vencimento': t.data_vencimento,
            'cliente_nome': t.cliente_nome 
        } for t in transacoes]
        return Response(data)

    @action(detail=False, methods=['post'], url_path='gerar-remessa')
    @transaction.atomic
    def gerar_remessa(self, request):
        """ Gera um arquivo de remessa para as transações selecionadas. """
        transacao_ids = request.data.get('transacao_ids', [])
        config_banco_id = request.data.get('config_banco_id')

        if not transacao_ids or not config_banco_id:
            raise ValidationError("IDs das transações e da configuração do banco são obrigatórios.")

        config_banco = get_object_or_404(ConfiguracaoBanco, pk=config_banco_id, imobiliaria=request.tenant)
        transacoes = Transacao.objects.filter(pk__in=transacao_ids, imobiliaria=request.tenant, boleto__isnull=True)

        if not transacoes.exists():
            raise ValidationError("Nenhuma transação válida encontrada para gerar a remessa.")

        # Criar os objetos Boleto
        boletos_criados = []
        for i, transacao in enumerate(transacoes):
            # Lógica simples para "Nosso Número" - em produção, seria mais complexa
            nosso_numero = f"{timezone.now().strftime('%Y%m%d')}{transacao.id}{i}"
            boleto = Boleto.objects.create(
                transacao=transacao,
                nosso_numero=nosso_numero,
                status='ENVIADO'
            )
            boletos_criados.append(boleto)

        # Simular a geração do arquivo CNAB
        conteudo_arquivo = simular_geracao_cnab(request.tenant, config_banco, boletos_criados)
        # Salvar o arquivo de remessa (aqui seria salvo no storage)
        # remessa = ArquivoRemessa.objects.create(...)
        # for boleto in boletos_criados: boleto.remessa = remessa; boleto.save()

        # Retornamos o conteúdo do arquivo para download
        from django.http import HttpResponse
        response = HttpResponse(conteudo_arquivo, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="REMESSA_{timezone.now().strftime("%Y%m%d%H%M")}.txt"'
        return response

    @action(detail=False, methods=['post'], url_path='processar-retorno')
    @transaction.atomic
    def processar_retorno(self, request):
        """ Processa um arquivo de retorno enviado pelo usuário. """
        arquivo = request.FILES.get('arquivo_retorno')
        if not arquivo:
            raise ValidationError("Arquivo de retorno não enviado.")

        # Simular o processamento do arquivo
        log, pagamentos = simular_processamento_retorno(arquivo.read())

        # Dar baixa nos boletos
        for pag in pagamentos:
            Boleto.objects.filter(nosso_numero=pag['nosso_numero']).update(
                status='PAGO',
                data_pagamento=pag['data_pagamento'],
                valor_pago=pag['valor_pago']
            )
        
        return Response({
            "mensagem": "Arquivo de retorno processado com sucesso!",
            "log": log
        })
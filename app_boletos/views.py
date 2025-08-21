# C:\wamp64\www\ImobCloud\app_boletos\views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
from .serializers import GerarBoletoRequestSerializer, BoletoSerializer
from .models import Boleto, ConfiguracaoBanco
from .bradesco_api import BradescoAPI
from app_financeiro.models import Transacao

class GerarBoletoView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # 1. Valida os dados da requisição
        serializer = GerarBoletoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transacao_id = serializer.validated_data['transacao_id']
        banco_id = serializer.validated_data['banco_id']

        try:
            # 2. Busca a Transação e a Configuração do Banco
            transacao = get_object_or_404(
                Transacao.objects.select_related('imobiliaria'),
                pk=transacao_id
            )
            config_banco = get_object_or_404(
                ConfiguracaoBanco,
                pk=banco_id,
                imobiliaria=request.tenant
            )

            # Verifica se a transação já tem um boleto
            if Boleto.objects.filter(transacao=transacao).exists():
                raise ValidationError("Um boleto já foi gerado para esta transação.")

            # 3. Lógica específica para o Bradesco (exemplo)
            if config_banco.nome_banco == 'Bradesco':
                bradesco_api = BradescoAPI(imobiliaria=request.tenant)
                
                # Prepara o payload para a API do Bradesco
                dados_payload_boleto = {
                    'valor': str(transacao.valor),
                    'data_vencimento': str(transacao.data_vencimento),
                    # Adicione outros dados do boleto necessários para a API
                }
                
                # 4. Chama a API do Bradesco
                response_bradesco = bradesco_api.gerar_boleto(dados_payload_boleto)
                
                # 5. Salva o Boleto no banco de dados
                novo_boleto = Boleto.objects.create(
                    imobiliaria=request.tenant,
                    transacao=transacao,
                    configuracao=config_banco,
                    codigo_barras=response_bradesco['codigo_barras'],
                    linha_digitavel=response_bradesco['linha_digitavel'],
                    url_boleto=response_bradesco['url_pdf'],
                    data_vencimento=transacao.data_vencimento,
                    status='EMITIDO'
                )
                
                return Response({
                    "status": "sucesso",
                    "mensagem": "Boleto gerado com sucesso!",
                    "boleto": BoletoSerializer(novo_boleto).data
                }, status=status.HTTP_201_CREATED)

            else:
                raise ValidationError("Banco não suportado ou lógica não implementada.")

        except Exception as e:
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import OpcaoVozDaMarca
from .serializers import OpcaoVozDaMarcaSerializer
from core.models import Imobiliaria

class ListarVozesDaMarcaView(APIView):
    """
    Endpoint da API para listar todas as opções de Voz da Marca
    disponíveis no sistema.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        opcoes = OpcaoVozDaMarca.objects.all()
        serializer = OpcaoVozDaMarcaSerializer(opcoes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConfiguracaoImobiliariaView(APIView):
    """
    Endpoint para obter e atualizar a Voz da Marca preferida
    da imobiliária logada (tenant).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """ Retorna a configuração atual da imobiliária. """
        imobiliaria = request.tenant
        voz_id = imobiliaria.voz_da_marca_preferida.id if imobiliaria.voz_da_marca_preferida else None
        return Response({'voz_da_marca_preferida_id': voz_id}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """ Atualiza a Voz da Marca da imobiliária. """
        voz_id = request.data.get('voz_da_marca_id')

        if voz_id is None:
            return Response(
                {"error": "O campo 'voz_da_marca_id' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        imobiliaria = request.tenant
        
        try:
            # Se voz_id for uma string vazia ou 0, desvincula a voz
            # Convertendo para int de forma segura para evitar erros de ValueError
            if not voz_id or str(voz_id).strip() == '0':
                 imobiliaria.voz_da_marca_preferida = None
            else:
                opcao_voz = OpcaoVozDaMarca.objects.get(pk=voz_id)
                imobiliaria.voz_da_marca_preferida = opcao_voz
            
            imobiliaria.save()
            return Response(
                {"success": "Configuração salva com sucesso!"},
                status=status.HTTP_200_OK
            )
        except OpcaoVozDaMarca.DoesNotExist:
            return Response(
                {"error": "A opção de voz selecionada não existe."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
             return Response(
                {"error": "O ID da voz fornecido é inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                 {"error": f"Ocorreu um erro inesperado: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# app_boletos/management/commands/test_bradesco_token.py

from django.core.management.base import BaseCommand, CommandError
from core.models import Imobiliaria
from app_boletos.bradesco_api import BradescoAPI
import traceback

class Command(BaseCommand):
    help = 'Testa a obtenção do token de acesso da API do Bradesco para uma imobiliária específica.'

    def add_arguments(self, parser):
        parser.add_argument('imobiliaria_id', type=int, help='O ID da imobiliária para a qual testar a API.')

    def handle(self, *args, **options):
        imobiliaria_id = options['imobiliaria_id']
        self.stdout.write(f"Iniciando teste para a Imobiliária ID: {imobiliaria_id}")

        try:
            imobiliaria = Imobiliaria.objects.get(pk=imobiliaria_id)
            self.stdout.write(self.style.SUCCESS(f"Imobiliária '{imobiliaria.nome}' encontrada."))
        except Imobiliaria.DoesNotExist:
            raise CommandError(f"Imobiliária com ID '{imobiliaria_id}' não encontrada.")

        try:
            self.stdout.write("Inicializando a classe BradescoAPI...")
            api = BradescoAPI(imobiliaria=imobiliaria)
            self.stdout.write(self.style.SUCCESS("BradescoAPI inicializada com sucesso."))
            self.stdout.write(f"  -> Caminho do Certificado: {api.cert_path}")
            self.stdout.write(f"  -> Caminho da Chave Privada: {api.key_path}")

            self.stdout.write("\nTentando obter o token de acesso...")
            access_token = api._get_access_token()

            if access_token:
                self.stdout.write(self.style.SUCCESS("\n=============================================="))
                self.stdout.write(self.style.SUCCESS("TOKEN DE ACESSO OBTIDO COM SUCESSO!"))
                self.stdout.write(self.style.SUCCESS(f"Token: {access_token[:15]}..."))
                self.stdout.write(self.style.SUCCESS("=============================================="))
                self.stdout.write("A lógica do backend para autenticação está funcionando corretamente.")
            else:
                self.stderr.write(self.style.ERROR("\nFalha ao obter o token de acesso. A resposta não continha um token."))

        except Exception as e:
            self.stderr.write(self.style.ERROR("\n=============================================="))
            self.stderr.write(self.style.ERROR("Ocorreu um erro durante o teste:"))
            self.stderr.write(self.style.ERROR("=============================================="))
            # Imprime o traceback completo do erro
            traceback.print_exc()
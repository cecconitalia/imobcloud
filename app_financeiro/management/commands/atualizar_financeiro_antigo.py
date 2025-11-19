from django.core.management.base import BaseCommand
from core.models import Imobiliaria
from app_financeiro.signals import criar_financeiro_padrao
import logging

class Command(BaseCommand):
    help = 'Gera dados financeiros padrão (Contas, Categorias) para imobiliárias antigas.'

    def handle(self, *args, **options):
        # Busca todas as imobiliárias
        imobiliarias = Imobiliaria.objects.all()
        total = imobiliarias.count()
        
        self.stdout.write(self.style.WARNING(f'--- INICIANDO ATUALIZAÇÃO DE {total} CLIENTES ---'))

        sucessos = 0
        erros = 0

        for i, imob in enumerate(imobiliarias, 1):
            try:
                self.stdout.write(f'[{i}/{total}] Processando: {imob.nome}...')
                
                # Chama a mesma função do Signal, forçando created=True
                # Isso reaproveita sua lógica centralizada no signals.py
                criar_financeiro_padrao(sender=Imobiliaria, instance=imob, created=True)
                
                sucessos += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ERRO em {imob.nome}: {e}'))
                erros += 1

        self.stdout.write(self.style.SUCCESS(f'\n--- CONCLUÍDO ---'))
        self.stdout.write(f'Sucessos: {sucessos}')
        self.stdout.write(f'Erros: {erros}')
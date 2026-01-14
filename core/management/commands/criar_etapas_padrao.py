from django.core.management.base import BaseCommand
from core.models import Imobiliaria
from app_clientes.models import FunilEtapa

class Command(BaseCommand):
    help = 'Cria etapas de funil padrão para todas as imobiliárias que não possuem'

    def handle(self, *args, **kwargs):
        etapas_padrao = [
            {'titulo': 'Novo Lead', 'ordem': 1, 'prob': 10},
            {'titulo': 'Primeiro Contato', 'ordem': 2, 'prob': 25},
            {'titulo': 'Visita Agendada', 'ordem': 3, 'prob': 50},
            {'titulo': 'Proposta Enviada', 'ordem': 4, 'prob': 75},
            {'titulo': 'Em Negociação', 'ordem': 5, 'prob': 90},
            {'titulo': 'Ganho', 'ordem': 6, 'prob': 100},
            {'titulo': 'Perdido', 'ordem': 7, 'prob': 0},
        ]

        imobiliarias = Imobiliaria.objects.all()
        
        count_total = 0
        for imob in imobiliarias:
            if not FunilEtapa.objects.filter(imobiliaria=imob).exists():
                self.stdout.write(f"Criando etapas para: {imob.nome}...")
                for etapa in etapas_padrao:
                    FunilEtapa.objects.create(
                        imobiliaria=imob,
                        titulo=etapa['titulo'],
                        ordem=etapa['ordem'],
                        probabilidade_fechamento=etapa['prob']
                    )
                count_total += 1
        
        self.stdout.write(self.style.SUCCESS(f'Concluído! Etapas criadas para {count_total} imobiliárias.'))
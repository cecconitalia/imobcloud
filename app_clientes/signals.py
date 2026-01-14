from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Imobiliaria
from app_clientes.models import FunilEtapa

@receiver(post_save, sender=Imobiliaria)
def criar_etapas_padrao_imobiliaria(sender, instance, created, **kwargs):
    """
    Cria as etapas de funil padrão automaticamente quando uma 
    nova Imobiliária é cadastrada no sistema.
    """
    if created:
        etapas_padrao = [
            {'titulo': 'Lead', 'ordem': 1, 'prob': 10},
            {'titulo': 'Contato', 'ordem': 2, 'prob': 25},
            {'titulo': 'Visita', 'ordem': 3, 'prob': 50},
            {'titulo': 'Proposta', 'ordem': 4, 'prob': 75},
            {'titulo': 'Negociação', 'ordem': 5, 'prob': 90},
            {'titulo': 'Ganho', 'ordem': 6, 'prob': 100},
            {'titulo': 'Perdido', 'ordem': 7, 'prob': 0},
        ]

        for etapa in etapas_padrao:
            FunilEtapa.objects.create(
                imobiliaria=instance,
                titulo=etapa['titulo'],
                ordem=etapa['ordem'],
                probabilidade_fechamento=etapa['prob'],
                ativa=True
            )
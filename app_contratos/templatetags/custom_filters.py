# app_contratos/templatetags/custom_filters.py

from django import template
from django.utils.safestring import mark_safe
from num2words import num2words
from unidecode import unidecode # Adicionada a importação de 'unidecode'

register = template.Library()

@register.filter(name='num2words')
def num_to_words(value, lang="pt_BR"):
    """Converte um número em texto por extenso, como "mil e duzentos".
       A capitalização é tratada separadamente para flexibilidade.
    """
    try:
        if value is None:
            return ""
        # Converte o valor para palavras, depois para ASCII com unidecode
        # para evitar problemas de codificação
        text_value = num2words(value, lang=lang)
        return unidecode(text_value)
    except Exception as e:
        return f"Erro: {e}"

@register.filter(name='capfirst')
def capfirst_filter(value):
    """Capitaliza a primeira letra de uma string."""
    if value:
        # Garante que a primeira letra seja maiúscula, mesmo após a normalização
        return value[0].upper() + value[1:]
    return ""
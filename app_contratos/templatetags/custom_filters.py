# app_contratos/templatetags/custom_filters.py

from django import template
from django.utils.safestring import mark_safe
from num2words import num2words
from unidecode import unidecode
from django.utils.formats import number_format # Importação necessária para formatação BRL

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
        # CORREÇÃO: Usar mark_safe para indicar que o output é seguro para renderização HTML
        return mark_safe(unidecode(text_value))
    except Exception as e:
        return f"Erro: {e}"

@register.filter(name='capfirst')
def capfirst_filter(value):
    """Capitaliza a primeira letra de uma string."""
    if value:
        # Garante que a primeira letra seja maiúscula, mesmo após a normalização
        return value[0].upper() + value[1:]
    return ""

@register.filter(name='format_currency_brl')
def format_currency_brl(value):
    """
    Formata um valor numérico para o padrão BRL (ex: 890000 -> 890.000,00).
    Usa o sistema de localização do Django para garantir os separadores corretos.
    """
    try:
        if value is None:
            value = 0
        
        # number_format força a localização (L10N) do Django.
        # Garante USE_THOUSAND_SEPARATOR = True e DECIMAL_SEPARATOR = ','
        # (Conforme definido em settings.py para pt-BR)
        return number_format(value, decimal_pos=2, force_grouping=True)
    
    except (ValueError, TypeError):
        return "Valor inválido"

@register.filter(name='get_tipo_negocio')
def get_tipo_negocio(status_imovel):
    """
    Converte o status do imóvel (ex: 'A_VENDA') no tipo de negócio
    correto para o contrato (ex: 'Venda').
    """
    if status_imovel in ['A_VENDA', 'VENDIDO']:
        return "Venda"
    if status_imovel in ['PARA_ALUGAR', 'ALUGADO']:
        return "Locação" # "Locação" é mais formal para contratos
    
    # Fallback para outros status (ex: Em Construção)
    return "Negociação"
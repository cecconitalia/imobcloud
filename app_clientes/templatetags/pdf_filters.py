import os
from django import template
from django.conf import settings

register = template.Library()

@register.filter
def absolute_path(image_field):
    """
    Retorna o caminho absoluto do sistema de arquivos para uma imagem.
    Essencial para geração de PDF (xhtml2pdf/WeasyPrint) onde URLs relativas falham.
    """
    if not image_field:
        return ""
    
    try:
        # Se estiver usando armazenamento local (Docker/Disco), usa o path físico
        # Isso é muito mais rápido e confiável para o gerador de PDF
        if hasattr(image_field, 'path'):
            return image_field.path
            
        # Se for S3 ou outro storage remoto que não tem path local, usa a URL completa
        # O gerador de PDF fará o download da imagem
        if hasattr(image_field, 'url'):
            url = image_field.url
            if url.startswith('http'):
                return url
            # Se a URL for relativa mas não tem path (caso raro), tenta montar URL completa
            return f"{settings.SITE_URL}{url}"
            
    except Exception:
        # Fallback de segurança
        if hasattr(image_field, 'url'):
            return image_field.url
            
    return ""
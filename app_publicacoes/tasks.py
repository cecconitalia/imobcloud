# C:\wamp64\www\imobcloud\app_publicacoes\tasks.py

import requests
import os
from ImobCloud.celery import app
from django.conf import settings
from .models import PostAgendado, PublicacaoHistorico, PublicacaoSocial
from app_imoveis.models import Imovel, ImagemImovel
from django.utils import timezone
from core.models import Notificacao
import logging
from PIL import Image  # Necessário para processar a imagem

logger = logging.getLogger(__name__)

def get_base_url():
    """Recupera a URL base do site definida nas configurações."""
    base_url = getattr(settings, 'SITE_URL', 'http://localhost:8001')
    if not settings.DEBUG and not base_url.startswith('https://'):
        base_url = base_url.replace('http://', 'https://')
    return base_url

def preparar_imagem_quadrada(imagem_model):
    """
    Pega uma ImagemImovel, converte para quadrado (com fundo branco) 
    salva numa pasta temporária e retorna a URL pública dessa nova imagem.
    """
    try:
        # Caminho físico do arquivo original
        caminho_original = imagem_model.imagem.path
        
        # Abre a imagem
        img = Image.open(caminho_original)
        
        # Define o tamanho do quadrado (usa o maior lado da imagem)
        max_dim = max(img.size)
        tamanho_quadrado = (max_dim, max_dim)
        
        # Cria uma nova imagem branca quadrada
        nova_imagem = Image.new("RGB", tamanho_quadrado, (255, 255, 255))
        
        # Calcula a posição para centralizar a imagem original
        posicao_x = (max_dim - img.width) // 2
        posicao_y = (max_dim - img.height) // 2
        
        # Cola a imagem original no centro
        nova_imagem.paste(img, (posicao_x, posicao_y))
        
        # Define caminho para salvar (pasta media/temp_insta)
        pasta_temp = os.path.join(settings.MEDIA_ROOT, 'temp_insta')
        if not os.path.exists(pasta_temp):
            os.makedirs(pasta_temp)
            
        nome_arquivo = f"ig_sq_{imagem_model.id}.jpg"
        caminho_destino = os.path.join(pasta_temp, nome_arquivo)
        
        # Salva a nova imagem com alta qualidade
        nova_imagem.save(caminho_destino, quality=95)
        
        # Retorna a URL completa para esta nova imagem
        base_url = get_base_url()
        # Assume que MEDIA_URL é /media/
        url_relativa = f"{settings.MEDIA_URL}temp_insta/{nome_arquivo}"
        
        # Limpa barras duplas se houver
        full_url = f"{base_url}{url_relativa}".replace('//media', '/media')
        
        return full_url

    except Exception as e:
        logger.error(f"Erro ao processar imagem {imagem_model.id}: {e}")
        # Se der erro na conversão, tenta enviar a original mesmo
        return f"{get_base_url()}{imagem_model.imagem.url}"

def publicar_instagram_api(imovel, texto, imagens_ids=None):
    imobiliaria = imovel.imobiliaria
    ig_user_id = imobiliaria.instagram_business_account_id
    access_token = imobiliaria.facebook_page_access_token 

    if not ig_user_id or not access_token:
        raise Exception("Credenciais do Instagram não configuradas (ID ou Token).")

    # Seleciona imagens
    if imagens_ids:
        imagens = ImagemImovel.objects.filter(id__in=imagens_ids, imovel=imovel).order_by('ordem')
    else:
        imagens = ImagemImovel.objects.filter(imovel=imovel).order_by('ordem')[:1] 
    
    if not imagens.exists():
        raise Exception("Imóvel não possui imagem para publicação.")

    media_ids = []

    # Passo 1: Upload dos Containers de Mídia
    for img in imagens:
        # AQUI ESTÁ A MÁGICA: Processamos a imagem para ser quadrada antes do upload
        image_url = preparar_imagem_quadrada(img)
        
        url_media = f'https://graph.facebook.com/v18.0/{ig_user_id}/media'
        params_media = { 
            'image_url': image_url, 
            'access_token': access_token,
        }
        
        if imagens.count() > 1:
            params_media['is_carousel_item'] = 'true'
        else:
            params_media['caption'] = texto

        response_media = requests.post(url_media, params=params_media)
        media_data = response_media.json()

        if 'error' in media_data:
             raise Exception(f"Erro no upload da imagem {img.id}: {media_data['error']['message']}")
        
        creation_id = media_data.get('id')
        if creation_id:
            media_ids.append(creation_id)

    if not media_ids:
        raise Exception("Nenhuma mídia foi carregada com sucesso.")

    final_creation_id = None

    # Passo 2: Se for Carrossel, criar o container do Carrossel
    if len(media_ids) > 1:
        url_carousel = f'https://graph.facebook.com/v18.0/{ig_user_id}/media'
        params_carousel = {
            'media_type': 'CAROUSEL',
            'children': ','.join(media_ids),
            'caption': texto,
            'access_token': access_token
        }
        response_carousel = requests.post(url_carousel, params=params_carousel)
        carousel_data = response_carousel.json()
        
        if 'error' in carousel_data:
            raise Exception(f"Erro ao criar container carrossel: {carousel_data['error']['message']}")
            
        final_creation_id = carousel_data.get('id')
    else:
        final_creation_id = media_ids[0]

    # Passo 3: Publicar
    url_publish = f'https://graph.facebook.com/v18.0/{ig_user_id}/media_publish'
    params_publish = { 'creation_id': final_creation_id, 'access_token': access_token }
    response_publish = requests.post(url_publish, params=params_publish)
    publish_data = response_publish.json()

    if 'error' in publish_data:
        raise Exception(publish_data['error']['message'])

    return publish_data

@app.task(bind=True)
def publicar_post_agendado(self, post_agendado_id):
    """
    Tarefa Celery que publica APENAS no Instagram e envia notificação em caso de erro.
    """
    try:
        post = PostAgendado.objects.get(pk=post_agendado_id)
    except PostAgendado.DoesNotExist:
        return f"Post agendado com ID {post_agendado_id} não encontrado."

    imovel = post.imovel
    resultados = {}
    sucesso_geral = False 

    if post.status != 'PROCESSANDO':
        post.status = 'PROCESSANDO'
        post.save() 
    
    imagens_ids = post.imagens_ids if hasattr(post, 'imagens_ids') else []

    try:
        publish_data = publicar_instagram_api(imovel, post.texto, imagens_ids)
        resultados['instagram'] = 'Publicado com sucesso'
        sucesso_geral = True
        
        PublicacaoHistorico.objects.create(
            imovel=imovel, 
            rede_social='Instagram',
            link_publicacao=publish_data.get('id') if publish_data else None
        )
        
        if post.agendado_por:
            PublicacaoSocial.objects.create(
                imovel=imovel, 
                texto_gerado=post.texto, 
                plataforma='instagram', 
                sucesso=True, 
                publicado_por=post.agendado_por
            )
            
    except Exception as e:
        sucesso_geral = False
        erro_msg = f'Erro: {str(e)}'
        resultados['instagram'] = erro_msg
        
        # Tenta notificar, mas envolve num try para não quebrar se o model estiver desatualizado
        if post.agendado_por and hasattr(post.agendado_por, 'user'):
            try:
                Notificacao.objects.create(
                    destinatario=post.agendado_por.user, 
                    mensagem=f'❌ Falha Instagram {imovel.codigo_referencia}: {erro_msg[:100]}...',
                    tipo='ERRO_CRITICO',
                    link=f'/publicacoes' 
                )
            except Exception as notify_e:
                logger.error(f"Falha ao criar notificação: {notify_e}")
        
        if post.agendado_por:
            PublicacaoSocial.objects.create(
                imovel=imovel, 
                texto_gerado=post.texto, 
                plataforma='instagram', 
                sucesso=False, 
                publicado_por=post.agendado_por
            )
    
    post.status = 'PUBLICADO' if sucesso_geral else 'ERRO'
    post.resultado_publicacao = resultados
    post.data_publicacao_real = timezone.now()
    post.save()

    return resultados

@app.task(bind=True)
def verificar_publicacoes_agendadas(self):
    agora = timezone.now()
    posts_para_publicar = PostAgendado.objects.filter(
        status='AGENDADO',
        data_agendamento__lte=agora
    )

    count = 0
    for post in posts_para_publicar:
        post.status = 'PROCESSANDO'
        post.save()
        publicar_post_agendado.delay(post.id)
        count += 1

    return f"{count} posts enviados para processamento."
from celery import shared_task
from django.utils import timezone
from .models import PostAgendado
from .views import PublicacaoRedeSocialView # Reutilizamos a lógica de publicação!
from django.test import RequestFactory
from django.contrib.auth import get_user_model

@shared_task
def publicar_posts_agendados():
    agora = timezone.now()
    # Busca todos os posts que estão agendados para agora ou para o passado e que ainda não foram publicados
    posts_para_publicar = PostAgendado.objects.filter(
        data_agendamento__lte=agora,
        status='AGENDADO'
    )

    print(f"[{agora}] Verificando posts... Encontrados: {posts_para_publicar.count()}")

    for post in posts_para_publicar:
        print(f"Processando post agendado ID: {post.id} para o imóvel ID: {post.imovel.id}")
        
        # Simula uma requisição para reutilizar a view
        factory = RequestFactory()
        User = get_user_model()
        
        # Precisamos de um utilizador para a requisição (o utilizador que agendou)
        if post.agendado_por:
            user = post.agendado_por.user
        else: # Fallback para o primeiro superusuário se o utilizador foi deletado
            user = User.objects.filter(is_superuser=True).first()

        if not user:
            post.status = 'ERRO'
            post.resultado_publicacao = {'error': 'Nenhum utilizador válido para executar a publicação.'}
            post.save()
            continue
            
        # Criamos um objeto de requisição 'fake'
        request = factory.post('/fake-path/')
        request.user = user
        request.tenant = post.imobiliaria # Adicionamos o tenant à requisição
        request.data = {
            'imovel_id': post.imovel.id,
            'texto': post.texto,
            'plataformas': post.plataformas
        }
        
        try:
            # Instancia e chama a nossa view de publicação existente
            publisher_view = PublicacaoRedeSocialView()
            response = publisher_view.post(request)
            
            post.status = 'PUBLICADO'
            post.resultado_publicacao = response.data
        except Exception as e:
            post.status = 'ERRO'
            post.resultado_publicacao = {'error': str(e)}
            print(f"ERRO ao publicar post agendado ID {post.id}: {e}")
        
        post.data_publicacao_real = timezone.now()
        post.save()
        
    return f"Verificação concluída. {posts_para_publicar.count()} posts processados."
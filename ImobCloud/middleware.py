# C:\wamp64\www\ImobCloud\ImobCloud\middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import get_object_or_404
from core.models import Imobiliaria
from django.http import HttpResponseNotFound # Mantenha esta importação

class TenantIdentificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0] # Pega o host sem a porta
        request.tenant = None # Define como None por padrão

        # === Lógica para hosts de desenvolvimento (localhost, 127.0.0.1, e *.localhost) ===
        if host == 'localhost' or host == '127.0.0.1':
            # Se for localhost ou 127.0.0.1, tenta pegar a primeira imobiliária cadastrada.
            try:
                request.tenant = Imobiliaria.objects.first()
                if not request.tenant:
                    print("AVISO: Nenhuma imobiliária encontrada no banco de dados para localhost. Por favor, crie uma no /admin/.")
            except Exception as e:
                print(f"ERRO ao carregar imobiliária padrão para localhost: {e}")
            return # Sai do middleware aqui se for localhost/127.0.0.1

        # === Lógica para hosts com subdomínios (incluindo *.localhost em hosts válidos) ===
        # Ex: 'sol.localhost' ou 'imobiliaria.imobcloud.com'
        subdomain = None
        if '.' in host: # Garante que é um domínio/subdomínio
            parts = host.split('.')
            # Verifica se termina com '.localhost' (para desenvolvimento)
            if parts[-1] == 'localhost':
                if len(parts) > 1: # Pega o subdomínio antes do '.localhost'
                    subdomain = parts[0]
            # Verifica se termina com '.imobcloud.com' (para produção ou simulação mais real)
            # Adapte 'imobcloud.com' para seu domínio real se já tiver um.
            elif parts[-2:] == ['imobcloud', 'com']:
                if len(parts) > 2: # Pega o subdomínio antes de 'imobcloud.com'
                    subdomain = parts[0]
                
        if subdomain and subdomain != 'www': # 'www' ou vazio será o painel principal/público
            try:
                tenant = Imobiliaria.objects.get(subdominio=subdomain)
                request.tenant = tenant
            except Imobiliaria.DoesNotExist:
                print(f"AVISO: Imobiliária com subdomínio '{subdomain}' não encontrada no banco de dados.")
                # Opcional: retornar um 404 para subdomínios não mapeados
                # return HttpResponseNotFound(f"Imobiliária '{subdomain}' não encontrada.")
                pass # Permite que a view decida o que fazer

        # Se após toda a lógica, request.tenant ainda for None,
        # e a requisição não for para o admin (se você quiser forçar um 404 para URLs não mapeadas)
        # if not request.tenant and not request.path.startswith('/admin/'):
        #     return HttpResponseNotFound("Recurso não encontrado ou imobiliária inválida para este domínio.")
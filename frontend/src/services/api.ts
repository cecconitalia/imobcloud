// frontend/src/services/api.ts

// Usamos 'type' para importar tipos, corrigindo o erro de 'AxiosInstance'
import axios, { type AxiosInstance, type AxiosError, type AxiosResponse } from 'axios';
import type { Router } from 'vue-router'; // Apenas para tipagem

// Configuração base do Axios
const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api', // Garanta que a URL base termine aqui
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Requisição (Permanece inalterado: adiciona o token)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Função para configurar o Interceptor de Resposta de Erro.
 * É chamada em main.ts após a criação do router.
 */
export const setupInterceptors = (router: Router) => {
    apiClient.interceptors.response.use(
        (response: AxiosResponse) => {
            // Se a resposta for bem-sucedida, apenas retorne
            return response;
        },
        async (error: AxiosError) => {
            
            // ==================================================================
            // CORREÇÃO APLICADA (CONFORME SOLICITADO):
            // Agora, o interceptor captura tanto o erro 401 (Não Autorizado)
            // quanto o 403 (Proibido) e redireciona para o login.
            // ==================================================================
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                
                const status = error.response.status;
                
                // 1. Limpar tokens locais para encerrar a sessão
                localStorage.removeItem('authToken');
                localStorage.removeItem('refreshToken');
                localStorage.removeItem('userCargo');
                
                // 2. Redirecionar para a tela de login se não estiver já nela
                if (router.currentRoute.value.name !== 'login') {
                    if (status === 401) {
                        console.log("Token expirado ou inválido (401). Redirecionando para login.");
                    } else {
                        console.log("Acesso proibido (403). Redirecionando para login.");
                    }
                    router.replace({ name: 'login' });
                }

                return Promise.reject(new Error("Sessão encerrada (401/403). Por favor, faça login novamente."));
            }

            // Para outros erros (como 500 - Erro de Servidor),
            // rejeita a promessa. O componente (DashboardView)
            // ainda pode mostrar "Erro ao carregar", mas não
            // irá deslogar o usuário por um erro interno do servidor.
            return Promise.reject(error);
        }
    );
};

// Exportamos o cliente API como default
export default apiClient;
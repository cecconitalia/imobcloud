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
            // CORREÇÃO APLICADA:
            // Incluído o tratamento para o erro 403, que é o status retornado 
            // pelo middleware do Django para token expirado/inválido em 
            // endpoints protegidos (além do 401).
            // ==================================================================
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                
                console.log("Token expirado, inválido (401/403) ou usuário anônimo. Redirecionando para login.");
                
                // 1. Limpar tokens locais para encerrar a sessão
                localStorage.removeItem('authToken');
                localStorage.removeItem('refreshToken');
                localStorage.removeItem('userCargo');
                
                // 2. Redirecionar para a tela de login se não estiver já nela
                if (router.currentRoute.value.name !== 'login') {
                    router.replace({ name: 'login' });
                }

                // Rejeita a promessa com uma mensagem mais clara para o console
                return Promise.reject(new Error("Sessão encerrada (401/403). Por favor, faça login novamente."));
            }

            // Para outros erros (404, 500, ou 403 de permissão genuína de negócio
            // que deve ser tratada pelo componente), rejeita a promessa.
            return Promise.reject(error);
        }
    );
};

// Exportamos o cliente API como default
export default apiClient;
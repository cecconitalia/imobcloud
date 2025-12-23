// frontend/src/services/api.ts

import axios, { type AxiosInstance, type AxiosError, type AxiosResponse } from 'axios';
import type { Router } from 'vue-router'; // Apenas para tipagem

// Configuração base do Axios
const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api', // Garanta que a URL base termine aqui
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Requisição
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
 * Recebe o Router e a Store de Autenticação para realizar o logout completo.
 */
export const setupInterceptors = (router: Router, authStore: any) => {
    apiClient.interceptors.response.use(
        (response: AxiosResponse) => {
            return response;
        },
        async (error: AxiosError) => {
            
            // Tratamento para token expirado ou inválido (401 e 403)
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                
                console.warn("Sessão expirada (401/403). Realizando logout e redirecionando...");
                
                // CORREÇÃO PRINCIPAL:
                // Chamamos o logout da store. Isso limpa o localStorage E o estado do Pinia.
                // Se limparmos apenas o localStorage, o Pinia ainda achará que está logado
                // e o router guard impedirá a ida para o /login.
                if (authStore && typeof authStore.logout === 'function') {
                    authStore.logout();
                } else {
                    // Fallback de segurança
                    localStorage.clear();
                }
                
                // Redirecionar para a tela de login se não estiver já nela
                if (router.currentRoute.value.name !== 'login') {
                    const returnUrl = router.currentRoute.value.fullPath;
                    
                    router.replace({ 
                        name: 'login', 
                        query: { next: returnUrl } 
                    });
                }

                return Promise.reject(new Error("Sessão encerrada. Por favor, faça login novamente."));
            }

            return Promise.reject(error);
        }
    );
};

export default apiClient;
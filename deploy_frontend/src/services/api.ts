// frontend/src/services/api.ts

import axios, { type AxiosInstance, type AxiosError, type AxiosResponse } from 'axios';
import type { Router } from 'vue-router'; 

// Configuração base do Axios
// Ajustado para 'http://localhost:8000/api' para alinhar com as chamadas que já incluem '/v1/'
const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api', 
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
            
            // Tratamento para token expirado (403) ou inválido (401)
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                
                console.warn(`Sessão expirada ou inválida (${error.response.status}). Realizando logout...`);
                
                // CORREÇÃO CRÍTICA: Limpa o estado do Pinia.
                // Se isso falhar, o router guard impedirá o acesso à tela de login.
                if (authStore && typeof authStore.logout === 'function') {
                    authStore.logout();
                } else {
                    // Fallback se a store não for passada corretamente
                    console.error("AuthStore não disponível no interceptor. Limpando apenas LocalStorage.");
                    localStorage.clear();
                    // Força um reload para limpar a memória se a store falhar
                    window.location.href = '/login';
                    return Promise.reject(error);
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
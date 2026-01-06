// frontend/src/services/api.ts

import axios, { type AxiosInstance, type AxiosError, type AxiosResponse } from 'axios';
import type { Router } from 'vue-router'; 

// --- CORREÇÃO DA URL ---
// Função para definir a URL base dinamicamente
const getBaseUrl = () => {
  // Se estiver acessando pelo navegador em localhost, usa a porta 8000
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000/api';
  }
  // Caso contrário (produção na Vultr), usa o domínio atual com HTTPS
  return 'https://imobhome.com.br/api';
};

const apiClient: AxiosInstance = axios.create({
  baseURL: getBaseUrl(), // Usa a função inteligente aqui
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de Requisição (Adiciona o Token automaticamente)
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
 * Interceptor de Resposta (Trata erros de sessão e bloqueio)
 */
export const setupInterceptors = (router: Router, authStore: any) => {
    apiClient.interceptors.response.use(
        (response: AxiosResponse) => {
            return response;
        },
        async (error: AxiosError) => {
            
            if (error.response) {
                
                // --- 1. LÓGICA DE BLOQUEIO FINANCEIRO (SaaS) ---
                if (error.response.status === 403) {
                    const errorMessage = (error.response.data as any)?.detail || '';
                    
                    // Verifica se é Expiração de Teste
                    if (errorMessage === 'TRIAL_EXPIRED') {
                        router.push({ name: 'lock-screen', query: { reason: 'trial' } });
                        return Promise.reject(error);
                    }

                    // Verifica se é Expiração de Assinatura (Plano)
                    if (errorMessage === 'SUBSCRIPTION_EXPIRED' || 
                        (typeof errorMessage === 'string' && errorMessage.includes('suspenso'))) {
                        router.push({ name: 'lock-screen', query: { reason: 'subscription' } });
                        return Promise.reject(error);
                    }
                }

                // --- 2. TRATAMENTO DE TOKEN EXPIRADO / INVÁLIDO ---
                if (error.response.status === 401) {
                    
                    if (router.currentRoute.value.name === 'login') {
                        return Promise.reject(error);
                    }

                    console.warn(`Sessão expirada (${error.response.status}). Realizando logout...`);
                    
                    if (authStore && typeof authStore.logout === 'function') {
                        authStore.logout();
                    } else {
                        localStorage.clear();
                    }
                    
                    router.replace({ 
                        name: 'login', 
                        query: { next: router.currentRoute.value.fullPath } 
                    });

                    return Promise.reject(new Error("Sessão encerrada."));
                }
            }

            return Promise.reject(error);
        }
    );
};

export default apiClient;
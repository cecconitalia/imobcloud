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
 * Interceptor de Resposta (Trata erros de sessão e 401)
 */
export const setupInterceptors = (router: Router, authStore: any) => {
    apiClient.interceptors.response.use(
        (response: AxiosResponse) => {
            return response;
        },
        async (error: AxiosError) => {
            
            // Tratamento para token expirado (403) ou inválido (401)
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                
                // Evita loop infinito se já estiver na tela de login
                if (router.currentRoute.value.name === 'login') {
                    return Promise.reject(error);
                }

                console.warn(`Sessão expirada ou inválida (${error.response.status}). Realizando logout...`);
                
                if (authStore && typeof authStore.logout === 'function') {
                    authStore.logout();
                } else {
                    console.error("AuthStore não disponível. Limpando LocalStorage.");
                    localStorage.clear();
                }
                
                // Redireciona para o login
                router.replace({ 
                    name: 'login', 
                    query: { next: router.currentRoute.value.fullPath } 
                });

                return Promise.reject(new Error("Sessão encerrada. Por favor, faça login novamente."));
            }

            return Promise.reject(error);
        }
    );
};

export default apiClient;
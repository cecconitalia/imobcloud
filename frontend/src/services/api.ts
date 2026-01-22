import axios, { type AxiosInstance, type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

// Lógica de URL Base Inteligente
const getBaseUrl = () => {
  // 1. Em Produção (Build/Docker), forçamos '/api' relativo.
  // Isso resolve o problema do IP antigo no .env e evita a duplicação do 'v1'
  if (import.meta.env.PROD) {
    return '/api';
  }

  // 2. Em Desenvolvimento, tenta ler do .env ou fallback
  const envUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL;
  
  // Se o envUrl já tiver '/v1' no final, removemos para evitar duplicação
  if (envUrl && envUrl.endsWith('/v1')) {
    return envUrl.slice(0, -3);
  }

  return envUrl || '/api';
};

const api: AxiosInstance = axios.create({
  baseURL: getBaseUrl(),
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// --- INTERCEPTOR DE REQUISIÇÃO ---
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// --- INTERCEPTOR DE RESPOSTA ---
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    const authStore = useAuthStore();

    if (error.response) {
      // 1. Token Expirado (401)
      if (error.response.status === 401 && !originalRequest._retry) {
        if (originalRequest.url?.includes('token/') || originalRequest.url?.includes('login/')) {
          authStore.logout();
          router.push({ name: 'login' });
          return Promise.reject(error);
        }

        originalRequest._retry = true;

        try {
          await authStore.refreshToken();
          originalRequest.headers.Authorization = `Bearer ${authStore.token}`;
          return api(originalRequest);
        } catch (refreshError) {
          authStore.logout();
          router.push({ 
            name: 'login', 
            query: { next: router.currentRoute.value.fullPath } 
          });
          return Promise.reject(refreshError);
        }
      }

      // 2. Bloqueio SaaS (403)
      if (error.response.status === 403) {
        const errorMessage = (error.response.data as any)?.detail || '';
        const errorCode = (error.response.data as any)?.code || '';

        if (errorMessage === 'TRIAL_EXPIRED' || errorCode === 'trial_expired') {
          router.push({ name: 'lock-screen', query: { reason: 'trial' } });
          return Promise.reject(error);
        }

        if (
          errorMessage === 'SUBSCRIPTION_EXPIRED' || 
          errorCode === 'subscription_expired' ||
          (typeof errorMessage === 'string' && errorMessage.toLowerCase().includes('suspenso'))
        ) {
          router.push({ name: 'lock-screen', query: { reason: 'subscription' } });
          return Promise.reject(error);
        }
      }
    }

    if (error.code === 'ECONNABORTED') {
      console.error('Timeout na requisição.');
    }

    return Promise.reject(error);
  }
);

export default api;
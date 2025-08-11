// frontend/src/services/api.ts
import axios from 'axios';
import router from '@/router'; // Importamos o router para fazer o redirecionamento

const apiClient = axios.create({
  // A sua URL base para a API
  baseURL: 'http://localhost:8000/api', 
});

// --- INTERCEPTOR DE REQUISIÇÃO ---
// Adiciona o token de autenticação a cada requisição enviada para a API
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      // Garante que o cabeçalho de autorização é adicionado se o token existir
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Retorna o erro se algo falhar durante a configuração da requisição
    return Promise.reject(error);
  }
);

// --- INTERCEPTOR DE RESPOSTA (ATUALIZADO) ---
// Verifica cada resposta recebida da API
apiClient.interceptors.response.use(
  // Se a resposta for bem-sucedida (status 2xx), apenas a retorna sem modificação
  (response) => {
    return response;
  },
  // Se a resposta der erro, esta função será executada
  (error) => {
    // Verifica se o erro é o 401 Unauthorized (o que geralmente significa sessão expirada)
    if (error.response && error.response.status === 401) {
      
      // 1. Limpa todos os dados de sessão do localStorage para evitar inconsistências
      localStorage.removeItem('authToken');
      localStorage.removeItem('userCargo');
      localStorage.removeItem('imobiliariaName');
      localStorage.removeItem('userName');

      // 2. Redireciona o utilizador para a página de login de forma programática
      router.push({ name: 'login' });
      
      // 3. ATUALIZAÇÃO: Em vez de um alert(), registamos um aviso na consola.
      // Isto evita bloquear o utilizador e é uma prática de UX melhor.
      // No futuro, pode-se substituir isto por um sistema de notificação global (toast).
      console.warn("Sessão expirada. Redirecionando para a página de login.");
    }

    // É crucial retornar o erro para que outras partes do código (ex: um .catch() num componente)
    // possam lidar com outros tipos de erro (como 404, 500, etc.)
    return Promise.reject(error);
  }
);

export default apiClient;
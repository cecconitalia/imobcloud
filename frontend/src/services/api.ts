// frontend/src/services/api.ts
import axios from 'axios';
import router from '@/router'; // Importamos o router para fazer o redirecionamento

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// --- INTERCEPTOR DE REQUISIÇÃO (EXISTENTE) ---
// Adiciona o token de autenticação a cada requisição enviada para a API
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

// --- NOVO: INTERCEPTOR DE RESPOSTA ---
// Verifica cada resposta da API
apiClient.interceptors.response.use(
  // Se a resposta for bem-sucedida (status 2xx), apenas a retorna
  (response) => {
    return response;
  },
  // Se a resposta der erro, executa esta função
  (error) => {
    // Verifica se o erro é o 401 Unauthorized (sessão expirada)
    if (error.response && error.response.status === 401) {
      // 1. Limpa os dados do usuário do localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('userCargo');
      localStorage.removeItem('imobiliariaName');
      localStorage.removeItem('userName');

      // 2. Redireciona para a página de login
      // Usamos router.push para navegar programaticamente
      router.push({ name: 'login' });
      
      // 3. (Opcional) Mostra um alerta para o usuário
      alert("A sua sessão expirou. Por favor, faça o login novamente.");
    }

    // Retorna o erro para que outras partes do código possam lidar com ele se necessário
    return Promise.reject(error);
  }
);

export default apiClient;
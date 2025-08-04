import axios from 'axios';

const apiClient = axios.create({
  // Esta é a linha crucial. Aponta para a base da sua API no backend.
  baseURL: 'http://localhost:8000/api', 
  headers: {
    'Content-Type': 'application/json',
  },
});

// Este interceptor adiciona o token de autenticação a todos os pedidos
// depois de o utilizador ter feito o login.
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default apiClient;
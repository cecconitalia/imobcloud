// frontend/src/services/api.ts

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // Garanta que a URL base termine aqui
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default apiClient;
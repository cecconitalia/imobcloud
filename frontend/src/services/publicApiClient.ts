// Em frontend/src/services/publicApiClient.ts

import axios from 'axios';

// Este é um cliente de API limpo, SEM o interceptor de autenticação.
// Ele será usado apenas para as páginas do site público.
const publicApiClient = axios.create({
  baseURL: 'http://localhost:8000/api', 
  headers: {
    'Content-Type': 'application/json',
  },
});

export default publicApiClient;
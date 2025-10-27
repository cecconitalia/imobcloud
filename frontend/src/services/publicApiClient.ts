// Em frontend/src/services/publicApiClient.ts

import axios from 'axios';

// Este é um cliente de API limpo, SEM o interceptor de autenticação.
// Ele será usado apenas para as páginas do site público.
// CORRIGIDO: Adicionado o prefixo 'v1' para garantir que as rotas públicas sejam resolvidas corretamente.
const publicApiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1', 
  headers: {
    'Content-Type': 'application/json',
  },
});

export default publicApiClient;
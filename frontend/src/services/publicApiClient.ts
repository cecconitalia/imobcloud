// Em frontend/src/services/publicApiClient.ts

import axios from 'axios';

// Este é um cliente de API limpo, SEM o interceptor de autenticação.
// Ele será usado apenas para as páginas do site público.
// CORRIGIDO: A base deve ser a raiz do domínio (http://localhost:8000) porque as rotas públicas (public/imoveis/)
// estão mapeadas diretamente na raiz do projeto Django, fora do prefixo /api/v1.
const publicApiClient = axios.create({
  baseURL: 'http://localhost:8000', 
  headers: {
    'Content-Type': 'application/json',
  },
});

export default publicApiClient;
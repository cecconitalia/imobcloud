import axios from 'axios';

// --- CONFIGURAÇÃO INTELIGENTE DA URL ---
let baseURL = '';

if (import.meta.env.MODE === 'development') {
    // Ambiente Local (Docker)
    baseURL = 'http://localhost:8001';
} else {
    // Ambiente de Produção (Pega o domínio atual do navegador)
    // Isso resolve o erro de tentar conectar no IP:8080
    baseURL = window.location.origin; 
}

const http = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  async getImoveis(params: any = {}) {
    try {
      // CORREÇÃO CRÍTICA: 
      // O Django registrou a rota como 'public/imoveis/', não '/api/public/imoveis/'
      // Removemos a barra inicial para o axios concatenar corretamente com a baseURL
      const response = await http.get('public/imoveis/', { params });
      return response.data;
    } catch (error) {
      console.error('Erro de conexão (getImoveis):', error);
      throw error;
    }
  },

  async getImovelDetalhe(id: number) {
    try {
      const response = await http.get(`public/imoveis/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Erro ao buscar detalhe do imóvel ${id}:`, error);
      throw error;
    }
  }
};
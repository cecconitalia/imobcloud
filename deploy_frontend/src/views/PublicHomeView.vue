<template>
  <div class="container">
    <div class="main-content-wrapper">
      <div class="ai-search-fixed-top">
        <AIChatSearch @search-results="handleSearchResults" />
      </div>

      <div v-if="isLoading" class="loading-message">
        <div class="spinner"></div>
        <p>A carregar imóveis...</p>
      </div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div v-if="imoveis.length > 0" class="imoveis-grid-container">
        <div class="grid-header">
          <p v-if="aiMessage" class="ai-message-title">{{ aiMessage }}</p>
          <h2 v-else class="section-title">Imóveis em Destaque</h2>
          <span class="results-count">{{ imoveis.length }} resultado{{ imoveis.length > 1 ? 's' : '' }}</span>
        </div>
        <div class="imoveis-grid">
          <ImovelPublicCard v-for="imovel in imoveis" :key="imovel.id" :imovel="imovel" />
        </div>
      </div>

      <div v-if="!isLoading && imoveis.length === 0 && !error" class="no-results">
        <p>Nenhum imóvel encontrado que corresponda à sua pesquisa.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import publicApiClient from '@/services/publicApiClient';
import AIChatSearch from '@/components/AIChatSearch.vue';
import ImovelPublicCard from '@/components/ImovelPublicCard.vue';

const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const aiMessage = ref<string | null>(null);

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    let subdomain = null;
    
    // Lógica corrigida para extração de subdomínio em ambientes locais como 'estilo.localhost'
    if (parts.length > 1 && parts[0] !== 'www') {
      subdomain = parts[0];
    }
    
    // Fallback seguro
    if (subdomain === 'localhost' || !subdomain) {
        subdomain = 'estilomusical';
    }
    
    if (!subdomain) {
      imoveis.value = [];
      error.value = "Site não encontrado. Aceda através de um endereço de imobiliária válido.";
      return;
    }
    
    const params: { [key: string]: any } = { subdomain };
    // O caminho é apenas '/public/imoveis/' porque o publicApiClient.ts foi corrigido para a raiz.
    const response = await publicApiClient.get('/public/imoveis/', { params });
    imoveis.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis. Verifique a configuração da sua API (portas, CORS e se o servidor está a correr).';
  } finally {
    isLoading.value = false;
  }
}

function handleSearchResults(results: any) {
  imoveis.value = results.imoveis;
  aiMessage.value = results.mensagem;
}

onMounted(() => {
  fetchImoveis();
});
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem; /* Margem e padding do topo removidos para o hero section */
}

.main-content-wrapper {
  margin-top: 0; /* Espaçamento do topo removido */
}

.ai-search-fixed-top {
  margin: 0 auto; /* Espaçamento do topo e rodapé removidos */
  width: 100%;
  max-width: 600px;
}

.imoveis-grid-container {
  margin-top: 0; /* Espaçamento do topo removido */
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.section-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #343a40;
}

.ai-message-title {
  font-size: 1.25rem;
  font-weight: 500;
  color: #6c757d;
  margin: 0;
}

.results-count {
  font-size: 1rem;
  color: #6c757d;
  font-weight: 500;
}

.imoveis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
}

.loading-message, .error-message, .no-results {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
  font-size: 1.2rem;
}

.spinner {
  border: 4px solid rgba(0, 123, 255, 0.1);
  border-left-color: #007bff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  .hero-subtitle {
    font-size: 1.2rem;
  }
}
</style>
<template>
  <div class="container">
    <div class="filters-container">
      <div class="filter-group">
        <label for="finalidade">Finalidade</label>
        <select id="finalidade" v-model="filters.finalidade" @change="fetchImoveis">
          <option value="">Todas</option>
          <option value="Venda">Venda</option>
          <option value="Aluguel">Aluguel</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="tipo">Tipo de Imóvel</label>
        <select id="tipo" v-model="filters.tipo" @change="fetchImoveis">
          <option value="">Todos</option>
          <option value="Casa">Casa</option>
          <option value="Apartamento">Apartamento</option>
          <option value="Terreno">Terreno</option>
          <option value="Sala Comercial">Sala Comercial</option>
          <option value="Galpão">Galpão</option>
          <option value="Outro">Outro</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="cidade">Cidade</label>
        <input 
          type="text" 
          id="cidade" 
          v-model="filters.cidade" 
          @input="fetchImoveis"
          placeholder="Nome da cidade..." 
        />
      </div>
    </div>

    <div v-if="isLoading">A carregar imóveis...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="imoveis.length > 0" class="imoveis-grid">
      <div v-for="imovel in imoveis" :key="imovel.id" class="imovel-card">
        <router-link :to="`/site/imovel/${imovel.id}`" class="card-link">
          <img 
            :src="getPrincipalImage(imovel.imagens)" 
            alt="Imagem do imóvel" 
            class="imovel-image"
          />
          <div class="imovel-info">
            <h3 class="imovel-endereco">{{ imovel.endereco }}</h3>
            <p class="imovel-cidade">{{ imovel.cidade }}, {{ imovel.estado }}</p>
            <p class="imovel-preco">{{ formatarPreco(imovel) }}</p>
          </div>
        </router-link>
      </div>
    </div>

    <div v-if="!isLoading && imoveis.length === 0 && !error" class="no-results">
      <p>Nenhum imóvel encontrado com os filtros selecionados.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import publicApiClient from '@/services/publicApiClient';

const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// NOVO: Estado reativo para os filtros
const filters = ref({
  finalidade: '',
  tipo: '',
  cidade: ''
});

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    let subdomain = null;

    if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
      subdomain = parts[0];
    }
    
    if (!subdomain) {
      imoveis.value = [];
      error.value = "Site não encontrado. Aceda através de um endereço de imobiliária válido.";
      return;
    }
    
    // ATUALIZADO: Adiciona os filtros aos parâmetros da API
    const params = {
        subdomain: subdomain,
        ...filters.value // Adiciona os valores do objeto de filtros
    };

    const response = await publicApiClient.get('/v1/imoveis/imoveis/', { params });
    imoveis.value = response.data;

  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchImoveis();
});

// As funções `getPrincipalImage` e `formatarPreco` permanecem iguais
function getPrincipalImage(imagens: any[]) {
  if (!imagens || imagens.length === 0) {
    return 'https://via.placeholder.com/400x300.png?text=Sem+Imagem';
  }
  const principal = imagens.find(img => img.principal);
  return principal ? principal.imagem : imagens[0].imagem;
}
function formatarPreco(imovel: any) {
  if (imovel.finalidade === 'Venda' && imovel.valor_venda) {
    return parseFloat(imovel.valor_venda).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  if (imovel.finalidade === 'Aluguel' && imovel.valor_aluguel) {
    return `${parseFloat(imovel.valor_aluguel).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} /mês`;
  }
  return 'Valor a consultar';
}
</script>

<style scoped>
/* NOVOS ESTILOS PARA OS FILTROS */
.filters-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}
.filter-group {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.filter-group label {
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}
.filter-group select, .filter-group input {
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 1rem;
}
.no-results {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

/* O seu CSS existente permanece sem alterações */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
.error-message {
  color: red;
  text-align: center;
  padding: 2rem;
}
.imoveis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.imovel-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.2s;
}
.imovel-card:hover {
  transform: translateY(-5px);
}
.card-link {
  text-decoration: none;
  color: inherit;
}
.imovel-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}
.imovel-info {
  padding: 1rem;
}
.imovel-endereco {
  font-size: 1.1rem;
  font-weight: bold;
  margin: 0 0 0.5rem 0;
}
.imovel-cidade {
  color: #6c757d;
  margin: 0 0 1rem 0;
}
.imovel-preco {
  font-size: 1.2rem;
  font-weight: bold;
  color: #007bff;
  margin: 0;
}
</style>
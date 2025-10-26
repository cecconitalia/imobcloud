<template>
  <div class="imoveis-container">
    <div class="search-and-filter-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Buscar por código, título, cidade..." 
        class="search-input"
      />
      <div class="filter-group">
        <label for="tipo">Tipo:</label>
        <select id="tipo" v-model="filters.tipo">
          <option value="">Todos</option>
          <option value="CASA">Casa</option>
          <option value="APARTAMENTO">Apartamento</option>
          <option value="TERRENO">Terreno</option>
          <option value="SALA_COMERCIAL">Sala Comercial</option>
          <option value="GALPAO">Galpão</option>
          <option value="RURAL">Rural</option>
          <option value="OUTRO">Outro</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="finalidade">Finalidade:</label>
        <select id="finalidade" v-model="filters.finalidade">
          <option value="">Todas</option>
          <option value="RESIDENCIAL">Residencial</option>
          <option value="COMERCIAL">Comercial</option>
          <option value="INDUSTRIAL">Industrial</option>
          <option value="RURAL">Rural</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filters.status">
          <option value="">Todos</option>
          <option value="A_VENDA">À Venda</option>
          <option value="PARA_ALUGAR">Para Alugar</option>
          <option value="VENDIDO">Vendido</option>
          <option value="ALUGADO">Alugado</option>
          <option value="EM_CONSTRUCAO">Em Construção</option>
          <option value="DESATIVADO">Desativado</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="loading-message">
      A carregar imóveis...
    </div>
    <div v-else-if="imoveis.length === 0" class="empty-message">
      Nenhum imóvel encontrado.
    </div>
    <div v-else class="imoveis-grid">
      <div v-for="imovel in filteredImoveis" :key="imovel.id" class="imovel-card">
        <div class="card-image-container" @click="editImovel(imovel.id)">
          <img 
            :src="getPrincipalImage(imovel.imagens)" 
            alt="Imagem do Imóvel" 
            class="imovel-image"
          />
          <span :class="['status-badge', getStatusClass(imovel.status)]">
            {{ formatStatus(imovel.status) }}
          </span>
        </div>
        <div class="card-content">
          <div class="card-header-content">
            <h3 class="card-title">{{ imovel.titulo_anuncio || 'Imóvel sem título' }}</h3>
            <span class="card-codigo">#{{ imovel.codigo_referencia }}</span>
          </div>
          <div class="card-details">
            <p><strong>Tipo:</strong> {{ imovel.tipo }}</p>
            <p><strong>Finalidade:</strong> {{ imovel.finalidade }}</p>
            <p><strong>Localização:</strong> {{ imovel.bairro }}, {{ imovel.cidade }}</p>
            <p v-if="imovel.valor_venda"><strong>Valor de Venda:</strong> {{ formatCurrency(imovel.valor_venda) }}</p>
            <p v-if="imovel.valor_aluguel"><strong>Valor de Aluguel:</strong> {{ formatCurrency(imovel.valor_aluguel) }}</p>
            <p><strong>Área:</strong> {{ imovel.area_total }} m²</p>
            <p><strong>Quartos:</strong> {{ imovel.quartos }} | <strong>Suítes:</strong> {{ imovel.suites }}</p>
          </div>
        </div>
        <div class="card-actions">
          <button @click="editImovel(imovel.id)" class="btn-edit">
            <i class="fas fa-edit"></i> Editar
          </button>
          <button @click="confirmInativar(imovel.id)" class="btn-delete">
            <i class="fas fa-trash-alt"></i> Inativar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { formatCurrency, formatStatus } from '@/utils/formatters';

const router = useRouter();
const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const searchQuery = ref('');
const filters = ref({
  tipo: '',
  finalidade: '',
  status: '',
});

const defaultImage = 'https://via.placeholder.com/400x300.png?text=Sem+imagem';
let debounceTimeout: number | undefined = undefined;

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/imoveis/');
    imoveis.value = response.data;
  } catch (error) {
    console.error("Erro ao carregar imóveis:", error);
  } finally {
    isLoading.value = false;
  }
}

function getPrincipalImage(imagens: any[]): string {
  if (!imagens || imagens.length === 0) {
    return defaultImage;
  }
  const principal = imagens.find(img => img.principal);
  return principal ? principal.imagem : imagens[0].imagem;
}

function getStatusClass(status: string) {
    switch (status) {
        case 'A_VENDA':
        case 'PARA_ALUGAR':
            return 'status-ativo';
        case 'VENDIDO':
        case 'ALUGADO':
            return 'status-concluido';
        case 'EM_CONSTRUCAO':
            return 'status-pendente';
        case 'DESATIVADO':
            return 'status-inativo';
        default:
            return '';
    }
}

const filteredImoveis = computed(() => {
  return imoveis.value.filter(imovel => {
    const matchesSearch = searchQuery.value
      ? (imovel.codigo_referencia?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
         imovel.titulo_anuncio?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
         imovel.cidade?.toLowerCase().includes(searchQuery.value.toLowerCase()))
      : true;
    
    const matchesFilters = 
      (filters.value.tipo === '' || imovel.tipo === filters.value.tipo) &&
      (filters.value.finalidade === '' || imovel.finalidade === filters.value.finalidade) &&
      (filters.value.status === '' || imovel.status === filters.value.status);
      
    return matchesSearch && matchesFilters;
  });
});

/*
  // A função goToCreateImovel foi REMOVIDA por não ser mais necessária
  function goToCreateImovel() {
    router.push({ name: 'imovel-novo' });
  }
*/

function editImovel(id: number) {
  router.push({ name: 'imovel-editar', params: { id } });
}

function confirmInativar(id: number) {
  if (confirm('Tem certeza que deseja inativar este imóvel? Ele continuará existindo, mas não estará disponível para venda/aluguel.')) {
    inativarImovel(id);
  }
}

async function inativarImovel(id: number) {
  try {
    // Altera a chamada para uma requisição PATCH
    await apiClient.patch(`/v1/imoveis/${id}/`, { status: 'DESATIVADO' });
    
    // Atualiza a lista localmente para refletir a mudança de status
    const index = imoveis.value.findIndex(imovel => imovel.id === id);
    if (index !== -1) {
      imoveis.value[index].status = 'DESATIVADO';
    }

    alert('Imóvel inativado com sucesso!');
  } catch (error) {
    console.error("Erro ao inativar imóvel:", error);
    alert('Ocorreu um erro ao inativar o imóvel.');
  }
}

onMounted(() => {
  fetchImoveis();
});

watch([filters.value, searchQuery], () => {
    if (debounceTimeout) {
        clearTimeout(debounceTimeout);
    }
    debounceTimeout = setTimeout(() => {
        fetchImoveis();
    }, 500);
}, { deep: true });

</script>

<style scoped>
.imoveis-container {
  padding: 0;
  background-color: transparent;
}

/* Os estilos .view-header, .header-actions e .btn-primary 
  foram REMOVIDOS pois o header não existe mais.
*/

.search-and-filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem; 
  align-items: center;
  
  /* CORREÇÕES APLICADAS AQUI (remoção da "caixa"):
    - background-color: #ffffff; (REMOVIDO)
    - padding: 1.5rem; (ALTERADO PARA 0)
    - border-radius: 8px; (REMOVIDO)
    - box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); (REMOVIDO)
  */
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  box-shadow: none;
}

.search-input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 100%;
  max-width: 350px;
  box-sizing: border-box;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: #555;
  white-space: nowrap;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 0.95rem;
  background-color: #f8f9fa;
  min-width: 120px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

.imoveis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.imovel-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.07);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.imovel-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.card-image-container {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
  cursor: pointer;
}

.imovel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 16px;
  color: white;
  font-weight: bold;
  font-size: 0.75em;
}

.status-badge.status-ativo { background-color: #28a745; }
.status-badge.status-concluido { background-color: #007bff; }
.status-badge.status-pendente { background-color: #ffc107; color: #333; }
.status-badge.status-inativo { background-color: #6c757d; }

.card-content {
  padding: 1rem;
  flex-grow: 1;
}

.card-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.card-title {
  font-size: 1.1rem;
  margin: 0;
  color: #333;
  font-weight: 600;
}

.card-codigo {
  font-size: 0.85rem;
  font-weight: 600;
  color: #6c757d;
}

.card-details p {
  margin: 0.3rem 0;
  font-size: 0.85rem;
  color: #666;
}

.card-details strong {
  color: #333;
}

.card-actions {
  display: flex;
  justify-content: space-around;
  padding: 0.8rem;
  border-top: 1px solid #f0f0f0;
  gap: 0.8rem;
}

.btn-edit, .btn-delete {
  flex-grow: 1;
  padding: 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s ease;
  font-size: 0.9rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

.btn-edit {
  background-color: #17a2b8;
  color: white;
}

.btn-edit:hover {
  background-color: #138496;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

.loading-message, .empty-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #6c757d;
}
</style>
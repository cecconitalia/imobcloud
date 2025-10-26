<template>
  <div class="imoveis-container">

    <div v-if="sumarioImoveis" class="summary-cards">
      <div class="card" @click="setFilter('status', 'A_VENDA')" :class="{ active: filters.status === 'A_VENDA' }">
        <p class="card-value">{{ sumarioImoveis.a_venda }}</p>
        <p class="card-label">Imóveis à Venda</p>
      </div>
      <div class="card" @click="setFilter('status', 'PARA_ALUGAR')" :class="{ active: filters.status === 'PARA_ALUGAR' }">
        <p class="card-value">{{ sumarioImoveis.para_alugar }}</p>
        <p class="card-label">Imóveis para Alugar</p>
      </div>
      <div class="card" @click="setFilter('status', 'VENDIDO_OU_ALUGADO')" :class="{ active: filters.status === 'VENDIDO_OU_ALUGADO' }">
        <p class="card-value">{{ sumarioImoveis.vendidos_e_alugados }}</p>
        <p class="card-label">Vendidos/Alugados (Mês)</p>
      </div>
      <div class="card" @click="setFilter('status', '')" :class="{ active: filters.status === '' && !searchQuery }">
        <p class="card-value">{{ imoveis.length }}</p>
        <p class="card-label">Total de Imóveis</p>
      </div>
    </div>
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
      <button @click="goToCreateImovel" class="btn-add">
        <i class="fas fa-plus"></i> Adicionar Imóvel
      </button>
      </div>

    <div v-if="isLoading" class="loading-message">
      A carregar imóveis...
    </div>
    <div v-else-if="filteredImoveis.length === 0" class="empty-message">
      Nenhum imóvel encontrado para os filtros e pesquisa aplicados.
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

// VARIÁVEL PARA O SUMÁRIO MANTIDA
const sumarioImoveis = ref<any>(null); 
// FIM

const defaultImage = 'https://via.placeholder.com/400x300.png?text=Sem+imagem';
let debounceTimeout: number | undefined = undefined;

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/imoveis/');
    imoveis.value = response.data;
    
    // CÁLCULO DO SUMÁRIO MANTIDO
    calculateSummary(imoveis.value);

  } catch (error) {
    console.error("Erro ao carregar imóveis:", error);
  } finally {
    isLoading.value = false;
  }
}

// FUNÇÃO DE CÁLCULO DO SUMÁRIO MANTIDA
function calculateSummary(list: any[]) {
    const a_venda = list.filter(i => i.status === 'A_VENDA').length;
    const para_alugar = list.filter(i => i.status === 'PARA_ALUGAR').length;
    const vendidos_e_alugados = list.filter(i => i.status === 'VENDIDO' || i.status === 'ALUGADO').length; 

    sumarioImoveis.value = {
        a_venda,
        para_alugar,
        vendidos_e_alugados
    };
}

// FUNÇÃO DE FILTRO PELO CARD MANTIDA
function setFilter(key: 'tipo' | 'finalidade' | 'status', value: string) {
    if (key === 'status' && value === 'VENDIDO_OU_ALUGADO') {
        if (filters.value.status === 'VENDIDO_OU_ALUGADO') {
            filters.value.status = '';
        } else {
            filters.value.status = 'VENDIDO_OU_ALUGADO';
        }
    } else {
        if (filters.value[key] === value) {
            filters.value[key] = ''; // Limpa o filtro se clicar novamente
        } else {
            filters.value[key] = value;
        }
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
    const searchLower = searchQuery.value.toLowerCase();
    
    const matchesSearch = searchQuery.value
      ? (imovel.codigo_referencia?.toLowerCase().includes(searchLower) ||
         imovel.titulo_anuncio?.toLowerCase().includes(searchLower) ||
         imovel.cidade?.toLowerCase().includes(searchLower))
      : true;
    
    let matchesStatus = true;
    if (filters.value.status !== '') {
        if (filters.value.status === 'VENDIDO_OU_ALUGADO') {
            matchesStatus = (imovel.status === 'VENDIDO' || imovel.status === 'ALUGADO');
        } else {
            matchesStatus = imovel.status === filters.value.status;
        }
    }

    const matchesFilters = 
      (filters.value.tipo === '' || imovel.tipo === filters.value.tipo) &&
      (filters.value.finalidade === '' || imovel.finalidade === filters.value.finalidade) &&
      matchesStatus; 
      
    return matchesSearch && matchesFilters;
  });
});

function goToCreateImovel() {
  router.push({ name: 'imovel-novo' });
}

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
    await apiClient.patch(`/v1/imoveis/${id}/`, { status: 'DESATIVADO' });
    
    const index = imoveis.value.findIndex(imovel => imovel.id === id);
    if (index !== -1) {
      imoveis.value[index].status = 'DESATIVADO';
    }

    // Reacalcula o sumário após a alteração
    calculateSummary(imoveis.value);

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
         // Apenas para que o watch seja executado e reaja a mudanças, o computed já filtra
    }, 500);
}, { deep: true });

</script>

<style scoped>
.imoveis-container {
  padding: 0;
  background-color: transparent;
}

/* ESTILOS DO DASHBOARD (MANTIDOS) */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  display: flex; 
  flex-direction: column;
  justify-content: center;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 12px rgba(0,0,0,0.1);
}
.card.active {
    border-color: #007bff;
    box-shadow: 0 6px 10px rgba(0, 123, 255, 0.2);
}
.card-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  color: #007bff;
}
.card-label {
  margin: 0.5rem 0 0 0;
  color: #6c757d;
  font-size: 0.9rem;
}
/* FIM ESTILOS DO DASHBOARD */

.search-and-filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem; 
  align-items: center;
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

/* CORREÇÃO: Estilo do botão para alinhar no far-right da barra de filtros */
.btn-add {
  background-color: #007bff; /* Cor primária padrão */
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s ease;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto; /* IMPORTANTE: Empurra o botão para a direita */
  width: auto;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

.btn-add:hover {
  background-color: #0056b3;
}
/* FIM CORREÇÃO */

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
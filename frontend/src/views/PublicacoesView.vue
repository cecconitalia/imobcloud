<template>
  <div class="publicacoes-container">
    <div class="metrics-panel">
      <div class="metric-card">
        <i class="fas fa-home metric-icon"></i>
        <div class="metric-info">
          <span>Total de Imóveis</span>
          <strong>{{ imoveis.length }}</strong>
        </div>
      </div>
      <div class="metric-card">
        <i class="fas fa-bullhorn metric-icon"></i>
        <div class="metric-info">
          <span>Não Publicados</span>
          <strong>{{ totalNaoPublicados }}</strong>
        </div>
      </div>
       <div class="metric-card">
        <i class="fas fa-calendar-check metric-icon"></i>
         <div class="metric-info">
           <span>Próximo Agendamento</span>
           <strong>{{ proximoAgendamento ? formatarDataHora(proximoAgendamento.data_agendada) : 'Nenhum' }}</strong>
        </div>
      </div>
       <div class="metric-card">
         <i class="fas fa-history metric-icon"></i>
         <div class="metric-info">
           <span>Publicações (30d)</span>
           <strong>{{ totalPublicado30d }}</strong>
        </div>
      </div>
    </div>

    <div class="filters-panel">
      <div class="filters-header" @click="toggleFilters">
        <h3 class="filters-title">
          <i :class="['fas', isFiltersOpen ? 'fa-chevron-up' : 'fa-chevron-down']"></i>
          Filtros
        </h3>
        <button v-if="hasActiveFilters" @click.stop="resetFilters" class="btn-secondary reset-btn">
          <i class="fas fa-undo-alt"></i> Limpar Filtros
        </button>
      </div>

      <div v-if="isFiltersOpen" class="filters-content">
        <div class="filter-group">
          <label class="filter-label">Busca Rápida</label>
          <div class="search-input-wrapper">
            <i class="fas fa-search search-icon"></i>
            <input
              type="text"
              v-model="searchTerm"
              placeholder="Endereço, código..."
            />
            <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <div class="chip-filters-container">
          <div class="chip-group">
            <span class="chip-label">Status do Imóvel:</span>
            <div class="chip-options">
              <label :class="['chip', { 'chip-active': statusFilter === '' }]">
                <input type="radio" v-model="statusFilter" value="" />
                Todos
              </label>
              <label :class="['chip', { 'chip-active': statusFilter === 'A_VENDA' }]">
                <input type="radio" v-model="statusFilter" value="A_VENDA" />
                À Venda
              </label>
              <label :class="['chip', { 'chip-active': statusFilter === 'PARA_ALUGAR' }]">
                <input type="radio" v-model="statusFilter" value="PARA_ALUGAR" />
                Para Alugar
              </label>
              <label :class="['chip', { 'chip-active': statusFilter === 'VENDIDO' }]">
                <input type="radio" v-model="statusFilter" value="VENDIDO" />
                Vendido
              </label>
              <label :class="['chip', { 'chip-active': statusFilter === 'ALUGADO' }]">
                <input type="radio" v-model="statusFilter" value="ALUGADO" />
                Alugado
              </label>
            </div>
          </div>

          <div class="chip-group">
            <span class="chip-label">Status da Publicação:</span>
            <div class="chip-options">
              <label :class="['chip', { 'chip-active': publicationStatusFilter === '' }]">
                <input type="radio" v-model="publicationStatusFilter" value="" />
                Todos
              </label>
              <label :class="['chip', { 'chip-active': publicationStatusFilter === 'not_published' }]">
                <input type="radio" v-model="publicationStatusFilter" value="not_published" />
                Não Publicado
              </label>
              <label :class="['chip', { 'chip-active': publicationStatusFilter === 'published' }]">
                <input type="radio" v-model="publicationStatusFilter" value="published" />
                Publicado
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-message">
      <div class="spinner"></div>
      <p>A carregar imóveis...</p>
    </div>
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
    </div>

    <div v-if="paginatedImoveis.length > 0" class="imoveis-list">
      <ImovelCard
        v-for="imovel in paginatedImoveis"
        :key="imovel.id"
        :imovel="imovel"
        @open-modal="openModal(imovel)"
        @open-history-modal="openHistoryModal(imovel.id)"
      />
    </div>

    <div v-if="!isLoading && filteredImoveis.length === 0" class="no-data-message">
      <i class="fas fa-box-open"></i>
      <p>Nenhum imóvel encontrado com os filtros atuais.</p>
    </div>

    <div class="pagination-controls">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn-secondary">Anterior</button>
      <span>Página {{ currentPage }} de {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-secondary">Próxima</button>
    </div>

    <PublicacaoModal
      v-if="selectedImovel"
      :imovel-id="selectedImovel.id"
      @close="closeModal"
    />

    <HistoricoPublicacoesModal
      v-if="showHistoryModal"
      :imovel-id="selectedImovelIdForHistory"
      @close="closeHistoryModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';
import PublicacaoModal from '@/components/PublicacaoModal.vue';
import ImovelCard from "@/components/ImovelPublicCard.vue"; // Componente ImovelCard foi renomeado para ImovelPublicCard
import HistoricoPublicacoesModal from '@/components/HistoricoPublicacoesModal.vue';
import '@fortawesome/fontawesome-free/css/all.css';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Simulação de dados para evitar erro de undefined, tipagem conforme código do usuário
interface ImovelPublicacao {
    id: number;
    titulo_anuncio?: string;
    endereco?: string;
    codigo_referencia?: string;
    status: string;
    isPublished: boolean;
    valor_venda: number;
    valor_aluguel?: number;
}
interface AgendamentoResumo { id: number; data_agendada: string; } // Adicionado para evitar erro

const imoveis = ref<ImovelPublicacao[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Estado dos Filtros
const searchTerm = ref('');
const statusFilter = ref('');
const publicationStatusFilter = ref('');
const isFiltersOpen = ref(true);

// Estado dos Modais
const selectedImovel = ref<any | null>(null);
const showHistoryModal = ref(false);
const selectedImovelIdForHistory = ref<number | null>(null);

// Paginação
const currentPage = ref(1);
const itemsPerPage = ref(10);


// Placeholder para as métricas ausentes no script original
const totalPublicado30d = ref(0);
const ultimaPublicacao = ref(null);
const proximoAgendamento = ref<AgendamentoResumo | null>(null);

function formatarDataHora(dataIso: string | null): string {
  if (!dataIso) return 'N/A';
  try {
    return format(new Date(dataIso), 'dd/MM/yyyy HH:mm', { locale: ptBR });
  } catch {
    return 'Inválido';
  }
}
function formatarValor(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return 'R$ -';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}


async function fetchImoveis() {
  isLoading.value = true;
  try {
    const response = await apiClient.get<any[]>('/v1/imoveis/');
    // Mantendo a lógica original de simulação de publicação
    imoveis.value = response.data.map((imovel: any, index: number) => ({
      ...imovel,
      isPublished: index % 3 === 0, // Simula status de publicado
      // Simula valores para evitar erro se a API não retornar
      valor_venda: imovel.valor_venda || Math.floor(Math.random() * (1000000 - 100000 + 1) + 100000),
      // Simula agendamento (necessário para as métricas, mesmo que simplificado)
      proximo_agendamento: index === 0 ? { id: 1, data_agendada: new Date(new Date().setDate(new Date().getDate() + 5)).toISOString() } : null,
      ultima_publicacao: index === 1 ? { id: 2, data_publicacao: new Date(new Date().setDate(new Date().getDate() - 10)).toISOString() } : null,
    }));
  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis.';
  } finally {
    isLoading.value = false;
  }
}

const totalNaoPublicados = computed(() => {
  return imoveis.value.filter(imovel => !imovel.isPublished).length;
});

const hasActiveFilters = computed(() => {
  return (
    searchTerm.value !== '' ||
    statusFilter.value !== '' ||
    publicationStatusFilter.value !== ''
  );
});

const filteredImoveis = computed(() => {
  let filtered = imoveis.value;

  // Filtro por termo de busca
  if (searchTerm.value) {
    const normalizedSearch = searchTerm.value.toLowerCase().trim();
    filtered = filtered.filter(imovel =>
      (imovel.titulo_anuncio && imovel.titulo_anuncio.toLowerCase().includes(normalizedSearch)) ||
      (imovel.endereco && imovel.endereco.toLowerCase().includes(normalizedSearch)) ||
      (imovel.codigo_referencia && imovel.codigo_referencia.toLowerCase().includes(normalizedSearch))
    );
  }

  // Filtro por status do imóvel
  if (statusFilter.value) {
    filtered = filtered.filter(imovel => imovel.status === statusFilter.value);
  } else {
    // Mantém o filtro original que excluía 'DESATIVADO' (se existir)
    filtered = filtered.filter(imovel => imovel.status !== 'DESATIVADO');
  }

  // Filtro por status de publicação
  if (publicationStatusFilter.value) {
    const isPublished = publicationStatusFilter.value === 'published';
    filtered = filtered.filter(imovel => imovel.isPublished === isPublished);
  }

  // Ordena para que os não publicados fiquem no topo
  filtered.sort((a, b) => {
    if (!a.isPublished && b.isPublished) return -1;
    if (a.isPublished && !b.isPublished) return 1;
    return 0;
  });

  // Reseta a página para a primeira a cada novo filtro
  currentPage.value = 1;
  return filtered;
});

const totalPages = computed(() => {
  return Math.ceil(filteredImoveis.value.length / itemsPerPage.value);
});

const paginatedImoveis = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredImoveis.value.slice(start, end);
});

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
}

function clearSearch() {
  searchTerm.value = '';
}

function resetFilters() {
  searchTerm.value = '';
  statusFilter.value = '';
  publicationStatusFilter.value = '';
}

function toggleFilters() {
  isFiltersOpen.value = !isFiltersOpen.value;
}

function openModal(imovel: any) {
  selectedImovel.value = imovel;
}

function closeModal() {
  selectedImovel.value = null;
}

function openHistoryModal(imovelId: number) {
  selectedImovelIdForHistory.value = imovelId;
  showHistoryModal.value = true;
}

function closeHistoryModal() {
  showHistoryModal.value = false;
  selectedImovelIdForHistory.value = null;
}

onMounted(() => {
  fetchImoveis();
});
</script>

<style scoped>
/* Variáveis CSS */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --bg-light: #f8f9fa;
  --card-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
}

.publicacoes-container {
  padding: 0;
  background-color: var(--bg-light);
  min-height: 100vh;
}

/* --- CARDS DE MÉTRICAS (PADRÃO DASHBOARD) --- */
.metrics-panel {
  display: grid; /* Usar grid para melhor controle de colunas */
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: 2.5rem;
}
.metric-card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Sombra mais suave */
  display: flex;
  align-items: center;
  justify-content: space-between; /* Novo: Ícone à direita, info à esquerda */
  gap: 1rem;
  border-left: 5px solid; /* Borda lateral padrão */
  transition: box-shadow 0.2s;
}
/* Cores das Bordas (simulando cores do dashboard) */
.metric-card:nth-child(1) { border-color: #0d6efd; } /* Azul - Total Imóveis */
.metric-card:nth-child(2) { border-color: #dc3545; } /* Vermelho - Não Publicados (Alerta) */
.metric-card:nth-child(3) { border-color: #ffc107; } /* Amarelo - Próximo Agendamento */
.metric-card:nth-child(4) { border-color: #198754; } /* Verde - Publicações 30d (Sucesso) */

.metric-icon {
  font-size: 2.5rem; /* Ícone maior */
  color: #adb5bd; /* Cor cinza suave */
  order: 2; /* Move o ícone para a direita */
}
.metric-info {
  display: flex;
  flex-direction: column;
  text-align: left;
  order: 1; /* Move as informações para a esquerda */
}
.metric-info span {
  font-size: 0.9rem; /* Label menor */
  color: #6c757d;
}
.metric-info strong {
  font-size: 1.8rem; /* Valor maior */
  font-weight: 600;
  color: #343a40;
}
/* FIM CARDS DE MÉTRICAS */


/* Painel de Filtros */
.filters-panel {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 1rem;
  margin-bottom: 2rem;
}
.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem;
}
.filters-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #343a40;
}
.filters-title i {
  margin-right: 0.5rem;
  color: #6c757d;
  transition: transform 0.3s;
}
.filters-content {
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  margin-top: 0.5rem;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.filter-group label {
  font-weight: 600;
  color: #495057;
}
.search-input-wrapper {
  position: relative;
}
.search-input-wrapper input,
.price-inputs input,
.filter-group input,
.filter-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  transition: box-shadow 0.2s;
}
.search-input-wrapper input {
  padding-left: 40px;
}
.search-icon, .clear-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: #aaa;
}
.search-icon { left: 15px; }
.clear-btn { right: 15px; background: none; border: none; cursor: pointer; }
.chip-filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-top: 1rem;
}
.chip-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.chip-label { font-weight: 600; color: #495057; white-space: nowrap; }
.chip-options { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.chip {
  padding: 8px 16px;
  border-radius: 20px;
  background-color: #e9ecef;
  color: #495057;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid #e9ecef;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}
.chip input[type="radio"] { display: none; }
.chip-active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}
.reset-btn {
  background-color: #f1f1f1 !important;
  color: #343a40 !important;
  font-weight: 600;
  border: none;
}
.reset-btn:hover {
  background-color: #e2e6ea !important;
}

/* Lista de Imóveis (Grid de Cartões) */
.imoveis-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  padding: 0;
  margin-top: 3rem;
}

/* Paginação */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: 2rem;
}
.btn-secondary {
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-secondary:hover { background-color: #d1d5db; }
.btn-secondary:disabled { background-color: #f1f1f1; color: #c4c4c4; cursor: not-allowed; }

/* Mensagens de status */
.loading-message, .no-data-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.loading-message .spinner {
  border: 4px solid rgba(0, 123, 255, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
.no-data-message i, .error-message i { font-size: 2.5rem; margin-bottom: 0.5rem; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 767px) {
  .publicacoes-container { padding: 1rem; }
  .filters-panel { padding: 1rem; }
  .filters-header { padding: 0.25rem; }
  .filters-content { padding-top: 0.5rem; }
  .filters-row { grid-template-columns: 1fr; }
  .chip-filters-container { flex-direction: column; gap: 1rem; }
  .chip-group { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .chip-options { flex-wrap: wrap; }
}
</style>
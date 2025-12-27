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
          Filtros & Busca
        </h3>
        <button v-if="hasActiveFilters" @click.stop="resetFilters" class="btn-secondary reset-btn">
          <i class="fas fa-undo-alt"></i> Limpar
        </button>
      </div>

      <div v-if="isFiltersOpen" class="filters-content">
        <div class="filter-group">
          <div class="search-input-wrapper">
            <i class="fas fa-search search-icon"></i>
            <input
              type="text"
              v-model="searchTerm"
              placeholder="Buscar por título, código ou endereço..."
            />
            <button v-if="searchTerm" @click="clearSearch" class="clear-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <div class="chip-filters-container">
          <div class="chip-group">
            <span class="chip-label">Imóvel:</span>
            <div class="chip-options">
              <label :class="['chip', { 'chip-active': statusFilter === '' }]">
                <input type="radio" v-model="statusFilter" value="" /> Todos
              </label>
              <label :class="['chip', { 'chip-active': statusFilter === 'A_VENDA' }]">
                <input type="radio" v-model="statusFilter" value="A_VENDA" /> À Venda
              </label>
              <label :class="['chip', { 'chip-active': statusFilter === 'PARA_ALUGAR' }]">
                <input type="radio" v-model="statusFilter" value="PARA_ALUGAR" /> Alugar
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
      <p>Nenhum imóvel encontrado.</p>
    </div>

    <div class="pagination-controls" v-if="totalPages > 1">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn-secondary">Anterior</button>
      <span>Página {{ currentPage }} de {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-secondary">Próxima</button>
    </div>

    <AgendarPostModal
      v-if="selectedImovel"
      :is-open="!!selectedImovel"
      :imovel="selectedImovel"
      @close="closeModal"
      @success="handleSuccess"
    />

    <HistoricoPublicacoesModal
      v-if="showHistoryModal"
      :imovel-id="selectedImovelIdForHistory"
      @close="closeHistoryModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
// IMPORTANTE: Atualize o import para o novo componente que criamos
import AgendarPostModal from '@/components/AgendarPostModal.vue';
import ImovelCard from "@/components/ImovelPublicCard.vue"; 
import HistoricoPublicacoesModal from '@/components/HistoricoPublicacoesModal.vue';
import '@fortawesome/fontawesome-free/css/all.css';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

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

const imoveis = ref<ImovelPublicacao[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Filtros
const searchTerm = ref('');
const statusFilter = ref('');
const publicationStatusFilter = ref('');
const isFiltersOpen = ref(true);

// Modais
const selectedImovel = ref<any | null>(null);
const showHistoryModal = ref(false);
const selectedImovelIdForHistory = ref<number | null>(null);

// Paginação
const currentPage = ref(1);
const itemsPerPage = ref(9);

// Métricas
const totalPublicado30d = ref(0);
const proximoAgendamento = ref<any | null>(null);

function formatarDataHora(dataIso: string | null): string {
  if (!dataIso) return 'N/A';
  try {
    return format(new Date(dataIso), 'dd/MM/yyyy HH:mm', { locale: ptBR });
  } catch {
    return 'Inválido';
  }
}

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const response = await apiClient.get<any[]>('/v1/imoveis/');
    imoveis.value = response.data.map((imovel: any) => ({
      ...imovel,
      // Lógica simples para frontend, idealmente viria do backend se tem post agendado
      isPublished: false 
    }));
  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis.';
  } finally {
    isLoading.value = false;
  }
}

const totalNaoPublicados = computed(() => imoveis.value.length);

const hasActiveFilters = computed(() => {
  return searchTerm.value !== '' || statusFilter.value !== '';
});

const filteredImoveis = computed(() => {
  let filtered = imoveis.value;

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase().trim();
    filtered = filtered.filter(imovel =>
      (imovel.titulo_anuncio?.toLowerCase().includes(term)) ||
      (imovel.codigo_referencia?.toLowerCase().includes(term))
    );
  }

  if (statusFilter.value) {
    filtered = filtered.filter(imovel => imovel.status === statusFilter.value);
  } else {
    filtered = filtered.filter(imovel => imovel.status !== 'DESATIVADO');
  }

  // Ordenar: mais recentes primeiro (assumindo id maior = mais recente)
  filtered.sort((a, b) => b.id - a.id);

  return filtered;
});

const totalPages = computed(() => Math.ceil(filteredImoveis.value.length / itemsPerPage.value));

const paginatedImoveis = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredImoveis.value.slice(start, start + itemsPerPage.value);
});

function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++; }
function prevPage() { if (currentPage.value > 1) currentPage.value--; }
function clearSearch() { searchTerm.value = ''; }
function resetFilters() { searchTerm.value = ''; statusFilter.value = ''; }
function toggleFilters() { isFiltersOpen.value = !isFiltersOpen.value; }

// --- Abertura do Modal ---
function openModal(imovel: any) {
  selectedImovel.value = imovel;
}

function closeModal() {
  selectedImovel.value = null;
}

function handleSuccess() {
  // Opcional: Atualizar lista ou mostrar toast
  console.log("Post agendado com sucesso!");
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
/* Mesmos estilos anteriores, mantidos para consistência */
:root { --primary-color: #007bff; --bg-light: #f8f9fa; }
.publicacoes-container { padding: 1.5rem; background-color: var(--bg-light); min-height: 100vh; }

.metrics-panel {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;
}
.metric-card {
  background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex; align-items: center; justify-content: space-between; border-left: 4px solid #007bff;
}
.metric-icon { font-size: 2rem; color: #e2e8f0; }
.metric-info { display: flex; flex-direction: column; }
.metric-info strong { font-size: 1.5rem; color: #1e293b; }

.filters-panel { background: #fff; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.filters-header { display: flex; justify-content: space-between; cursor: pointer; margin-bottom: 1rem; }
.search-input-wrapper { position: relative; margin-bottom: 1rem; }
.search-input-wrapper input { width: 100%; padding: 10px 40px; border: 1px solid #cbd5e1; border-radius: 8px; }
.search-icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #94a3b8; }

.imoveis-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }

.pagination-controls { display: flex; justify-content: center; gap: 1rem; margin-top: 2rem; align-items: center; }
.btn-secondary { padding: 8px 16px; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-message { text-align: center; padding: 3rem; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
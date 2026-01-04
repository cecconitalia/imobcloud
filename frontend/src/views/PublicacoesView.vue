<template>
  <div class="publicacoes-container">
    <div class="metrics-panel">
      <div class="metric-card bg-gradient-blue">
        <div class="metric-icon-wrapper">
          <i class="fas fa-home"></i>
        </div>
        <div class="metric-info">
          <span>Total</span>
          <strong>{{ imoveis.length }}</strong>
        </div>
      </div>
      <div class="metric-card bg-gradient-orange">
        <div class="metric-icon-wrapper">
          <i class="fas fa-bullhorn"></i>
        </div>
        <div class="metric-info">
          <span>Ocultos</span>
          <strong>{{ totalNaoPublicados }}</strong>
        </div>
      </div>
       <div class="metric-card bg-gradient-green">
        <div class="metric-icon-wrapper">
          <i class="fas fa-calendar-check"></i>
        </div>
         <div class="metric-info">
           <span>Agendado</span>
           <strong class="text-sm">{{ proximoAgendamento ? formatarDataHora(proximoAgendamento.data_agendada) : 'Nenhum' }}</strong>
        </div>
      </div>
       <div class="metric-card bg-gradient-purple">
         <div class="metric-icon-wrapper">
           <i class="fas fa-history"></i>
         </div>
         <div class="metric-info">
           <span>30 Dias</span>
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
        <button v-if="hasActiveFilters" @click.stop="resetFilters" class="btn-reset">
          <i class="fas fa-undo-alt"></i> Limpar
        </button>
      </div>

      <transition name="slide-fade">
        <div v-if="isFiltersOpen" class="filters-content">
          <div class="search-row">
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

          <div class="chips-row">
            <div class="chip-group">
              <span class="chip-label">Finalidade:</span>
              <div class="chip-options">
                <label :class="['chip', { 'chip-active': statusFilter === '' }]">
                  <input type="radio" v-model="statusFilter" value="" /> Todos
                </label>
                <label :class="['chip', { 'chip-active': statusFilter === 'A_VENDA' }]">
                  <input type="radio" v-model="statusFilter" value="A_VENDA" /> Venda
                </label>
                <label :class="['chip', { 'chip-active': statusFilter === 'PARA_ALUGAR' }]">
                  <input type="radio" v-model="statusFilter" value="PARA_ALUGAR" /> Aluguel
                </label>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <div v-if="error" class="error-banner">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ error }}</span>
      <button @click="fetchImoveis" class="btn-retry">Tentar Novamente</button>
    </div>

    <div v-if="isLoading" class="imoveis-list">
      <div v-for="n in 6" :key="n" class="skeleton-card">
        <div class="skeleton-image"></div>
        <div class="skeleton-content">
          <div class="skeleton-title"></div>
          <div class="skeleton-text"></div>
          <div class="skeleton-footer"></div>
        </div>
      </div>
    </div>

    <TransitionGroup 
      v-else-if="paginatedImoveis.length > 0" 
      name="list" 
      tag="div" 
      class="imoveis-list"
    >
      <ImovelCard
        v-for="imovel in paginatedImoveis"
        :key="imovel.id"
        :imovel="imovel"
      />
    </TransitionGroup>

    <div v-else-if="!isLoading && filteredImoveis.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-search"></i>
      </div>
      <h3>Nenhum imóvel encontrado</h3>
      <p>Tente ajustar seus filtros ou busca.</p>
      <button @click="resetFilters" class="btn-primary-outline">Limpar Filtros</button>
    </div>

    <div class="pagination-controls" v-if="totalPages > 1 && !isLoading">
      <button @click="prevPage" :disabled="currentPage === 1" class="btn-page">
        <i class="fas fa-chevron-left"></i> Anterior
      </button>
      <span class="page-info">Página <strong>{{ currentPage }}</strong> de {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">
        Próxima <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import ImovelCard from "@/components/ImovelPublicCard.vue"; 
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
const isFiltersOpen = ref(true);

// Paginação
const currentPage = ref(1);
const itemsPerPage = ref(9);

// Métricas Fictícias
const totalPublicado30d = ref(12); 
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
  error.value = null;
  setTimeout(async () => {
    try {
      const response = await apiClient.get<any[]>('/v1/imoveis/');
      imoveis.value = response.data.map((imovel: any) => ({
        ...imovel,
        isPublished: false 
      }));
    } catch (err) {
      console.error("Erro ao buscar imóveis:", err);
      error.value = 'Não foi possível carregar os imóveis.';
    } finally {
      isLoading.value = false;
    }
  }, 600);
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

  filtered.sort((a, b) => b.id - a.id);
  return filtered;
});

const totalPages = computed(() => Math.ceil(filteredImoveis.value.length / itemsPerPage.value));

const paginatedImoveis = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredImoveis.value.slice(start, start + itemsPerPage.value);
});

function nextPage() { if (currentPage.value < totalPages.value) currentPage.value++; window.scrollTo({top:0, behavior:'smooth'}); }
function prevPage() { if (currentPage.value > 1) currentPage.value--; window.scrollTo({top:0, behavior:'smooth'}); }
function clearSearch() { searchTerm.value = ''; }
function resetFilters() { searchTerm.value = ''; statusFilter.value = ''; currentPage.value = 1; }
function toggleFilters() { isFiltersOpen.value = !isFiltersOpen.value; }

onMounted(() => {
  fetchImoveis();
});
</script>

<style scoped>
:root { --primary-color: #3b82f6; --bg-light: #f8fafc; --text-dark: #1e293b; }
.publicacoes-container { padding: 1.5rem; background-color: var(--bg-light); min-height: 100vh; font-family: 'Inter', sans-serif; }

/* Métricas - Compactadas */
.metrics-panel {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;
}
.metric-card {
  background: #fff; padding: 1rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
  display: flex; align-items: center; gap: 0.8rem; border: 1px solid rgba(0,0,0,0.02);
  transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); }

.metric-icon-wrapper {
  width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}
.bg-gradient-blue .metric-icon-wrapper { background: linear-gradient(135deg, #e0f2fe, #bae6fd); color: #0284c7; }
.bg-gradient-orange .metric-icon-wrapper { background: linear-gradient(135deg, #ffedd5, #fed7aa); color: #ea580c; }
.bg-gradient-green .metric-icon-wrapper { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #16a34a; }
.bg-gradient-purple .metric-icon-wrapper { background: linear-gradient(135deg, #f3e8ff, #d8b4fe); color: #9333ea; }

.metric-info { display: flex; flex-direction: column; }
.metric-info span { font-size: 0.75rem; color: #64748b; font-weight: 500; }
.metric-info strong { font-size: 1.2rem; color: #1e293b; line-height: 1.1; }
.text-sm { font-size: 0.9rem !important; }

/* Filtros - Otimizado e Compacto */
.filters-panel { background: #fff; border-radius: 12px; margin-bottom: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.03); overflow: hidden; }
.filters-header { display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 1.25rem; cursor: pointer; background: #fff; border-bottom: 1px solid #f1f5f9; }
.filters-title { margin: 0; font-size: 1rem; color: #334155; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.btn-reset { color: #64748b; background: none; border: none; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; gap: 4px; }
.btn-reset:hover { color: #ef4444; }

.filters-content { padding: 1rem 1.25rem; background: #fcfcfc; }
.search-input-wrapper { position: relative; max-width: 100%; margin-bottom: 0.75rem; }
.search-input-wrapper input { 
  width: 100%; padding: 10px 40px; border: 1px solid #e2e8f0; border-radius: 8px; 
  font-size: 0.9rem; transition: all 0.2s; outline: none;
}
.search-input-wrapper input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.clear-btn { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #94a3b8; cursor: pointer; }

.chip-group { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; }
.chip-label { font-weight: 600; color: #475569; font-size: 0.85rem; }
.chip-options { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.chip { 
  padding: 5px 14px; border-radius: 20px; border: 1px solid #e2e8f0; background: #fff; 
  color: #64748b; cursor: pointer; font-size: 0.85rem; transition: all 0.2s; display: flex; align-items: center;
}
.chip input { display: none; }
.chip:hover { background: #f8fafc; border-color: #cbd5e1; }
.chip-active { background: #eff6ff; border-color: #3b82f6; color: #2563eb; font-weight: 600; }

/* Lista e Grid */
.imoveis-list { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
  gap: 1.5rem; 
}

/* Skeleton Loader */
.skeleton-card { background: #fff; border-radius: 16px; height: 400px; padding: 0; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.skeleton-image { height: 220px; background: #e2e8f0; animation: pulse 1.5s infinite; }
.skeleton-content { padding: 1.25rem; }
.skeleton-title { height: 24px; background: #e2e8f0; margin-bottom: 10px; width: 80%; border-radius: 4px; animation: pulse 1.5s infinite; }
.skeleton-text { height: 16px; background: #e2e8f0; margin-bottom: 20px; width: 60%; border-radius: 4px; animation: pulse 1.5s infinite; }
.skeleton-footer { height: 40px; background: #e2e8f0; margin-top: 30px; border-radius: 8px; animation: pulse 1.5s infinite; }

@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

/* Empty State */
.empty-state { text-align: center; padding: 3rem 1rem; color: #64748b; }
.empty-icon { font-size: 2.5rem; color: #cbd5e1; margin-bottom: 0.8rem; }
.btn-primary-outline { margin-top: 1rem; padding: 8px 20px; border: 1px solid #3b82f6; color: #3b82f6; background: transparent; border-radius: 8px; cursor: pointer; transition: 0.2s; }
.btn-primary-outline:hover { background: #eff6ff; }

/* Paginação */
.pagination-controls { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 2rem; padding-bottom: 1rem; }
.btn-page { padding: 8px 16px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; color: #475569; font-weight: 500; cursor: pointer; transition: 0.2s; display: flex; align-items: center; gap: 6px; font-size: 0.9rem; }
.btn-page:hover:not(:disabled) { border-color: #94a3b8; color: #1e293b; }
.btn-page:disabled { opacity: 0.5; cursor: not-allowed; }

/* Animações */
.list-enter-active, .list-leave-active { transition: all 0.4s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateY(20px); }
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }

.error-banner { background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c; padding: 0.8rem; border-radius: 8px; display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem; font-size: 0.9rem; }
.btn-retry { margin-left: auto; background: #fff; border: 1px solid #b91c1c; color: #b91c1c; padding: 2px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
</style>
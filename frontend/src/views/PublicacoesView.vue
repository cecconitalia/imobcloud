<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Marketing</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Publicações</span>
           </nav>
           
           <h1>Gerenciar Publicações</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-secondary-action" @click="goToCalendar" title="Ver Calendário de Agendamentos">
              <i class="fas fa-calendar-alt"></i> Ver Calendário
            </button>

            <button class="btn-icon-thin" @click="fetchImoveis" title="Atualizar Lista">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: statusFilter === '' }" @click="setQuickFilter('')">
        <div class="kpi-content">
          <span class="kpi-value">{{ imoveis.length }}</span>
          <span class="kpi-label">Total Imóveis</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-home"></i></div>
      </div>
      
      <div class="kpi-card orange" :class="{ active: statusFilter === 'DESATIVADO' }" @click="setQuickFilter('DESATIVADO')">
        <div class="kpi-content">
          <span class="kpi-value">{{ totalNaoPublicados }}</span>
          <span class="kpi-label">Não Publicados</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-eye-slash"></i></div>
      </div>
      
      <div class="kpi-card green" @click="goToCalendar" title="Ver no Calendário">
        <div class="kpi-content">
          <span class="kpi-value text-sm-kpi">{{ proximoAgendamento ? formatarDataHora(proximoAgendamento.data_agendada) : '-' }}</span>
          <span class="kpi-label">Próximo Agendamento</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-calendar-check"></i></div>
      </div>
      
      <div class="kpi-card purple" @click="goToCalendar" title="Ver Histórico no Calendário">
        <div class="kpi-content">
          <span class="kpi-value">{{ totalPublicado30d }}</span>
          <span class="kpi-label">Posts (30 dias)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-share-alt"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Título, código ou endereço..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Finalidade</label>
          <select v-model="statusFilter" class="form-control">
            <option value="">Todos</option>
            <option value="A_VENDA">Venda</option>
            <option value="PARA_ALUGAR">Aluguel</option>
            <option value="VENDIDO">Vendidos</option>
            <option value="ALUGADO">Alugados</option>
          </select>
        </div>

        <div class="filter-group small-btn">
            <label>&nbsp;</label>
            <button @click="resetFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="content-wrapper">
        <div v-if="isLoading" class="imoveis-grid">
            <div v-for="n in 6" :key="n" class="skeleton-card">
                <div class="skeleton-img"></div>
                <div class="skeleton-text"></div>
            </div>
        </div>

        <div v-else-if="filteredImoveis.length === 0" class="empty-state">
            <i class="fas fa-filter"></i>
            <p>Nenhum imóvel encontrado com estes filtros.</p>
        </div>

        <div v-else class="imoveis-grid">
            <div 
                v-for="imovel in paginatedImoveis" 
                :key="imovel.id" 
                class="standard-card clickable-card"
                @click="goToImovel(imovel.id)"
            >
                <div class="card-body">
                    <ImovelCard :imovel="imovel" />
                </div>
                
                <div class="card-footer-action">
                    <button 
                        @click.stop="openModal(imovel)" 
                        class="btn-action-full" 
                    >
                        <i class="fas fa-magic"></i> Gerar Post IA
                    </button>
                </div>
            </div>
        </div>

        <div class="pagination-controls" v-if="totalPages > 1 && !isLoading">
            <button @click="prevPage" :disabled="currentPage === 1" class="btn-page">
                <i class="fas fa-chevron-left"></i>
            </button>
            <span class="page-info">Página <strong>{{ currentPage }}</strong> de {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>
    </main>

    <AgendarPostModal 
      :isOpen="showModal" 
      :imovel="selectedImovel"
      @close="closeModal"
      @success="handleSuccess"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import ImovelCard from "@/components/ImovelPublicCard.vue"; 
import AgendarPostModal from "@/components/AgendarPostModal.vue";
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
    imagens?: any[];
}

const router = useRouter();
const imoveis = ref<ImovelPublicacao[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Filtros
const searchTerm = ref('');
const statusFilter = ref('');

// Paginação
const currentPage = ref(1);
const itemsPerPage = ref(8);

// Métricas
const totalPublicado30d = ref(12); 
const proximoAgendamento = ref<any | null>(null);

// Modal
const showModal = ref(false);
const selectedImovel = ref<ImovelPublicacao | null>(null);

// --- NAVEGAÇÃO ---
function goToCalendar() {
  router.push({ name: 'calendario-publicacoes' });
}

// CORREÇÃO: Função para navegar para os detalhes/edição do imóvel
function goToImovel(id: number) {
  router.push({ name: 'imovel-editar', params: { id } });
}

function openModal(imovel: ImovelPublicacao) {
    selectedImovel.value = imovel;
    showModal.value = true;
}

function closeModal() {
    showModal.value = false;
    selectedImovel.value = null;
}

function handleSuccess() {
    console.log("Post agendado!");
}

function formatarDataHora(dataIso: string | null): string {
  if (!dataIso) return '-';
  try {
    return format(new Date(dataIso), 'dd/MM HH:mm', { locale: ptBR });
  } catch { return '-'; }
}

async function fetchImoveis() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<any[]>('/v1/imoveis/');
    imoveis.value = response.data.map((imovel: any) => ({
      ...imovel,
      isPublished: false 
    }));
  } catch (err) {
    console.error("Erro:", err);
    error.value = 'Erro ao carregar dados.';
  } finally {
    isLoading.value = false;
  }
}

const totalNaoPublicados = computed(() => {
    return imoveis.value.filter(i => i.status === 'DESATIVADO' || i.status === 'RASCUNHO').length;
});

const setQuickFilter = (status: string) => {
    statusFilter.value = statusFilter.value === status ? '' : status;
};

const resetFilters = () => {
    searchTerm.value = '';
    statusFilter.value = '';
    currentPage.value = 1;
};

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
  }

  // Ordenação padrão
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

onMounted(() => { fetchImoveis(); });
</script>

<style scoped>
/* ==========================================================================
   LAYOUT PADRÃO
   ========================================================================== */

.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA */
.page-header { margin-bottom: 2rem; }

.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 {
  font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em;
}

.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;
}
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; align-items: center; }

/* Botão secundário */
.btn-secondary-action {
  background: white; border: 1px solid #cbd5e1; color: #475569;
  height: 34px; padding: 0 16px; border-radius: 6px;
  font-size: 0.85rem; font-weight: 500; cursor: pointer;
  display: flex; align-items: center; gap: 8px;
  transition: all 0.2s;
}
.btn-secondary-action:hover {
  border-color: #2563eb; color: #2563eb; background: #f8fafc;
}

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* KPIS (Cards Coloridos) */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: pointer; transition: all 0.2s;
  position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.text-sm-kpi { font-size: 1.1rem; font-weight: 600; color: #111; line-height: 1.4; } 
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

/* Cores KPI */
.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value { color: #2563eb; }

.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value, .kpi-card.green .text-sm-kpi { color: #059669; }

.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value { color: #d97706; }

.kpi-card.purple.active { background-color: #fcf5ff; border-color: #9333ea; }
.kpi-card.purple .kpi-value { color: #9333ea; }

/* TOOLBAR (Filtros) */
.toolbar-row {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}

.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 160px; }
.search-group { flex: 2; min-width: 260px; }
.small-btn { flex: 0 0 auto; min-width: auto; }

.filter-group label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }

.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }

.form-control {
  width: 100%; padding: 0.5rem 0.8rem; font-size: 0.85rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 38px; box-sizing: border-box; transition: all 0.2s;
}
.input-with-icon .form-control { padding-left: 2.2rem; }
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.btn-clear {
    width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc;
    border-radius: 6px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #fee2e2; color: #ef4444; border-color: #fca5a5; }

/* GRID DE CONTEÚDO */
.imoveis-grid {
    display: grid; 
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
    gap: 1.5rem;
}

.standard-card {
    background: white; border-radius: 8px; 
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    display: flex; flex-direction: column; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.standard-card:hover {
    transform: translateY(-3px); 
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
}

/* Novo estilo para cards clicáveis */
.clickable-card {
  cursor: pointer;
}

.card-body { flex: 1; }

.card-footer-action {
    padding: 10px 12px;
    background-color: #f8fafc;
    border-top: 1px solid #f1f5f9;
}

.btn-action-full {
    width: 100%;
    background-color: #2563eb; color: white;
    border: none; border-radius: 6px;
    padding: 8px; font-size: 0.85rem; font-weight: 500;
    cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;
    transition: background 0.2s;
}
.btn-action-full:hover { background-color: #1d4ed8; }

/* EMPTY STATE */
.empty-state {
    text-align: center; padding: 4rem; color: #94a3b8;
    background: white; border-radius: 8px; border: 1px dashed #e2e8f0;
}
.empty-state i { font-size: 2.5rem; margin-bottom: 1rem; color: #cbd5e1; }

/* PAGINAÇÃO */
.pagination-controls { 
    display: flex; justify-content: center; align-items: center; gap: 1rem; 
    margin-top: 2rem; padding-bottom: 1rem; 
}
.btn-page { 
    width: 36px; height: 36px; background: #fff; border: 1px solid #e2e8f0; 
    border-radius: 6px; color: #64748b; cursor: pointer; display: flex; 
    align-items: center; justify-content: center; transition: all 0.2s; 
}
.btn-page:hover:not(:disabled) { border-color: #94a3b8; color: #1e293b; }
.btn-page:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 0.85rem; color: #64748b; }

/* Skeleton */
.skeleton-card { background: #fff; border-radius: 8px; height: 350px; border: 1px solid #e2e8f0; overflow: hidden; }
.skeleton-img { height: 200px; background: #f1f5f9; animation: pulse 1.5s infinite; }
.skeleton-text { height: 20px; margin: 15px; width: 70%; background: #f1f5f9; animation: pulse 1.5s infinite; border-radius: 4px; }

@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .filter-group, .search-group { width: 100%; }
}
</style>
<template>
  <div class="report-view-root">
    
    <header class="view-header-section">
      <div class="header-row">
        <div class="title-group">
          <h1>Relatório de Autorizações</h1>
          <p class="subtitle">Controle de vigência e status das autorizações de venda/aluguel</p>
        </div>
        
        <div class="actions-group">
          <button class="btn-secondary btn-icon" @click="fetchAutorizacoes" title="Atualizar Dados">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
          </button>
          
          <button class="btn-primary" @click="generateGeneralReportPdf" :disabled="isGeneratingPdf">
            <i class="fas fa-print" :class="{ 'fa-spin': isGeneratingPdf }"></i>
            <span class="btn-label">{{ isGeneratingPdf ? 'Gerando PDF...' : 'Imprimir Relatório' }}</span>
          </button>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card blue" :class="{ active: filters.status === '' }" @click="setQuickFilter('')">
          <span class="kpi-label">Total Autorizações</span>
          <span class="kpi-value">{{ kpis.total }}</span>
        </div>
        <div class="kpi-card green" :class="{ active: filters.status === 'VIGENTE' }" @click="setQuickFilter('VIGENTE')">
          <span class="kpi-label">Vigentes</span>
          <span class="kpi-value">{{ kpis.vigentes }}</span>
        </div>
        <div class="kpi-card orange" :class="{ active: filters.status === 'A_VENCER' }" @click="setQuickFilter('A_VENCER')">
          <span class="kpi-label">A Vencer (30 dias)</span>
          <span class="kpi-value">{{ kpis.aVencer }}</span>
        </div>
        <div class="kpi-card red" :class="{ active: filters.status === 'VENCIDA' }" @click="setQuickFilter('VENCIDA')">
          <span class="kpi-label">Vencidas</span>
          <span class="kpi-value">{{ kpis.vencidas }}</span>
        </div>
      </div>

      <div class="toolbar-row">
        
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="Imóvel, proprietário..." 
              class="form-control"
              @input="filterList"
            >
          </div>
        </div>

        <div class="filter-group date-group">
          <label>Vencimento (De - Até)</label>
          <div class="date-inputs">
            <input type="date" v-model="filters.vencimentoInicio" @change="filterList" class="form-control">
            <span class="date-separator">a</span>
            <input type="date" v-model="filters.vencimentoFim" @change="filterList" class="form-control">
          </div>
        </div>

        <div class="filter-group">
          <label>Status</label>
          <select v-model="filters.status" @change="filterList" class="form-control">
            <option value="">Todos</option>
            <option value="VIGENTE">Vigentes</option>
            <option value="A_VENCER">A Vencer</option>
            <option value="VENCIDA">Vencidas</option>
          </select>
        </div>
        
        <div class="filter-group">
           <label>Tipo</label>
           <select v-model="filters.tipoNegocio" @change="filterList" class="form-control">
            <option value="">Todos</option>
            <option value="A_VENDA">Venda</option>
            <option value="PARA_ALUGAR">Aluguel</option>
          </select>
        </div>

        <div class="filter-group small-btn">
            <label>&nbsp;</label>
            <button @click="clearFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>

      </div>
    </header>

    <main class="report-main-wrapper">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando dados...</p>
      </div>

      <div v-else-if="filteredList.length === 0" class="empty-state">
        <i class="fas fa-folder-open"></i>
        <p>Nenhuma autorização encontrada para os filtros.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="10%">Imóvel</th>
              <th width="25%">Endereço / Título</th>
              <th width="20%">Proprietário</th>
              <th width="10%">Tipo</th>
              <th width="10%">Início</th>
              <th width="10%">Vencimento</th>
              <th width="5%" class="text-center">Dias</th>
              <th width="5%">Status</th>
              <th width="5%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredList" :key="item.id">
              <td>
                <span class="imovel-code">#{{ item.codigo }}</span>
              </td>
              
              <td>
                <span class="imovel-addr" :title="item.endereco">
                    {{ item.endereco }}
                </span>
              </td>

              <td>
                  <span class="prop-name">{{ item.proprietario }}</span>
              </td>

              <td>
                <span class="badge-type" :class="item.raw_status === 'A_VENDA' ? 'bg-blue' : 'bg-green'">
                    {{ item.raw_status === 'A_VENDA' ? 'Venda' : 'Aluguel' }}
                </span>
              </td>

              <td class="text-muted">{{ formatDate(item.data_inicio) }}</td>
              <td><strong>{{ formatDate(item.data_fim) }}</strong></td>
              
              <td class="text-center">
                  <span :class="getDaysClass(item.dias_restantes)">
                      {{ item.dias_restantes === 9999 ? '∞' : item.dias_restantes }}
                  </span>
              </td>

              <td>
                <span :class="['status-pill', getStatusClass(item)]">
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td class="text-right">
                <div class="actions-flex">
                    <button class="btn-action edit" @click="editAutorizacao(item.id)" title="Editar Imóvel">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action pdf" @click="downloadIndividualPdf(item.id)" title="Baixar PDF Individual">
                        <i class="fas fa-file-pdf"></i>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { format, parseISO, isAfter, isBefore, addDays, startOfDay, endOfDay } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const router = useRouter();

interface Autorizacao {
  id: number;
  codigo: string;
  endereco: string;
  proprietario: string;
  raw_status: string;
  data_inicio: string;
  data_fim: string | null;
  dias_restantes: number;
}

const rawList = ref<Autorizacao[]>([]);
const filteredList = ref<Autorizacao[]>([]);
const isLoading = ref(true);
const isGeneratingPdf = ref(false);

const filters = ref({
  search: '',
  status: '',
  tipoNegocio: '',
  vencimentoInicio: '',
  vencimentoFim: ''
});

// KPIs com lógica de frontend para reatividade instantânea
const kpis = computed(() => {
  const total = rawList.value.length;
  let vigentes = 0, vencidas = 0, aVencer = 0;

  rawList.value.forEach(item => {
    // 9999 é o código do backend para 'sem data'
    if (item.dias_restantes === 9999 || item.dias_restantes >= 0) {
        vigentes++;
        if (item.dias_restantes >= 0 && item.dias_restantes <= 30) {
            aVencer++;
        }
    } else {
        vencidas++;
    }
  });
  return { total, vigentes, vencidas, aVencer };
});

const fetchAutorizacoes = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('/v1/imoveis/relatorio/autorizacoes/'); 
    
    // =====================================================================
    // CORREÇÃO CRÍTICA DO MAPEAMENTO DE DADOS (Frontend <-> Backend)
    // =====================================================================
    rawList.value = response.data.map((item: any) => ({
      id: item.id || 0,
      
      // 1. Backend manda 'codigo_referencia', Frontend exibe 'codigo'
      codigo: item.codigo_referencia || item.codigo || '?',
      
      // 2. Backend manda 'titulo_anuncio' ou 'endereco_completo', Frontend exibe 'endereco'
      endereco: item.titulo_anuncio || item.endereco_completo || item.endereco_resumido || 'Endereço não informado',
      
      // 3. Backend manda 'proprietario_nome', Frontend exibe 'proprietario'
      proprietario: item.proprietario_nome || item.proprietario || 'N/A',
      
      // 4. Status para cor
      raw_status: item.raw_status || (item.finalidade === 'Venda' ? 'A_VENDA' : 'PARA_ALUGAR'),
      
      // 5. Datas (backend manda 'data_captacao' e 'data_fim_autorizacao')
      data_inicio: item.data_captacao || item.data_inicio, 
      data_fim: item.data_fim_autorizacao || item.data_fim,
      
      // 6. Dias
      dias_restantes: (item.dias_restantes !== undefined && item.dias_restantes !== null) ? item.dias_restantes : 9999
    }));
    
    filterList();
  } catch (error) {
    console.error("Erro ao buscar dados:", error);
  } finally {
    isLoading.value = false;
  }
};

const setQuickFilter = (statusValue: string) => {
    filters.value.status = (filters.value.status === statusValue) ? '' : statusValue;
    filterList();
};

const clearFilters = () => {
    filters.value = { search: '', status: '', tipoNegocio: '', vencimentoInicio: '', vencimentoFim: '' };
    filterList();
}

const filterList = () => {
  let temp = rawList.value;
  const searchLower = filters.value.search.toLowerCase();

  if (filters.value.search) {
    temp = temp.filter(item => 
      item.codigo.toString().toLowerCase().includes(searchLower) ||
      item.endereco.toLowerCase().includes(searchLower) ||
      item.proprietario.toLowerCase().includes(searchLower)
    );
  }

  if (filters.value.tipoNegocio) {
    temp = temp.filter(item => item.raw_status === filters.value.tipoNegocio);
  }

  // Lógica de Filtro baseada em Dias Restantes
  if (filters.value.status) {
    temp = temp.filter(item => {
        if (filters.value.status === 'VENCIDA') return item.dias_restantes < 0 && item.dias_restantes !== 9999;
        if (filters.value.status === 'A_VENCER') return item.dias_restantes >= 0 && item.dias_restantes <= 30;
        if (filters.value.status === 'VIGENTE') return item.dias_restantes >= 0 || item.dias_restantes === 9999;
        return true;
    });
  }

  if (filters.value.vencimentoInicio) {
      const inicio = parseISO(filters.value.vencimentoInicio);
      temp = temp.filter(item => item.data_fim && (isAfter(parseISO(item.data_fim), startOfDay(inicio)) || parseISO(item.data_fim).getTime() === startOfDay(inicio).getTime()));
  }
  if (filters.value.vencimentoFim) {
      const fimRange = parseISO(filters.value.vencimentoFim);
      temp = temp.filter(item => item.data_fim && (isBefore(parseISO(item.data_fim), endOfDay(fimRange)) || parseISO(item.data_fim).getTime() === endOfDay(fimRange).getTime()));
  }

  filteredList.value = temp;
};

const formatDate = (dateString: string | null) => {
  if (!dateString) return '-';
  try { return format(parseISO(dateString), 'dd/MM/yy', { locale: ptBR }); } catch { return '-'; }
};

const getStatusLabel = (item: Autorizacao) => {
    if (item.dias_restantes === 9999) return 'Vigente';
    if (item.dias_restantes < 0) return 'Vencida';
    if (item.dias_restantes <= 30) return 'A Vencer';
    return 'Vigente';
};

const getStatusClass = (item: Autorizacao) => {
    if (item.dias_restantes < 0 && item.dias_restantes !== 9999) return 'status-red';
    if (item.dias_restantes >= 0 && item.dias_restantes <= 30) return 'status-orange';
    return 'status-green';
};

const getDaysClass = (days: number) => {
    if (days === 9999) return 'text-muted font-bold';
    if (days < 0) return 'text-red font-bold';
    if (days <= 30) return 'text-orange font-bold';
    return 'text-green font-bold';
}

const editAutorizacao = (id: number) => router.push({ name: 'imovel-editar', params: { id } });

const downloadIndividualPdf = async (id: number) => {
    try {
        const response = await api.get(`/v1/imoveis/${id}/gerar-autorizacao-pdf/`, { responseType: 'blob' });
        window.open(window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' })), '_blank');
    } catch { alert("Erro ao gerar PDF."); }
};

const generateGeneralReportPdf = async () => {
    isGeneratingPdf.value = true;
    try {
        const params = {
            search: filters.value.search,
            status_vigencia: filters.value.status,
            tipo_negocio: filters.value.tipoNegocio,
            vencimento_de: filters.value.vencimentoInicio,
            vencimento_ate: filters.value.vencimentoFim
        };
        const response = await api.get('/v1/imoveis/relatorio-geral-autorizacoes/', { params, responseType: 'blob' });
        window.open(window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' })), '_blank');
    } catch { alert("Não foi possível gerar o relatório PDF."); } 
    finally { isGeneratingPdf.value = false; }
};

onMounted(fetchAutorizacoes);
</script>

<style scoped>
/* ================================================== */
/* 1. Layout Geral */
/* ================================================== */
.report-view-root {
  height: calc(100vh - 120px); 
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  gap: 1rem;
  font-family: 'Inter', sans-serif;
  color: #334155;
}

/* ================================================== */
/* 2. Header & Stats */
/* ================================================== */
.view-header-section {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header-row { display: flex; justify-content: space-between; align-items: flex-end; }
.title-group h1 { font-size: 1.5rem; font-weight: 700; color: #1e293b; margin: 0; }
.subtitle { font-size: 0.875rem; color: #64748b; margin: 0.25rem 0 0 0; }

.actions-group { display: flex; gap: 0.5rem; }
.btn-primary {
  background: #2563eb; color: white; border: none; padding: 0.6rem 1.2rem;
  border-radius: 8px; font-weight: 600; font-size: 0.9rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; transition: background 0.2s; white-space: nowrap;
}
.btn-primary:hover { background: #1d4ed8; }
.btn-secondary {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 40px; height: 40px;
  border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.btn-secondary:hover { background: #f8fafc; color: #2563eb; border-color: #cbd5e1; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.kpi-card {
  background: white; border-radius: 10px; padding: 0.8rem 1rem; border: 1px solid #e2e8f0;
  display: flex; flex-direction: column; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  cursor: pointer; transition: all 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); border-color: #cbd5e1; }
.kpi-card.active { border-width: 2px; background-color: #f8fafc; }
.kpi-card.blue.active { border-color: #2563eb; }
.kpi-card.green.active { border-color: #16a34a; }
.kpi-card.orange.active { border-color: #f97316; }
.kpi-card.red.active { border-color: #ef4444; }

.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #64748b; margin-bottom: 2px; }
.kpi-value { font-size: 1.25rem; font-weight: 700; color: #0f172a; }
.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.green .kpi-value { color: #16a34a; }
.kpi-card.orange .kpi-value { color: #f97316; }
.kpi-card.red .kpi-value { color: #ef4444; }

/* ================================================== */
/* 3. Toolbar */
/* ================================================== */
.toolbar-row {
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 1.25rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end; /* Alinha inputs pela base */
  position: relative;
  z-index: 10; /* Garante que dropdowns fiquem por cima */
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
  min-width: 140px;
}

.search-group { flex: 2; min-width: 250px; }
.date-group { flex: 2; min-width: 250px; }
.small-btn { flex: 0 0 auto; min-width: auto; }

.filter-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.input-with-icon { position: relative; width: 100%; }
.input-with-icon i {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  color: #9ca3af; font-size: 0.9rem;
}

/* Estilo unificado para inputs e selects */
.form-control {
  width: 100%;
  padding: 0.6rem 0.8rem;
  font-size: 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background-color: #fff;
  color: #374151;
  outline: none;
  height: 40px; /* Altura fixa para alinhamento */
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-with-icon .form-control { padding-left: 2.2rem; }

.form-control:focus {
  border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.date-inputs {
  display: flex; align-items: center; gap: 0.5rem;
}
.date-separator { font-size: 0.8rem; color: #94a3b8; }

.btn-clear {
    width: 40px; height: 40px; border: 1px solid #d1d5db; background: #fff;
    border-radius: 8px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #f1f5f9; color: #ef4444; border-color: #cbd5e1; }

/* ================================================== */
/* 4. Tabela & Scroll */
/* ================================================== */
.report-main-wrapper {
  flex: 1; position: relative; width: 100%; min-height: 0; overflow: hidden;
  background: white; border-radius: 10px; border: 1px solid #e2e8f0;
  display: flex; flex-direction: column;
}

.report-scroll-viewport { width: 100%; height: 100%; overflow: auto; }
.report-scroll-viewport::-webkit-scrollbar { width: 8px; height: 8px; }
.report-scroll-viewport::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }

.report-table { width: 100%; border-collapse: collapse; min-width: 800px; }
.report-table th {
  position: sticky; top: 0; background: #f8fafc; z-index: 5;
  padding: 0.8rem 1rem; text-align: left; font-size: 0.75rem; font-weight: 700;
  color: #64748b; text-transform: uppercase; border-bottom: 1px solid #e2e8f0;
}
.report-table td {
  padding: 0.8rem 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem;
  color: #334155; vertical-align: middle;
}
.report-table tr:hover { background-color: #f8fafc; }

.cell-imovel { display: flex; flex-direction: column; gap: 2px; }
.imovel-code { font-weight: 700; font-size: 0.75rem; color: #2563eb; }
.imovel-addr { font-size: 0.8rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px; }
.prop-name { font-weight: 600; color: #1e293b; }

.badge-type {
  font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;
}
.bg-blue { background: #eff6ff; color: #1e40af; }
.bg-green { background: #f0fdf4; color: #166534; }

.status-pill {
  display: inline-block; padding: 2px 10px; border-radius: 99px;
  font-size: 0.75rem; font-weight: 600; text-align: center;
}
.status-green { background: #dcfce7; color: #166534; }
.status-orange { background: #ffedd5; color: #9a3412; }
.status-red { background: #fee2e2; color: #991b1b; }

.text-right { text-align: right; }
.text-center { text-align: center; }
.text-muted { color: #94a3b8; }
.text-red { color: #dc2626; }
.text-orange { color: #d97706; }
.text-green { color: #16a34a; }
.font-bold { font-weight: 700; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  background: none; border: none; cursor: pointer; width: 32px; height: 32px;
  border-radius: 6px; transition: all 0.2s; display: flex; align-items: center; justify-content: center;
}
.btn-action.edit { color: #2563eb; background-color: #eff6ff; }
.btn-action.edit:hover { background-color: #dbeafe; }
.btn-action.pdf { color: #ef4444; background-color: #fef2f2; }
.btn-action.pdf:hover { background-color: #fee2e2; }

.loading-state, .empty-state {
  height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; gap: 1rem;
}
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.empty-state i { font-size: 3rem; opacity: 0.5; }

/* Mobile */
@media (max-width: 1024px) {
  .toolbar-row { flex-direction: column; align-items: stretch; gap: 0.8rem; }
  .filter-group, .search-group, .date-group { width: 100%; min-width: auto; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .report-main-wrapper { height: 600px; }
}
</style>
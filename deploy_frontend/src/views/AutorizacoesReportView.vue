<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Relatórios</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Autorizações</span>
           </nav>
           
           <h1>Relatório de Autorizações</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchAutorizacoes" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <button class="btn-primary-thin" @click="generateGeneralReportPdf" :disabled="isGeneratingPdf">
              <i class="fas fa-print" :class="{ 'fa-spin': isGeneratingPdf }"></i>
              {{ isGeneratingPdf ? 'Gerando...' : 'Imprimir Relatório' }}
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: filters.status === '' }" @click="setQuickFilter('')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.total }}</span>
          <span class="kpi-label">Total Autorizações</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-file-contract"></i></div>
      </div>

      <div class="kpi-card green" :class="{ active: filters.status === 'VIGENTE' }" @click="setQuickFilter('VIGENTE')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.vigentes }}</span>
          <span class="kpi-label">Vigentes</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-check-circle"></i></div>
      </div>

      <div class="kpi-card orange" :class="{ active: filters.status === 'A_VENCER' }" @click="setQuickFilter('A_VENCER')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.aVencer }}</span>
          <span class="kpi-label">A Vencer (30 dias)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-exclamation-circle"></i></div>
      </div>

      <div class="kpi-card red" :class="{ active: filters.status === 'VENCIDA' }" @click="setQuickFilter('VENCIDA')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.vencidas }}</span>
          <span class="kpi-label">Vencidas</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-times-circle"></i></div>
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
              placeholder="Ref, imóvel ou proprietário..." 
              class="form-control"
              @input="filterList"
            >
          </div>
        </div>

        <div class="filter-group" style="min-width: 240px;">
          <label>Vencimento (De - Até)</label>
          <div class="date-group-row">
            <input type="date" v-model="filters.vencimentoInicio" @change="filterList" class="form-control">
            <span class="date-sep">-</span>
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

    <main class="report-main-wrapper">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando dados...</p>
      </div>

      <div v-else-if="filteredList.length === 0" class="empty-state">
        <i class="fas fa-folder-open empty-icon"></i>
        <p>Nenhuma autorização encontrada para os filtros.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="8%">Ref.</th>
              <th width="25%">Imóvel / Endereço</th>
              <th width="20%">Proprietário</th>
              <th width="10%">Tipo</th>
              <th width="10%">Início</th>
              <th width="10%">Vencimento</th>
              <th width="7%" class="text-center">Dias</th>
              <th width="10%" class="text-center">Status</th>
              <th width="10%" class="text-right">Ações</th>
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

              <td class="text-center">
                <span :class="['status-pill', getStatusClass(item)]">
                  {{ getStatusLabel(item) }}
                </span>
              </td>

              <td class="text-right">
                <div class="actions-flex">
                    <button class="btn-action edit" @click="editAutorizacao(item.id)" title="Editar Imóvel">
                        <i class="fas fa-pen"></i>
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
import { format, parseISO, isAfter, isBefore, startOfDay, endOfDay } from 'date-fns';
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

// KPIs com lógica de frontend
const kpis = computed(() => {
  const total = rawList.value.length;
  let vigentes = 0, vencidas = 0, aVencer = 0;

  rawList.value.forEach(item => {
    // 9999 é o código para 'sem data de fim' (indeterminado)
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
    
    rawList.value = response.data.map((item: any) => ({
      id: item.id || 0,
      codigo: item.codigo_referencia || item.codigo || '?',
      endereco: item.titulo_anuncio || item.endereco_completo || item.endereco_resumido || 'Endereço não informado',
      proprietario: item.proprietario_nome || item.proprietario || 'N/A',
      raw_status: item.raw_status || (item.finalidade === 'Venda' ? 'A_VENDA' : 'PARA_ALUGAR'),
      data_inicio: item.data_captacao || item.data_inicio, 
      data_fim: item.data_fim_autorizacao || item.data_fim,
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
/* CONFIGURAÇÃO GERAL (PADRONIZADO) */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA (PADRONIZADO) */
.page-header { margin-bottom: 2rem; }
.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Fino (PADRONIZADO) */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer; text-decoration: none;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15);
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* KPI GRID (PADRONIZADO) */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; position: relative; overflow: hidden;
  cursor: pointer;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }

.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }

.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }

.kpi-card.red.active { background-color: #fef2f2; border-color: #ef4444; }
.kpi-card.red .kpi-value, .kpi-card.red .kpi-icon { color: #ef4444; }

/* TOOLBAR (PADRONIZADO) */
.toolbar-row {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 1rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
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

.date-group-row { display: flex; align-items: center; gap: 0.5rem; }
.date-sep { color: #94a3b8; }

.btn-clear {
    width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc;
    border-radius: 6px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #fee2e2; color: #ef4444; border-color: #fca5a5; }

/* TABELA E LAYOUT */
.report-main-wrapper {
  background: white; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  display: flex; flex-direction: column; overflow: hidden;
}
.report-scroll-viewport { width: 100%; overflow-x: auto; }

.report-table { width: 100%; border-collapse: collapse; min-width: 900px; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid #e2e8f0;
}
.report-table td {
  padding: 0.8rem 1.2rem; border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem; color: #334155; vertical-align: middle;
}
.report-table tr:hover { background-color: #fcfcfc; }

.imovel-code { font-weight: 700; font-size: 0.75rem; color: #64748b; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
.imovel-addr { font-size: 0.85rem; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 280px; display: block; }
.prop-name { font-weight: 600; color: #1e293b; font-size: 0.85rem; }

.badge-type {
  font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;
}
.bg-blue { background: #eff6ff; color: #1d4ed8; }
.bg-green { background: #f0fdf4; color: #15803d; }

.status-pill {
  display: inline-block; padding: 2px 10px; border-radius: 99px;
  font-size: 0.7rem; font-weight: 600; text-align: center; text-transform: uppercase;
}
.status-green { background: #dcfce7; color: #15803d; }
.status-orange { background: #fffbeb; color: #b45309; }
.status-red { background: #fef2f2; color: #ef4444; }

.text-right { text-align: right; }
.text-center { text-align: center; }
.text-muted { color: #94a3b8; }
.text-red { color: #ef4444; }
.text-orange { color: #d97706; }
.text-green { color: #15803d; }
.font-bold { font-weight: 700; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-action.edit { background-color: #eff6ff; color: #2563eb; }
.btn-action.edit:hover { background-color: #2563eb; color: #fff; }
.btn-action.pdf { background-color: #fff1f2; color: #e11d48; }
.btn-action.pdf:hover { background-color: #e11d48; color: #fff; }

.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.empty-icon { font-size: 2.5rem; color: #e2e8f0; margin-bottom: 1rem; }
.spinner {
  border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%;
  width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .filter-group, .search-group { width: 100%; }
}
</style>
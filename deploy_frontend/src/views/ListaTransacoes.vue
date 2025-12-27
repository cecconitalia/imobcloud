<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Financeiro</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Transações</span>
           </nav>
           
           <h1>Extrato de Transações</h1>
        </div>
        
        <div class="actions-area">
            <div class="quick-actions">
                <button @click="setQuickFilter('currentMonth')" class="btn-text" title="Este Mês">Mês Atual</button>
                <span class="divider">|</span>
                <button @click="setQuickFilter('lastMonth')" class="btn-text" title="Mês Passado">Mês Anterior</button>
            </div>

            <button class="btn-icon-thin" @click="fetchData" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <router-link :to="{ name: 'transacao-nova' }" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Nova Transação
            </router-link>
        </div>
      </div>
    </header>

    <div class="kpi-grid" v-if="stats">
      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.saldo_atual) }}</span>
          <span class="kpi-label">Saldo em Caixa</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-wallet"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.receitas_mes) }}</span>
          <span class="kpi-label">Receitas (Mês)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-arrow-up"></i></div>
      </div>

      <div class="kpi-card red">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.despesas_mes) }}</span>
          <span class="kpi-label">Despesas (Mês)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-arrow-down"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.resultado_mes) }}</span>
          <span class="kpi-label">Resultado (Mês)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell search-cell">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="Descrição, categoria, valor..." 
              class="form-control"
              @keyup.enter="fetchData"
            >
          </div>
        </div>

        <div class="filter-cell" style="min-width: 240px;">
          <label>Período (De - Até)</label>
          <div class="date-group-row">
            <input type="date" v-model="filters.data_inicio" @change="fetchData" class="form-control">
            <span class="date-sep">-</span>
            <input type="date" v-model="filters.data_fim" @change="fetchData" class="form-control">
          </div>
        </div>

        <div class="filter-cell">
          <label>Tipo</label>
          <select v-model="filters.tipo" @change="fetchData" class="form-control">
            <option value="">Todos</option>
            <option value="RECEITA">Receitas</option>
            <option value="DESPESA">Despesas</option>
          </select>
        </div>

        <div class="filter-cell">
          <label>Status</label>
          <select v-model="filters.status" @change="fetchData" class="form-control">
            <option value="">Todos</option>
            <option value="PAGO">Pago / Recebido</option>
            <option value="PENDENTE">Pendente</option>
            <option value="ATRASADO">Atrasado</option>
          </select>
        </div>

        <div class="filter-cell clear-cell">
            <label>&nbsp;</label>
            <button @click="resetFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="report-main-wrapper">
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando transações...</p>
      </div>

      <div v-else-if="error" class="empty-state">
        <i class="fas fa-exclamation-triangle empty-icon text-red"></i>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="transacoes.length === 0" class="empty-state">
        <i class="fas fa-folder-open empty-icon"></i>
        <p>Nenhuma transação encontrada com os filtros atuais.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="10%">Data</th>
              <th width="8%" class="text-center">Tipo</th>
              <th width="25%">Descrição / Categoria</th>
              <th width="20%">Conta / Forma</th>
              <th width="15%" class="text-right">Valor</th>
              <th width="10%" class="text-center">Status</th>
              <th width="12%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in transacoes" :key="item.id">
              <td>
                 <div class="date-cell">
                    <span class="date-day">{{ formatarData(item.data_pagamento || item.data_vencimento).split('/')[0] }}</span>
                    <span class="date-month">{{ formatarData(item.data_pagamento || item.data_vencimento).substring(3) }}</span>
                 </div>
              </td>
              
              <td class="text-center">
                  <span class="type-badge" :class="item.tipo === 'RECEITA' ? 'type-in' : 'type-out'">
                      <i :class="item.tipo === 'RECEITA' ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
                  </span>
              </td>

              <td>
                  <div class="desc-col">
                      <span class="desc-main" :title="item.descricao">{{ item.descricao }}</span>
                      <span class="desc-sub">
                          <i class="fas fa-tag"></i> {{ item.categoria_nome || 'Sem categoria' }}
                      </span>
                  </div>
              </td>

              <td>
                  <div class="desc-col">
                      <span class="info-text">{{ item.conta_nome || '-' }}</span>
                      <span class="info-sub">{{ item.forma_pagamento_nome || '-' }}</span>
                  </div>
              </td>

              <td class="text-right font-bold" :class="item.tipo === 'RECEITA' ? 'text-success' : 'text-danger'">
                  {{ item.tipo === 'DESPESA' ? '- ' : '' }}{{ formatarValor(item.valor) }}
              </td>

              <td class="text-center">
                <span :class="['status-pill', getStatusClass(item.status)]">
                  {{ formatStatus(item.status) }}
                </span>
              </td>

              <td class="text-right">
                <div class="actions-flex">
                    <router-link :to="{ name: 'transacao-editar', params: { id: item.id } }" class="btn-action primary" title="Editar">
                        <i class="fas fa-pen"></i>
                    </router-link>
                    <button @click="handleDelete(item.id)" class="btn-action danger" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="table-footer" v-if="totalCount > transacoes.length">
         <span class="footer-info">Exibindo {{ transacoes.length }} de {{ totalCount }} registros. Utilize os filtros para ver mais.</span>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import apiClient from '@/services/api';
import { format, startOfMonth, endOfMonth, subMonths } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useToast } from 'vue-toast-notification';

// --- Interfaces ---
interface Transacao {
    id: number;
    tipo: 'RECEITA' | 'DESPESA';
    descricao: string;
    valor: number;
    data_vencimento: string;
    data_pagamento?: string;
    status: string;
    categoria_nome?: string;
    conta_nome?: string;
    forma_pagamento_nome?: string;
}

interface StatsFinanceiro {
    saldo_atual: number;
    receitas_mes: number;
    despesas_mes: number;
    resultado_mes: number;
}

interface Filters {
    search: string;
    data_inicio: string;
    data_fim: string;
    tipo: string;
    status: string;
}

// --- State ---
const transacoes = ref<Transacao[]>([]);
const stats = ref<StatsFinanceiro | null>(null);
const totalCount = ref(0);
const isLoading = ref(true);
const error = ref<string | null>(null);
const toast = useToast();

const filters = ref<Filters>({
    search: '',
    data_inicio: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
    data_fim: format(endOfMonth(new Date()), 'yyyy-MM-dd'),
    tipo: '',
    status: ''
});

// --- Formatters ---
const formatarValor = (valor: number | null | undefined): string => {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatarData = (data: string | null | undefined): string => {
    if (!data) return '--/--';
    try {
        return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
    } catch { return 'Data Inválida'; }
};

const formatStatus = (status: string) => {
    switch (status) {
        case 'PAGO': return 'Pago';
        case 'PENDENTE': return 'Pendente';
        case 'ATRASADO': return 'Atrasado';
        default: return status;
    }
};

const getStatusClass = (status: string): string => {
  switch (status) {
    case 'PENDENTE': return 'status-orange';
    case 'ATRASADO': return 'status-red';
    case 'PAGO': return 'status-green';
    default: return 'status-gray';
  }
};

// --- Actions ---
const setQuickFilter = (period: 'currentMonth' | 'lastMonth') => {
    const today = new Date();
    let startDate, endDate;

    if (period === 'currentMonth') {
        startDate = startOfMonth(today);
        endDate = endOfMonth(today);
    } else {
        const lastMonth = subMonths(today, 1);
        startDate = startOfMonth(lastMonth);
        endDate = endOfMonth(lastMonth);
    }

    filters.value.data_inicio = format(startDate, 'yyyy-MM-dd');
    filters.value.data_fim = format(endDate, 'yyyy-MM-dd');
    fetchData();
};

const resetFilters = () => {
    filters.value.search = '';
    filters.value.tipo = '';
    filters.value.status = '';
    setQuickFilter('currentMonth');
};

const fetchData = async () => {
    isLoading.value = true;
    error.value = null;
    try {
        // 1. Stats
        const statsRes = await apiClient.get('/v1/financeiro/transacoes/stats/');
        stats.value = statsRes.data;

        // 2. Lista
        const params: any = { ...filters.value };
        // Mapear filtros de data para os nomes esperados pelo backend se necessário
        // (Assumindo que o backend aceita data_inicio/data_fim ou similar)
        
        const response = await apiClient.get('/v1/financeiro/transacoes/', { params });
        const results = response.data.results || response.data;
        transacoes.value = results;
        totalCount.value = response.data.count || results.length;

    } catch (err) {
        console.error(err);
        error.value = "Erro ao carregar transações.";
    } finally {
        isLoading.value = false;
    }
};

const handleDelete = async (id: number) => {
    if(!confirm("Tem certeza que deseja excluir esta transação?")) return;
    try {
        await apiClient.delete(`/v1/financeiro/transacoes/${id}/`);
        toast.success("Transação excluída.");
        fetchData();
    } catch (err) {
        toast.error("Erro ao excluir transação.");
    }
};

onMounted(() => {
    fetchData();
});
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (Page Scroll) */
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  box-sizing: border-box;
}

/* HEADER */
.page-header { margin-bottom: 2rem; flex-shrink: 0; }
.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; align-items: center; }

/* Botões */
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

/* Atalhos */
.quick-actions { display: flex; align-items: center; gap: 8px; margin-right: 8px; font-size: 0.8rem; color: #64748b; }
.btn-text { background: none; border: none; color: #64748b; cursor: pointer; font-weight: 500; padding: 0; }
.btn-text:hover { color: #2563eb; text-decoration: underline; }
.divider { color: #e2e8f0; }

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(4, 1fr); 
    gap: 1.25rem; margin-bottom: 2rem; flex-shrink: 0;
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }
.kpi-card.red .kpi-value, .kpi-card.red .kpi-icon { color: #ef4444; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR */
.toolbar-grid {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: grid; grid-template-columns: 2fr 2fr 1fr 1fr auto; 
  gap: 1rem; align-items: end; margin-bottom: 1.5rem; flex-shrink: 0;
}

.filter-cell { display: flex; flex-direction: column; gap: 0.3rem; }
.search-cell { grid-column: span 1; } 
.clear-cell { justify-self: start; }

.filter-cell label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }

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
  /* Layout que permite scroll da página */
  width: 100%;
  background: white; border-radius: 8px; border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  display: flex; flex-direction: column;
}

.report-scroll-viewport { 
    width: 100%; overflow-x: auto; /* Apenas scroll horizontal */
    scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent;
}
.report-scroll-viewport::-webkit-scrollbar { width: 8px; height: 8px; }
.report-scroll-viewport::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 4px; border: 2px solid white; }

.report-table { width: 100%; border-collapse: collapse; min-width: 900px; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left; 
  position: sticky; top: 0; z-index: 10;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.report-table td {
  padding: 0.75rem 1.2rem; border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem; color: #334155; vertical-align: middle;
}
.report-table tr:hover { background-color: #fcfcfc; }

/* Elementos da Tabela */
.date-cell { display: flex; flex-direction: column; line-height: 1.1; }
.date-day { font-weight: 700; color: #334155; font-size: 0.95rem; }
.date-month { font-size: 0.7rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }

.type-badge {
    width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
}
.type-in { background-color: #dcfce7; color: #15803d; }
.type-out { background-color: #fee2e2; color: #ef4444; }

.desc-col { display: flex; flex-direction: column; gap: 2px; }
.desc-main { font-weight: 500; color: #334155; }
.desc-sub, .info-sub { font-size: 0.75rem; color: #94a3b8; }
.info-text { font-size: 0.85rem; color: #475569; }

.status-pill {
  display: inline-block; padding: 2px 10px; border-radius: 99px;
  font-size: 0.7rem; font-weight: 600; text-align: center; text-transform: uppercase;
}
.status-green { background: #dcfce7; color: #15803d; }
.status-orange { background: #fffbeb; color: #b45309; }
.status-red { background: #fef2f2; color: #ef4444; }
.status-gray { background: #f1f5f9; color: #64748b; }

.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-action.success { background-color: #dcfce7; color: #15803d; }
.btn-action.danger { background-color: #fee2e2; color: #ef4444; }
.btn-action.primary { background-color: #eff6ff; color: #2563eb; }
.btn-action:hover { opacity: 0.8; }

.table-footer { padding: 0.8rem 1rem; border-top: 1px solid #e2e8f0; background: #f8fafc; font-size: 0.75rem; color: #64748b; text-align: center; }

/* Utils */
.text-right { text-align: right; }
.text-center { text-align: center; }
.font-bold { font-weight: 700; }
.text-success { color: #15803d; }
.text-danger { color: #ef4444; }
.text-red { color: #ef4444; }

.loading-state, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.empty-icon { font-size: 2.5rem; color: #e2e8f0; margin-bottom: 1rem; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; height: auto; }
  .report-main-wrapper { min-height: 500px; }
  .toolbar-grid { grid-template-columns: 1fr 1fr; }
  .search-cell { grid-column: span 2; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
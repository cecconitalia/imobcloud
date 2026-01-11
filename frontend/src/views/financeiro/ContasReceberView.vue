<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Financeiro</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Contas a Receber</span>
           </nav>
           
           <h1>Contas a Receber</h1>
        </div>
        
        <div class="actions-area">
            <div class="quick-actions">
                <button @click="setQuickFilter('currentMonth')" class="btn-text" title="Filtrar Mês Atual">Mês Atual</button>
                <span class="divider">|</span>
                <button @click="setQuickFilter('next30Days')" class="btn-text" title="Próximos 30 Dias">30 Dias</button>
            </div>

            <button class="btn-icon-thin" @click="fetchData(false)" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <router-link :to="{ name: 'transacao-nova', query: { tipo: 'RECEITA' } }" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Nova Receita
            </router-link>
        </div>
      </div>
    </header>

    <div class="kpi-grid" v-if="stats && stats.a_receber">
      <div class="kpi-card orange">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.a_receber.pendente) }}</span>
          <span class="kpi-label">A Receber (Pendente)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-clock"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.a_receber.pago_mes_atual) }}</span>
          <span class="kpi-label">Recebido (Mês)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-check-circle"></i></div>
      </div>

      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.saldo_previsto) }}</span>
          <span class="kpi-label">Saldo Previsto (Fluxo)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-wallet"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ totalCount }}</span>
          <span class="kpi-label">Transações Listadas</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-list-ol"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell search-cell">
          <label>Buscar Cliente</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filters.cliente_search" 
              placeholder="Nome, CPF ou ID..." 
              class="form-control"
              @keyup.enter="fetchData(true)"
            >
          </div>
        </div>

        <div class="filter-cell" style="min-width: 240px;">
          <label>Vencimento (De - Até)</label>
          <div class="date-group-row">
            <input type="date" v-model="filters.data_vencimento_inicio" @change="fetchData(true)" class="form-control">
            <span class="date-sep">-</span>
            <input type="date" v-model="filters.data_vencimento_fim" @change="fetchData(true)" class="form-control">
          </div>
        </div>

        <div class="filter-cell">
          <label>Status</label>
          <select v-model="filters.status" @change="fetchData(true)" class="form-control">
            <option value="">Todos</option>
            <option value="PENDENTE">Pendente</option>
            <option value="ATRASADO">Atrasado</option>
            <option value="PAGO">Pago</option>
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
        <p>Carregando finanças...</p>
      </div>

      <div v-else-if="error" class="empty-state">
        <i class="fas fa-exclamation-triangle empty-icon text-red"></i>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="transacoes.length === 0" class="empty-state">
        <i class="fas fa-folder-open empty-icon"></i>
        <p>Nenhuma conta a receber encontrada com os filtros atuais.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="12%" @click="ordenar('data_vencimento')" class="sortable">
                  Vencimento <i class="fas" :class="getIconeOrdenacao('data_vencimento')"></i>
              </th>
              <th width="25%" @click="ordenar('cliente__nome')" class="sortable">
                  Cliente <i class="fas" :class="getIconeOrdenacao('cliente__nome')"></i>
              </th>
              <th width="25%" @click="ordenar('descricao')" class="sortable">
                  Descrição <i class="fas" :class="getIconeOrdenacao('descricao')"></i>
              </th>
              <th width="15%" @click="ordenar('valor')" class="sortable text-right">
                  Valor <i class="fas" :class="getIconeOrdenacao('valor')"></i>
              </th>
              <th width="10%" @click="ordenar('status')" class="sortable text-center">
                  Status <i class="fas" :class="getIconeOrdenacao('status')"></i>
              </th>
              <th width="13%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transacao in transacoes" :key="transacao.id">
              <td>
                 <div class="date-cell">
                    <span class="date-day">{{ formatarData(transacao.data_vencimento).split('/')[0] }}</span>
                    <span class="date-month">{{ formatarData(transacao.data_vencimento).substring(3) }}</span>
                 </div>
              </td>
              
              <td class="font-medium text-slate-700">
                  {{ transacao.cliente_nome || 'Cliente não identificado' }}
              </td>

              <td class="text-muted text-sm">
                  {{ transacao.descricao }}
              </td>

              <td class="text-right font-bold text-success">
                  {{ formatarValor(transacao.valor) }}
              </td>

              <td class="text-center">
                <span :class="['status-pill', getStatusClass(transacao.status)]">
                  {{ transacao.status }}
                </span>
              </td>

              <td class="text-right">
                <div class="actions-flex">
                    <button 
                      v-if="transacao.status !== 'PAGO'" 
                      @click="abrirModalPagamento(transacao)" 
                      class="btn-action success" 
                      title="Receber"
                      :disabled="transacao.isUpdating"
                    >
                      <i class="fas fa-hand-holding-usd"></i>
                    </button>

                    <button 
                      v-else 
                      @click="reverterPagamento(transacao)" 
                      class="btn-action danger" 
                      title="Reverter Pagamento"
                      :disabled="transacao.isUpdating"
                    >
                      <i class="fas fa-undo"></i>
                    </button>
                    
                    <router-link :to="{ name: 'transacao-editar', params: { id: transacao.id } }" class="btn-action primary" title="Editar">
                        <i class="fas fa-pen"></i>
                    </router-link>
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

    <div v-if="showModal" class="modal-overlay" @click.self="fecharModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Baixar Conta a Receber</h3>
          <button class="close-btn" @click="fecharModal">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedTransacao">
          <div class="summary-box">
             <div class="summary-item">
                <span class="label">Cliente</span>
                <span class="value">{{ selectedTransacao.cliente_nome || 'N/A' }}</span>
             </div>
             <div class="summary-item">
                <span class="label">Valor</span>
                <span class="value highlight">{{ formatarValor(selectedTransacao.valor) }}</span>
             </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
                <label>Data Recebimento</label>
                <input type="date" v-model="formPagamento.data_pagamento" class="form-control">
            </div>

            <div class="form-group">
                <label>Forma de Pagamento</label>
                <select v-model="formPagamento.forma_pagamento" class="form-control">
                    <option value="" disabled>Selecione...</option>
                    <option v-for="forma in listaFormasPagamento" :key="forma.id" :value="forma.id">
                        {{ forma.nome }}
                    </option>
                </select>
            </div>
            
            <div class="form-group full-width">
                <label>Conta de Entrada</label>
                <select v-model="formPagamento.conta" class="form-control">
                    <option :value="null">Não alterar conta</option>
                    <option v-for="conta in listaContas" :key="conta.id" :value="conta.id">
                        {{ conta.nome }}
                    </option>
                </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-ghost" @click="fecharModal">Cancelar</button>
          <button class="btn-primary-modal" @click="confirmarRecebimento" :disabled="isProcessing">
            <i class="fas fa-check" v-if="!isProcessing"></i>
            <span v-if="isProcessing">Processando...</span>
            <span v-else>Confirmar</span>
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import apiClient from '@/services/api';
import { format, startOfMonth, endOfMonth, addDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useRouter } from 'vue-router';

// --- Interfaces ---
interface TransacaoReceber {
    id: number;
    data_vencimento: string;
    data_transacao: string;
    cliente_nome?: string;
    descricao: string;
    valor: number;
    status: 'PENDENTE' | 'ATRASADO' | 'PAGO' | string;
    conta?: number;
    isUpdating?: boolean; 
}

interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

interface StatsFinanceiro {
    a_receber: { pendente: number; pago_mes_atual: number; };
    a_pagar: { pendente: number; pago_mes_atual: number; };
    saldo_previsto: number;
}

interface Filters {
    status: string;
    data_vencimento_inicio: string;
    data_vencimento_fim: string;
    cliente_search: string;
    cliente_id?: number | string | null; 
}

interface FormaPagamento { id: number; nome: string; }
interface Conta { id: number; nome: string; }

// --- State ---
const router = useRouter();
const transacoes = ref<TransacaoReceber[]>([]);
const totalCount = ref(0);
const stats = ref<StatsFinanceiro | null>(null); 
const isLoading = ref(true);
const error = ref<string | null>(null);

// Dados Modal
const showModal = ref(false);
const selectedTransacao = ref<TransacaoReceber | null>(null);
const isProcessing = ref(false);
const listaFormasPagamento = ref<FormaPagamento[]>([]);
const listaContas = ref<Conta[]>([]);

const formPagamento = reactive({
    data_pagamento: '',
    forma_pagamento: '' as number | '',
    conta: null as number | null
});

// ALTERAÇÃO: Inicializando com Status PENDENTE
const filters = ref<Filters>({
    status: 'PENDENTE', 
    data_vencimento_inicio: '',
    data_vencimento_fim: '',
    cliente_search: '',
    cliente_id: null,
});

// --- Ordenação (Padrão Crescente) ---
const ordenacao = ref('data_vencimento'); 

// --- Formatters ---
const formatarValor = (valor: number | null | undefined): string => {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    const numValue = typeof valor === 'string' ? parseFloat(valor) : valor;
    if (isNaN(numValue)) return 'R$ 0,00';
    return numValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatarData = (data: string | null): string => {
    if (!data) return 'N/A';
    try {
        return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
    } catch { return 'Inválida'; }
};

const getStatusClass = (status: string): string => {
  switch (status) {
    case 'PENDENTE': return 'status-orange';
    case 'ATRASADO': return 'status-red';
    case 'PAGO': return 'status-green';
    default: return 'status-gray';
  }
};

// --- Lógica de Ordenação ---
function ordenar(campo: string) {
  if (ordenacao.value === campo) {
    ordenacao.value = `-${campo}`; 
  } else if (ordenacao.value === `-${campo}`) {
    ordenacao.value = campo; 
  } else {
    ordenacao.value = campo; 
  }
  fetchData(true);
}

function getIconeOrdenacao(campo: string) {
  if (ordenacao.value === campo) return 'fa-sort-up text-blue-600';
  if (ordenacao.value === `-${campo}`) return 'fa-sort-down text-blue-600';
  return 'fa-sort text-slate-300 hover:text-slate-500';
}

// --- Ações do Modal ---
const abrirModalPagamento = (transacao: TransacaoReceber) => {
    selectedTransacao.value = transacao;
    formPagamento.data_pagamento = format(new Date(), 'yyyy-MM-dd');
    formPagamento.forma_pagamento = ''; 
    formPagamento.conta = transacao.conta || null;
    showModal.value = true;
};

const fecharModal = () => {
    showModal.value = false;
    selectedTransacao.value = null;
    isProcessing.value = false;
};

const confirmarRecebimento = async () => {
    if (!selectedTransacao.value) return;
    
    isProcessing.value = true;
    try {
        const id = selectedTransacao.value.id;
        const payload: any = {
            status: 'PAGO',
            data_pagamento: formPagamento.data_pagamento
        };
        
        if (formPagamento.forma_pagamento) payload.forma_pagamento = formPagamento.forma_pagamento;
        if (formPagamento.conta) payload.conta = formPagamento.conta;

        await apiClient.patch(`/v1/financeiro/transacoes/${id}/`, payload);
        
        fecharModal();
        fetchData(false);
    } catch (err) {
        console.error("Erro ao baixar recebimento:", err);
        alert('Erro ao registrar recebimento.');
    } finally {
        isProcessing.value = false;
    }
};

const reverterPagamento = async (transacao: TransacaoReceber) => {
    if (!confirm(`Deseja reverter o recebimento de "${transacao.descricao}" para PENDENTE?`)) return;
    
    transacao.isUpdating = true;
    try {
        await apiClient.patch(`/v1/financeiro/transacoes/${transacao.id}/`, { 
            status: 'PENDENTE',
            data_pagamento: null 
        });
        fetchData(false); 
    } catch (err) {
        alert('Erro ao reverter o status.');
    } finally {
        transacao.isUpdating = false;
    }
};

// --- Filtros ---
const setQuickFilter = (period: 'currentMonth' | 'next30Days') => {
    const today = new Date();
    let startDate: Date;
    let endDate: Date;
    const apiDateFormat = 'yyyy-MM-dd';

    if (period === 'currentMonth') {
        startDate = startOfMonth(today);
        endDate = endOfMonth(today);
    } else {
        startDate = today;
        endDate = addDays(today, 30);
    }

    filters.value.status = 'PENDENTE'; // Mantém o foco em pendentes no filtro rápido
    filters.value.data_vencimento_inicio = format(startDate, apiDateFormat);
    filters.value.data_vencimento_fim = format(endDate, apiDateFormat);

    fetchData(true);
};

// ALTERAÇÃO: ResetFilters volta para PENDENTE
const resetFilters = () => {
    filters.value = {
        status: 'PENDENTE', 
        data_vencimento_inicio: '',
        data_vencimento_fim: '',
        cliente_search: '',
        cliente_id: null,
    };
    fetchData(true);
};

// --- Data Fetching ---
async function fetchData(isFilterChange: boolean = false) {
  if (!isFilterChange) isLoading.value = true;
  error.value = null;

  try {
    const statsResponse = await apiClient.get<StatsFinanceiro>('/v1/financeiro/transacoes/stats/');
    stats.value = statsResponse.data;

    const params: Record<string, any> = {};
    if (filters.value.status) params.status = filters.value.status;
    if (filters.value.data_vencimento_inicio) params.data_vencimento_inicio = filters.value.data_vencimento_inicio;
    if (filters.value.data_vencimento_fim) params.data_vencimento_fim = filters.value.data_vencimento_fim;
    if (filters.value.cliente_search) params.search = filters.value.cliente_search;
    else if (filters.value.cliente_id) params.cliente_id = filters.value.cliente_id;
    
    params.page_size = 50;
    params.ordenacao = ordenacao.value; // Envia a ordenação

    const transacoesResponse = await apiClient.get<PaginatedResponse<TransacaoReceber>>(
      '/v1/financeiro/transacoes/a-receber/', 
      { params: params }
    );

    const results = transacoesResponse.data.results || []; 
    totalCount.value = transacoesResponse.data.count || 0;
    transacoes.value = results.map(t => ({...t, isUpdating: false}));

  } catch (err) {
    console.error(err);
    error.value = "Não foi possível carregar os dados.";
  } finally {
    isLoading.value = false;
  }
}

async function fetchAuxiliaryData() {
    try {
        const [formasRes, contasRes] = await Promise.all([
            apiClient.get('/v1/financeiro/formas-pagamento/'),
            apiClient.get('/v1/financeiro/contas/')
        ]);
        listaFormasPagamento.value = Array.isArray(formasRes.data) ? formasRes.data : (formasRes.data.results || []);
        listaContas.value = Array.isArray(contasRes.data) ? contasRes.data : (contasRes.data.results || []);
    } catch (err) { console.warn(err); }
}

onMounted(() => {
  // Chamamos fetchData diretamente no onMounted, que usará o estado inicial (PENDENTE)
  fetchData(false);
  fetchAuxiliaryData();
});
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL */
.page-container {
  min-height: 100vh; /* Permite rolagem padrão do navegador */
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

/* Botões Estilo Fino */
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

/* Atalhos Rápidos (Header) */
.quick-actions { 
    display: flex; align-items: center; gap: 8px; margin-right: 8px; 
    font-size: 0.8rem; color: #64748b; 
}
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
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR */
.toolbar-grid {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: grid; grid-template-columns: 2fr 2fr 1fr auto; 
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
  /* Removemos o height fixo e overflow hidden para usar o scroll da página */
  width: 100%;
  background: white; border-radius: 8px; border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  display: flex; flex-direction: column;
}

.report-scroll-viewport { 
    width: 100%; overflow-x: auto; /* Apenas scroll horizontal se necessário */
    scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent;
}
.report-scroll-viewport::-webkit-scrollbar { width: 8px; height: 8px; }
.report-scroll-viewport::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 4px; border: 2px solid white; }

.report-table { width: 100%; border-collapse: collapse; min-width: 900px; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left; 
  /* Sticky no topo relativo à janela */
  position: sticky; top: 0; z-index: 10;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  cursor: pointer;
  user-select: none;
}
.report-table th:hover { background: #f1f5f9; color: #1e293b; }
.report-table th i { margin-left: 6px; }

.report-table td {
  padding: 0.75rem 1.2rem; border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem; color: #334155; vertical-align: middle;
}
.report-table tr:hover { background-color: #fcfcfc; }

/* Celulas Tabela */
.date-cell { display: flex; flex-direction: column; line-height: 1.1; }
.date-day { font-weight: 700; color: #334155; font-size: 0.95rem; }
.date-month { font-size: 0.7rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }

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
.btn-action.success:hover { background-color: #15803d; color: white; }
.btn-action.danger { background-color: #fee2e2; color: #ef4444; }
.btn-action.danger:hover { background-color: #ef4444; color: white; }
.btn-action.primary { background-color: #eff6ff; color: #2563eb; }
.btn-action.primary:hover { background-color: #2563eb; color: white; }

.table-footer { padding: 0.8rem 1rem; border-top: 1px solid #e2e8f0; background: #f8fafc; font-size: 0.75rem; color: #64748b; text-align: center; }

/* MODAL */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 1.5rem; border-radius: 12px; width: 420px; max-width: 90%; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; font-weight: 700; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }

.summary-box { background: #f8fafc; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; border: 1px solid #f1f5f9; }
.summary-item { display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem; }
.summary-item:last-child { margin-bottom: 0; }
.summary-item .label { color: #64748b; }
.summary-item .value { font-weight: 600; color: #334155; }
.summary-item .highlight { color: #15803d; font-size: 1.1rem; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.full-width { grid-column: span 2; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }

.modal-footer { display: flex; justify-content: flex-end; gap: 0.8rem; margin-top: 1.5rem; pt: 1rem; border-top: 1px solid #f1f5f9; }
.btn-ghost { background: none; border: none; color: #64748b; cursor: pointer; font-weight: 600; padding: 0.6rem 1rem; }
.btn-primary-modal { background: #2563eb; color: white; border: none; padding: 0.6rem 1.5rem; border-radius: 6px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; }
.btn-primary-modal:hover { background: #1d4ed8; }

/* Utils */
.text-right { text-align: right; }
.text-center { text-align: center; }
.font-bold { font-weight: 700; }
.font-medium { font-weight: 500; }
.text-success { color: #15803d; }
.text-muted { color: #94a3b8; }
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
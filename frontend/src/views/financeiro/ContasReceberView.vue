<template>
  <div class="page-container">
    
    <div v-if="stats && stats.a_receber" class="summary-grid"> 
      <div class="summary-card pending-revenue">
        <h4 class="card-title">Total Pendente (Previsto)</h4>
        <p class="card-value">{{ formatarValor(stats.a_receber.pendente) }}</p>
      </div>
      
      <div class="summary-card received-month">
        <h4 class="card-title">Recebido no Mês (Caixa)</h4>
        <p class="card-value">{{ formatarValor(stats.a_receber.pago_mes_atual) }}</p>
      </div>
      
      <div :class="['summary-card', (stats.saldo_previsto ?? 0) >= 0 ? 'card-positive' : 'card-negative']">
        <h4 class="card-title">Saldo Previsto (Fluxo)</h4>
        <p class="card-value">{{ formatarValor(stats.saldo_previsto) }}</p>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-state card">A carregar dados financeiros...</div>
    <div v-if="error" class="error-message card">{{ error }}</div>

    <div class="filter-card card">
        <h5 class="filter-header">Filtros de Busca</h5>
        
        <div class="quick-filters">
            <button @click="setQuickFilter('currentMonth')" class="quick-filter-btn">Mês Atual</button>
            <button @click="setQuickFilter('next30Days')" class="quick-filter-btn">Próximos 30 Dias</button>
        </div>

        <div class="filter-controls">
          <div class="filter-group filter-cliente">
            <label for="cliente_search">Buscar Cliente</label>
            <input 
                type="text" 
                id="cliente_search" 
                v-model="filters.cliente_search" 
                @keyup.enter="fetchData(true)"
                placeholder="Nome, CPF ou ID do cliente"
            >
          </div>
          
          <div class="filter-group">
            <label for="status">Status</label>
            <select id="status" v-model="filters.status" @change="fetchData(true)">
              <option value="">Todos</option>
              <option value="PENDENTE">Pendente</option>
              <option value="ATRASADO">Atrasado</option>
              <option value="PAGO">Pago</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="data_inicio">Vencimento Início</label>
            <input type="date" id="data_inicio" v-model="filters.data_vencimento_inicio" @change="fetchData(true)">
          </div>

          <div class="filter-group">
            <label for="data_fim">Vencimento Fim</label>
            <input type="date" id="data_fim" v-model="filters.data_vencimento_fim" @change="fetchData(true)">
          </div>

          <router-link :to="{ name: 'transacao-nova', query: { tipo: 'RECEITA' } }" class="btn-primary align-bottom">
            + Nova Receita
          </router-link>

          <button @click="resetFilters" class="btn-secondary align-bottom">Limpar Filtros</button>
        </div>
    </div>

    <div class="table-card" v-if="!isLoading && !error">
      <div v-if="transacoes.length">
        <table class="styled-table">
          <thead>
            <tr>
              <th>Vencimento</th>
              <th>Cliente</th>
              <th>Descrição</th>
              <th class="text-right">Valor</th>
              <th class="text-center">Status</th>
              <th class="text-center" style="width: 130px;">Ações</th> 
              </tr>
          </thead>
          <tbody>
            <tr v-for="transacao in transacoes" :key="transacao.id" class="table-row">
              <td>{{ formatarData(transacao.data_vencimento) }}</td>
              <td>{{ transacao.cliente_nome || 'N/A' }}</td>
              <td>{{ transacao.descricao }}</td>
              <td class="text-right text-success">{{ formatarValor(transacao.valor) }}</td>
              <td class="text-center">
                <span :class="['status-badge', getStatusClass(transacao.status)]">
                  {{ transacao.status }}
                </span>
              </td>
              <td class="action-column">
                <button 
                  v-if="transacao.status !== 'PAGO'" 
                  @click="updateStatus(transacao.id, 'PAGO')" 
                  class="btn-action btn-solid-success" 
                  title="Marcar como Pago Agora"
                  :disabled="transacao.isUpdating"
                >
                  <span v-if="transacao.isUpdating">...</span>
                  <span v-else>Pagar</span>
                </button>

                <button 
                  v-else 
                  @click="updateStatus(transacao.id, 'PENDENTE')" 
                  class="btn-action btn-outline-danger" 
                  title="Reverter para Pendente"
                  :disabled="transacao.isUpdating"
                >
                  <span v-if="transacao.isUpdating">...</span>
                  <span v-else>Reverter</span>
                </button>
                
                <router-link :to="{ name: 'transacao-editar', params: { id: transacao.id } }" class="btn-action btn-outline-info" title="Editar">
                    &#9998;
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div class="pagination-info" v-if="totalCount > transacoes.length">
            Exibindo {{ transacoes.length }} de {{ totalCount }} registos. (Use o Extrato Completo para ver mais)
        </div>

      </div>
      <div v-else class="no-data-message">
        Nenhuma conta a receber encontrada com os filtros atuais.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import { format, startOfMonth, endOfMonth, addDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useRouter } from 'vue-router';

// --- Interfaces ---
interface TransacaoReceber {
    id: number;
    data_vencimento: string;
    cliente_nome?: string;
    descricao: string;
    valor: number;
    status: 'PENDENTE' | 'ATRASADO' | 'PAGO' | string;
    isUpdating?: boolean; 
}

// Interface para a resposta paginada do Django REST Framework
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

const router = useRouter();

// Estados Reativos
const transacoes = ref<TransacaoReceber[]>([]);
const totalCount = ref(0);
const stats = ref<StatsFinanceiro | null>(null); 
const isLoading = ref(true);
const error = ref<string | null>(null);

const filters = ref<Filters>({
    status: '',
    data_vencimento_inicio: '',
    data_vencimento_fim: '',
    cliente_search: '',
    cliente_id: null,
});

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
    case 'PENDENTE': return 'status-pending';
    case 'ATRASADO': return 'status-overdue';
    case 'PAGO': return 'status-paid';
    default: return '';
  }
};

// --- Ações ---
async function updateStatus(id: number, newStatus: 'PAGO' | 'PENDENTE') {
    const transacaoToUpdate = transacoes.value.find(t => t.id === id);
    if (!transacaoToUpdate) return;
    
    transacaoToUpdate.isUpdating = true;

    try {
        const payload: { status: string; data_pagamento?: string | null } = { status: newStatus };

        if (newStatus === 'PAGO') {
            payload.data_pagamento = format(new Date(), 'yyyy-MM-dd');
        } else {
            payload.data_pagamento = null;
        }

        await apiClient.patch(`/v1/financeiro/transacoes/${id}/`, payload);
        alert(`Transação atualizada para ${newStatus}!`);
        fetchData(false); 
    } catch (err) {
        console.error(`Erro ao atualizar status:`, err);
        alert('Erro ao atualizar o status.');
    } finally {
        transacaoToUpdate.isUpdating = false;
    }
}

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

    filters.value.status = '';
    filters.value.data_vencimento_inicio = format(startDate, apiDateFormat);
    filters.value.data_vencimento_fim = format(endDate, apiDateFormat);

    fetchData(true);
};

const resetFilters = () => {
    filters.value = {
        status: '',
        data_vencimento_inicio: '',
        data_vencimento_fim: '',
        cliente_search: '',
        cliente_id: null,
    };
    fetchData(true);
};


// --- Data Fetching ---
async function fetchData(isFilterChange: boolean = false) {
  if (!isFilterChange) {
      isLoading.value = true;
  }
  error.value = null;

  try {
    // 1. Fetch Estatísticas
    const statsResponse = await apiClient.get<StatsFinanceiro>('/v1/financeiro/transacoes/stats/');
    stats.value = statsResponse.data;

    // 2. Fetch Transações (com filtros)
    const params: Record<string, any> = {};

    if (filters.value.status) { params.status = filters.value.status; }
    if (filters.value.data_vencimento_inicio) { params.data_vencimento_inicio = filters.value.data_vencimento_inicio; }
    if (filters.value.data_vencimento_fim) { params.data_vencimento_fim = filters.value.data_vencimento_fim; }
    
    if (filters.value.cliente_search) {
        params.cliente_search = filters.value.cliente_search;
    } else if (filters.value.cliente_id) {
        params.cliente_id = filters.value.cliente_id;
    }
    
    // Adiciona paginação para garantir retorno consistente
    params.page_size = 50; 

    // CORREÇÃO AQUI: Tipagem correta da resposta paginada
    const transacoesResponse = await apiClient.get<PaginatedResponse<TransacaoReceber>>(
      '/v1/financeiro/transacoes/a-receber/', 
      { params: params }
    );

    // CORREÇÃO AQUI: Acessa .results em vez de .data diretamente
    const results = transacoesResponse.data.results || []; 
    totalCount.value = transacoesResponse.data.count || 0;

    transacoes.value = results.map(t => ({...t, isUpdating: false}));

  } catch (err) {
    console.error("Erro ao carregar contas a receber:", err);
    error.value = "Não foi possível carregar os dados. Tente recarregar a página.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
/* ======================================= */
/* ESTILOS GERAIS/BOTÕES                   */
/* ======================================= */
.page-container { padding: 0; }

.btn-primary {
    background-color: #007bff;
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.3s;
    font-size: 0.9rem;
}
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary {
    background-color: #6c757d;
    color: white;
    padding: 0.4rem 0.8rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.3s;
    font-size: 0.9rem;
}
.btn-secondary:hover { background-color: #5a6268; }

.align-bottom {
    align-self: flex-end; 
    height: 36px; 
    padding-top: 0;
    padding-bottom: 0;
    display: flex;
    align-items: center;
}
.card {
    background: white; 
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06); 
}

/* ======================================= */
/* SUMMARY CARDS                           */
/* ======================================= */
.summary-grid {
    margin-top: 0; 
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 0.75rem; 
}
.summary-card {
    padding: 1rem;
    border-radius: 8px; 
    background-color: #fcfcfc;
    border-left: 5px solid;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); 
}
.card-title {
    margin: 0 0 0.4rem 0;
    font-size: 0.9rem; 
    color: #6c757d; 
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
} 
.card-value {
    margin: 0; 
    font-size: 1.8rem;
    font-weight: 700; 
    color: #343a40; 
}

.pending-revenue { border-color: #ffc107; } 
.received-month { border-color: #28a745; } 
.card-positive { border-color: #17a2b8; } 
.card-negative { border-color: #dc3545; }
.card-positive .card-value { color: #17a2b8; }
.card-negative .card-value { color: #dc3545; }

/* ======================================= */
/* FILTROS                                 */
/* ======================================= */
.filter-card {
    padding: 0.75rem 1.5rem;
    margin-bottom: 0.5rem;
}
.filter-header {
    margin-top: 0;
    margin-bottom: 0.75rem; 
    font-size: 1rem; 
    color: #343a40;
    border-bottom: 1px solid #e9ecef;
    padding-bottom: 0.5rem;
    font-weight: 600;
}
.quick-filters {
    margin-bottom: 0.75rem;
    display: flex;
    gap: 0.5rem;
}
.quick-filter-btn {
    background-color: #e9ecef;
    color: #495057;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 0.3rem 0.6rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background-color 0.2s;
}
.quick-filter-btn:hover { background-color: #dee2e6; }

.filter-controls {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end; 
    flex-wrap: wrap; 
}
.filter-group {
    display: flex;
    flex-direction: column;
    min-width: 140px;
}
.filter-cliente { min-width: 200px; flex-grow: 1; }
.filter-group label {
    font-size: 0.8rem;
    color: #6c757d; 
    margin-bottom: 0.25rem;
    font-weight: 500;
}
.filter-group select, .filter-group input {
    padding: 0.4rem 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 0.9rem;
    height: 36px;
    background-color: #ffffff;
}

/* ======================================= */
/* TABELA E AÇÕES                          */
/* ======================================= */
.table-card {
    padding: 1rem; 
    overflow-x: auto; 
    margin-top: 0.5rem;
}
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th {
    padding: 0.75rem 1rem;
    text-align: left; 
    border-bottom: 2px solid #dee2e6;
    color: #495057; 
    background-color: #f8f9fa;
    font-weight: 600; 
    font-size: 0.9rem;
}
.styled-table td {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #f1f1f1;
    vertical-align: middle; 
    font-size: 0.9rem;
}
.styled-table tbody tr:hover {
    background-color: #fefefe;
    box-shadow: inset 3px 0 0 0 #007bff;
}

.action-column {
    text-align: center;
    display: flex;
    gap: 5px;
    justify-content: center;
}
.btn-action {
    padding: 0.3rem 0.6rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.75rem; 
    font-weight: 600;
    text-decoration: none;
    min-width: 55px;
    display: flex; align-items: center; justify-content: center;
}
.btn-action:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-solid-success { background-color: #28a745; color: white !important; border: 1px solid #28a745; }
.btn-solid-success:hover { background-color: #1e7e34; }

.btn-outline-danger { background-color: transparent; color: #dc3545 !important; border: 1px solid #dc3545; }
.btn-outline-danger:hover { background-color: #dc3545; color: white !important; }

.btn-outline-info { background-color: transparent; color: #17a2b8 !important; border: 1px solid #17a2b8; min-width: 30px; }
.btn-outline-info:hover { background-color: #17a2b8; color: white !important; }

.status-badge { padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 700; }
.status-pending { background-color: #ffc107; color: #3c3c3c; } 
.status-overdue { background-color: #dc3545; color: white; } 
.status-paid { background-color: #28a745; color: white; }    

.text-success { color: #198754; font-weight: bold; } 
.loading-state, .error-message, .no-data-message { padding: 1.5rem; text-align: center; }
.pagination-info { margin-top: 1rem; text-align: center; font-size: 0.85rem; color: #6c757d; }
</style>
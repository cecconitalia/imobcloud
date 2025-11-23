<template>
  <div class="page-container">
    
    <div v-if="stats && stats.a_pagar" class="summary-grid"> 
      <div class="summary-card pending-expense">
        <h4 class="card-title">Total Pendente (Previsto)</h4>
        <p class="card-value">{{ formatarValor(stats.a_pagar.pendente) }}</p>
      </div>
      <div class="summary-card paid-month">
        <h4 class="card-title">Pago no Mês (Caixa)</h4>
        <p class="card-value">{{ formatarValor(stats.a_pagar.pago_mes_atual) }}</p>
      </div>
      <div :class="['summary-card', (stats.saldo_previsto ?? 0) >= 0 ? 'card-positive' : 'card-negative']">
        <h4 class="card-title">Saldo Previsto (Fluxo)</h4>
        <p class="card-value">{{ formatarValor(stats.saldo_previsto) }}</p>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-state card">A carregar...</div>
    <div v-if="error" class="error-message card">{{ error }}</div>

    <div class="filter-card card">
        <h5 class="filter-header">Filtros de Busca</h5>
        <div class="quick-filters">
            <button @click="setQuickFilter('currentMonth')" class="quick-filter-btn">Mês Atual</button>
            <button @click="setQuickFilter('next30Days')" class="quick-filter-btn">Próximos 30 Dias</button>
        </div>

        <div class="filter-controls">
          <div class="filter-group filter-cliente">
            <label for="cliente_search">Buscar Credor/Cliente</label>
            <input type="text" id="cliente_search" v-model="filters.cliente_search" @keyup.enter="fetchData(true)" placeholder="Nome ou ID">
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
          <router-link :to="{ name: 'transacao-nova', query: { tipo: 'DESPESA' } }" class="btn-primary align-bottom">
            + Nova Despesa
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
              <th>Credor/Cliente</th>
              <th>Descrição</th>
              <th class="text-right">Valor</th>
              <th class="text-center">Status</th>
              <th class="text-center" style="width: 140px;">Ações</th> 
              </tr>
          </thead>
          <tbody>
            <tr v-for="transacao in transacoes" :key="transacao.id" class="table-row">
              <td>{{ formatarData(transacao.data_vencimento) }}</td> 
              <td>{{ transacao.cliente_nome || 'N/A' }}</td>
              <td>{{ transacao.descricao }}</td>
              <td class="text-right text-danger">{{ formatarValor(transacao.valor) }}</td>
              <td class="text-center">
                <span :class="['status-badge', getStatusClass(transacao.status)]">
                  {{ transacao.status }} </span>
              </td>
              <td class="action-column">
                <button 
                  v-if="transacao.status !== 'PAGO'" 
                  @click="abrirModalPagamento(transacao)" 
                  class="btn-action btn-solid-success" 
                  title="Baixar Conta"
                  :disabled="transacao.isUpdating"
                >
                  Pagar
                </button>

                <button 
                  v-else 
                  @click="reverterPagamento(transacao)" 
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
      </div>
      <div v-else class="no-data-message">
        Nenhuma conta a pagar encontrada com os filtros atuais.
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="fecharModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Baixar Conta a Pagar</h3>
          <button class="close-btn" @click="fecharModal">&times;</button>
        </div>
        
        <div class="modal-body" v-if="selectedTransacao">
          <div class="info-row">
            <label>Descrição:</label>
            <span>{{ selectedTransacao.descricao }}</span>
          </div>
          <div class="info-row">
            <label>Valor Original:</label>
            <span class="val-highlight">{{ formatarValor(selectedTransacao.valor) }}</span>
          </div>
          <div class="info-row">
            <label>Vencimento:</label>
            <span>{{ formatarData(selectedTransacao.data_vencimento) }}</span>
          </div>

          <hr class="modal-divider">

          <div class="form-group">
            <label for="data_pagamento">Data do Pagamento</label>
            <input type="date" id="data_pagamento" v-model="formPagamento.data_pagamento" class="form-control">
          </div>

          <div class="form-group">
            <label for="forma_pagamento">Forma de Pagamento</label>
            <select id="forma_pagamento" v-model="formPagamento.forma_pagamento" class="form-control">
                <option value="" disabled>Selecione...</option>
                <option v-for="forma in listaFormasPagamento" :key="forma.id" :value="forma.id">
                    {{ forma.nome }}
                </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="conta_bancaria">Conta de Saída (Opcional)</label>
            <select id="conta_bancaria" v-model="formPagamento.conta" class="form-control">
                <option :value="null">Manter atual / Não alterar</option>
                <option v-for="conta in listaContas" :key="conta.id" :value="conta.id">
                    {{ conta.nome }}
                </option>
            </select>
          </div>

        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="fecharModal">Cancelar</button>
          <button class="btn-primary" @click="confirmarPagamento" :disabled="isProcessing">
            <span v-if="isProcessing">Processando...</span>
            <span v-else>Confirmar Baixa</span>
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

// --- INTERFACES ---
interface TransacaoPagar {
    id: number;
    data_vencimento: string;
    data_transacao: string; // Mantido na interface para compatibilidade com o backend
    cliente_nome?: string;
    descricao: string;
    valor: number;
    status: 'PENDENTE' | 'ATRASADO' | 'PAGO';
    conta?: number; 
    isUpdating?: boolean; 
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

// --- STATE ---
const router = useRouter();
const transacoes = ref<TransacaoPagar[]>([]);
const stats = ref<StatsFinanceiro | null>(null); 
const isLoading = ref(true);
const error = ref<string | null>(null);

// Dados para o Modal
const showModal = ref(false);
const selectedTransacao = ref<TransacaoPagar | null>(null);
const isProcessing = ref(false);
const listaFormasPagamento = ref<FormaPagamento[]>([]);
const listaContas = ref<Conta[]>([]);

const formPagamento = reactive({
    data_pagamento: '',
    forma_pagamento: '' as number | '',
    conta: null as number | null
});

const filters = ref<Filters>({
    status: '',
    data_vencimento_inicio: '',
    data_vencimento_fim: '',
    cliente_search: '',
    cliente_id: null,
});

// --- HELPERS ---
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

// --- AÇÕES DO MODAL ---
const abrirModalPagamento = (transacao: TransacaoPagar) => {
    selectedTransacao.value = transacao;
    // Reseta o form
    formPagamento.data_pagamento = format(new Date(), 'yyyy-MM-dd');
    formPagamento.forma_pagamento = ''; 
    formPagamento.conta = transacao.conta || null; // Pré-seleciona conta se já existir
    
    showModal.value = true;
};

const fecharModal = () => {
    showModal.value = false;
    selectedTransacao.value = null;
    isProcessing.value = false;
};

const confirmarPagamento = async () => {
    if (!selectedTransacao.value) return;
    
    isProcessing.value = true;
    try {
        const id = selectedTransacao.value.id;
        const payload: any = {
            status: 'PAGO',
            data_pagamento: formPagamento.data_pagamento
        };
        
        if (formPagamento.forma_pagamento) {
            payload.forma_pagamento = formPagamento.forma_pagamento;
        }
        if (formPagamento.conta) {
            payload.conta = formPagamento.conta;
        }

        await apiClient.patch(`/v1/financeiro/transacoes/${id}/`, payload);
        
        alert('Pagamento registrado com sucesso!');
        fecharModal();
        fetchData(false); 
        
    } catch (err) {
        console.error("Erro ao baixar conta:", err);
        alert('Erro ao registrar pagamento. Verifique os dados.');
    } finally {
        isProcessing.value = false;
    }
};

// --- AÇÃO DE REVERTER ---
const reverterPagamento = async (transacao: TransacaoPagar) => {
    if (!confirm(`Deseja realmente reverter o pagamento de "${transacao.descricao}" para PENDENTE?`)) {
        return;
    }
    
    transacao.isUpdating = true;
    try {
        await apiClient.patch(`/v1/financeiro/transacoes/${transacao.id}/`, { 
            status: 'PENDENTE',
            data_pagamento: null // Limpa a data
        });
        fetchData(false);
    } catch (err) {
        console.error("Erro ao reverter:", err);
        alert('Erro ao reverter status.');
    } finally {
        transacao.isUpdating = false;
    }
};


// --- FILTROS E DATA ---
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

// --- CARREGAMENTO DE DADOS ---
async function fetchData(isFilterChange: boolean = false) {
  if (!isFilterChange) isLoading.value = true;
  error.value = null;

  try {
    // 1. Stats
    const statsResponse = await apiClient.get<StatsFinanceiro>('/v1/financeiro/transacoes/stats/');
    stats.value = statsResponse.data;

    // 2. Transações
    const params: Record<string, any> = {};
    if (filters.value.status) params.status = filters.value.status;
    if (filters.value.data_vencimento_inicio) params.data_vencimento_inicio = filters.value.data_vencimento_inicio;
    if (filters.value.data_vencimento_fim) params.data_vencimento_fim = filters.value.data_vencimento_fim;
    
    if (filters.value.cliente_search) params.search = filters.value.cliente_search; // Usa 'search' no backend
    
    const transacoesResponse = await apiClient.get<any>('/v1/financeiro/transacoes/a-pagar/', { params });
    const resultsList = transacoesResponse.data.results ? transacoesResponse.data.results : transacoesResponse.data;

    if (Array.isArray(resultsList)) {
        transacoes.value = resultsList.map((t: any) => ({...t, isUpdating: false}));
    } else {
        transacoes.value = [];
    }
  } catch (err) {
    console.error("Erro ao buscar dados:", err);
    error.value = "Não foi possível carregar os dados.";
  } finally {
    isLoading.value = false;
  }
}

// Carrega dados auxiliares para o modal (Formas de Pagamento e Contas)
async function fetchAuxiliaryData() {
    try {
        const [formasRes, contasRes] = await Promise.all([
            apiClient.get('/v1/financeiro/formas-pagamento/'),
            apiClient.get('/v1/financeiro/contas/')
        ]);
        // Garante que a lista seja um array mesmo se a resposta for paginada
        listaFormasPagamento.value = Array.isArray(formasRes.data) ? formasRes.data : (formasRes.data.results || []);
        listaContas.value = Array.isArray(contasRes.data) ? contasRes.data : (contasRes.data.results || []);
    } catch (err) {
        console.warn("Erro ao carregar formas de pagamento/contas:", err);
    }
}

onMounted(() => {
  resetFilters(); // Já chama fetchData
  fetchAuxiliaryData();
});
</script>

<style scoped>
/* ESTILOS GERAIS */
.btn-primary {
    background-color: #007bff; color: white; padding: 0.4rem 0.8rem; border-radius: 4px;
    text-decoration: none; font-weight: 500; font-size: 0.9rem; border: none; cursor: pointer;
}
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary {
    background-color: #6c757d; color: white; padding: 0.4rem 0.8rem; border: none;
    border-radius: 4px; cursor: pointer; font-weight: 500; font-size: 0.9rem;
}
.btn-secondary:hover { background-color: #5a6268; }
.align-bottom { align-self: flex-end; height: 36px; display: flex; align-items: center; }
.card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.page-container { padding: 0; }

/* SUMMARY CARDS */
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 0.75rem; }
.summary-card { padding: 1rem; border-radius: 8px; background-color: #fcfcfc; border-left: 5px solid; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.card-title { margin: 0 0 0.4rem 0; font-size: 0.9rem; color: #6c757d; font-weight: 500; text-transform: uppercase; } 
.card-value { margin: 0; font-size: 1.8rem; font-weight: 700; color: #343a40; }
.pending-expense { border-color: #ffc107; } 
.paid-month { border-color: #dc3545; } 
.paid-month .card-value { color: #dc3545; }
.card-positive { border-color: #17a2b8; } .card-positive .card-value { color: #17a2b8; }
.card-negative { border-color: #dc3545; } .card-negative .card-value { color: #dc3545; }

/* FILTROS */
.filter-card { padding: 0.75rem 1.5rem; margin-bottom: 0.5rem; }
.filter-header { margin: 0 0 0.75rem 0; font-size: 1rem; border-bottom: 1px solid #e9ecef; padding-bottom: 0.5rem; font-weight: 600; }
.quick-filters { margin-bottom: 0.75rem; display: flex; gap: 0.5rem; }
.quick-filter-btn { background-color: #e9ecef; border: 1px solid #e9ecef; border-radius: 4px; padding: 0.3rem 0.6rem; cursor: pointer; }
.quick-filter-btn:hover { background-color: #dee2e6; }
.filter-controls { display: flex; gap: 0.75rem; align-items: flex-end; flex-wrap: wrap; }
.filter-group { display: flex; flex-direction: column; min-width: 140px; }
.filter-cliente { min-width: 200px; flex-grow: 1; }
.filter-group label { font-size: 0.8rem; color: #6c757d; margin-bottom: 0.25rem; }
.filter-group input, .filter-group select { padding: 0.4rem; border: 1px solid #ced4da; border-radius: 4px; height: 36px; }

/* TABELA */
.table-card { padding: 1rem; overflow-x: auto; margin-top: 0.5rem; }
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th { padding: 0.75rem 1rem; text-align: left; border-bottom: 2px solid #dee2e6; background-color: #f8f9fa; color: #495057; font-size: 0.9rem; }
.styled-table td { padding: 0.6rem 1rem; border-bottom: 1px solid #f1f1f1; font-size: 0.9rem; vertical-align: middle; }
.styled-table tbody tr:hover { background-color: #fefefe; }
.text-danger { color: #dc3545; font-weight: bold; } 
.text-right { text-align: right; } .text-center { text-align: center; }
.action-column { display: flex; gap: 5px; justify-content: center; }
.btn-action { padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; min-width: 55px; display: flex; justify-content: center; align-items: center; text-decoration: none; }
.btn-solid-success { background-color: #28a745; color: white; border: 1px solid #28a745; }
.btn-outline-danger { background: transparent; color: #dc3545; border: 1px solid #dc3545; }
.btn-outline-info { background: transparent; color: #17a2b8; border: 1px solid #17a2b8; min-width: 30px; }
.status-badge { padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 700; color: white; }
.status-pending { background-color: #ffc107; color: #3c3c3c; } 
.status-overdue { background-color: #dc3545; } 
.status-paid { background-color: #28a745; }    

/* MODAL STYLES */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background: white; padding: 20px; border-radius: 8px; width: 400px; max-width: 90%;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.modal-header h3 { margin: 0; font-size: 1.2rem; color: #333; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #666; }
.modal-body { font-size: 0.95rem; }
.info-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
.info-row label { color: #666; font-weight: 500; }
.val-highlight { font-weight: bold; color: #dc3545; font-size: 1.1rem; }
.modal-divider { border: 0; border-top: 1px solid #eee; margin: 15px 0; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #444; }
.form-control { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

.loading-state, .error-message, .no-data-message { padding: 1.5rem; text-align: center; color: #666; }
</style>
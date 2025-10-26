<template>
  <div class="page-container">
    <div v-if="isLoading" class="loading-state card">A carregar transações...</div>
    <div v-if="error" class="error-message card">{{ error }}</div>

    <div class="filter-controls card">
      <div class="filter-group">
        <label for="searchDescricao">Descrição/Cliente:</label>
        <input type="text" id="searchDescricao" v-model="filtros.search" placeholder="Buscar..." class="filter-input"/>
      </div>
      <div class="filter-group">
        <label for="selectTipo">Tipo:</label>
        <select id="selectTipo" v-model="filtros.tipo" class="filter-input">
          <option value="">Todos</option>
          <option value="RECEITA">Receita</option>
          <option value="DESPESA">Despesa</option>
        </select>
      </div>
      <div class="filter-group">
        <label for="selectStatus">Status:</label>
        <select id="selectStatus" v-model="filtros.status" class="filter-input">
          <option value="">Todos</option>
          <option value="PENDENTE">Pendente</option>
          <option value="PAGO">Pago/Recebido</option>
          <option value="VENCIDO">Vencido</option>
          <option value="CANCELADO">Cancelado</option>
        </select>
      </div>
       <div class="filter-group">
        <label for="dateInicio">Data De:</label>
        <input type="date" id="dateInicio" v-model="filtros.data_inicio" class="filter-input"/>
      </div>
       <div class="filter-group">
        <label for="dateFim">Data Até:</label>
        <input type="date" id="dateFim" v-model="filtros.data_fim" class="filter-input"/>
      </div>
       <div class="filter-group">
            <label for="selectCategoria">Categoria:</label>
            <select id="selectCategoria" v-model="filtros.categoria" class="filter-input">
                <option value="">Todas</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nome }}</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="selectConta">Conta:</label>
            <select id="selectConta" v-model="filtros.conta" class="filter-input">
                <option value="">Todas</option>
                <option v-for="c in contas" :key="c.id" :value="c.id">{{ c.nome }} ({{ c.banco }})</option>
            </select>
        </div>
      <div class="filter-actions">
          <button @click="aplicarFiltros" class="btn-filtrar">Filtrar</button>
          <button @click="limparFiltros" class="btn-limpar">Limpar</button>
      </div>
    </div>

    <div class="table-wrapper card" v-if="!isLoading && !error">
      <div v-if="transacoes.length">
        <table class="styled-table">
          <thead>
            <tr>
              <th>Descrição</th>
              <th>Valor</th>
              <th>Data Pag./Rec.</th>
              <th>Vencimento</th>
              <th>Tipo</th>
              <th>Status</th>
              <th>Categoria</th>
              <th>Conta</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transacao in transacoes" :key="transacao.id" :class="getRowClass(transacao)">
              <td class="col-descricao">{{ transacao.descricao }}</td>
              <td :class="['text-right', transacao.tipo === 'RECEITA' ? 'text-success' : 'text-danger']">{{ formatarValor(transacao.valor) }}</td>
              <td>{{ formatarData(transacao.data_pagamento) }}</td>
              <td>{{ formatarData(transacao.data_vencimento) }}</td>
              <td>
                 <span :class="['type-badge', transacao.tipo === 'RECEITA' ? 'type-receita' : 'type-despesa']">
                     {{ transacao.tipo === 'RECEITA' ? 'Receita' : 'Despesa' }}
                 </span>
              </td>
              <td>
                 <span :class="['status-badge', getStatusClass(transacao.status)]">
                    {{ formatarStatus(transacao.status) }}
                 </span>
              </td>
              <td>{{ transacao.categoria_detalhes?.nome || 'N/A' }}</td>
              <td>{{ transacao.conta_detalhes?.nome || 'N/A' }}</td>
              <td class="actions-cell">
                 <button @click="editarTransacao(transacao.id)" class="btn-action btn-edit" title="Editar">
                    <i class="fas fa-edit"></i>
                 </button>
                 <button @click="confirmarExclusao(transacao.id)" class="btn-action btn-delete" title="Excluir">
                    <i class="fas fa-trash-alt"></i>
                 </button>
              </td>
            </tr>
          </tbody>
        </table>
         <div class="pagination-controls" v-if="totalPages > 1">
              <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1">Anterior</button>
              <span>Página {{ currentPage }} de {{ totalPages }}</span>
              <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">Próxima</button>
          </div>
      </div>
      <div v-else class="empty-state">
          Nenhuma transação encontrada com os filtros atuais.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { format, differenceInDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Interfaces
interface Categoria { id: number; nome: string; }
interface Conta { id: number; nome: string; banco?: string; }
interface Transacao {
  id: number;
  descricao: string;
  valor: number;
  data_transacao?: string | null;
  data_pagamento?: string | null;
  data_vencimento: string;
  tipo: 'RECEITA' | 'DESPESA';
  status: 'PENDENTE' | 'PAGO' | 'VENCIDO' | 'CANCELADO';
  categoria: number;
  categoria_detalhes?: Categoria;
  conta: number | null;
  conta_detalhes?: Conta;
}

const router = useRouter();
const transacoes = ref<Transacao[]>([]);
const categorias = ref<Categoria[]>([]);
const contas = ref<Conta[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Paginação
const currentPage = ref(1);
const totalPages = ref(1);
const pageSize = 15;

// Filtros
const filtros = reactive({
  search: '',
  tipo: '',
  status: '',
  data_inicio: '',
  data_fim: '',
  categoria: '',
  conta: '',
});

// --- Funções de Formatação ---
function formatarValor(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return 'R$ 0,00';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(data: string | null | undefined): string {
  if (!data) return '-';
  try {
    return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
  } catch {
    return 'Inválida';
  }
}

function formatarStatus(status: string): string {
    const map: { [key: string]: string } = {
        'PENDENTE': 'Pendente', 'PAGO': 'Pago/Rec.', 'VENCIDO': 'Vencido', 'CANCELADO': 'Cancelado',
    };
    return map[status] || status;
}

// --- Funções de Estilização ---
function getStatusClass(status: string): string {
    switch (status) {
        case 'PENDENTE': return 'status-pendente';
        case 'PAGO': return 'status-pago';
        case 'VENCIDO': return 'status-vencido';
        case 'CANCELADO': return 'status-cancelado';
        default: return '';
    }
}
function getRowClass(transacao: Transacao): string {
    if (transacao.status === 'VENCIDO') return 'row-vencido';
    if (transacao.status === 'PENDENTE' && transacao.data_vencimento) {
        if (differenceInDays(new Date(), new Date(transacao.data_vencimento + 'T00:00:00')) > 0) {
            return 'row-vencido';
        }
        const diff = differenceInDays(new Date(transacao.data_vencimento + 'T00:00:00'), new Date());
        if (diff >= 0 && diff <= 3) {
            return 'row-vencendo';
        }
    }
    return '';
}


// --- Funções de Acesso à API ---
async function fetchTransacoes(page = 1) {
  isLoading.value = true;
  error.value = null;
  try {
     const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ordering: '-data_vencimento',
     });
     if (filtros.search) params.append('search', filtros.search);
     if (filtros.tipo) params.append('tipo', filtros.tipo);
     if (filtros.status) params.append('status', filtros.status);
     if (filtros.data_inicio) params.append('data_vencimento__gte', filtros.data_inicio);
     if (filtros.data_fim) params.append('data_vencimento__lte', filtros.data_fim);
     if (filtros.categoria) params.append('categoria', filtros.categoria);
     if (filtros.conta) params.append('conta', filtros.conta);

    const response = await apiClient.get<{ count: number; next: string | null; previous: string | null; results: Transacao[] }>(`/v1/financeiro/transacoes/?${params.toString()}`);
    transacoes.value = response.data.results;
    totalPages.value = Math.ceil(response.data.count / pageSize);
    currentPage.value = page;

  } catch (err) {
    console.error("Erro ao buscar transações:", err);
    error.value = 'Falha ao carregar as transações.';
  } finally {
    isLoading.value = false;
  }
}

async function fetchFilterOptions() {
    try {
        const [catRes, contRes] = await Promise.all([
            apiClient.get<Categoria[]>('/v1/financeiro/categorias/'),
            apiClient.get<Conta[]>('/v1/financeiro/contas/')
        ]);
        categorias.value = catRes.data;
        contas.value = contRes.data;
    } catch (err) {
        console.error("Erro ao buscar opções de filtro (categorias/contas):", err);
    }
}


// --- Funções de Ação ---
function editarTransacao(id: number) {
  router.push(`/financeiro/transacoes/editar/${id}`);
}

async function confirmarExclusao(id: number) {
    if (window.confirm("Tem certeza que deseja excluir esta transação? Esta ação não pode ser desfeita.")) {
        try {
            await apiClient.delete(`/v1/financeiro/transacoes/${id}/`);
            alert('Transação excluída com sucesso!');
            await fetchTransacoes(currentPage.value);
        } catch (err) {
            console.error("Erro ao excluir transação:", err);
            alert('Não foi possível excluir a transação.');
        }
    }
}


// --- Funções de Filtro e Paginação ---
function aplicarFiltros() {
  fetchTransacoes(1);
}

function limparFiltros() {
  filtros.search = '';
  filtros.tipo = '';
  filtros.status = '';
  filtros.data_inicio = '';
  filtros.data_fim = '';
  filtros.categoria = '';
  filtros.conta = '';
  fetchTransacoes(1);
}

function changePage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
        fetchTransacoes(page);
    }
}

// --- Inicialização ---
onMounted(() => {
  fetchFilterOptions();
  fetchTransacoes(1);
});
</script>

<style scoped>
.page-container {
  /* padding: 2rem; */ /* Removido */
  padding: 0; /* Adicionado */
}

/* Regras .view-header e .btn-primary removidas */

.loading-state, .error-message, .empty-state {
  text-align: center; padding: 2rem; color: #6c757d;
  background-color: #fff; border-radius: 8px; margin-bottom: 1.5rem;
}
.error-message { color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; }

.card { /* Estilo base para cards */
    background-color: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}

/* Filtros Melhorados com Flexbox */
.filter-controls {
  display: flex; /* Alterado para flex */
  flex-wrap: wrap; /* Permite quebrar linha */
  gap: 1rem 1.5rem; /* Espaço vertical e horizontal */
  align-items: flex-end; /* Alinha itens na base */
}
.filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    flex: 1 1 180px; /* Flex-grow, Flex-shrink, Flex-basis */
    min-width: 180px; /* Garante largura mínima */
}
.filter-group label { font-weight: 500; font-size: 0.85rem; color: #495057; }
.filter-input { padding: 0.6rem 0.8rem; border: 1px solid #ced4da; border-radius: 5px; font-size: 0.9rem; width: 100%; box-sizing: border-box; }

/* Ações dos Filtros */
.filter-actions {
    display: flex;
    gap: 0.8rem; /* Espaço entre botões */
    margin-top: 1rem; /* Adiciona espaço acima quando quebrar linha */
    flex-basis: 100%; /* Ocupa linha inteira em telas pequenas */
    justify-content: flex-end; /* Alinha botões à direita */
}
@media (min-width: 992px) { /* Em telas maiores, alinha junto aos filtros */
    .filter-actions {
        flex-basis: auto; /* Volta ao tamanho natural */
        margin-top: 0;
        margin-left: 1rem; /* Espaço à esquerda dos botões */
    }
}

.btn-filtrar, .btn-limpar {
  padding: 0.6rem 1rem; border: none; border-radius: 5px; cursor: pointer;
  font-size: 0.9rem; font-weight: 500; height: fit-content; /* Mantém alinhamento vertical */
}
.btn-filtrar { background-color: #0d6efd; color: white; }
.btn-limpar { background-color: #6c757d; color: white; }


.table-wrapper {
   overflow-x: auto;
}
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th, .styled-table td {
    padding: 0.8rem 1rem; text-align: left; border-bottom: 1px solid #dee2e6;
    vertical-align: middle; white-space: nowrap;
}
.col-descricao { white-space: normal; min-width: 250px; max-width: 400px; }

.styled-table th { background-color: #f8f9fa; font-weight: 600; color: #495057; font-size: 0.9rem; }
.styled-table tbody tr:nth-of-type(even) { background-color: #f8f9fa; }
.styled-table tbody tr:hover { background-color: #e9ecef; }

.text-right { text-align: right; }
.text-success { color: #198754; font-weight: 500; }
.text-danger { color: #dc3545; font-weight: 500; }

.type-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; color: white; display: inline-block;}
.type-receita { background-color: #198754; }
.type-despesa { background-color: #dc3545; }

.status-badge { padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; color: white; text-transform: uppercase; display: inline-block; }
.status-pendente { background-color: #ffc107; color: #333; }
.status-pago { background-color: #198754; }
.status-vencido { background-color: #dc3545; }
.status-cancelado { background-color: #6c757d; }

.row-vencido td { background-color: #f8d7da !important; }
.row-vencido:hover td { background-color: #f5c6cb !important; }
.row-vencendo td { background-color: #fff3cd !important; }
.row-vencendo:hover td { background-color: #ffeeba !important; }


.actions-cell { text-align: right; white-space: nowrap; }
.btn-action { background: none; border: none; padding: 5px 8px; margin-left: 5px; cursor: pointer; border-radius: 4px; transition: background-color 0.2s; color: #6c757d; }
.btn-action i { font-size: 1rem; vertical-align: middle; }
.btn-edit:hover { background-color: #cfe2ff; color: #0d6efd; }
.btn-delete:hover { background-color: #f8d7da; color: #dc3545; }

.pagination-controls { display: flex; justify-content: center; align-items: center; margin-top: 1.5rem; gap: 1rem; }
.pagination-controls button { padding: 8px 15px; border: 1px solid #dee2e6; background-color: #fff; border-radius: 4px; cursor: pointer; }
.pagination-controls button:disabled { cursor: not-allowed; opacity: 0.5; }
.pagination-controls span { font-size: 0.9rem; color: #495057; }

</style>
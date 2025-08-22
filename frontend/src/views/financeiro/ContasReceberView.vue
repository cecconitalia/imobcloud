<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">Contas a Receber</h1>
      <p class="page-subtitle">Gestão de receitas pendentes e pagas.</p>
    </div>

    <div v-if="stats" class="stats-grid">
        <div class="stat-card a-receber">
            <span class="stat-label">Total a Receber</span>
            <span class="stat-value">{{ formatCurrency(stats.total_a_receber) }}</span>
        </div>
        <div class="stat-card vencidas">
            <span class="stat-label">Total Vencido</span>
            <span class="stat-value">{{ formatCurrency(stats.total_vencido) }}</span>
            <span class="stat-sub-value">{{ stats.quantidade_vencidas }} conta(s)</span>
        </div>
    </div>

    <div class="content-card">
      <div class="toolbar">
        <div class="filters-wrapper">
          <div class="filter-group search-filter">
            <label for="search">Pesquisa Rápida</label>
            <input type="text" v-model="filters.search" placeholder="Descrição, cliente, contrato..." class="search-input" />
          </div>

          <div class="filter-group date-filter">
            <label for="start-date">Período de Vencimento</label>
            <div class="date-inputs">
              <input type="date" id="start-date" v-model="filters.start_date" />
              <span>até</span>
              <input type="date" id="end-date" v-model="filters.end_date" />
            </div>
          </div>

          <div class="filter-group category-filter">
            <label for="categoria">Categoria</label>
            <select id="categoria" v-model="filters.categoria">
              <option value="">Todas</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nome }}</option>
            </select>
          </div>

          <div class="filter-group actions-filter">
            <button @click="clearFilters" class="clear-filters-btn" title="Limpar todos os filtros">
              Limpar
            </button>
          </div>
        </div>
        <div class="date-shortcuts-wrapper">
          <div class="date-shortcuts">
            <button @click="setPeriod('this_month')">Este Mês</button>
            <button @click="setPeriod('next_30_days')">Próximos 30d</button>
            <button @click="setPeriod('last_month')">Mês Passado</button>
          </div>
        </div>
      </div>

      <div v-if="isLoading" class="loading-state">
        <p>A carregar contas a receber...</p>
      </div>
      
      <div v-else class="table-wrapper">
        <table class="styled-table">
          <thead>
            <tr>
              <th @click="sortBy('data_vencimento')" class="sortable">Vencimento</th>
              <th>Cliente</th>
              <th>Origem/Descrição</th>
              <th>Categoria</th>
              <th @click="sortBy('valor')" class="text-right sortable">Valor</th>
              <th class="text-center">Status</th>
              <th class="text-center">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="contas.length === 0">
              <td colspan="7" class="text-center">Nenhuma conta a receber encontrada.</td>
            </tr>
            <tr v-for="conta in contas" :key="conta.id">
              <td>{{ formatDate(conta.data_vencimento) }}</td>
              <td>{{ conta.cliente_nome }}</td>
              <td>
                <div class="descricao-cell">
                  <span>{{ conta.descricao }}</span>
                  <small v-if="conta.contrato">Contrato #{{ conta.contrato }}</small>
                </div>
              </td>
              <td>{{ conta.categoria_nome || 'N/A' }}</td>
              <td class="text-right">{{ formatCurrency(conta.valor) }}</td>
              <td class="text-center">
                <span class="status-badge" :class="getStatusClass(conta)">{{ getStatusLabel(conta) }}</span>
              </td>
              <td class="text-center actions-cell">
                <button v-if="conta.status !== 'PAGO'" @click="abrirFormularioPagamento(conta.id)" class="action-button pay-button">
                  ✓ Receber
                </button>
                <button v-if="conta.status !== 'PAGO'" @click="abrirModalBoleto(conta)" class="action-button boleto-button">
                  <i class="fas fa-barcode"></i> Boleto
                </button>
                </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <GerarBoletoModal
      v-if="isBoletoModalVisible"
      :pagamento="selectedConta"
      @close="fecharModalBoleto"
      @boletoGerado="handleBoletoGerado"
    />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router'; 
import api from '@/services/api';
import { debounce } from 'lodash';
import '@fortawesome/fontawesome-free/css/all.css';
// ==========================================================================================
// <<< IMPORTAÇÃO DO NOVO COMPONENTE >>>
import GerarBoletoModal from '@/components/GerarBoletoModal.vue';
// ==========================================================================================


// Interfaces
interface Conta { id: number; data_vencimento: string; descricao: string; categoria_nome?: string; valor: number; status: 'PENDENTE' | 'PAGO' | 'ATRASADO'; contrato: number | null; cliente_nome: string; }
interface Stats { total_a_receber: number; total_vencido: number; quantidade_vencidas: number; }
interface Categoria { id: number; nome: string; }

// State
const stats = ref<Stats | null>(null);
const categorias = ref<Categoria[]>([]);
const getInitialFilters = () => ({ start_date: '', end_date: '', categoria: '', search: '' });
const filters = ref(getInitialFilters());
const sortKey = ref('data_vencimento');
const sortOrder = ref(1);
const router = useRouter(); 
const isLoading = ref(true);
const contas = ref<Conta[]>([]);

// ==========================================================================================
// <<< NOVAS VARIÁVEIS DE ESTADO PARA O MODAL >>>
const isBoletoModalVisible = ref(false);
const selectedConta = ref<Conta | null>(null);
// ==========================================================================================

// Methods
const fetchStats = async () => {
  try {
    const response = await api.get('/v1/financeiro/transacoes/contas-pendentes-stats/');
    stats.value = response.data;
  } catch (error) { console.error('Erro ao buscar estatísticas:', error); }
};
const fetchCategorias = async () => {
  try {
    const response = await api.get('/v1/financeiro/categorias/?tipo=RECEITA');
    categorias.value = response.data;
  } catch (error) { console.error('Erro ao buscar categorias:', error); }
};
const fetchData = async () => {
  isLoading.value = true;
  try {
    const params: any = { ...filters.value, ordering: (sortOrder.value === 1 ? '' : '-') + sortKey.value };
    Object.keys(params).forEach(key => (params[key] === '' || params[key] === null) && delete params[key]);
    const response = await api.get('/v1/financeiro/transacoes/a-receber/', { params });
    contas.value = response.data;
  } catch (error) { console.error('Erro ao buscar contas a receber:', error); } 
  finally { isLoading.value = false; }
};
const debouncedFetchData = debounce(fetchData, 300);
const sortBy = (key: string) => {
  sortKey.value = key;
  sortOrder.value *= -1;
  fetchData();
};
const setPeriod = (period: 'this_month' | 'next_30_days' | 'last_month') => {
  const today = new Date();
  if (period === 'this_month') {
    filters.value.start_date = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
    filters.value.end_date = new Date(today.getFullYear(), today.getMonth() + 1, 0).toISOString().split('T')[0];
  } else if (period === 'next_30_days') {
    const futureDate = new Date();
    futureDate.setDate(today.getDate() + 30);
    filters.value.start_date = today.toISOString().split('T')[0];
    filters.value.end_date = futureDate.toISOString().split('T')[0];
  } else if (period === 'last_month') {
    filters.value.start_date = new Date(today.getFullYear(), today.getMonth() - 1, 1).toISOString().split('T')[0];
    filters.value.end_date = new Date(today.getFullYear(), today.getMonth(), 0).toISOString().split('T')[0];
  }
};
const clearFilters = () => { filters.value = getInitialFilters(); };
const abrirFormularioPagamento = (id: number) => { router.push({ name: 'transacao-editar', params: { id } }); };
const formatDate = (date: string) => new Date(date + 'T00:00:00').toLocaleDateString('pt-BR');
const formatCurrency = (val: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);
const isAtrasado = (date: string) => new Date(date + 'T00:00:00') < new Date(new Date().toDateString());
const getStatusClass = (c: Conta) => c.status === 'PAGO' ? 'status-pago' : isAtrasado(c.data_vencimento) ? 'status-atrasado' : 'status-pendente';
const getStatusLabel = (c: Conta) => c.status === 'PAGO' ? 'Pago' : isAtrasado(c.data_vencimento) ? 'Atrasado' : 'Pendente';

// ==========================================================================================
// <<< NOVAS FUNÇÕES PARA CONTROLAR O MODAL >>>
const abrirModalBoleto = (conta: Conta) => {
  selectedConta.value = conta;
  isBoletoModalVisible.value = true;
};
const fecharModalBoleto = () => {
  isBoletoModalVisible.value = false;
  selectedConta.value = null;
};
const handleBoletoGerado = () => {
  fecharModalBoleto();
  alert('Boleto gerado e registrado com sucesso!');
  fetchData(); // Atualiza a lista para refletir possíveis mudanças
};
// ==========================================================================================


// Lifecycle
watch(filters, debouncedFetchData, { deep: true });
onMounted(() => {
  fetchData();
  fetchStats();
  fetchCategorias();
});
</script>

<style scoped>
.page-container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
.header-section { margin-bottom: 2rem; }
.page-title { font-size: 2.2rem; font-weight: bold; }
.page-subtitle { font-size: 1.1rem; color: #666; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
.stat-card { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); display: flex; flex-direction: column; }
.stat-card.a-receber { border-left: 5px solid #28a745; }
.stat-card.vencidas { border-left: 5px solid #dc3545; }
.stat-label { font-size: 1rem; color: #6c757d; margin-bottom: 0.5rem; }
.stat-value { font-size: 2rem; font-weight: bold; }
.stat-sub-value { font-size: 0.9rem; color: #6c757d; margin-top: 0.25rem; }
.content-card { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.toolbar { display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #ddd; }
.filters-wrapper { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 1rem; width: 100%; }
.filter-group { display: flex; flex-direction: column; gap: 0.25rem; }
.filter-group label { font-size: 0.8rem; color: #666; }
.search-filter { flex: 2 1 250px; }
.date-filter { display: flex; flex-direction: row; align-items: center; gap: 0.5rem; flex: 1 1 350px; }
.date-inputs { display: flex; align-items: center; gap: 0.5rem; }
.date-shortcuts-wrapper { width: 100%; display: flex; justify-content: flex-start; padding-top: 0.5rem; }
.date-shortcuts { display: flex; gap: 0.5rem; }
.date-shortcuts button { background: #f0f0f0; border: 1px solid #ddd; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.category-filter { flex: 1 1 180px; }
.filter-group input, .filter-group select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; height: 38px; }
.clear-filters-btn { height: 38px; padding: 8px 15px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer; }
.table-wrapper { overflow-x: auto; }
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table thead th { background-color: #f8f9fa; padding: 12px 15px; border-bottom: 2px solid #ddd; text-align: left; }
.styled-table th.sortable { cursor: pointer; }
.styled-table tbody td { padding: 15px; border-bottom: 1px solid #eee; vertical-align: middle; }
.descricao-cell { display: flex; flex-direction: column; }
.descricao-cell span { font-weight: 500; }
.descricao-cell small { font-size: 0.8rem; color: #6c757d; }
.text-right { text-align: right; }
.text-center { text-align: center; }
.actions-cell { display: flex; gap: 0.5rem; justify-content: center; }
.status-badge { padding: 5px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
.status-pendente { background-color: #ffc107; color: #212529; }
.status-atrasado { background-color: #dc3545; }
.status-pago { background-color: #28a745; }
.action-button { padding: 6px 12px; border-radius: 5px; border: none; cursor: pointer; font-weight: 500; color: white; display: flex; align-items: center; gap: 0.5rem; }
.pay-button { background-color: #28a745; }
.boleto-button { background-color: #17a2b8; }
.loading-state { text-align: center; padding: 2rem; }
</style>
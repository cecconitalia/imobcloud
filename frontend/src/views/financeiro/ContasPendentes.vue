<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">Contas a Pagar e a Receber</h1>
      <p class="page-subtitle">Gestão de contas pendentes e pagas.</p>
    </div>

    <div class="tabs">
      <button :class="{ 'active': activeTab === 'a-pagar' }" @click="changeTab('a-pagar')">
        Contas a Pagar
      </button>
      <button :class="{ 'active': activeTab === 'a-receber' }" @click="changeTab('a-receber')">
        Contas a Receber
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>A carregar contas...</p>
    </div>

    <div v-else class="content-card">
      <table class="styled-table">
        <thead>
          <tr>
            <th>Vencimento</th>
            <th>Descrição</th>
            <th>Categoria</th>
            <th class="text-right">Valor</th>
            <th class="text-center">Status</th>
            <th class="text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="contas.length === 0">
            <td colspan="6" class="text-center">Nenhuma conta encontrada.</td>
          </tr>
          <tr v-for="conta in contas" :key="conta.id">
            <td>{{ formatDate(conta.data_vencimento) }}</td>
            <td>{{ conta.descricao }}</td>
            <td>{{ conta.categoria_nome || 'N/A' }}</td>
            <td class="text-right">{{ formatCurrency(conta.valor) }}</td>
            <td class="text-center">
              <span class="status-badge" :class="getStatusClass(conta)">
                {{ getStatusLabel(conta) }}
              </span>
            </td>
            <td class="text-center">
              <button
                v-if="conta.status !== 'PAGO'"
                @click="marcarComoPaga(conta.id)"
                class="action-button pay-button"
                title="Marcar como Paga"
              >
                ✓ Pagar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import api from '@/services/api';

interface Conta {
  id: number;
  data_vencimento: string;
  descricao: string;
  categoria_nome?: string;
  valor: number;
  status: 'PENDENTE' | 'PAGO' | 'ATRASADO';
}

const isLoading = ref(true);
const activeTab = ref<'a-pagar' | 'a-receber'>('a-pagar');
const contas = ref<Conta[]>([]);

const fetchData = async () => {
  isLoading.value = true;
  try {
    const endpoint = activeTab.value === 'a-pagar'
      ? '/v1/financeiro/transacoes/a-pagar/'
      : '/v1/financeiro/transacoes/a-receber/';
    const response = await api.get(endpoint);
    contas.value = response.data;
  } catch (error) {
    console.error(`Erro ao buscar contas (${activeTab.value}):`, error);
    // A notificação de erro foi removida daqui
  } finally {
    isLoading.value = false;
  }
};

const marcarComoPaga = async (id: number) => {
  if (confirm('Tem a certeza que deseja marcar esta conta como paga?')) {
    try {
      await api.post(`/v1/financeiro/transacoes/${id}/marcar-pago/`);
      console.log('Conta marcada como paga!'); // Usamos console.log em vez de toast
      fetchData(); 
    } catch (error) {
      console.error("Erro ao marcar como paga:", error);
      alert('Ocorreu um erro ao processar o pagamento.'); // Usamos um alert simples para o erro
    }
  }
};

const changeTab = (tabName: 'a-pagar' | 'a-receber') => {
    activeTab.value = tabName;
};

const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { day: '2-digit', month: '2-digit', year: 'numeric' };
  return new Date(dateString + 'T00:00:00').toLocaleDateString('pt-PT', options);
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
};

const isAtrasado = (dataVencimento: string): boolean => {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    return new Date(dataVencimento + 'T00:00:00') < hoje;
};

const getStatusClass = (conta: Conta) => {
  if (conta.status === 'PAGO') return 'status-pago';
  if (conta.status === 'PENDENTE' && isAtrasado(conta.data_vencimento)) return 'status-atrasado';
  return 'status-pendente';
};

const getStatusLabel = (conta: Conta) => {
    if (conta.status === 'PAGO') return 'Pago';
    if (conta.status === 'PENDENTE' && isAtrasado(conta.data_vencimento)) return 'Atrasado';
    return 'Pendente';
}

watch(activeTab, fetchData);

onMounted(fetchData);
</script>

<style scoped>
.page-container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
.header-section { margin-bottom: 2rem; text-align: left; }
.page-title { font-size: 2.2rem; font-weight: bold; }
.page-subtitle { font-size: 1.1rem; color: #666; }
.tabs { margin-bottom: 1.5rem; border-bottom: 1px solid #ddd; }
.tabs button { padding: 10px 20px; border: none; background-color: transparent; cursor: pointer; font-size: 1rem; font-weight: 500; color: #555; border-bottom: 3px solid transparent; margin-bottom: -1px; }
.tabs button.active { color: #007bff; border-bottom-color: #007bff; font-weight: bold; }
.content-card { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); }
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table thead th { background-color: #f8f9fa; color: #333; padding: 12px 15px; border-bottom: 2px solid #ddd; text-align: left; }
.styled-table tbody td { padding: 15px; border-bottom: 1px solid #eee; }
.text-right { text-align: right; }
.text-center { text-align: center; }
.status-badge { padding: 5px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; color: white; text-transform: uppercase; }
.status-pendente { background-color: #ffc107; color: #212529; }
.status-atrasado { background-color: #dc3545; }
.status-pago { background-color: #28a745; }
.action-button { padding: 6px 12px; border-radius: 5px; border: none; cursor: pointer; font-weight: 500; color: white; }
.pay-button { background-color: #28a745; }
.pay-button:hover { background-color: #218838; }
.loading-state { text-align: center; padding: 2rem; }
</style>
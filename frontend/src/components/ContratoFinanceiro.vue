<template>
  <div class="financeiro-container">
    <h3 class="financeiro-title">Gestão Financeira do Contrato</h3>

    <div v-if="isLoading" class="loading-message">A carregar pagamentos...</div>
    <div v-else-if="pagamentos.length === 0" class="no-data-message">
      Nenhum pagamento registado para este contrato.
    </div>
    <table v-else class="pagamentos-table">
      <thead>
        <tr>
          <th>Vencimento</th>
          <th>Valor</th>
          <th>Status</th>
          <th>Data de Pagamento</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="pagamento in pagamentos" :key="pagamento.id" :class="getStatusClass(pagamento)">
          <td>{{ formatarData(pagamento.data_vencimento) }}</td>
          <td>{{ formatarValor(pagamento.valor) }}</td>
          <td>
            <span class="status-badge" :class="`status-${pagamento.status.toLowerCase()}`">
              {{ pagamento.status }}
            </span>
          </td>
          <td>{{ pagamento.data_pagamento ? formatarData(pagamento.data_pagamento) : '-' }}</td>
          <td class="actions-cell">
            <button
              v-if="pagamento.status === 'PENDENTE' || pagamento.status === 'ATRASADO'"
              @click="marcarComoPago(pagamento)"
              class="btn-pagar"
              :disabled="isSubmitting"
            >
              Marcar como Pago
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, computed } from 'vue';
import apiClient from '@/services/api';

const props = defineProps({
  contrato: {
    type: Object,
    required: true
  }
});

const pagamentos = ref<any[]>([]);
const isLoading = ref(true);
const isSubmitting = ref(false);

// Usamos um computed property para ter a lista de pagamentos reativa
const listaDePagamentos = computed(() => props.contrato.pagamentos || []);

async function carregarPagamentos() {
    isLoading.value = true;
    // Os pagamentos já são passados via props, então apenas atualizamos o estado
    pagamentos.value = props.contrato.pagamentos || [];
    // Verificamos o status de cada pagamento
    verificarStatusPagamentos();
    isLoading.value = false;
}

// Função para marcar um pagamento como "PAGO"
async function marcarComoPago(pagamento: any) {
  if (!window.confirm(`Confirma o recebimento de ${formatarValor(pagamento.valor)}?`)) return;
  
  isSubmitting.value = true;
  try {
    const hoje = new Date().toISOString().split('T')[0];
    await apiClient.patch(`/v1/contratos/pagamentos/${pagamento.id}/`, {
      status: 'PAGO',
      data_pagamento: hoje
    });
    // Atualiza o objeto localmente para feedback imediato
    pagamento.status = 'PAGO';
    pagamento.data_pagamento = hoje;
  } catch (error) {
    console.error("Erro ao marcar como pago:", error);
    alert('Ocorreu um erro ao atualizar o pagamento.');
  } finally {
    isSubmitting.value = false;
  }
}

// Verifica se algum pagamento pendente está atrasado
function verificarStatusPagamentos() {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0); // Zera a hora para comparar apenas a data

    pagamentos.value.forEach(p => {
        const dataVencimento = new Date(p.data_vencimento);
        if (p.status === 'PENDENTE' && dataVencimento < hoje) {
            p.status = 'ATRASADO';
        }
    });
}

onMounted(() => {
  carregarPagamentos();
});

// Funções de formatação
function formatarData(data: string) {
  if (!data) return '-';
  const dataObj = new Date(data);
  // Adiciona um dia para corrigir problemas de fuso horário na exibição
  dataObj.setDate(dataObj.getDate() + 1);
  return dataObj.toLocaleDateString('pt-BR');
}
function formatarValor(valor: number) {
  return parseFloat(valor.toString()).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
function getStatusClass(pagamento: any) {
  if (pagamento.status === 'ATRASADO') return 'atrasado-row';
  if (pagamento.status === 'PAGO') return 'pago-row';
  return '';
}
</script>

<style scoped>
.financeiro-container {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}
.financeiro-title {
  margin-bottom: 1.5rem;
}
.pagamentos-table {
  width: 100%;
  border-collapse: collapse;
}
.pagamentos-table th, .pagamentos-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
}
.pagamentos-table th {
  background-color: #f2f2f2;
}
.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: bold;
  color: white;
}
.status-pendente { background-color: #ffc107; color: #333; }
.status-pago { background-color: #28a745; }
.status-atrasado { background-color: #dc3545; }

.atrasado-row {
    background-color: #f8d7da; /* Vermelho claro */
}
.pago-row {
    background-color: #d4edda; /* Verde claro */
}

.actions-cell {
  text-align: center;
}
.btn-pagar {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-pagar:disabled {
  background-color: #a0cfff;
}
</style>
<template>
  <div class="financeiro-dashboard-container">
    <div v-if="isLoading" class="loading-message">
      A carregar dados financeiros...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="stats" class="stats-grid">
      <div class="stat-card revenue">
        <h3 class="stat-title">Receitas Pagas (Mês)</h3>
        <p class="stat-value">{{ formatarValor(stats.a_receber.pago_mes_atual) }}</p>
      </div>
      <div class="stat-card pending-revenue">
        <h3 class="stat-title">A Receber (Pendente)</h3>
        <p class="stat-value">{{ formatarValor(stats.a_receber.pendente) }}</p>
      </div>
      <div class="stat-card expenses">
        <h3 class="stat-title">Despesas Pagas (Mês)</h3>
        <p class="stat-value">{{ formatarValor(stats.a_pagar.pago_mes_atual) }}</p>
      </div>
      <div class="stat-card pending-expenses">
        <h3 class="stat-title">A Pagar (Pendente)</h3>
        <p class="stat-value">{{ formatarValor(stats.a_pagar.pendente) }}</p>
      </div>
      <div class="stat-card balance">
        <h3 class="stat-title">Saldo Previsto</h3>
        <p class="stat-value">{{ formatarValor(stats.saldo_previsto) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

// Interface baseada na estrutura de dados que o endpoint /stats/ parece retornar
interface StatsFinanceiro {
  a_receber: {
    pago_mes_atual: number;
    pendente: number;
  };
  a_pagar: {
    pago_mes_atual: number;
    pendente: number;
  };
  saldo_previsto: number; // Campo que estava sendo usado no template
}


const stats = ref<StatsFinanceiro | null>(null); // Tipagem aplicada
const isLoading = ref(true);
const error = ref<string | null>(null);

function formatarValor(valor: number | null | undefined): string { // Ajustado para aceitar undefined também
  if (valor === null || valor === undefined) return 'R$ 0,00';
  // Removido parseFloat(valor.toString()) pois já esperamos number
  return valor.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

async function fetchStats() {
  isLoading.value = true;
  error.value = null; // Limpa erro anterior
  try {
    // Usando o endpoint que funcionava anteriormente
    const response = await apiClient.get<StatsFinanceiro>('/v1/financeiro/transacoes/stats/'); // Tipagem aplicada à resposta
    stats.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar estatísticas financeiras:", err);
    error.value = 'Não foi possível carregar as estatísticas financeiras.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.financeiro-dashboard-container {
  /* padding: 2rem; */ /* Removido */
  padding: 0; /* Adicionado */
}

/* Regras .view-header, .header-actions, .btn-primary, .btn-secondary removidas */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
.stat-card {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}
/* Cores das bordas */
.stat-card.revenue {
  border-left: 5px solid #28a745; /* Verde */
}
.stat-card.pending-revenue {
  border-left: 5px solid #ffc107; /* Amarelo */
}
.stat-card.expenses {
  border-left: 5px solid #dc3545; /* Vermelho */
}
.stat-card.pending-expenses {
    border-left: 5px solid #fd7e14; /* Laranja */
}
.stat-card.balance {
  border-left: 5px solid #007bff; /* Azul */
}

.stat-title {
  font-size: 1rem;
  color: #6c757d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #343a40;
  margin: 0;
}
.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
</style>
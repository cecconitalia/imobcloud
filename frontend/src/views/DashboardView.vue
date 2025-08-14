<template>
  <div class="dashboard-container">
    <header class="view-header">
      <h1>Dashboard</h1>
    </header>

    <div v-if="isLoading" class="loading-message">
      A carregar estatísticas...
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="stats" class="stats-grid">
      <div class="stat-card">
        <h3 class="stat-title">Imóveis Ativos</h3>
        <p class="stat-value">{{ stats.imoveis_ativos }}</p>
      </div>
      <div class="stat-card">
        <h3 class="stat-title">Clientes Ativos</h3>
        <p class="stat-value">{{ stats.clientes_ativos }}</p>
      </div>
      <div class="stat-card">
        <h3 class="stat-title">Contratos Ativos</h3>
        <p class="stat-value">{{ stats.contratos_ativos }}</p>
      </div>
      <div class="stat-card">
        <h3 class="stat-title">Novos Clientes (Últimos 30 dias)</h3>
        <p class="stat-value">{{ stats.novos_clientes_30d }}</p>
      </div>
      
      <div class="stat-card financial">
        <h3 class="stat-title">Faturamento (Últimos 30 dias)</h3>
        <p class="stat-value">{{ formatCurrency(stats.faturamento_30d) }}</p>
      </div>
      <div class="stat-card financial">
        <h3 class="stat-title">Pagamentos Pendentes</h3>
        <p class="stat-value">{{ formatCurrency(stats.pagamentos_pendentes) }}</p>
      </div>
      <div class="stat-card financial">
        <h3 class="stat-title">Valor em Vendas (Ativas)</h3>
        <p class="stat-value">{{ formatCurrency(stats.total_vendas_ativas) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const stats = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

function formatCurrency(value: number) {
  if (typeof value !== 'number') {
    return 'R$ 0,00';
  }
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

onMounted(async () => {
  try {
    // A CORREÇÃO ESTÁ AQUI:
    // Removemos a palavra 'core' do URL.
    const response = await apiClient.get('/v1/stats/');
    stats.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar estatísticas:", err);
    error.value = 'Não foi possível carregar as estatísticas.';
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
.stat-card {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  border-left: 5px solid #007bff;
}
.stat-card.financial {
  border-left-color: #28a745;
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
</style>
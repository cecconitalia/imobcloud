<template>
  <div class="dashboard-container">
    <header class="view-header">
      <h1 class="main-title">Dashboard</h1>
      <p class="subtitle">Visão geral do desempenho da sua imobiliária.</p>
    </header>

    <div v-if="isLoading" class="loading-message">
      A carregar estatísticas...
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="stats" class="content-wrapper">
      <div class="stats-grid">
        <div class="stat-card primary-card">
          <div class="icon-wrapper"><i class="fas fa-home"></i></div>
          <h3 class="stat-title">Imóveis Ativos</h3>
          <p class="stat-value">{{ stats.imoveis_ativos }}</p>
          <router-link to="/imoveis" class="card-link">Gerir Imóveis <i class="fas fa-arrow-right"></i></router-link>
        </div>
        <div class="stat-card primary-card">
          <div class="icon-wrapper"><i class="fas fa-users"></i></div>
          <h3 class="stat-title">Clientes Ativos</h3>
          <p class="stat-value">{{ stats.clientes_ativos }}</p>
          <router-link to="/clientes" class="card-link">Gerir Clientes <i class="fas fa-arrow-right"></i></router-link>
        </div>
        <div class="stat-card primary-card">
          <div class="icon-wrapper"><i class="fas fa-file-signature"></i></div>
          <h3 class="stat-title">Contratos Ativos</h3>
          <p class="stat-value">{{ stats.contratos_ativos }}</p>
          <router-link to="/contratos" class="card-link">Gerir Contratos <i class="fas fa-arrow-right"></i></router-link>
        </div>
        <div class="stat-card primary-card">
          <div class="icon-wrapper"><i class="fas fa-user-plus"></i></div>
          <h3 class="stat-title">Novos Clientes (30 dias)</h3>
          <p class="stat-value">{{ stats.novos_clientes_30d }}</p>
          <router-link to="/clientes" class="card-link">Ver Clientes <i class="fas fa-arrow-right"></i></router-link>
        </div>
      </div>

      <div class="financial-stats-grid">
        <div class="stat-card financial-card">
          <div class="icon-wrapper"><i class="fas fa-dollar-sign"></i></div>
          <h3 class="stat-title">Faturamento (30 dias)</h3>
          <p class="stat-value">{{ formatCurrency(stats.faturamento_30d) }}</p>
        </div>
        <div class="stat-card financial-card">
          <div class="icon-wrapper"><i class="fas fa-hand-holding-usd"></i></div>
          <h3 class="stat-title">Contas a Receber</h3>
          <p class="stat-value">{{ formatCurrency(stats.pagamentos_pendentes) }}</p>
        </div>
        <div class="stat-card financial-card">
          <div class="icon-wrapper"><i class="fas fa-chart-line"></i></div>
          <h3 class="stat-title">Valor em Vendas Ativas</h3>
          <p class="stat-value">{{ formatCurrency(stats.total_vendas_ativas) }}</p>
        </div>
      </div>

      <div class="action-buttons">
          <router-link to="/financeiro/contas-pendentes" class="btn-action">
              <i class="fas fa-calendar-times"></i> Contas Pendentes
          </router-link>
          <router-link to="/financeiro/dre" class="btn-action">
              <i class="fas fa-chart-bar"></i> Relatório DRE
          </router-link>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

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
  padding: 1.5rem;
}
.view-header {
  text-align: left;
  margin-bottom: 1.5rem;
}
.main-title {
    font-size: 2rem;
    margin: 0;
}
.subtitle {
    font-size: 1rem;
    color: #6c757d;
    margin-top: 0.25rem;
}
.loading-message, .error-message {
  text-align: center;
  padding: 1.5rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.content-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}
.stats-grid, .financial-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}
.stat-card {
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: left;
}
.primary-card {
    border-left: 4px solid #007bff;
}
.financial-card {
    border-left: 4px solid #28a745;
}
.icon-wrapper {
    color: #007bff;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}
.financial-card .icon-wrapper {
    color: #28a745;
}
.stat-title {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #343a40;
  margin: 0.25rem 0 0 0;
}
.card-link {
    margin-top: 0.75rem;
    font-size: 0.8rem;
    color: #007bff;
    text-decoration: none;
    font-weight: bold;
    transition: color 0.2s;
}
.card-link:hover {
    color: #0056b3;
}
.action-buttons {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 1rem;
}
.btn-action {
    background-color: #f8f9fa;
    color: #495057;
    border: 1px solid #ced4da;
    padding: 10px 20px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: bold;
    font-size: 0.9rem;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.btn-action i {
    font-size: 1rem;
    color: #007bff;
}
.btn-action:hover {
    background-color: #e2e6ea;
}

@media (max-width: 768px) {
  .stats-grid, .financial-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
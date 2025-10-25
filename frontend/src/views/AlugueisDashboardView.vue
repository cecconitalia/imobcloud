<template>
  <div class="dashboard-alugueis-container">
    <header class="view-header">
      <h1>Dashboard de Aluguéis</h1>
      <p class="subtitle">Visão geral e gestão de contratos de aluguel e pagamentos.</p>
    </header>

    <div v-if="isLoading" class="loading-message">
      A carregar dados...
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else class="content-wrapper">
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-file-contract stat-icon"></i>
          <div class="stat-info">
            <span class="stat-label">Contratos de Aluguel Ativos</span>
            <span class="stat-value">{{ stats.contratos_ativos }}</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-money-check-alt stat-icon"></i>
          <div class="stat-info">
            <span class="stat-label">Aluguéis a Vencer (Próximos 7 dias)</span>
            <span class="stat-value">{{ stats.alugueis_a_vencer }}</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-exclamation-triangle stat-icon"></i>
          <div class="stat-info">
            <span class="stat-label">Aluguéis Atrasados</span>
            <span class="stat-value">{{ stats.alugueis_atrasados }}</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-hand-holding-usd stat-icon"></i>
          <div class="stat-info">
            <span class="stat-label">Valor Recebido (mês atual)</span>
            <span class="stat-value">{{ formatarValor(stats.valor_recebido_mes) }}</span>
          </div>
        </div>
      </div>

      <div class="section-card">
        <h3 class="section-title">Aluguéis Próximos de Vencer</h3>
        <div v-if="stats.proximos_alugueis && stats.proximos_alugueis.length > 0" class="tabela-wrapper">
          <table class="tabela-list">
            <thead>
              <tr>
                <th>Imóvel</th>
                <th>Inquilino</th>
                <th>Vencimento</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="aluguel in stats.proximos_alugueis" :key="aluguel.id">
                <td>{{ aluguel.imovel_titulo }}</td>
                <td>{{ aluguel.inquilino_nome }}</td>
                <td>{{ aluguel.data_vencimento }}</td>
                <td>{{ formatarValor(aluguel.valor) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="no-data">Nenhum aluguel a vencer nos próximos 7 dias.</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

// CORREÇÃO: Inicializa stats com valores padrão para evitar o erro de `undefined`
const stats = ref<any>({
  contratos_ativos: 0,
  alugueis_a_vencer: 0,
  alugueis_atrasados: 0,
  valor_recebido_mes: 0,
  proximos_alugueis: []
});
const isLoading = ref(true);
const error = ref<string | null>(null);

function formatarValor(valor: number) {
  if (typeof valor !== 'number') return 'R$ 0,00';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

onMounted(async () => {
  try {
    const response = await apiClient.get('/v1/alugueis/dashboard-stats/');
    stats.value = response.data;
  } catch (err) {
    console.error("Erro ao carregar dashboard de aluguéis:", err);
    error.value = 'Não foi possível carregar as informações do dashboard.';
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.dashboard-alugueis-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 2rem;
}
.view-header h1 {
  font-size: 2.5rem;
  margin: 0;
}
.subtitle {
  color: #6c757d;
  font-size: 1.1rem;
}
.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
.stat-card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.stat-icon {
  font-size: 3rem;
  color: #007bff;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-label {
  font-size: 1rem;
  color: #6c757d;
}
.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #343a40;
}
.section-card {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.section-title {
  font-size: 1.5rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #007bff;
  padding-bottom: 0.5rem;
}
.tabela-wrapper {
  overflow-x: auto;
}
.tabela-list {
  width: 100%;
  border-collapse: collapse;
}
.tabela-list th, .tabela-list td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}
.tabela-list th {
  background-color: #f8f9fa;
  font-weight: bold;
}
.tabela-list tbody tr:hover {
  background-color: #f1f3f5;
}
.no-data {
  text-align: center;
  color: #6c757d;
  padding: 1rem;
}
</style>
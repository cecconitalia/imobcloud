<template>
  <div class="relatorios-container">
    <header class="view-header">
      <h1>Relatórios de Desempenho</h1>
    </header>

    <div v-if="isLoading" class="loading-message">A carregar relatórios...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="relatorios" class="relatorios-grid">
      <div class="report-card">
        <h3 class="card-title">Funil de Vendas</h3>
        <ul class="funil-list">
          <li v-for="fase in relatorios.funil_vendas.fases" :key="fase.fase">
            <span>{{ getFaseNome(fase.fase) }}</span>
            <strong>{{ fase.total }}</strong>
          </li>
          <li class="total-item">
            <span>Total de Oportunidades</span>
            <strong>{{ relatorios.funil_vendas.total_oportunidades }}</strong>
          </li>
        </ul>
      </div>

      <div class="report-card">
        <h3 class="card-title">Origem dos Leads</h3>
        <ul class="origem-list">
          <li v-for="fonte in relatorios.origem_leads" :key="fonte.fonte">
            <span>{{ getFonteNome(fonte.fonte) }}</span>
            <strong>{{ fonte.total }}</strong>
          </li>
        </ul>
      </div>

      <div class="report-card full-width">
        <h3 class="card-title">Desempenho dos Corretores</h3>
        <table class="corretores-table">
          <thead>
            <tr>
              <th>Corretor</th>
              <th>Oportunidades Ganhas</th>
              <th>Oportunidades Perdidas</th>
              <th>Valor Total Ganho (R$)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="corretor in relatorios.desempenho_corretores" :key="corretor.corretor_id">
              <td>{{ corretor.nome }}</td>
              <td>{{ corretor.oportunidades_ganhas }}</td>
              <td>{{ corretor.oportunidades_perdidas }}</td>
              <td>{{ formatCurrency(corretor.valor_total_ganho) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const relatorios = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Mapeamento para nomes mais amigáveis
const nomesFases: { [key: string]: string } = {
  'LEAD': 'Novo Lead',
  'CONTATO': 'Primeiro Contato',
  'VISITA': 'Visita Agendada',
  'PROPOSTA': 'Proposta Enviada',
  'NEGOCIACAO': 'Em Negociação',
  'GANHO': 'Negócio Ganho',
  'PERDIDO': 'Negócio Perdido',
};

const nomesFontes: { [key: string]: string } = {
  'SITE': 'Site',
  'INDICACAO': 'Indicação',
  'ANUNCIO': 'Anúncio Online',
  'CLIENTE_ANTIGO': 'Cliente Antigo',
  'OUTRO': 'Outro',
};

function getFaseNome(faseId: string): string {
  return nomesFases[faseId] || faseId;
}

function getFonteNome(fonteId: string | null): string {
  if (!fonteId) return 'Não informada';
  return nomesFontes[fonteId] || fonteId;
}

function formatCurrency(value: number) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

async function fetchRelatorios() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/clientes/relatorios/');
    relatorios.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar relatórios:", err);
    error.value = err.response?.data?.detail || 'Não foi possível carregar os relatórios.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchRelatorios();
});
</script>

<style scoped>
.relatorios-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.relatorios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}
.report-card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.report-card.full-width {
  grid-column: 1 / -1;
}
.card-title {
  margin-top: 0;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}
.funil-list, .origem-list {
  list-style: none;
  padding: 0;
}
.funil-list li, .origem-list li {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f8f9fa;
}
.funil-list li.total-item {
  font-weight: bold;
  color: #007bff;
  border-top: 2px solid #e9ecef;
  margin-top: 0.5rem;
}
.corretores-table {
  width: 100%;
  border-collapse: collapse;
}
.corretores-table th, .corretores-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}
.corretores-table th {
  background-color: #f2f2f2;
}
.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
}
.error-message { color: red; }
</style>
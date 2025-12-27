<template>
  <div class="relatorios-container">
    <header class="view-header">
      <h1>Relatórios da Imobiliária</h1>
    </header>

    <div v-if="isLoading" class="loading-message">
      A carregar dados dos relatórios...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else class="relatorios-wrapper">
      <div class="relatorio-card">
        <h3 class="card-title">Resumo do Mês Atual</h3>
        <div class="summary-grid">
          <div class="summary-item">
            <span>Novas Oportunidades:</span>
            <strong>{{ relatorios.sumario_mes_atual?.novas_oportunidades || 0 }}</strong>
          </div>
          <div class="summary-item">
            <span>Oportunidades Ganhas:</span>
            <strong>{{ relatorios.sumario_mes_atual?.oportunidades_ganhas || 0 }}</strong>
          </div>
          <div class="summary-item">
            <span>Oportunidades Perdidas:</span>
            <strong>{{ relatorios.sumario_mes_atual?.oportunidades_perdidas || 0 }}</strong>
          </div>
        </div>
      </div>

      <div class="relatorio-card">
        <h3 class="card-title">Oportunidades por Mês (Ano Atual)</h3>
        <p class="chart-description">Negócios abertos, ganhos e perdidos mês a mês.</p>
        <div class="chart-container">
          <canvas ref="oportunidadesChartCanvas"></canvas>
        </div>
      </div>

      <div class="relatorio-card">
        <h3 class="card-title">Funil de Vendas por Origem</h3>
        <p class="chart-description">Distribuição das oportunidades por fonte de lead.</p>
        <div class="chart-container">
          <canvas ref="origemChartCanvas"></canvas>
        </div>
      </div>

      <div class="relatorio-card">
        <h3 class="card-title">Desempenho dos Corretores</h3>
        <div class="tabela-wrapper">
          <table class="tabela-desempenho">
            <thead>
              <tr>
                <th>Corretor</th>
                <th>Oportunidades Abertas</th>
                <th>Oportunidades Ganhas</th>
                <th>Oportunidades Perdidas</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="corretor in relatorios.corretores_desempenho" :key="corretor.id">
                <td>{{ corretor.nome_corretor }}</td>
                <td>{{ corretor.oportunidades_abertas }}</td>
                <td>{{ corretor.oportunidades_ganhas }}</td>
                <td>{{ corretor.oportunidades_perdidas }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import Chart from 'chart.js/auto';

const relatorios = ref<any>({
  sumario_mes_atual: {},
  oportunidades_por_mes: [],
  origem_oportunidades: [],
  corretores_desempenho: [],
});

const isLoading = ref(true);
const error = ref<string | null>(null);

const oportunidadesChartCanvas = ref<HTMLCanvasElement | null>(null);
const origemChartCanvas = ref<HTMLCanvasElement | null>(null);

let oportunidadesChart: Chart | null = null;
let origemChart: Chart | null = null;

function renderCharts() {
  if (oportunidadesChartCanvas.value) {
    const ctx = oportunidadesChartCanvas.value.getContext('2d');
    if (ctx) {
      if (oportunidadesChart) oportunidadesChart.destroy();
      oportunidadesChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: relatorios.value.oportunidades_por_mes.map((r: any) => r.mes),
          datasets: [
            {
              label: 'Abertas',
              data: relatorios.value.oportunidades_por_mes.map((r: any) => r.abertas),
              backgroundColor: '#4DA3FF',
            },
            {
              label: 'Ganhos',
              data: relatorios.value.oportunidades_por_mes.map((r: any) => r.ganhas),
              backgroundColor: '#28a745',
            },
            {
              label: 'Perdidas',
              data: relatorios.value.oportunidades_por_mes.map((r: any) => r.perdidas),
              backgroundColor: '#dc3545',
            },
          ],
        },
        options: {
          responsive: true,
        },
      });
    }
  }

  if (origemChartCanvas.value) {
    const ctx = origemChartCanvas.value.getContext('2d');
    if (ctx) {
      if (origemChart) origemChart.destroy();
      origemChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: relatorios.value.origem_oportunidades.map((r: any) => r.origem),
          datasets: [
            {
              data: relatorios.value.origem_oportunidades.map((r: any) => r.total),
              backgroundColor: ['#4DA3FF', '#28a745', '#ffc107', '#dc3545', '#6c757d'],
            },
          ],
        },
        options: {
          responsive: true,
        },
      });
    }
  }
}

async function fetchRelatorios() {
  isLoading.value = true;
  try {
    // AQUI ESTÁ A CORREÇÃO: URL alterada para o endpoint correto
    const response = await apiClient.get('/v1/relatorios/');
    relatorios.value = response.data;
    renderCharts();
  } catch (err) {
    console.error("Erro ao carregar relatórios:", err);
    error.value = 'Não foi possível carregar os relatórios.';
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
  margin-bottom: 2rem;
}
.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.relatorios-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}
.relatorio-card {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.card-title {
  font-size: 1.5rem;
  margin-top: 0;
  margin-bottom: 1rem;
  border-bottom: 2px solid #007bff;
  padding-bottom: 0.5rem;
}
.summary-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 1.1rem;
}
.chart-description {
  color: #6c757d;
}
.chart-container {
  height: 300px;
}
.tabela-wrapper {
  overflow-x: auto;
}
.tabela-desempenho {
  width: 100%;
  border-collapse: collapse;
}
.tabela-desempenho th, .tabela-desempenho td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}
.tabela-desempenho th {
  background-color: #f8f9fa;
  font-weight: bold;
}
</style>
<template>
  <div class="relatorios-container">
    <header class="view-header">
      <h1>Relatórios de Desempenho</h1>
    </header>

    <div v-if="isLoading" class="loading-message">
      <p>A carregar relatórios...</p>
    </div>
    
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-if="relatorios.fases && relatorios.fases.length > 0" class="report-section">
      <div class="chart-container">
        <canvas id="oportunidadesFunilChart"></canvas>
      </div>
    </div>
    
    <div v-if="!isLoading && (!relatorios.fases || relatorios.fases.length === 0) && !error" class="no-data-message">
      <p>Nenhum dado de relatório encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const relatorios = ref<any>({});
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchRelatorios() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/clientes/relatorios/');
    relatorios.value = response.data;
    if (relatorios.value.fases && relatorios.value.fases.length > 0) {
      renderFunnelChart(relatorios.value.fases);
    }
  } catch (err: any) {
    console.error('Erro ao buscar relatórios:', err);
    if (err.response && err.response.status === 403) {
      error.value = 'Você não tem permissão para executar essa ação.';
    } else {
      error.value = 'Ocorreu um erro ao carregar os dados dos relatórios.';
    }
  } finally {
    isLoading.value = false;
  }
}

function renderFunnelChart(data: any[]) {
  const ctx = document.getElementById('oportunidadesFunilChart') as HTMLCanvasElement;
  if (!ctx) return;

  const labels = data.map(item => {
    switch (item.fase) {
      case 'LEAD': return 'Lead';
      case 'CONTATO': return 'Contato';
      case 'VISITA': return 'Visita';
      case 'PROPOSTA': return 'Proposta';
      case 'NEGOCIACAO': return 'Negociação';
      case 'GANHO': return 'Ganho';
      case 'PERDIDO': return 'Perdido';
      default: return item.fase;
    }
  });

  const chartData = data.map(item => item.total);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Número de Oportunidades',
        data: chartData,
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(40, 167, 69, 0.6)', // Ganho
          'rgba(220, 53, 69, 0.6)' // Perdido
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(40, 167, 69, 1)',
          'rgba(220, 53, 69, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Número de Oportunidades'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Fase'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Funil de Vendas'
        }
      }
    }
  });
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
  text-align: center;
}
.report-section {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.chart-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}
.loading-message, .error-message, .no-data-message {
  text-align: center;
  padding: 2rem;
}
.error-message {
  color: #dc3545;
  font-weight: bold;
}
</style>
<template>
  <div class="financeiro-dashboard-container">
    
    <div class="header-actions-compact">
      <router-link :to="{ name: 'transacao-nova', query: { tipo: 'RECEITA' } }" class="btn-primary">
        <i class="fas fa-plus"></i> Receita
      </router-link>
      <router-link :to="{ name: 'transacao-nova', query: { tipo: 'DESPESA' } }" class="btn-secondary">
        <i class="fas fa-minus"></i> Despesa
      </router-link>
      <router-link :to="{ name: 'dre' }" class="btn-info">
        <i class="fas fa-file-alt"></i> Ver DRE
      </router-link>
    </div>
    
    <div v-if="isLoading" class="loading-message">
      <div class="spinner"></div>
      <p>A carregar dados financeiros...</p>
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="stats" class="dashboard-content">
        
      <div class="group-section">
        <h3 class="group-title"><i class="fas fa-cash-register"></i> Caixa do Mês (Realizado)</h3>
        <div class="stats-grid">
          <div class="stat-card revenue">
            <h4 class="card-title">Receitas (Entradas)</h4>
            <p class="card-value text-success">{{ formatarValor(stats.a_receber.pago_mes_atual) }}</p>
          </div>
          
          <div class="stat-card expense">
            <h4 class="card-title">Despesas (Saídas)</h4>
            <p class="card-value text-danger">{{ formatarValor(stats.a_pagar.pago_mes_atual) }}</p>
          </div>
            
          <div :class="['stat-card highlight-card', saldoCaixa >= 0 ? 'net-positive' : 'net-negative']">
            <h4 class="card-title">Saldo em Caixa</h4>
            <p class="card-value">{{ formatarValor(saldoCaixa) }}</p>
            <small class="card-subtitle">Receitas - Despesas</small>
          </div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-card">
          <h4>Balanço Mensal</h4>
          <div class="chart-wrapper">
            <canvas ref="barChartCanvas"></canvas>
          </div>
        </div>
        <div class="chart-card">
          <h4>Proporção E/S</h4>
          <div class="chart-wrapper">
            <canvas ref="doughnutChartCanvas"></canvas>
          </div>
        </div>
      </div>

      <div class="group-section mt-4">
        <h3 class="group-title"><i class="fas fa-calendar-alt"></i> Contas Pendentes (Futuro)</h3>
        <div class="stats-grid">
          <div class="stat-card pending">
            <h4 class="card-title">A Receber</h4>
            <p class="card-value text-warning">{{ formatarValor(stats.a_receber.pendente) }}</p>
          </div>
            
          <div class="stat-card pending">
            <h4 class="card-title">A Pagar</h4>
            <p class="card-value text-muted">{{ formatarValor(stats.a_pagar.pendente) }}</p>
          </div>

          <div :class="['stat-card', (stats.saldo_previsto ?? 0) >= 0 ? 'balance-positive' : 'balance-negative']">
            <h4 class="card-title">Saldo da Previsão</h4>
            <p class="card-value">{{ formatarValor(stats.saldo_previsto) }}</p>
            <small class="card-subtitle">Fluxo Futuro</small>
          </div>
        </div>
      </div>
    
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue';
import apiClient from '@/services/api';
import Chart from 'chart.js/auto';
import '@fortawesome/fontawesome-free/css/all.css';

// Interfaces
interface StatsData {
    pendente: number;
    pago_mes_atual: number;
}
interface StatsFinanceiro {
    a_receber: StatsData;
    a_pagar: StatsData;
    saldo_previsto: number;
}

const stats = ref<StatsFinanceiro | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

// Referências para os Canvas
const barChartCanvas = ref<HTMLCanvasElement | null>(null);
const doughnutChartCanvas = ref<HTMLCanvasElement | null>(null);
let barChartInstance: Chart | null = null;
let doughnutChartInstance: Chart | null = null;

// Computado: Saldo de Caixa (Receita Paga - Despesa Paga)
const saldoCaixa = computed(() => {
  if (!stats.value) return 0;
  return stats.value.a_receber.pago_mes_atual - stats.value.a_pagar.pago_mes_atual;
});

const formatarValor = (valor: number | null | undefined): string => {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

async function fetchStats() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<StatsFinanceiro>('/v1/financeiro/transacoes/stats/');
    stats.value = response.data;
    
    // Renderiza gráficos após o DOM atualizar
    nextTick(() => {
      renderCharts();
    });

  } catch (err) {
    console.error("Erro ao buscar estatísticas:", err);
    error.value = 'Não foi possível carregar as estatísticas financeiras.';
  } finally {
    isLoading.value = false;
  }
}

function renderCharts() {
  if (!stats.value) return;

  const receitas = stats.value.a_receber.pago_mes_atual;
  const despesas = stats.value.a_pagar.pago_mes_atual;

  // 1. Gráfico de Barras (Comparativo)
  if (barChartCanvas.value) {
    if (barChartInstance) barChartInstance.destroy();
    
    barChartInstance = new Chart(barChartCanvas.value, {
      type: 'bar',
      data: {
        labels: ['Receitas', 'Despesas'],
        datasets: [{
          label: 'Valores do Mês (R$)',
          data: [receitas, despesas],
          backgroundColor: [
            'rgba(40, 167, 69, 0.7)', // Verde
            'rgba(220, 53, 69, 0.7)'  // Vermelho
          ],
          borderColor: [
            'rgba(40, 167, 69, 1)',
            'rgba(220, 53, 69, 1)'
          ],
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
             callbacks: {
                label: (context) => formatarValor(Number(context.raw))
             }
          }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  }

  // 2. Gráfico de Rosca (Proporção)
  if (doughnutChartCanvas.value) {
    if (doughnutChartInstance) doughnutChartInstance.destroy();

    doughnutChartInstance = new Chart(doughnutChartCanvas.value, {
      type: 'doughnut',
      data: {
        labels: ['Entradas', 'Saídas'],
        datasets: [{
          data: [receitas, despesas],
          backgroundColor: [
            '#28a745',
            '#dc3545'
          ],
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
             callbacks: {
                label: (context) => ' ' + formatarValor(Number(context.raw))
             }
          }
        }
      }
    });
  }
}

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
/* --- Base --- */
.financeiro-dashboard-container { padding: 0; }

.header-actions-compact {
    display: flex; justify-content: flex-start; gap: 0.8rem;
    margin-bottom: 1.5rem; padding-top: 0.5rem;
}

/* --- Botões --- */
.btn-primary, .btn-secondary, .btn-info {
    padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; font-size: 0.9rem;
    text-decoration: none; transition: all 0.2s; border: none; cursor: pointer;
    color: white; display: flex; align-items: center; gap: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.btn-primary { background-color: #0f172a; } .btn-primary:hover { background-color: #334155; transform: translateY(-1px); }
.btn-secondary { background-color: #dc2626; } .btn-secondary:hover { background-color: #b91c1c; transform: translateY(-1px); }
.btn-info { background-color: #0284c7; } .btn-info:hover { background-color: #0369a1; transform: translateY(-1px); }

/* --- Loading/Error --- */
.loading-message { text-align: center; padding: 2rem; color: #64748b; }
.spinner { border: 3px solid #f3f3f3; border-top: 3px solid #0f172a; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.error-message { background: #fef2f2; color: #dc2626; padding: 1rem; border-radius: 8px; text-align: center; border: 1px solid #fecaca; }

/* --- Layout do Dashboard --- */
.dashboard-content { display: flex; flex-direction: column; gap: 2rem; }

.group-section {
  background: white; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f1f5f9;
}

.group-title {
    font-size: 1.1rem; font-weight: 700; color: #334155;
    margin: 0 0 1.2rem 0; display: flex; align-items: center; gap: 8px;
    border-bottom: 1px solid #f1f5f9; padding-bottom: 0.8rem;
}
.group-title i { color: #64748b; }

.stats-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem;
}

/* --- Cartões de Estatística --- */
.stat-card {
  padding: 1.2rem; border-radius: 10px; background-color: #f8fafc;
  border: 1px solid #e2e8f0; transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

.card-title { font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin: 0 0 0.5rem 0; }
.card-value { font-size: 1.8rem; font-weight: 800; color: #1e293b; margin: 0; }
.card-subtitle { display: block; font-size: 0.8rem; color: #94a3b8; margin-top: 4px; font-weight: 500; }

/* Cores Específicas */
.text-success { color: #16a34a; }
.text-danger { color: #dc2626; }
.text-warning { color: #d97706; }
.text-muted { color: #64748b; }

/* Destaque para o Saldo */
.highlight-card { background-color: #fff; border-width: 2px; }
.net-positive { border-color: #16a34a; background-color: #f0fdf4; }
.net-positive .card-value { color: #16a34a; }

.net-negative { border-color: #dc2626; background-color: #fef2f2; }
.net-negative .card-value { color: #dc2626; }

.balance-positive { border-left: 4px solid #0ea5e9; }
.balance-negative { border-left: 4px solid #ef4444; }

/* --- Gráficos --- */
.charts-section {
  display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem;
}
@media (max-width: 900px) { .charts-section { grid-template-columns: 1fr; } }

.chart-card {
  background: white; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f1f5f9;
}
.chart-card h4 { margin: 0 0 1rem 0; color: #334155; font-size: 1rem; font-weight: 600; }
.chart-wrapper { position: relative; height: 250px; width: 100%; }

.mt-4 { margin-top: 1.5rem; }
</style>
<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Financeiro</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Dashboard</span>
           </nav>
           
           <h1>Painel Financeiro</h1>
        </div>
        
        <div class="actions-area">
            <router-link :to="{ name: 'dre' }" class="btn-white-thin" title="Demonstrativo de Resultado">
                <i class="fas fa-file-invoice-dollar"></i> DRE
            </router-link>

            <router-link :to="{ name: 'transacao-nova', query: { tipo: 'DESPESA' } }" class="btn-danger-thin">
                <i class="fas fa-minus-circle"></i> Despesa
            </router-link>

            <router-link :to="{ name: 'transacao-nova', query: { tipo: 'RECEITA' } }" class="btn-success-thin">
                <i class="fas fa-plus-circle"></i> Receita
            </router-link>

            <button class="btn-icon-thin" @click="fetchAllData" title="Atualizar">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
        </div>
      </div>
    </header>

    <div v-if="isLoading && !stats" class="loading-state">
       <div class="spinner"></div>
       <p>Carregando indicadores...</p>
    </div>
    <div v-else-if="error" class="error-state">
       <i class="fas fa-exclamation-triangle"></i> {{ error }}
    </div>

    <div v-else-if="stats" class="dashboard-content">
        
      <div class="kpi-grid">
        <div class="kpi-card green">
            <div class="kpi-content">
                <span class="kpi-value">{{ formatarValor(stats.a_receber.pago_mes_atual) }}</span>
                <span class="kpi-label">Receitas (Mês)</span>
                <span class="kpi-sublabel">Pendente: {{ formatarValor(stats.a_receber.pendente) }}</span>
            </div>
            <div class="kpi-icon"><i class="fas fa-arrow-up"></i></div>
        </div>

        <div class="kpi-card orange">
            <div class="kpi-content">
                <span class="kpi-value">{{ formatarValor(stats.a_pagar.pago_mes_atual) }}</span>
                <span class="kpi-label">Despesas (Mês)</span>
                <span class="kpi-sublabel">Pendente: {{ formatarValor(stats.a_pagar.pendente) }}</span>
            </div>
            <div class="kpi-icon"><i class="fas fa-arrow-down"></i></div>
        </div>

        <div class="kpi-card blue">
            <div class="kpi-content">
                <span class="kpi-value" :class="saldoCaixa >= 0 ? 'text-blue' : 'text-red-internal'">
                    {{ formatarValor(saldoCaixa) }}
                </span>
                <span class="kpi-label">Saldo em Caixa</span>
                <span class="kpi-sublabel">Realizado</span>
            </div>
            <div class="kpi-icon"><i class="fas fa-wallet"></i></div>
        </div>

        <div class="kpi-card purple">
            <div class="kpi-content">
                <span class="kpi-value">{{ formatarValor(stats.saldo_previsto) }}</span>
                <span class="kpi-label">Saldo Previsto</span>
                <span class="kpi-sublabel">Com pendências</span>
            </div>
            <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
        </div>
      </div>

      <main class="content-wrapper">
          <div class="charts-grid">
            
            <div class="chart-card">
                <div class="chart-header">
                    <h3><i class="fas fa-balance-scale"></i> Balanço Mensal (Dia a Dia)</h3>
                </div>
                <div class="chart-body">
                    <canvas ref="barChartCanvas"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <div class="chart-header">
                    <h3><i class="fas fa-chart-area"></i> Evolução (6 Meses)</h3>
                </div>
                <div class="chart-body">
                    <canvas ref="lineChartCanvas"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <div class="chart-header">
                    <h3><i class="fas fa-chart-pie"></i> Despesas por Categoria</h3>
                </div>
                <div class="chart-body">
                    <canvas ref="doughnutChartCanvas"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <div class="chart-header">
                    <h3><i class="fas fa-building"></i> Top Imóveis (Despesas)</h3>
                </div>
                <div class="chart-body">
                    <canvas ref="rankingChartCanvas"></canvas>
                </div>
            </div>

          </div>
      </main>
    
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue';
import apiClient from '@/services/api';
import Chart from 'chart.js/auto';
import '@fortawesome/fontawesome-free/css/all.css';

// --- Interfaces ---
interface StatsData { pendente: number; pago_mes_atual: number; }
interface StatsFinanceiro { a_receber: StatsData; a_pagar: StatsData; saldo_previsto: number; }
interface RankingItem { label: string; value: number; }
interface EvolucaoItem { mes: string; receitas: number; despesas: number; }
interface CategoriaItem { label: string; value: number; }
interface DiarioItem { dia: string; receitas: number; despesas: number; }

interface GeneralStats {
    ranking_imoveis: RankingItem[];
    evolucao_financeira: EvolucaoItem[];
    despesas_categoria: CategoriaItem[];
    balanco_diario?: DiarioItem[];
}

// --- State ---
const stats = ref<StatsFinanceiro | null>(null);
const generalStats = ref<GeneralStats | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

// --- Canvas Refs ---
const barChartCanvas = ref<HTMLCanvasElement | null>(null);
const lineChartCanvas = ref<HTMLCanvasElement | null>(null);
const doughnutChartCanvas = ref<HTMLCanvasElement | null>(null);
const rankingChartCanvas = ref<HTMLCanvasElement | null>(null);

// --- Instances ---
let charts: Chart[] = [];

const saldoCaixa = computed(() => {
  if (!stats.value) return 0;
  return stats.value.a_receber.pago_mes_atual - stats.value.a_pagar.pago_mes_atual;
});

const formatarValor = (valor: number | null | undefined): string => {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

async function fetchAllData() {
  isLoading.value = true;
  error.value = null;
  try {
    const statsRes = await apiClient.get<StatsFinanceiro>('/v1/financeiro/transacoes/stats/');
    stats.value = statsRes.data;

    const generalRes = await apiClient.get<GeneralStats>('/v1/financeiro/transacoes/dashboard-general-stats/');
    generalStats.value = generalRes.data;
    
    nextTick(() => { renderCharts(); });

  } catch (err) {
    console.error("Erro ao buscar dados:", err);
    error.value = 'Erro ao carregar dashboard. Verifique sua conexão.';
  } finally {
    isLoading.value = false;
  }
}

function destroyCharts() {
    charts.forEach(c => c.destroy());
    charts = [];
}

const commonAnimation = {
    duration: 2000,
    easing: 'easeInOutQuart'
};

function renderCharts() {
  destroyCharts();
  if (!stats.value || !generalStats.value) return;

  // 1. Gráfico de Balanço Diário (2 Linhas: Receita x Despesa)
  if (barChartCanvas.value) {
    const dailyData = generalStats.value.balanco_diario || [];
    
    charts.push(new Chart(barChartCanvas.value, {
      type: 'line',
      data: {
        labels: dailyData.map(d => d.dia), // Dias que tiveram alteração
        datasets: [
            {
                label: 'Receitas',
                data: dailyData.map(d => d.receitas),
                borderColor: '#10b981', // Verde
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#10b981',
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: false, // Linha separada
                tension: 0.3
            },
            {
                label: 'Despesas',
                data: dailyData.map(d => d.despesas),
                borderColor: '#ef4444', // Vermelho
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#ef4444',
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: false, // Linha separada
                tension: 0.3
            }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: commonAnimation as any,
        plugins: { 
            legend: { position: 'top', align: 'end' },
            tooltip: { mode: 'index', intersect: false }
        },
        scales: { 
            y: { 
                beginAtZero: true, 
                grid: { color: '#f3f4f6' } 
            }, 
            x: { 
                grid: { display: false } 
            } 
        }
      }
    }));
  }

  // 2. Evolução Financeira (Linha Mensal)
  if (lineChartCanvas.value) {
    const data = generalStats.value.evolucao_financeira;
    charts.push(new Chart(lineChartCanvas.value, {
      type: 'line',
      data: {
        labels: data.map(d => d.mes),
        datasets: [
            {
                label: 'Receitas',
                data: data.map(d => d.receitas),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3
            },
            {
                label: 'Despesas',
                data: data.map(d => d.despesas),
                borderColor: '#f59e0b', 
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3
            }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: commonAnimation as any,
        plugins: { legend: { position: 'top' } },
        interaction: { mode: 'index', intersect: false },
        scales: { y: { beginAtZero: true, grid: { color: '#f3f4f6' } }, x: { grid: { display: false } } }
      }
    }));
  }

  // 3. Despesas por Categoria (Rosca)
  if (doughnutChartCanvas.value) {
    const data = generalStats.value.despesas_categoria;
    charts.push(new Chart(doughnutChartCanvas.value, {
      type: 'doughnut',
      data: {
        labels: data.map(d => d.label),
        datasets: [{
          data: data.map(d => d.value),
          backgroundColor: [
            '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#10b981'
          ],
          borderWidth: 0,
          hoverOffset: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            animateScale: true,
            animateRotate: true,
            duration: 2000,
            easing: 'easeOutBounce'
        },
        cutout: '65%',
        plugins: { 
            legend: { position: 'right', labels: { boxWidth: 15, font: { size: 11 } } } 
        }
      }
    }));
  }

  // 4. Top Imóveis (Barra Horizontal)
  if (rankingChartCanvas.value) {
    const data = generalStats.value.ranking_imoveis;
    charts.push(new Chart(rankingChartCanvas.value, {
      type: 'bar',
      data: {
        labels: data.map(d => d.label.length > 20 ? d.label.substring(0, 20) + '...' : d.label),
        datasets: [{
          label: 'Despesas (R$)',
          data: data.map(d => d.value),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderRadius: 4,
          barThickness: 15
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        animation: commonAnimation as any,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, grid: { color: '#f3f4f6' } }, y: { grid: { display: false } } }
      }
    }));
  }
}

onMounted(() => { fetchAllData(); });
</script>

<style scoped>
/* ==========================================================================
   LAYOUT PADRONIZADO (BASEADO EM CLIENTESVIEW)
   ========================================================================== */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA */
.page-header { margin-bottom: 2rem; }
.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }

.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; align-items: center; }

/* BOTÕES PADRONIZADOS (Estilo "Thin" 34px) */
/* Botão Base Thin */
.btn-white-thin, .btn-danger-thin, .btn-success-thin {
  height: 34px; padding: 0 1.2rem; border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 0.5rem; transition: all 0.2s; text-decoration: none;
}

/* Variante Branca (Secundária) */
.btn-white-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b;
}
.btn-white-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* Variante Ícone (Quadrada) */
.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* Variante Sucesso (Receita) */
.btn-success-thin {
  background: #10b981; border: 1px solid #059669; color: white;
  box-shadow: 0 1px 2px rgba(16, 185, 129, 0.15);
}
.btn-success-thin:hover { background: #059669; transform: translateY(-1px); }

/* Variante Perigo (Despesa) */
.btn-danger-thin {
  background: #ef4444; border: 1px solid #dc2626; color: white;
  box-shadow: 0 1px 2px rgba(239, 68, 68, 0.15);
}
.btn-danger-thin:hover { background: #dc2626; transform: translateY(-1px); }


/* KPIS (PADRONIZADO COM CLIENTESVIEW) */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: default; transition: all 0.2s;
  position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-sublabel { font-size: 0.7rem; color: #94a3b8; margin-top: 2px; }
.kpi-icon { 
    font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; 
}

/* Cores KPI */
.kpi-card.blue { border-left: 4px solid #3b82f6; } 
.kpi-card.blue .kpi-value.text-blue { color: #2563eb; }
.kpi-card.blue .kpi-value.text-red-internal { color: #dc2626; }

.kpi-card.green { border-left: 4px solid #10b981; } 
.kpi-card.green .kpi-value { color: #059669; }

.kpi-card.orange { border-left: 4px solid #f59e0b; } 
.kpi-card.orange .kpi-value { color: #d97706; }

.kpi-card.purple { border-left: 4px solid #9333ea; } 
.kpi-card.purple .kpi-value { color: #9333ea; }

.kpi-card.red { border-left: 4px solid #ef4444; } 
.kpi-card.red .kpi-value { color: #dc2626; }


/* ÁREA DE GRÁFICOS (Substitui Tabela do ClientesView mas mantém consistência) */
.content-wrapper { display: flex; flex-direction: column; gap: 2rem; }
.charts-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }

.chart-card { 
    background: white; border-radius: 8px; border: 1px solid #e5e7eb; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column; height: 400px; 
}
.chart-header { 
    padding: 0.8rem 1.2rem; border-bottom: 1px solid #f1f5f9; background: #f8fafc;
}
.chart-header h3 { 
    margin: 0; font-size: 0.75rem; font-weight: 700; color: #64748b; 
    text-transform: uppercase; letter-spacing: 0.06em; display: flex; align-items: center; gap: 8px; 
}
.chart-body { padding: 1.5rem; position: relative; flex: 1; min-height: 0; }

/* ESTADOS DE CARREGAMENTO */
.loading-state, .error-state { text-align: center; padding: 4rem; background: white; border-radius: 8px; border: 1px dashed #e2e8f0; color: #64748b; }
.error-state { color: #dc2626; border-color: #fca5a5; background: #fef2f2; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; flex-wrap: wrap; }
  .charts-grid { grid-template-columns: 1fr; }
}
</style>
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
                    <h3><i class="fas fa-chart-line"></i> Evolução Financeira Acumulada</h3>
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
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue';
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
    
    // Pequeno delay para garantir que o DOM renderizou os canvas
    setTimeout(() => {
        renderCharts();
    }, 100);

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
    duration: 1500,
    easing: 'easeOutQuart'
};

function renderCharts() {
  destroyCharts();
  if (!stats.value || !generalStats.value) return;

  // 1. Gráfico de Evolução ACUMULADA (Line Chart)
  if (lineChartCanvas.value) {
    const data = generalStats.value.balanco_diario || [];
    
    // Calcula valores ACUMULADOS para mostrar evolução crescente
    let accReceita = 0;
    let accDespesa = 0;
    
    const evolucaoReceitas = data.map(d => {
        accReceita += Number(d.receitas || 0);
        return accReceita;
    });
    
    const evolucaoDespesas = data.map(d => {
        accDespesa += Number(d.despesas || 0);
        return accDespesa;
    });

    charts.push(new Chart(lineChartCanvas.value, {
      type: 'line',
      data: {
        labels: data.map(d => d.dia),
        datasets: [
            {
                label: 'Receitas (Acumulado)',
                data: evolucaoReceitas,
                borderColor: '#10b981', // Verde
                borderWidth: 2,
                pointRadius: 0, 
                pointHoverRadius: 6,
                fill: false, // 1 LINHA (sem preenchimento)
                tension: 0.4 
            },
            {
                label: 'Despesas (Acumulado)',
                data: evolucaoDespesas,
                borderColor: '#ef4444', // Vermelho
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 6,
                fill: false, // 1 LINHA (sem preenchimento)
                tension: 0.4
            }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        animation: commonAnimation as any,
        plugins: { 
            legend: { 
                position: 'top', 
                align: 'end',
                labels: { usePointStyle: true, boxWidth: 8, font: { size: 11 } }
            }, 
            tooltip: {
                backgroundColor: '#1f2937',
                padding: 12,
                cornerRadius: 8,
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.parsed.y);
                        }
                        return label;
                    }
                }
            }
        },
        scales: { 
            y: { 
                beginAtZero: true, 
                grid: { color: '#f3f4f6', borderDash: [5, 5] },
                ticks: { 
                    font: { size: 10 },
                    color: '#94a3b8',
                    callback: function(value) {
                        if (typeof value === 'number') {
                            if (value >= 1000) return (value/1000).toFixed(0) + 'k';
                        }
                        return value;
                    }
                },
                border: { display: false }
            }, 
            x: { 
                grid: { display: false },
                ticks: { 
                    font: { size: 10 }, 
                    color: '#94a3b8', 
                    maxTicksLimit: 12,
                    maxRotation: 0 
                },
                border: { display: false }
            } 
        }
      }
    }));
  }

  // 2. Despesas por Categoria
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
        cutout: '80%',
        plugins: { 
            legend: { 
                position: 'right', 
                labels: { boxWidth: 8, usePointStyle: true, font: { size: 11 } } 
            } 
        }
      }
    }));
  }

  // 3. Top Imóveis
  if (rankingChartCanvas.value) {
    const data = generalStats.value.ranking_imoveis;
    charts.push(new Chart(rankingChartCanvas.value, {
      type: 'bar',
      data: {
        labels: data.map(d => d.label.length > 15 ? d.label.substring(0, 15) + '...' : d.label),
        datasets: [{
          label: 'Despesas (R$)',
          data: data.map(d => d.value),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderRadius: 4,
          barThickness: 16 
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        animation: commonAnimation as any,
        plugins: { legend: { display: false } },
        scales: { 
            x: { display: false }, 
            y: { 
                grid: { display: false },
                border: { display: false }
            } 
        }
      }
    }));
  }
}

onMounted(() => { fetchAllData(); });
onUnmounted(() => { destroyCharts(); });
</script>

<style scoped>
/* ==========================================================================
   LAYOUT & ESTILO MODERNO
   ========================================================================== */
.page-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 2rem;
}

/* HEADER DA PÁGINA */
.page-header { margin-bottom: 2.5rem; }
.title-area { display: flex; flex-direction: column; gap: 8px; }
.title-area h1 { font-size: 1.75rem; font-weight: 600; color: #0f172a; margin: 0; letter-spacing: -0.03em; }

.breadcrumb { display: flex; align-items: center; gap: 8px; font-size: 0.75rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.6rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 1rem; align-items: center; }

/* BOTÕES REFINADOS */
.btn-white-thin, .btn-danger-thin, .btn-success-thin {
  height: 38px; padding: 0 1.2rem; border-radius: 8px; font-weight: 500; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 0.6rem; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); text-decoration: none;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.btn-white-thin { background: white; border: 1px solid #e2e8f0; color: #475569; }
.btn-white-thin:hover { border-color: #cbd5e1; color: #1e293b; background: #f8fafc; transform: translateY(-1px); }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 38px; height: 38px;
  border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.9rem;
}
.btn-icon-thin:hover { color: #2563eb; border-color: #bfdbfe; background: #eff6ff; }

.btn-success-thin { background: #10b981; border: 1px solid transparent; color: white; }
.btn-success-thin:hover { background: #059669; transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2); }

.btn-danger-thin { background: #ef4444; border: 1px solid transparent; color: white; }
.btn-danger-thin:hover { background: #dc2626; transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2); }


/* KPIS MODERNOS (Cards Flutuantes) */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
    gap: 1.5rem; margin-bottom: 2.5rem; 
}

.kpi-card {
  background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid transparent;
  display: flex; justify-content: space-between; align-items: flex-start;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02); 
  transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); }

.kpi-content { display: flex; flex-direction: column; z-index: 2; }
.kpi-value { font-size: 1.75rem; font-weight: 700; line-height: 1.1; color: #0f172a; margin-bottom: 0.25rem; letter-spacing: -0.02em; }
.kpi-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; }
.kpi-sublabel { font-size: 0.75rem; color: #94a3b8; margin-top: 6px; display: flex; align-items: center; gap: 4px; }

.kpi-icon { 
    width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem;
}

/* Cores KPI Refinadas */
.kpi-card.green .kpi-icon { background: #ecfdf5; color: #10b981; }
.kpi-card.green .kpi-value { color: #059669; }

.kpi-card.orange .kpi-icon { background: #fff7ed; color: #f97316; }
.kpi-card.orange .kpi-value { color: #ea580c; }

.kpi-card.blue .kpi-icon { background: #eff6ff; color: #3b82f6; }
.kpi-card.blue .kpi-value.text-blue { color: #2563eb; }
.kpi-card.blue .kpi-value.text-red-internal { color: #ef4444; }

.kpi-card.purple .kpi-icon { background: #faf5ff; color: #a855f7; }
.kpi-card.purple .kpi-value { color: #9333ea; }


/* ÁREA DE GRÁFICOS (Cards Brancos Limpos) */
.content-wrapper { display: flex; flex-direction: column; gap: 2rem; }

/* GRID CONFIGURADO PARA 3 COLUNAS */
.charts-grid { 
    display: grid; 
    grid-template-columns: repeat(3, 1fr); /* 3 Gráficos na mesma linha */
    gap: 1.5rem; 
}

.chart-card { 
    background: white; border-radius: 12px; border: 1px solid #f1f5f9; 
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02); display: flex; flex-direction: column; height: 400px; 
    overflow: hidden;
}
.chart-header { 
    padding: 1.2rem 1.5rem; border-bottom: 1px solid #f8fafc; background: white;
    display: flex; align-items: center; justify-content: space-between;
}
.chart-header h3 { 
    margin: 0; font-size: 0.9rem; font-weight: 600; color: #334155; 
    display: flex; align-items: center; gap: 10px; 
}
.chart-header h3 i { color: #94a3b8; }

.chart-body { padding: 1.5rem; position: relative; flex: 1; min-height: 0; }

/* LOADING STATE */
.loading-state { padding: 4rem; text-align: center; color: #94a3b8; }
.spinner { border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* RESPONSIVIDADE */
@media (max-width: 1280px) {
  .charts-grid { grid-template-columns: repeat(2, 1fr); } /* 2 Colunas em telas médias */
}

@media (max-width: 768px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; flex-wrap: wrap; }
  .charts-grid { grid-template-columns: 1fr; } /* 1 Coluna em mobile */
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
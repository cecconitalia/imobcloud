<template>
  <div class="dashboard-container">
    
    <div v-if="isLoading" class="skeleton-wrapper">
      <div class="skeleton-header"></div>
      <div class="skeleton-grid-main">
        <div class="skeleton-card" v-for="n in 4" :key="`sk-main-${n}`"></div>
      </div>
      <div class="skeleton-grid-secondary">
          <div class="skeleton-card-tall" v-for="n in 2" :key="`sk-fin-${n}`"></div>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <strong><i class="fas fa-exclamation-triangle"></i> Atenção</strong>
      <p>{{ error }}</p>
    </div>

    <div v-if="!isLoading" class="content-wrapper">
      
      <div class="section-header">
        <h3><i class="fas fa-chart-pie"></i> Visão Geral</h3>
      </div>

      <div class="stats-grid">
        <div class="stat-card card-primary">
          <div class="icon-wrapper primary"><i class="fas fa-home"></i></div>
          <div class="card-content">
            <p class="stat-title">Imóveis Ativos</p>
            <p class="stat-value">{{ geralStats?.imoveis_ativos || 0 }}</p>
          </div>
          <router-link to="/imoveis" class="card-link">Ver Imóveis <i class="fas fa-arrow-right"></i></router-link>
        </div>

        <div class="stat-card card-info">
          <div class="icon-wrapper info"><i class="fas fa-users"></i></div>
          <div class="card-content">
            <p class="stat-title">Clientes Ativos</p>
            <p class="stat-value">{{ geralStats?.clientes_ativos || 0 }}</p>
          </div>
          <router-link to="/clientes" class="card-link">Ver Clientes <i class="fas fa-arrow-right"></i></router-link>
        </div>

        <div class="stat-card card-warning">
          <div class="icon-wrapper warning"><i class="fas fa-file-contract"></i></div>
          <div class="card-content">
            <p class="stat-title">Contratos Vigentes</p>
            <p class="stat-value">{{ geralStats?.contratos_ativos || 0 }}</p>
          </div>
          <router-link to="/contratos" class="card-link">Gerir Contratos <i class="fas fa-arrow-right"></i></router-link>
        </div>

        <div class="stat-card card-success">
          <div class="icon-wrapper success"><i class="fas fa-user-plus"></i></div>
          <div class="card-content">
            <p class="stat-title">Novos (30 dias)</p>
            <p class="stat-value">+{{ geralStats?.novos_clientes_30d || 0 }}</p>
          </div>
          <span class="card-subtext">Crescimento</span>
        </div>
      </div>

      <div class="section-header mt-6">
        <h3><i class="fas fa-wallet"></i> Resumo Financeiro</h3>
        <router-link to="/financeiro/dashboard" class="header-link">Ver Detalhes</router-link>
      </div>

      <div class="financial-grid">
        <div class="stat-card card-financial">
            <div class="financial-row">
                <div class="fin-icon income"><i class="fas fa-arrow-up"></i></div>
                <div>
                    <p class="stat-title">Receitas (Mês)</p>
                    <p class="stat-value text-success">{{ formatCurrency(finStats?.a_receber?.pago_mes_atual) }}</p>
                </div>
            </div>
        </div>

        <div class="stat-card card-financial">
            <div class="financial-row">
                <div class="fin-icon expense"><i class="fas fa-arrow-down"></i></div>
                <div>
                    <p class="stat-title">Despesas (Mês)</p>
                    <p class="stat-value text-danger">{{ formatCurrency(finStats?.a_pagar?.pago_mes_atual) }}</p>
                </div>
            </div>
        </div>

        <div class="stat-card card-financial">
             <div class="financial-row">
                <div class="fin-icon balance"><i class="fas fa-scale-balanced"></i></div>
                <div>
                    <p class="stat-title">Saldo do Mês (R - D)</p>
                    <p class="stat-value" :class="saldoMesAtual >= 0 ? 'text-primary' : 'text-danger'">
                        {{ formatCurrency(saldoMesAtual) }}
                    </p>
                </div>
            </div>
        </div>
      </div>

      <div class="section-header mt-6">
        <h3><i class="fas fa-key"></i> Controle de Aluguéis</h3>
        <router-link to="/contratos" class="header-link">Todos os Contratos</router-link>
      </div>

      <div class="rent-grid">
        <div class="rent-kpis">
            <div class="alert-card">
                <div class="alert-header">
                    <i class="fas fa-clock text-warning"></i>
                    <span>A Vencer (7 dias)</span>
                </div>
                <div class="alert-body">
                    <p class="alert-value">{{ aluguelStats?.alugueis_a_vencer || 0 }}</p>
                    <p class="alert-desc">Boletos</p>
                </div>
            </div>

            <div class="alert-card danger-border">
                <div class="alert-header">
                    <i class="fas fa-exclamation-circle text-danger"></i>
                    <span>Em Atraso</span>
                </div>
                <div class="alert-body">
                    <p class="alert-value text-danger">{{ aluguelStats?.alugueis_atrasados || 0 }}</p>
                    <p class="alert-desc">Inadimplentes</p>
                </div>
            </div>
        </div>

        <div class="rent-table-card">
            <h4>Próximos Vencimentos</h4>
            <div v-if="aluguelStats?.proximos_alugueis?.length" class="table-responsive">
                <table class="mini-table">
                    <thead>
                        <tr>
                            <th>Imóvel</th>
                            <th>Inquilino</th>
                            <th>Vencimento</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="aluguel in aluguelStats.proximos_alugueis.slice(0, 5)" :key="aluguel.id">
                            <td class="truncate-text" :title="aluguel.imovel_titulo">
                                <i class="fas fa-building text-muted mr-1"></i> {{ aluguel.imovel_titulo }}
                            </td>
                            <td class="truncate-text" :title="aluguel.inquilino_nome">
                                {{ aluguel.inquilino_nome }}
                            </td>
                            <td>{{ formatDate(aluguel.data_vencimento) }}</td>
                            <td class="font-mono">{{ formatCurrency(aluguel.valor) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div v-else class="empty-msg">
                <i class="fas fa-check-circle text-success"></i> Nenhum aluguel a vencer nos próximos dias.
            </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

// --- Interfaces ---
interface GeralStats {
  imoveis_ativos: number;
  clientes_ativos: number;
  contratos_ativos: number;
  novos_clientes_30d: number;
}

interface FinStats {
    a_receber: { pendente: number; pago_mes_atual: number; };
    a_pagar: { pendente: number; pago_mes_atual: number; };
    saldo_previsto: number;
}

interface AluguelItem {
    id: number;
    imovel_titulo: string;
    inquilino_nome: string; 
    data_vencimento: string;
    valor: number;
}

interface AluguelStats {
  alugueis_a_vencer: number;
  alugueis_atrasados: number;
  proximos_alugueis: AluguelItem[];
}

// --- Estados ---
const geralStats = ref<GeralStats | null>(null);
const finStats = ref<FinStats | null>(null);
const aluguelStats = ref<AluguelStats | null>(null);

const isLoading = ref(true);
const error = ref<string | null>(null);

// --- COMPUTED: Saldo do Mês (Realizado) ---
const saldoMesAtual = computed(() => {
  if (!finStats.value) return 0;
  return (finStats.value.a_receber.pago_mes_atual || 0) - (finStats.value.a_pagar.pago_mes_atual || 0);
});

// --- Helpers ---
function formatCurrency(value: number | undefined) {
  if (value === undefined || value === null || isNaN(value)) return 'R$ 0,00';
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatDate(dateStr: string) {
    if (!dateStr) return '-';
    try {
        const [year, month, day] = dateStr.split('-');
        return `${day}/${month}`;
    } catch { return dateStr; }
}

// --- Data Fetching ---
onMounted(async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    const [resGeral, resFin, resAluguel] = await Promise.all([
        apiClient.get<GeralStats>('/v1/stats/'),
        apiClient.get<FinStats>('/v1/financeiro/transacoes/stats/'),
        apiClient.get<AluguelStats>('/v1/alugueis/dashboard-stats/')
    ]);

    geralStats.value = resGeral.data;
    finStats.value = resFin.data;
    aluguelStats.value = resAluguel.data;

  } catch (err: any) {
    console.error("Erro ao carregar dashboard:", err);
    error.value = 'Falha ao carregar dados do painel.';
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
/* --- Variáveis & Base --- */
.dashboard-container {
  --color-primary: #007bff;
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-danger: #dc3545;
  --color-info: #17a2b8;
  --color-text: #343a40;
  --color-text-muted: #6c757d;
  --bg-card: #ffffff;
  --radius: 8px;
  --shadow: 0 2px 8px rgba(0,0,0,0.05);
  
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* --- Tipografia & Headers --- */
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e9ecef;
}
.section-header h3 {
    font-size: 1.1rem; font-weight: 700; color: var(--color-text); margin: 0;
    display: flex; align-items: center; gap: 8px;
}
.section-header h3 i { color: var(--color-primary); }
.header-link { font-size: 0.85rem; color: var(--color-primary); text-decoration: none; font-weight: 600; }
.mt-6 { margin-top: 2rem; }

/* --- GRID: Visão Geral --- */
.stats-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem;
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 1.2rem;
  display: flex; flex-direction: column; position: relative; overflow: hidden;
  transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }

.card-primary { border-left: 4px solid var(--color-primary); }
.card-info { border-left: 4px solid var(--color-info); }
.card-success { border-left: 4px solid var(--color-success); }
.card-warning { border-left: 4px solid var(--color-warning); }

.icon-wrapper {
    width: 40px; height: 40px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 0.5rem;
}
.primary { background: #e6f2ff; color: var(--color-primary); }
.info { background: #e0fcfc; color: var(--color-info); }
.success { background: #e6ffec; color: var(--color-success); }
.warning { background: #fff8e1; color: var(--color-warning); }

.stat-title { font-size: 0.85rem; color: var(--color-text-muted); margin: 0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.stat-value { font-size: 1.8rem; font-weight: 800; color: var(--color-text); margin: 0.2rem 0; }
.card-link { font-size: 0.8rem; color: var(--color-primary); text-decoration: none; font-weight: 600; margin-top: auto; }
.card-subtext { font-size: 0.75rem; color: var(--color-success); font-weight: 600; margin-top: auto; }

/* --- GRID: Financeiro --- */
.financial-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;
}
.card-financial { border-left: none; border-top: 4px solid #ccc; }
.card-financial:nth-child(1) { border-top-color: var(--color-success); }
.card-financial:nth-child(2) { border-top-color: var(--color-danger); }
.card-financial:nth-child(3) { border-top-color: var(--color-primary); }

.financial-row { display: flex; align-items: center; gap: 1rem; }
.fin-icon { width: 45px; height: 45px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; }
.income { background: #e6ffec; color: var(--color-success); }
.expense { background: #ffe6e6; color: var(--color-danger); }
.balance { background: #e6f2ff; color: var(--color-primary); }
.text-success { color: var(--color-success); }
.text-danger { color: var(--color-danger); }
.text-primary { color: var(--color-primary); }

/* --- GRID: Locação (Atualizada) --- */
.rent-grid {
    display: grid;
    grid-template-columns: 1fr 3fr; /* KPI menor, Tabela maior */
    gap: 1rem;
}
.rent-kpis { display: flex; flex-direction: column; gap: 1rem; }

.alert-card {
    background: var(--bg-card); border-radius: var(--radius); padding: 1rem;
    box-shadow: var(--shadow); border: 1px solid #eee;
    display: flex; flex-direction: column; justify-content: center; text-align: center;
    flex: 1;
}
.danger-border { border-color: #f8d7da; background: #fff5f5; }

.alert-header { display: flex; align-items: center; justify-content: center; gap: 0.5rem; font-weight: 600; color: var(--color-text-muted); margin-bottom: 0.5rem; }
.alert-value { font-size: 1.8rem; font-weight: 800; color: var(--color-text); margin: 0; line-height: 1; }
.alert-desc { font-size: 0.8rem; color: var(--color-text-muted); margin: 0; }

.rent-table-card {
    background: var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow);
    padding: 1rem; overflow: hidden;
}
.rent-table-card h4 { margin: 0 0 0.8rem 0; font-size: 1rem; color: var(--color-text); font-weight: 600; }

.mini-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.mini-table th { text-align: left; color: var(--color-text-muted); font-weight: 600; padding: 8px; border-bottom: 1px solid #eee; background-color: #f8f9fa; }
.mini-table td { padding: 8px; border-bottom: 1px solid #f5f5f5; color: var(--color-text); vertical-align: middle; }
.mini-table tr:last-child td { border-bottom: none; }
.mini-table tr:hover { background-color: #f8f9fa; }

.truncate-text { max-width: 180px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mr-1 { margin-right: 0.25rem; }
.text-muted { color: #aaa; }
.font-mono { font-family: monospace; font-weight: 600; color: var(--color-primary); }
.empty-msg { font-size: 0.9rem; color: #6c757d; text-align: center; margin-top: 2rem; }

/* --- Skeleton & Error --- */
.skeleton-wrapper { display: flex; flex-direction: column; gap: 1rem; }
.skeleton-header { height: 40px; width: 200px; background: #ddd; border-radius: 4px; }
.skeleton-grid-main { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.skeleton-card { height: 120px; background: #eee; border-radius: var(--radius); animation: pulse 1.5s infinite; }
.skeleton-grid-secondary { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
.skeleton-card-tall { height: 150px; background: #eee; border-radius: var(--radius); animation: pulse 1.5s infinite; }
.error-message { background: #f8d7da; color: #721c24; padding: 1rem; border-radius: var(--radius); margin-bottom: 1rem; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }

@media (max-width: 1024px) {
    .rent-grid { grid-template-columns: 1fr; }
    .rent-kpis { flex-direction: row; }
}
@media (max-width: 768px) {
    .stats-grid { grid-template-columns: 1fr 1fr; }
    .financial-grid { grid-template-columns: 1fr; }
    .rent-kpis { flex-direction: column; }
}
</style>
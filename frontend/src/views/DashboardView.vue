<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Início</span>
              <i class="fas fa-chevron-right separator"></i>
              <span class="active">Visão Geral</span>
           </nav>
           
           <h1>Dashboard</h1>
        </div>
        
        <div class="header-actions">
            <button @click="fetchData" class="btn-icon-refresh" :disabled="isLoading" title="Atualizar">
                <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
        </div>
      </div>
    </header>

    <div v-if="isLoading" class="skeleton-wrapper">
      <div class="skeleton-grid-kpi">
        <div class="skeleton-card" v-for="n in 4" :key="`sk-kpi-${n}`"></div>
      </div>
      <div class="skeleton-grid-main">
          <div class="skeleton-card-tall" v-for="n in 2" :key="`sk-main-${n}`"></div>
      </div>
    </div>

    <div v-if="error" class="alert-box error">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ error }}</span>
        <button @click="fetchData" class="btn-retry">Tentar</button>
    </div>

    <div v-if="!isLoading && !error" class="dashboard-content fade-in">
      
      <section class="kpi-grid">
        <div class="kpi-card blue clickable" @click="$router.push('/imoveis')">
          <div class="kpi-content">
            <span class="kpi-value">{{ geralStats?.imoveis_ativos || 0 }}</span>
            <span class="kpi-label">Imóveis Ativos</span>
          </div>
          <div class="kpi-icon"><i class="fas fa-home"></i></div>
        </div>

        <div class="kpi-card purple clickable" @click="$router.push('/clientes')">
          <div class="kpi-content">
            <span class="kpi-value">{{ geralStats?.clientes_ativos || 0 }}</span>
            <span class="kpi-label">Clientes na Base</span>
          </div>
          <div class="kpi-icon"><i class="fas fa-users"></i></div>
        </div>

        <div class="kpi-card orange clickable" @click="$router.push('/contratos')">
          <div class="kpi-content">
            <span class="kpi-value">{{ geralStats?.contratos_ativos || 0 }}</span>
            <span class="kpi-label">Contratos Vigentes</span>
          </div>
          <div class="kpi-icon"><i class="fas fa-file-signature"></i></div>
        </div>

        <div class="kpi-card green">
          <div class="kpi-content">
            <span class="kpi-value">+{{ geralStats?.novos_clientes_30d || 0 }}</span>
            <span class="kpi-label">Novos (30 dias)</span>
          </div>
          <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
        </div>
      </section>

      <div class="main-grid">
        
        <div class="grid-column">
          <div class="card h-full">
            <div class="widget-header">
                <h3 class="widget-title"><i class="fas fa-wallet"></i> Finanças do Mês</h3>
                <router-link to="/financeiro" class="action-link">Detalhes</router-link>
            </div>

            <div class="finance-summary">
                <div class="finance-row income">
                    <div class="fin-icon"><i class="fas fa-arrow-up"></i></div>
                    <div class="fin-details">
                        <span class="fin-label">Receitas Recebidas</span>
                        <span class="fin-value text-success">{{ formatCurrency(finStats?.a_receber?.pago_mes_atual) }}</span>
                    </div>
                </div>

                <div class="finance-row expense">
                    <div class="fin-icon"><i class="fas fa-arrow-down"></i></div>
                    <div class="fin-details">
                        <span class="fin-label">Despesas Pagas</span>
                        <span class="fin-value text-danger">{{ formatCurrency(finStats?.a_pagar?.pago_mes_atual) }}</span>
                    </div>
                </div>

                <div class="finance-total">
                    <span class="total-label">Saldo em Caixa</span>
                    <span class="total-value" :class="saldoMesAtual >= 0 ? 'text-primary' : 'text-danger'">
                        {{ formatCurrency(saldoMesAtual) }}
                    </span>
                </div>
            </div>
          </div>
        </div>

        <div class="grid-column wide">
          <div class="card h-full">
            <div class="widget-header">
                <h3 class="widget-title"><i class="fas fa-key"></i> Monitoramento de Aluguéis</h3>
                <router-link to="/contratos" class="action-link">Ver Contratos</router-link>
            </div>

            <div class="rent-alerts">
                <div class="alert-badge warning" v-if="aluguelStats?.alugueis_a_vencer">
                    <i class="fas fa-clock"></i> <strong>{{ aluguelStats.alugueis_a_vencer }}</strong> a vencer (7d)
                </div>
                <div class="alert-badge danger" v-if="aluguelStats?.alugueis_atrasados">
                    <i class="fas fa-exclamation-circle"></i> <strong>{{ aluguelStats.alugueis_atrasados }}</strong> em atraso
                </div>
                <div v-if="!aluguelStats?.alugueis_a_vencer && !aluguelStats?.alugueis_atrasados" class="alert-badge success">
                    <i class="fas fa-check-circle"></i> Tudo em dia!
                </div>
            </div>

            <div class="table-responsive">
                <table class="clean-table" v-if="aluguelStats?.proximos_alugueis?.length">
                    <thead>
                        <tr>
                            <th>Imóvel</th>
                            <th>Inquilino</th>
                            <th>Vencimento</th>
                            <th class="text-right">Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="aluguel in aluguelStats.proximos_alugueis.slice(0, 5)" :key="aluguel.id">
                            <td>
                                <div class="info-cell">
                                    <span class="main-text truncate">{{ aluguel.imovel_titulo }}</span>
                                </div>
                            </td>
                            <td><span class="sub-text truncate">{{ aluguel.inquilino_nome }}</span></td>
                            <td><span class="date-badge">{{ formatDate(aluguel.data_vencimento) }}</span></td>
                            <td class="text-right font-weight-bold">{{ formatCurrency(aluguel.valor) }}</td>
                        </tr>
                    </tbody>
                </table>
                <div v-else class="empty-widget">
                    <p>Nenhum vencimento próximo.</p>
                </div>
            </div>
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

// --- COMPUTED ---
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

async function fetchData() {
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
    error.value = 'Não foi possível carregar os dados.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => { fetchData(); });
</script>

<style scoped>
/* =========================================================
   1. GERAL & HEADER
   ========================================================= */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  display: flex; flex-direction: column;
}

.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main { display: flex; justify-content: space-between; align-items: flex-end; }

.btn-icon-refresh {
    background: white; border: 1px solid #e2e8f0; color: #64748b; width: 36px; height: 36px;
    border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
}
.btn-icon-refresh:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* =========================================================
   2. KPIS (ESTILO PADRÃO)
   ========================================================= */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: default; 
  position: relative; overflow: hidden; transition: all 0.2s;
}
.kpi-card.clickable { cursor: pointer; }
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

/* Cores KPI */
.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.green .kpi-value { color: #059669; }
.kpi-card.purple .kpi-value { color: #9333ea; }
.kpi-card.orange .kpi-value { color: #d97706; }

/* =========================================================
   3. LAYOUT PRINCIPAL E CARDS
   ========================================================= */
.main-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 1.5rem; align-items: stretch; }
@media (max-width: 1024px) { .main-grid { grid-template-columns: 1fr; } }

.card {
  background-color: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
  border: 1px solid #e5e7eb; padding: 1.5rem; display: flex; flex-direction: column;
}
.h-full { height: 100%; }

.widget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.8rem; }
.widget-title { font-size: 0.95rem; font-weight: 600; color: #1f2937; display: flex; align-items: center; gap: 0.5rem; margin: 0; }
.action-link { font-size: 0.8rem; color: #2563eb; text-decoration: none; font-weight: 500; }
.action-link:hover { text-decoration: underline; }

/* Financeiro Widget */
.finance-summary { display: flex; flex-direction: column; gap: 1rem; }
.finance-row { display: flex; align-items: center; gap: 1rem; padding: 0.8rem; border-radius: 6px; background-color: #f8fafc; }
.fin-icon {
    width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    background: white; border: 1px solid #e2e8f0; color: #64748b; flex-shrink: 0;
}
.income .fin-icon { color: #059669; border-color: #86efac; background: #f0fdf4; }
.expense .fin-icon { color: #dc2626; border-color: #fca5a5; background: #fef2f2; }

.fin-details { display: flex; flex-direction: column; }
.fin-label { font-size: 0.75rem; color: #64748b; font-weight: 500; }
.fin-value { font-size: 1rem; font-weight: 600; }
.text-success { color: #059669; }
.text-danger { color: #dc2626; }
.text-primary { color: #2563eb; }

.finance-total {
    margin-top: 0.5rem; padding-top: 1rem; border-top: 1px dashed #e2e8f0;
    display: flex; justify-content: space-between; align-items: center;
}
.total-label { font-weight: 600; color: #374151; font-size: 0.9rem; }
.total-value { font-weight: 700; font-size: 1.2rem; }

/* Aluguéis Widget */
.rent-alerts { display: flex; gap: 0.8rem; margin-bottom: 1.2rem; flex-wrap: wrap; }
.alert-badge {
    padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.8rem; display: flex; align-items: center; gap: 0.4rem; border: 1px solid transparent;
}
.alert-badge.warning { background-color: #fffbeb; color: #d97706; border-color: #fcd34d; }
.alert-badge.danger { background-color: #fef2f2; color: #dc2626; border-color: #fca5a5; }
.alert-badge.success { background-color: #f0fdf4; color: #059669; border-color: #86efac; }

/* Tabela */
.clean-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.clean-table th { text-align: left; padding: 0.6rem 0.5rem; color: #94a3b8; font-weight: 600; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.03em; }
.clean-table td { padding: 0.8rem 0.5rem; border-bottom: 1px solid #f1f5f9; color: #334155; }
.clean-table tr:last-child td { border-bottom: none; }

.truncate { max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
.main-text { font-weight: 500; color: #1f2937; }
.sub-text { color: #64748b; font-size: 0.8rem; }
.date-badge { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; color: #475569; }
.text-right { text-align: right; }
.font-weight-bold { font-weight: 600; }

.empty-widget { text-align: center; color: #94a3b8; padding: 1.5rem; font-size: 0.85rem; }

/* =========================================================
   4. LOADING & ERROR
   ========================================================= */
.skeleton-wrapper { display: flex; flex-direction: column; gap: 1.5rem; margin-top: 1rem; }
.skeleton-grid-kpi { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.skeleton-grid-main { display: grid; grid-template-columns: 1fr 2fr; gap: 1rem; }
.skeleton-card { height: 100px; background: #e2e8f0; border-radius: 8px; animation: pulse 1.5s infinite; }
.skeleton-card-tall { height: 300px; background: #e2e8f0; border-radius: 8px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 0.3; } 100% { opacity: 0.6; } }

.alert-box {
    padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.8rem; font-size: 0.9rem;
}
.alert-box.error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.btn-retry { margin-left: auto; padding: 0.3rem 0.8rem; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }

.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .skeleton-grid-kpi { grid-template-columns: 1fr 1fr; }
  .skeleton-grid-main { grid-template-columns: 1fr; }
}
</style>
<template>
  <div class="dashboard-container">
    
    <div v-if="isLoading" class="skeleton-wrapper">
      <div class="skeleton-grid-main">
        <div class="skeleton-card" v-for="n in 4" :key="`sk-main-${n}`"></div>
      </div>
      <div class="skeleton-grid-secondary">
          <div class="skeleton-card-tall" v-for="n in 2" :key="`sk-fin-${n}`"></div>
      </div>
    </div>

    <div v-if="error" class="error-state">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Atenção</h3>
        <p>{{ error }}</p>
        <button @click="fetchData" class="btn-retry">Tentar Novamente</button>
      </div>
    </div>

    <div v-if="!isLoading && !error" class="content-wrapper fade-in">
      
      <section class="kpi-section">
        <div class="stat-card" @click="$router.push('/imoveis')">
          <div class="card-header">
            <span class="card-label">Portfólio</span>
            <div class="icon-bubble primary">
              <i class="fas fa-home"></i>
            </div>
          </div>
          <div class="card-body">
            <h3 class="stat-value">{{ geralStats?.imoveis_ativos || 0 }}</h3>
            <p class="stat-desc">Imóveis Ativos</p>
          </div>
          <div class="card-footer">
            <span class="link-text">Ver Imóveis <i class="fas fa-chevron-right"></i></span>
          </div>
        </div>

        <div class="stat-card" @click="$router.push('/clientes')">
          <div class="card-header">
            <span class="card-label">Relacionamento</span>
            <div class="icon-bubble info">
              <i class="fas fa-users"></i>
            </div>
          </div>
          <div class="card-body">
            <h3 class="stat-value">{{ geralStats?.clientes_ativos || 0 }}</h3>
            <p class="stat-desc">Clientes na Base</p>
          </div>
          <div class="card-footer">
            <span class="link-text">Ver Clientes <i class="fas fa-chevron-right"></i></span>
          </div>
        </div>

        <div class="stat-card" @click="$router.push('/contratos')">
          <div class="card-header">
            <span class="card-label">Comercial</span>
            <div class="icon-bubble warning">
              <i class="fas fa-file-signature"></i>
            </div>
          </div>
          <div class="card-body">
            <h3 class="stat-value">{{ geralStats?.contratos_ativos || 0 }}</h3>
            <p class="stat-desc">Contratos Vigentes</p>
          </div>
          <div class="card-footer">
            <span class="link-text">Gerir Contratos <i class="fas fa-chevron-right"></i></span>
          </div>
        </div>

        <div class="stat-card highlight">
          <div class="card-header">
            <span class="card-label">Crescimento</span>
            <div class="icon-bubble success">
              <i class="fas fa-chart-line"></i>
            </div>
          </div>
          <div class="card-body">
            <h3 class="stat-value">+{{ geralStats?.novos_clientes_30d || 0 }}</h3>
            <p class="stat-desc">Novos Clientes (30d)</p>
          </div>
          <div class="card-footer">
            <span class="trend-positive">Performance Positiva</span>
          </div>
        </div>
      </section>

      <div class="main-grid">
        
        <div class="grid-column">
          <div class="section-header">
            <h3><i class="fas fa-wallet text-muted"></i> Finanças do Mês</h3>
            <router-link to="/financeiro/dashboard" class="action-link">Detalhes</router-link>
          </div>

          <div class="finance-cards">
            <div class="fin-card income">
              <div class="fin-icon">
                <i class="fas fa-arrow-up"></i>
              </div>
              <div class="fin-info">
                <span class="fin-label">Receitas Recebidas</span>
                <span class="fin-value">{{ formatCurrency(finStats?.a_receber?.pago_mes_atual) }}</span>
              </div>
            </div>

            <div class="fin-card expense">
              <div class="fin-icon">
                <i class="fas fa-arrow-down"></i>
              </div>
              <div class="fin-info">
                <span class="fin-label">Despesas Pagas</span>
                <span class="fin-value">{{ formatCurrency(finStats?.a_pagar?.pago_mes_atual) }}</span>
              </div>
            </div>

            <div class="fin-card balance" :class="{ 'negative': saldoMesAtual < 0 }">
              <div class="fin-icon">
                <i class="fas fa-scale-balanced"></i>
              </div>
              <div class="fin-info">
                <span class="fin-label">Saldo em Caixa</span>
                <span class="fin-value">{{ formatCurrency(saldoMesAtual) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="grid-column wide">
          <div class="section-header">
            <h3><i class="fas fa-key text-muted"></i> Monitoramento de Aluguéis</h3>
            <router-link to="/contratos" class="action-link">Todos os Contratos</router-link>
          </div>

          <div class="rent-dashboard">
            <div class="rent-alerts">
              <div class="alert-box warning">
                <div class="alert-icon"><i class="fas fa-clock"></i></div>
                <div class="alert-content">
                  <span class="alert-number">{{ aluguelStats?.alugueis_a_vencer || 0 }}</span>
                  <span class="alert-text">A Vencer (7 dias)</span>
                </div>
              </div>

              <div class="alert-box danger">
                <div class="alert-icon"><i class="fas fa-exclamation-circle"></i></div>
                <div class="alert-content">
                  <span class="alert-number">{{ aluguelStats?.alugueis_atrasados || 0 }}</span>
                  <span class="alert-text">Em Atraso</span>
                </div>
              </div>
            </div>

            <div class="table-container">
              <h4 class="table-title">Próximos Vencimentos</h4>
              
              <div v-if="aluguelStats?.proximos_alugueis?.length" class="clean-table-wrapper">
                <table class="clean-table">
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
                        <div class="imovel-cell">
                          <i class="fas fa-building text-icon"></i>
                          <span class="truncate" :title="aluguel.imovel_titulo">{{ aluguel.imovel_titulo }}</span>
                        </div>
                      </td>
                      <td>
                        <span class="truncate block max-w-[150px]" :title="aluguel.inquilino_nome">{{ aluguel.inquilino_nome }}</span>
                      </td>
                      <td>
                        <span class="badge-date">{{ formatDate(aluguel.data_vencimento) }}</span>
                      </td>
                      <td class="text-right font-medium">
                        {{ formatCurrency(aluguel.valor) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div v-else class="empty-state">
                <div class="empty-icon"><i class="fas fa-check-circle"></i></div>
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
    error.value = 'Não foi possível carregar os dados. Verifique sua conexão.';
  } finally {
    isLoading.value = false;
  }
}

// --- Lifecycle ---
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
/* --- Variáveis Locais (Palette Elegante) --- */
.dashboard-container {
  --primary-color: #007bff;
  --primary-light: #e6f2ff;
  --success-color: #10b981;
  --success-light: #d1fae5;
  --warning-color: #f59e0b;
  --warning-light: #fef3c7;
  --danger-color: #ef4444;
  --danger-light: #fee2e2;
  --info-color: #3b82f6;
  --info-light: #dbeafe;
  
  --text-main: #1f2937;
  --text-secondary: #6b7280;
  --text-light: #9ca3af;
  
  --bg-card: #ffffff;
  --border-subtle: #f3f4f6;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
  --radius-lg: 16px;
  --radius-md: 12px;
  
  /* Padding removido para eliminar espaços em branco superiores, 
     pois o Layout já fornece padding */
  padding: 0; 
  max-width: 1600px;
  margin: 0 auto;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--text-main);
}

/* --- KPI Section (Cards Principais) --- */
.kpi-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-subtle);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(0, 123, 255, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  color: var(--text-light);
}

.icon-bubble {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}
.icon-bubble.primary { background: var(--primary-light); color: var(--primary-color); }
.icon-bubble.info { background: var(--info-light); color: var(--info-color); }
.icon-bubble.warning { background: var(--warning-light); color: var(--warning-color); }
.icon-bubble.success { background: var(--success-light); color: var(--success-color); }

.card-body {
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 300; /* Thin font for numbers */
  margin: 0;
  line-height: 1.1;
  color: var(--text-main);
}

.stat-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

.card-footer {
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
  margin-top: auto;
}

.link-text {
  font-size: 0.85rem;
  color: var(--primary-color);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.trend-positive {
  font-size: 0.8rem;
  color: var(--success-color);
  font-weight: 600;
  background: var(--success-light);
  padding: 4px 8px;
  border-radius: 6px;
}

/* --- Grids de Conteúdo --- */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.section-header h3 {
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.text-muted { color: var(--text-light); }

.action-link {
  font-size: 0.85rem;
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
}
.action-link:hover { text-decoration: underline; }

/* --- Financeiro --- */
.finance-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fin-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  border: 1px solid var(--border-subtle);
  transition: transform 0.2s;
}
.fin-card:hover { transform: translateX(4px); }

.fin-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}
.fin-card.income .fin-icon { background: var(--success-light); color: var(--success-color); }
.fin-card.expense .fin-icon { background: var(--danger-light); color: var(--danger-color); }
.fin-card.balance .fin-icon { background: var(--primary-light); color: var(--primary-color); }

.fin-info { display: flex; flex-direction: column; }
.fin-label { font-size: 0.8rem; color: var(--text-secondary); font-weight: 500; }
.fin-value { font-size: 1.25rem; font-weight: 600; color: var(--text-main); }
.fin-card.balance.negative .fin-value { color: var(--danger-color); }

/* --- Rent Dashboard (Alerts & Table) --- */
.rent-dashboard {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  padding: 1.5rem;
  height: calc(100% - 2.5rem); /* Adjust for header */
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.rent-alerts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.alert-box {
  border-radius: var(--radius-md);
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.alert-box.warning { background: var(--warning-light); border: 1px solid rgba(245, 158, 11, 0.1); }
.alert-box.danger { background: var(--danger-light); border: 1px solid rgba(239, 68, 68, 0.1); }

.alert-icon { font-size: 1.5rem; }
.warning .alert-icon { color: var(--warning-color); }
.danger .alert-icon { color: var(--danger-color); }

.alert-content { display: flex; flex-direction: column; }
.alert-number { font-size: 1.25rem; font-weight: 700; color: var(--text-main); line-height: 1; }
.alert-text { font-size: 0.8rem; color: var(--text-secondary); }

/* --- Table --- */
.table-container { flex-grow: 1; }
.table-title { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; color: var(--text-main); }

.clean-table-wrapper {
  overflow-x: auto;
}
.clean-table { width: 100%; border-collapse: separate; border-spacing: 0; }
.clean-table th {
  text-align: left;
  font-size: 0.75rem;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid var(--border-subtle);
}
.clean-table td {
  padding: 1rem 0.5rem;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.clean-table tr:last-child td { border-bottom: none; }

.text-right { text-align: right; }
.font-medium { font-weight: 500; color: var(--text-main); }
.imovel-cell { display: flex; align-items: center; gap: 0.75rem; }
.text-icon { color: #d1d5db; }
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
  display: block;
}
.badge-date {
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* --- Empty States & Errors --- */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-light);
}
.empty-icon { font-size: 2rem; margin-bottom: 0.5rem; color: #e5e7eb; }

.error-state {
  display: flex; justify-content: center; align-items: center;
  min-height: 300px;
}
.error-content { text-align: center; color: var(--danger-color); }
.error-content i { font-size: 3rem; margin-bottom: 1rem; }
.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

/* --- Skeleton Animation --- */
.skeleton-wrapper { display: flex; flex-direction: column; gap: 2rem; margin-top: 1rem; }
.skeleton-grid-main { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }
.skeleton-card { height: 160px; background: #f3f4f6; border-radius: var(--radius-lg); animation: pulse 1.5s infinite; }
.skeleton-grid-secondary { display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; }
.skeleton-card-tall { height: 300px; background: #f3f4f6; border-radius: var(--radius-lg); animation: pulse 1.5s infinite; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeIn 0.5s ease-out; }

/* --- Responsive --- */
@media (max-width: 1024px) {
  .main-grid { grid-template-columns: 1fr; }
  .rent-dashboard { height: auto; }
}
@media (max-width: 768px) {
  .kpi-section { grid-template-columns: 1fr; }
  .dashboard-container { padding: 0; }
  .skeleton-grid-main { grid-template-columns: 1fr; }
  .skeleton-grid-secondary { grid-template-columns: 1fr; }
}
</style>
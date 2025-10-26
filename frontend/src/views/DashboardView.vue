<template>
  <div class="dashboard-container">
    
    <div v-if="isLoading" class="skeleton-wrapper">
      <div class="skeleton-grid-main">
        <div class="skeleton-card" v-for="n in 4" :key="`sk-main-${n}`"></div>
      </div>
      <div class="skeleton-grid-secondary">
          <div class="skeleton-card-tall" v-for="n in 3" :key="`sk-fin-${n}`"></div>
          <div class="skeleton-card-actions" v-for="n in 4" :key="`sk-act-${n}`"></div>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <strong><i class="fas fa-exclamation-triangle"></i> Erro ao Carregar</strong>
      <p>{{ error }}</p>
    </div>

    <div v-if="stats" class="content-wrapper">
      <div class="stats-grid">
        <div class="stat-card card-primary">
          <div class="icon-wrapper primary"><i class="fas fa-home"></i></div>
          <p class="stat-title">Imóveis Ativos</p>
          <p class="stat-value">{{ stats.imoveis_ativos }}</p>
          <router-link to="/imoveis" class="card-link">Gerir <i class="fas fa-arrow-right"></i></router-link>
        </div>
        <div class="stat-card card-primary">
          <div class="icon-wrapper primary"><i class="fas fa-users"></i></div>
          <p class="stat-title">Clientes Ativos</p>
          <p class="stat-value">{{ stats.clientes_ativos }}</p>
          <router-link to="/clientes" class="card-link">Gerir <i class="fas fa-arrow-right"></i></router-link>
        </div>
        <div class="stat-card card-primary">
          <div class="icon-wrapper primary"><i class="fas fa-file-signature"></i></div>
          <p class="stat-title">Contratos Ativos</p>
          <p class="stat-value">{{ stats.contratos_ativos }}</p>
          <router-link to="/contratos" class="card-link">Gerir <i class="fas fa-arrow-right"></i></router-link>
        </div>
        <div class="stat-card card-primary">
          <div class="icon-wrapper primary"><i class="fas fa-user-plus"></i></div>
          <p class="stat-title">Novos Clientes (30d)</p>
          <p class="stat-value">{{ stats.novos_clientes_30d }}</p>
          <router-link to="/clientes" class="card-link">Ver <i class="fas fa-arrow-right"></i></router-link>
        </div>
      </div>

      <div class="secondary-section-grid">
        <div class="financial-column">
           <h3 class="column-title">Financeiro</h3>
           <div class="financial-stats-grid">
              <div class="stat-card card-financial">
                <div class="icon-wrapper financial"><i class="fas fa-dollar-sign"></i></div>
                <p class="stat-title">Faturamento (30 dias)</p>
                <p class="stat-value">{{ formatCurrency(stats.faturamento_30d) }}</p>
              </div>
              <div class="stat-card card-financial">
                <div class="icon-wrapper financial"><i class="fas fa-chart-line"></i></div>
                <p class="stat-title">Valor em Vendas Ativas</p>
                <p class="stat-value">{{ formatCurrency(stats.total_vendas_ativas) }}</p>
              </div>
              <div class="stat-card card-danger">
                <div class="icon-wrapper danger"><i class="fas fa-calendar-times"></i></div>
                <p class="stat-title">Contas a Receber</p>
                <p class="stat-value">{{ formatCurrency(stats.pagamentos_pendentes) }}</p>
                <router-link to="/financeiro/contas-a-receber" class="card-link">Conferir <i class="fas fa-arrow-right"></i></router-link>
              </div>
            </div>
        </div>

        <div class="actions-column">
           <h3 class="column-title">Ações Rápidas</h3>
           <div class="quick-actions-grid">
              <router-link to="/imoveis/novo" class="action-card">
                <i class="fas fa-plus-circle"></i>
                <span>Novo Imóvel</span>
              </router-link>
              <router-link to="/clientes/novo" class="action-card">
                <i class="fas fa-user-plus"></i>
                <span>Novo Cliente</span>
              </router-link>
              <router-link to="/contratos/novo" class="action-card">
                <i class="fas fa-file-medical"></i>
                <span>Gerar Contrato</span>
              </router-link>
              <router-link to="/financeiro/dre" class="action-card">
                <i class="fas fa-chart-bar"></i>
                <span>Relatório DRE</span>
              </router-link>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

interface DashboardStats {
  imoveis_ativos: number;
  clientes_ativos: number;
  contratos_ativos: number;
  novos_clientes_30d: number;
  faturamento_30d: number;
  pagamentos_pendentes: number;
  total_vendas_ativas: number;
}

const stats = ref<DashboardStats | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

function formatCurrency(value: number) {
  if (typeof value !== 'number' || isNaN(value)) { return 'R$ 0,00'; }
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

onMounted(async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<DashboardStats>('/v1/stats/');
    if (!response.data) { throw new Error("A API retornou uma resposta vazia."); }
    stats.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar estatísticas:", err);
    error.value = 'Não foi possível carregar as estatísticas. Verifique a conexão com a API.';
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
/* AJUSTES (ULTRA-COMPACTO v2):
  - Título H1 removido.
  - --padding-page/card/gap: 0.65rem -> 0.5rem (8px)
  - .stat-value: 1.65rem -> 1.6rem
  - .icon-wrapper: 32px -> 30px
  - .action-card padding: 0.65rem 1rem -> 0.5rem 0.75rem
  - .column-title font-size: 0.9rem -> 0.85rem
*/
.dashboard-container {
  --color-primary: #007bff;
  --color-primary-light: #e6f2ff;
  --color-financial: #28a745;
  --color-financial-light: #eaf6ec;
  --color-danger: #dc3545;
  --color-danger-light: #fdebec;
  --color-text-primary: #212529;
  --color-text-secondary: #6c757d;
  --color-background: #f8f9fa;
  --color-card-bg: #ffffff;
  --color-border: #e9ecef;
  --border-radius-md: 6px;
  --border-radius-lg: 8px;
  
  /* Valores de tamanho mínimos */
  --padding-card: 0.5rem;
  --padding-page: 0.5rem;
  --grid-gap: 0.5rem;
}

.dashboard-container {
  padding: var(--padding-page);
  background-color: var(--color-background);
  min-height: 100vh;
}

/* --- Mensagens de Estado --- */
.error-message {
  background-color: var(--color-danger-light);
  border: 1px solid var(--color-danger);
  color: var(--color-danger);
  padding: 0.75rem; /* Ajustado */
  border-radius: var(--border-radius-md);
  margin-bottom: var(--grid-gap);
}
.error-message strong { font-size: 0.9rem; display: block; margin-bottom: 0.25rem; } /* Ajustado */

/* --- Skeleton Loader Adaptado --- */
.skeleton-wrapper { width: 100%; display: flex; flex-direction: column; gap: var(--grid-gap); }
.skeleton-grid-main { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--grid-gap); }
.skeleton-grid-secondary { display: grid; grid-template-columns: 2fr 1fr; gap: var(--grid-gap); }
.skeleton-card { height: 100px; background-color: #e0e0e0; border-radius: var(--border-radius-md); animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite; } /* Ajustado */
.skeleton-card-tall { height: 100px; background-color: #e0e0e0; border-radius: var(--border-radius-md); animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite; } /* Ajustado */
.skeleton-card-actions { height: 35px; background-color: #e0e0e0; border-radius: var(--border-radius-md); animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite; } /* Ajustado */
.skeleton-grid-secondary > div:first-child { display: flex; flex-direction: column; gap: var(--grid-gap); } 
.skeleton-grid-secondary > div:last-child { display: flex; flex-direction: column; gap: var(--grid-gap); } 
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* --- Grids de Conteúdo --- */
.content-wrapper { display: flex; flex-direction: column; gap: var(--grid-gap); }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--grid-gap); }

/* --- Secção Secundária (Financeiro + Ações) --- */
.secondary-section-grid {
  display: grid;
  grid-template-columns: 2fr 1fr; 
  gap: var(--grid-gap);
  align-items: start;
}
.financial-column, .actions-column {
  display: flex;
  flex-direction: column;
  gap: 0.4rem; /* Ajustado */
}
.column-title {
    font-size: 0.85rem; /* Ajustado */
    font-weight: 600;
    color: var(--color-text-secondary);
    margin: 0 0 0.1rem 0.2rem; /* Ajustado */
    padding: 0;
}

.financial-stats-grid { display: grid; grid-template-columns: 1fr; gap: var(--grid-gap); }
.quick-actions-grid { display: grid; grid-template-columns: 1fr; gap: var(--grid-gap); }

/* --- Design dos Cards de Estatística (Flat) --- */
.stat-card {
  background-color: var(--color-card-bg);
  padding: var(--padding-card);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  text-align: left;
  transition: border-color 0.3s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  border-left: 3px solid var(--color-primary);
}
.stat-card:hover { border-left-color: #0056b3; border-color: #ced4da; }

.stat-card.card-primary { border-left-color: var(--color-primary); }
.stat-card.card-financial { border-left-color: var(--color-financial); }
.stat-card.card-danger { border-left-color: var(--color-danger); }
.stat-card.card-primary:hover { border-left-color: #0056b3; }
.stat-card.card-financial:hover { border-left-color: #1c7430; }
.stat-card.card-danger:hover { border-left-color: #a71d2a; }

.icon-wrapper {
  font-size: 1.1rem; margin-bottom: 0.35rem; width: 30px; height: 30px; /* Ajustado */
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
}
.icon-wrapper.primary { background-color: var(--color-primary-light); color: var(--color-primary); }
.icon-wrapper.financial { background-color: var(--color-financial-light); color: var(--color-financial); }
.icon-wrapper.danger { background-color: var(--color-danger-light); color: var(--color-danger); }

.stat-title {
  font-size: 0.75rem; font-weight: 500; color: var(--color-text-secondary); margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.stat-value {
  font-size: 1.6rem; font-weight: 700; color: var(--color-text-primary); /* Ajustado */
  margin: 0.1rem 0 0 0; flex-grow: 1; /* Ajustado */
}
.card-link {
  margin-top: 0.25rem; font-size: 0.75rem; color: var(--color-primary); /* Ajustado */
  text-decoration: none; font-weight: 600; align-self: flex-start;
}
.card-link:hover { color: #0056b3; }
.card-danger .card-link { color: var(--color-danger); }
.card-danger .card-link:hover { color: #a71d2a; }

/* --- Design dos Atalhos Rápidos (Horizontal) --- */
.action-card {
  background-color: var(--color-card-bg);
  padding: 0.5rem 0.75rem; border-radius: var(--border-radius-md); /* Ajustado */
  border: 1px solid var(--color-border); text-decoration: none;
  font-weight: 500; font-size: 0.8rem; color: var(--color-text-secondary); /* Ajustado */
  display: flex; flex-direction: row; align-items: center; justify-content: flex-start;
  gap: 0.5rem; transition: all 0.3s ease; /* Ajustado */
}
.action-card:hover { border-color: var(--color-primary); color: var(--color-primary); }
.action-card i { font-size: 1rem; color: var(--color-primary); } /* Ajustado */

/* --- Responsividade --- */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .secondary-section-grid { grid-template-columns: 1fr; }
  .financial-stats-grid { grid-template-columns: repeat(3, 1fr); } 
  .quick-actions-grid { grid-template-columns: repeat(2, 1fr); } 
  .skeleton-grid-main, .skeleton-grid-secondary { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .dashboard-container { padding: 0.5rem; --grid-gap: 0.5rem; }
  .stats-grid, .financial-stats-grid, .quick-actions-grid,
  .secondary-section-grid, .skeleton-grid-main, .skeleton-grid-secondary {
    grid-template-columns: 1fr; 
  }
}
</style>
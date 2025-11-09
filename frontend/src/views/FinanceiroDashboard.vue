<template>
  <div class="financeiro-dashboard-container">
    
    <div class="header-actions-compact">
      <router-link :to="{ name: 'transacao-nova', query: { tipo: 'RECEITA' } }" class="btn-primary">
        + Receita
      </router-link>
      <router-link :to="{ name: 'transacao-nova', query: { tipo: 'DESPESA' } }" class="btn-secondary">
        + Despesa
      </router-link>
      <router-link :to="{ name: 'dre' }" class="btn-info">
        Ver DRE
      </router-link>
    </div>
    
    <div v-if="isLoading" class="loading-message">
      A carregar dados financeiros...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="stats" class="stats-grid">
        
      <div class="group-header">
        <h3 class="group-title">Resultados do Mês (Caixa Realizado)</h3>
      </div>
        
      <div class="stat-card revenue">
        <h4 class="card-title">Receitas Pagas</h4>
        <p class="card-value">{{ formatarValor(stats.a_receber.pago_mes_atual) }}</p>
      </div>
      
      <div class="stat-card expense">
        <h4 class="card-title">Despesas Pagas</h4>
        <p class="card-value">{{ formatarValor(stats.a_pagar.pago_mes_atual) }}</p>
      </div>
        
      <div :class="['stat-card', (stats.a_receber.pago_mes_atual - stats.a_pagar.pago_mes_atual) >= 0 ? 'net-positive' : 'net-negative']">
        <h4 class="card-title">Lucro do Mês (Caixa)</h4>
        <p class="card-value">{{ formatarValor(stats.a_receber.pago_mes_atual - stats.a_pagar.pago_mes_atual) }}</p>
      </div>

      <div class="group-header">
        <h3 class="group-title">Próximo Fluxo e Saldo Previsto</h3>
      </div>
        
      <div class="stat-card pending-revenue">
        <h4 class="card-title">A Receber (Pendente)</h4>
        <p class="card-value">{{ formatarValor(stats.a_receber.pendente) }}</p>
      </div>
        
      <div class="stat-card pending-expense">
        <h4 class="card-title">A Pagar (Pendente)</h4>
        <p class="card-value">{{ formatarValor(stats.a_pagar.pendente) }}</p>
      </div>

      <div :class="['stat-card', (stats.saldo_previsto ?? 0) >= 0 ? 'balance-positive' : 'balance-negative']">
        <h4 class="card-title">Saldo Previsto</h4>
        <p class="card-value">{{ formatarValor(stats.saldo_previsto) }}</p>
      </div>
    </div>
    
    <div class="dashboard-section">
        <div class="section-title">Análise Visual do Fluxo de Caixa</div>
        <div class="chart-container card">
            <p class="placeholder-text">Gráfico de Receitas vs Despesas (Baseado em DRE)</p>
        </div>
    </div>
    
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

// Interfaces (Baseadas no retorno do /stats)
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

// Função formatarValor (Reutiliza a lógica de formatação)
const formatarValor = (valor: number | null | undefined): string => {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    const numValue = typeof valor === 'string' ? parseFloat(valor) : valor;
    if (isNaN(numValue)) return 'R$ 0,00';
    return numValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

async function fetchStats() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<StatsFinanceiro>('/v1/financeiro/transacoes/stats/');
    stats.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar estatísticas financeiras:", err);
    error.value = 'Não foi possível carregar as estatísticas financeiras.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
/* ======================================= */
/* ESTILOS GERAIS/BASE                      */
/* ======================================= */
.financeiro-dashboard-container {
  padding: 0; 
}

/* NOVO: Estilo para o container de ações no topo (compactado) */
.header-actions-compact {
    display: flex;
    justify-content: flex-start; /* Alinha os botões à esquerda (topo da página) */
    gap: 0.5rem;
    margin-bottom: 0.75rem; /* [OTIMIZAÇÃO] Reduzido o espaço */
    padding-top: 0.25rem; /* Espaço mínimo para não colar totalmente no topo da view */
}

/* Base Card Style */
.card {
    background: white; 
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06); 
}

/* Botões (Reutilizados do componente anterior para consistência) */
.btn-primary, .btn-secondary, .btn-info {
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    font-weight: 500;
    font-size: 0.9rem;
    text-decoration: none;
    transition: background-color 0.3s;
    border: none;
    cursor: pointer;
    color: white;
}
.btn-primary { background-color: #007bff; }
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary { background-color: #6c757d; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-info { background-color: #17a2b8; } 
.btn-info:hover { background-color: #138496; }


/* Loading and Error Messages */
.loading-message, .error-message {
    text-align: center;
    padding: 1rem; /* [OTIMIZAÇÃO] Reduzido */
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 0.75rem; /* [OTIMIZAÇÃO] Reduzido */
    color: #dc3545;
}


/* ======================================= */
/* STATS GRID E CARDS (O CORPO DO DASH)    */
/* ======================================= */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); 
  gap: 1rem; /* [OTIMIZAÇÃO] Reduzido */
  margin-bottom: 1rem; /* [OTIMIZAÇÃO] Reduzido */
}

.group-header {
    grid-column: 1 / -1; 
    margin-top: 0.25rem; /* [OTIMIZAÇÃO] Reduzido */
    margin-bottom: 0.4rem; /* [OTIMIZAÇÃO] Reduzido */
    padding-left: 0.5rem;
    border-bottom: 1px solid #eee;
}
.group-title {
    font-size: 1rem; /* [OTIMIZAÇÃO] Reduzido */
    font-weight: 600;
    color: #495057;
    margin: 0;
}

.stat-card {
  padding: 0.8rem 1rem; /* [OTIMIZAÇÃO] Reduzido padding */
  border-radius: 8px; 
  background-color: #fcfcfc;
  border-left: 5px solid;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.card-title {
    font-size: 0.85rem;
    color: #6c757d; 
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 0.4rem 0; /* [OTIMIZAÇÃO] Reduzido */
} 
.card-value {
    font-size: 1.6rem; /* [OTIMIZAÇÃO] Reduzido */
    font-weight: 700; 
    color: #343a40;
    margin: 0;
}

/* Cores de Status (Mantidas) */
.stat-card.revenue { border-color: #28a745; } 
.stat-card.expense { border-color: #dc3545; } 
.stat-card.pending-revenue { border-color: #ffc107; } 
.stat-card.pending-expense { border-color: #6c757d; } 

.net-positive, .balance-positive { border-color: #17a2b8; }
.net-negative, .balance-negative { border-color: #dc3545; }

.net-positive .card-value, .balance-positive .card-value { color: #17a2b8; }
.net-negative .card-value, .balance-negative .card-value { color: #dc3545; }


/* ======================================= */
/* RELATÓRIOS/GRÁFICOS                     */
/* ======================================= */
.dashboard-section {
    margin-top: 0.75rem; /* [OTIMIZAÇÃO] Reduzido */
}
.section-title {
    font-size: 1.1rem; /* [OTIMIZAÇÃO] Reduzido */
    font-weight: 600;
    color: #343a40;
    margin-bottom: 0.75rem; /* [OTIMIZAÇÃO] Reduzido */
    padding-left: 0.5rem;
}
.chart-container {
    padding: 1.5rem; /* [OTIMIZAÇÃO] Reduzido */
    height: 300px; /* [OTIMIZAÇÃO] Altura reduzida */
    display: flex;
    align-items: center;
    justify-content: center;
}
.placeholder-text {
    color: #999;
    font-style: italic;
}

/* Media Queries para responsividade */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .group-header {
      grid-column: 1 / -1;
  }
}
@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr; 
  }
  .header-actions-compact {
      flex-direction: column;
      gap: 0.25rem;
      align-items: stretch;
  }
}
</style>
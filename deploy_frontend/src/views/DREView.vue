<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Financeiro</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">DRE</span>
           </nav>
           
           <h1>Demonstrativo de Resultados (DRE)</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchDRE" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <button class="btn-primary-thin" @click="exportarPDF" :disabled="isLoading">
              <i class="fas fa-file-pdf"></i> Exportar PDF
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(dreData?.total_receitas || 0) }}</span>
          <span class="kpi-label">Receita Bruta</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-arrow-trend-up"></i></div>
      </div>

      <div class="kpi-card red">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(dreData?.total_despesas || 0) }}</span>
          <span class="kpi-label">Despesas Operacionais</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-arrow-trend-down"></i></div>
      </div>

      <div class="kpi-card" :class="(dreData?.lucro_prejuizo || 0) >= 0 ? 'blue' : 'orange'">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(dreData?.lucro_prejuizo || 0) }}</span>
          <span class="kpi-label">Resultado Líquido</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-scale-balanced"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ calcularMargem() }}%</span>
          <span class="kpi-label">Margem de Lucro</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-percentage"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell" style="min-width: 300px;">
          <label>Período de Análise (De - Até)</label>
          <div class="date-group-row">
            <input type="date" v-model="filtros.data_inicio" @change="fetchDRE" class="form-control">
            <span class="date-sep">até</span>
            <input type="date" v-model="filtros.data_fim" @change="fetchDRE" class="form-control">
          </div>
        </div>

        <div class="filter-cell">
          <label>Visualização</label>
          <select v-model="filtros.regime" @change="fetchDRE" class="form-control">
            <option value="caixa">Regime de Caixa (Pagamento)</option>
            <option value="competencia">Regime de Competência (Vencimento)</option>
          </select>
        </div>

        <div class="filter-cell clear-cell">
            <label>&nbsp;</label>
            <button @click="resetFilters" class="btn-clear" title="Resetar Período">
                <i class="fas fa-history"></i>
            </button>
        </div>
    </div>

    <main class="report-main-wrapper">
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Gerando demonstrativo...</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table dre-table">
          <thead>
            <tr>
              <th>Descrição da Conta</th>
              <th class="text-right">Valor Acumulado</th>
              <th class="text-right" width="10%">%</th>
            </tr>
          </thead>
          <tbody>
            <tr class="row-section">
              <td colspan="3">RECEITAS OPERACIONAIS</td>
            </tr>
            <tr v-for="cat in dreData?.detalhe_receitas" :key="cat.categoria">
              <td class="pl-indent">{{ cat.categoria }}</td>
              <td class="text-right text-success">{{ formatarValor(cat.total) }}</td>
              <td class="text-right text-muted">{{ calcularPercentual(cat.total, dreData.total_receitas) }}%</td>
            </tr>
            <tr class="row-subtotal">
              <td>(=) RECEITA BRUTA</td>
              <td class="text-right">{{ formatarValor(dreData?.total_receitas || 0) }}</td>
              <td class="text-right">100%</td>
            </tr>

            <tr class="row-section mt-section">
              <td colspan="3">DESPESAS OPERACIONAIS</td>
            </tr>
            <tr v-for="cat in dreData?.detalhe_despesas" :key="cat.categoria">
              <td class="pl-indent">{{ cat.categoria }}</td>
              <td class="text-right text-danger">{{ formatarValor(cat.total) }}</td>
              <td class="text-right text-muted">{{ calcularPercentual(cat.total, dreData.total_receitas) }}%</td>
            </tr>
            <tr class="row-subtotal">
              <td>(=) TOTAL DE DESPESAS</td>
              <td class="text-right">{{ formatarValor(dreData?.total_despesas || 0) }}</td>
              <td class="text-right text-muted">{{ calcularPercentual(dreData?.total_despesas, dreData?.total_receitas) }}%</td>
            </tr>

            <tr class="row-total-final" :class="(dreData?.lucro_prejuizo || 0) >= 0 ? 'positive' : 'negative'">
              <td>(=) RESULTADO LÍQUIDO DO PERÍODO</td>
              <td class="text-right">{{ formatarValor(dreData?.lucro_prejuizo || 0) }}</td>
              <td class="text-right">{{ calcularMargem() }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import apiClient from '@/services/api';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const isLoading = ref(true);
const dreData = ref<any>(null);

const filtros = reactive({
    data_inicio: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
    data_fim: format(endOfMonth(new Date()), 'yyyy-MM-dd'),
    regime: 'caixa'
});

const formatarValor = (valor: number) => {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const calcularPercentual = (valor: number, total: number) => {
    if (!total || total === 0) return '0.0';
    return ((valor / total) * 100).toFixed(1);
};

const calcularMargem = () => {
    if (!dreData.value?.total_receitas) return '0.0';
    return ((dreData.value.lucro_prejuizo / dreData.value.total_receitas) * 100).toFixed(1);
};

const resetFilters = () => {
    filtros.data_inicio = format(startOfMonth(new Date()), 'yyyy-MM-dd');
    filtros.data_fim = format(endOfMonth(new Date()), 'yyyy-MM-dd');
    fetchDRE();
};

const fetchDRE = async () => {
    isLoading.value = true;
    try {
        const response = await apiClient.get('/v1/financeiro/transacoes/dre/', { params: filtros });
        dreData.value = response.data;
    } catch (error) {
        console.error("Erro ao buscar DRE:", error);
    } finally {
        isLoading.value = false;
    }
};

const exportarPDF = () => {
    window.print(); // Ou chamar endpoint de PDF se existir
};

onMounted(fetchDRE);
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (Page Scroll) */
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fcfcfc;
  font-family: 'Inter', sans-serif;
  padding: 1.5rem 2.5rem;
  box-sizing: border-box;
}

/* HEADER */
.page-header { margin-bottom: 2rem; flex-shrink: 0; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Thin */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary-thin:hover { background: #1d4ed8; }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(4, 1fr); 
    gap: 1.25rem; margin-bottom: 2rem; flex-shrink: 0;
}
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); position: relative; overflow: hidden;
}
.kpi-value { font-size: 1.6rem; font-weight: 300; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.green .kpi-value { color: #059669; }
.kpi-card.red .kpi-value { color: #dc2626; }
.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.orange .kpi-value { color: #d97706; }
.kpi-card.purple .kpi-value { color: #9333ea; }

/* TOOLBAR GRID */
.toolbar-grid {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; display: grid; grid-template-columns: auto 1fr auto; 
  gap: 1.5rem; align-items: end; margin-bottom: 1.5rem; flex-shrink: 0;
}
.filter-cell { display: flex; flex-direction: column; gap: 0.3rem; }
.filter-cell label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.form-control {
  padding: 0.5rem 0.8rem; font-size: 0.85rem; border: 1px solid #cbd5e1; border-radius: 6px; height: 38px;
}
.date-group-row { display: flex; align-items: center; gap: 0.5rem; }
.date-sep { color: #94a3b8; font-size: 0.8rem; }
.btn-clear { width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 6px; color: #64748b; cursor: pointer; }

/* TABELA DRE */
.report-main-wrapper {
  width: 100%; background: white; border-radius: 8px; border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02); margin-bottom: 2rem;
}
.report-table { width: 100%; border-collapse: collapse; }
.report-table th {
  background: #f8fafc; padding: 1rem 1.5rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase;
  border-bottom: 1px solid #e2e8f0; position: sticky; top: 0;
}
.report-table td { padding: 0.8rem 1.5rem; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; color: #334155; }

/* DRE Specific Rows */
.row-section { background-color: #f8fafc; }
.row-section td { font-weight: 800; font-size: 0.75rem; color: #64748b; letter-spacing: 0.05em; padding-top: 1.2rem; }
.pl-indent { padding-left: 3rem !important; }

.row-subtotal td { font-weight: 700; background-color: #fafafa; border-top: 2px solid #f1f5f9; color: #1e293b; }

.row-total-final { border-top: 3px solid #1e293b; }
.row-total-final td { font-weight: 900; font-size: 1rem; padding: 1.2rem 1.5rem; }
.row-total-final.positive { background-color: #f0fdf4; color: #15803d; }
.row-total-final.negative { background-color: #fef2f2; color: #b91c1c; }

.mt-section { border-top: 20px solid transparent; }

/* Utils */
.text-right { text-align: right; }
.text-success { color: #16a34a; font-weight: 600; }
.text-danger { color: #dc2626; font-weight: 600; }
.text-muted { color: #94a3b8; font-size: 0.8rem; }
.font-bold { font-weight: 700; }

.loading-state { text-align: center; padding: 5rem; color: #94a3b8; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media print {
    .page-header, .kpi-grid, .toolbar-grid { display: none; }
    .page-container { padding: 0; }
    .report-main-wrapper { border: none; box-shadow: none; }
}

@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .toolbar-grid { grid-template-columns: 1fr; }
}
</style>
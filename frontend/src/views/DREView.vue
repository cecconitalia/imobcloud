<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <router-link to="/">Início</router-link>
              <i class="fas fa-chevron-right separator"></i> 
              <router-link to="/financeiro">Financeiro</router-link>
              <i class="fas fa-chevron-right separator"></i>
              <span class="active">DRE</span>
           </nav>
           
           <h1>Demonstrativo de Resultados</h1>
        </div>
      </div>
    </header>

    <div class="card filter-card no-print">
      <div class="filter-row">
        <div class="form-group">
            <label for="start-date">Data de Início</label>
            <div class="input-wrapper">
                <i class="far fa-calendar-alt input-icon"></i>
                <input type="date" id="start-date" v-model="startDate" class="form-input has-icon">
            </div>
        </div>
        <div class="form-group">
            <label for="end-date">Data de Fim</label>
            <div class="input-wrapper">
                <i class="far fa-calendar-alt input-icon"></i>
                <input type="date" id="end-date" v-model="endDate" class="form-input has-icon">
            </div>
        </div>
        <div class="actions-group">
            <button @click="fetchDRE" class="btn-primary" :disabled="isLoading">
                <i v-if="isLoading" class="fas fa-spinner fa-spin"></i>
                <span v-else><i class="fas fa-search"></i> Gerar Relatório</span>
            </button>
            <button @click="imprimirDRE" class="btn-secondary" :disabled="!dreData || isLoading">
                <i class="fas fa-print"></i> Imprimir
            </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading && !dreData" class="loading-state">
        <div class="spinner"></div>
        <p>Calculando resultados...</p>
    </div>
    
    <div v-if="error" class="alert-box error no-print">
        <i class="fas fa-exclamation-triangle"></i> {{ error }}
    </div>

    <div v-if="dreData" class="report-content fade-in" id="dre-print-area">
        
        <div class="report-header print-only">
             <h2>DRE - Demonstrativo de Resultados</h2>
             <p>Período: {{ formatarData(startDate) }} a {{ formatarData(endDate) }}</p>
        </div>

        <div class="summary-grid">
            <div class="kpi-card green">
                <div class="kpi-content">
                    <span class="kpi-label">Total Receitas</span>
                    <span class="kpi-value">{{ formatarValor(dreData.total_receitas) }}</span>
                </div>
                <div class="kpi-icon"><i class="fas fa-arrow-up"></i></div>
            </div>

            <div class="kpi-card red">
                <div class="kpi-content">
                    <span class="kpi-label">Total Despesas</span>
                    <span class="kpi-value">{{ formatarValor(dreData.total_despesas) }}</span>
                </div>
                <div class="kpi-icon"><i class="fas fa-arrow-down"></i></div>
            </div>

            <div class="kpi-card" :class="dreData.resultado_liquido >= 0 ? 'blue' : 'orange'">
                <div class="kpi-content">
                    <span class="kpi-label">Resultado Líquido</span>
                    <span class="kpi-value">{{ formatarValor(dreData.resultado_liquido) }}</span>
                </div>
                <div class="kpi-icon"><i class="fas fa-balance-scale"></i></div>
            </div>
        </div>

       <div class="card table-card">
           <table class="dre-table">
              <thead>
                  <tr>
                      <th>Categoria / Descrição</th>
                      <th class="text-right">Valor</th>
                  </tr>
              </thead>
              <tbody>
                  <tr class="section-header revenue-header">
                      <td colspan="2"><i class="fas fa-plus-circle"></i> Receitas Operacionais</td>
                  </tr>
                  <tr v-for="receita in dreData.detalhes_receitas" :key="`rec-${receita.categoria_id}`" class="item-row">
                      <td class="item-name">{{ receita.categoria_nome }}</td>
                      <td class="text-right text-success">{{ formatarValor(receita.total) }}</td>
                  </tr>
                  <tr class="subtotal-row revenue-bg">
                      <td><strong>Total de Receitas</strong></td>
                      <td class="text-right text-success"><strong>{{ formatarValor(dreData.total_receitas) }}</strong></td>
                  </tr>

                  <tr class="spacer-row"><td colspan="2"></td></tr>
                  <tr class="section-header expense-header">
                      <td colspan="2"><i class="fas fa-minus-circle"></i> Despesas Operacionais</td>
                  </tr>
                   <tr v-for="despesa in dreData.detalhes_despesas" :key="`desp-${despesa.categoria_id}`" class="item-row">
                      <td class="item-name">{{ despesa.categoria_nome }}</td>
                      <td class="text-right text-danger">{{ formatarValor(despesa.total) }}</td>
                  </tr>
                  <tr class="subtotal-row expense-bg">
                      <td><strong>Total de Despesas</strong></td>
                      <td class="text-right text-danger"><strong>{{ formatarValor(dreData.total_despesas) }}</strong></td>
                  </tr>

                   <tr class="spacer-row"><td colspan="2"></td></tr>
                   <tr class="resultado-final-row" :class="dreData.resultado_liquido >= 0 ? 'bg-success-light' : 'bg-danger-light'">
                      <td><strong>RESULTADO LÍQUIDO DO PERÍODO</strong></td>
                       <td class="text-right big-number" :class="dreData.resultado_liquido >= 0 ? 'text-success' : 'text-danger'">
                           {{ formatarValor(dreData.resultado_liquido) }}
                       </td>
                   </tr>
              </tbody>
          </table>
       </div>
    </div>

    <div v-if="!dreData && !isLoading && !error" class="empty-state">
        <div class="empty-content">
            <i class="fas fa-chart-pie"></i>
            <h3>Geração de DRE</h3>
            <p>Selecione o período desejado acima e clique em "Gerar Relatório".</p>
        </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import apiClient from '@/services/api';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface CategoriaDetalhe {
    categoria_id: number;
    categoria_nome: string;
    total: number;
}

interface DreData {
    total_receitas: number;
    total_despesas: number;
    resultado_liquido: number;
    detalhes_receitas: CategoriaDetalhe[];
    detalhes_despesas: CategoriaDetalhe[];
}

const today = new Date();
const startDate = ref(format(startOfMonth(today), 'yyyy-MM-dd'));
const endDate = ref(format(endOfMonth(today), 'yyyy-MM-dd'));

const dreData = ref<DreData | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

function formatarValor(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return 'R$ 0,00';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(data: string | null | undefined): string {
    if (!data) return '-';
    try {
        return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
    } catch { return 'Inválida'; }
}

async function fetchDRE() {
  isLoading.value = true;
  error.value = null;
  dreData.value = null;

  if (!startDate.value || !endDate.value) {
      error.value = "Por favor, selecione as datas de início e fim.";
      isLoading.value = false;
      return;
  }

  try {
    const response = await apiClient.get<DreData>('/v1/financeiro/dre/', {
      params: { start_date: startDate.value, end_date: endDate.value }
    });
    dreData.value = response.data;
  } catch (err) {
    console.error("Erro ao gerar DRE:", err);
    error.value = "Não foi possível gerar o relatório. Verifique a conexão.";
  } finally {
    isLoading.value = false;
  }
}

function imprimirDRE() {
    window.print();
}
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
.breadcrumb a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
.breadcrumb a:hover { color: #2563eb; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main { display: flex; justify-content: space-between; align-items: flex-end; }

/* =========================================================
   2. FILTROS
   ========================================================= */
.card {
  background-color: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
  border: 1px solid #e5e7eb; padding: 1.5rem;
}
.filter-card { margin-bottom: 2rem; }

.filter-row { display: flex; align-items: flex-end; gap: 1.5rem; flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; min-width: 180px; }
label { font-weight: 500; font-size: 0.85rem; color: #4b5563; }

.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; font-size: 0.85rem; pointer-events: none; }
.form-input {
    width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.9rem; transition: all 0.2s; background-color: #fff; box-sizing: border-box; color: #1f2937;
}
.form-input.has-icon { padding-left: 2.2rem; }
.form-input:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.actions-group { display: flex; gap: 0.8rem; margin-bottom: 1px; }
.btn-primary, .btn-secondary {
    padding: 0.6rem 1.2rem; border-radius: 6px; border: none; font-weight: 500; cursor: pointer; font-size: 0.9rem;
    display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary { background-color: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.1); }
.btn-primary:hover { background-color: #1d4ed8; transform: translateY(-1px); }
.btn-secondary { background-color: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.btn-secondary:hover { background-color: #f1f5f9; border-color: #cbd5e1; color: #334155; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

/* =========================================================
   3. RESUMO (KPIS)
   ========================================================= */
.summary-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
    gap: 1.5rem; margin-bottom: 2rem;
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 600; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-bottom: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.15; }

.kpi-card.green { border-bottom: 3px solid #16a34a; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #16a34a; }

.kpi-card.red { border-bottom: 3px solid #dc2626; }
.kpi-card.red .kpi-value, .kpi-card.red .kpi-icon { color: #dc2626; }

.kpi-card.blue { border-bottom: 3px solid #2563eb; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }

.kpi-card.orange { border-bottom: 3px solid #f97316; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #f97316; }

/* =========================================================
   4. TABELA
   ========================================================= */
.table-card { padding: 0; overflow: hidden; border: 1px solid #e2e8f0; }

.dre-table { width: 100%; border-collapse: collapse; }
.dre-table th { 
    background-color: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.8rem; 
    text-transform: uppercase; padding: 1rem 1.5rem; text-align: left; border-bottom: 1px solid #e2e8f0;
}
.dre-table td { padding: 0.8rem 1.5rem; font-size: 0.9rem; color: #334155; border-bottom: 1px solid #f1f5f9; }

.text-right { text-align: right; }
.text-success { color: #16a34a; }
.text-danger { color: #dc2626; }

/* Headers de Seção */
.section-header td { 
    background-color: #f8fafc; font-weight: 600; color: #475569; 
    padding-top: 1.2rem; padding-bottom: 0.5rem; font-size: 0.85rem; letter-spacing: 0.03em;
    border-top: 1px solid #e2e8f0;
}
.revenue-header td i { color: #16a34a; margin-right: 6px; }
.expense-header td i { color: #dc2626; margin-right: 6px; }

/* Linhas de Item */
.item-row td { padding-left: 2.5rem; }
.item-name { color: #475569; }

/* Subtotais */
.subtotal-row td { 
    background-color: #fcfcfc; font-weight: 600; border-top: 2px solid #e2e8f0; 
    padding-top: 0.8rem; padding-bottom: 0.8rem;
}
.revenue-bg td { background-color: #f0fdf4; border-top-color: #bbf7d0; }
.expense-bg td { background-color: #fef2f2; border-top-color: #fecaca; }

/* Resultado Final */
.spacer-row td { border: none; height: 1.5rem; }
.resultado-final-row td { 
    font-size: 1.1rem; padding: 1.5rem; border-top: 2px solid #cbd5e1;
    background-color: #f1f5f9; font-weight: 700; color: #1e293b;
}
.bg-success-light td { background-color: #dcfce7; border-top-color: #86efac; }
.bg-danger-light td { background-color: #fee2e2; border-top-color: #fca5a5; }
.big-number { font-size: 1.25rem; }

/* =========================================================
   5. UTILITÁRIOS
   ========================================================= */
.loading-state, .empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 4rem; color: #94a3b8; text-align: center;
}
.spinner { width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.empty-content i { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }
.empty-content h3 { font-size: 1.2rem; color: #475569; margin: 0 0 0.5rem 0; }

.alert-box { padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.8rem; font-size: 0.9rem; }
.alert-box.error { background-color: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.print-only { display: none; }

/* =========================================================
   6. IMPRESSÃO
   ========================================================= */
@media print {
    @page { margin: 1cm; size: A4; }
    body { background-color: white; color: black; font-family: 'Times New Roman', Times, serif; }
    .page-container { padding: 0; margin: 0; background: white; min-height: auto; }
    .no-print, .page-header, .filter-card, .btn-primary, .btn-secondary { display: none !important; }
    
    .print-only { display: block; text-align: center; margin-bottom: 2rem; border-bottom: 2px solid #000; padding-bottom: 1rem; }
    .print-only h2 { margin: 0; font-size: 24pt; }
    .print-only p { margin: 5px 0 0 0; font-size: 12pt; }

    .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem; }
    .kpi-card { border: 1px solid #ccc; box-shadow: none; padding: 1rem; break-inside: avoid; }
    .kpi-icon { display: none; }
    .kpi-value { font-size: 16pt; }
    .kpi-label { font-size: 10pt; color: #000; }

    .table-card { border: none; box-shadow: none; }
    .dre-table { border: 1px solid #000; }
    .dre-table th { background-color: #eee !important; color: black !important; border: 1px solid #000; }
    .dre-table td { border: 1px solid #000; color: black !important; }
    
    .revenue-bg td { background-color: #f0f0f0 !important; }
    .expense-bg td { background-color: #f0f0f0 !important; }
    .resultado-final-row td { background-color: #ddd !important; border-top: 2px solid #000 !important; }
    
    .text-success { color: black !important; } /* Impressão P&B geralmente */
    .text-danger { color: black !important; }
}

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .summary-grid { grid-template-columns: 1fr; }
}
</style>
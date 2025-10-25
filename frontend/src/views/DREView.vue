<template>
  <div class="page-container">
    <header class="view-header">
      <h1>Relatório DRE (Demonstrativo de Resultados)</h1>
    </header>

    <div class="filters-card">
      <div class="form-group">
        <label for="start-date">Data de Início:</label>
        <input type="date" id="start-date" v-model="startDate">
      </div>
      <div class="form-group">
        <label for="end-date">Data de Fim:</label>
        <input type="date" id="end-date" v-model="endDate">
      </div>
      <button @click="fetchDRE" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'A carregar...' : 'Gerar Relatório' }}
      </button>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="dreData" class="results-container">
      <div class="summary-grid">
        <div class="summary-card revenue">
          <h4>Total de Receitas</h4>
          <p>{{ formatarValor(dreData.total_receitas) }}</p>
        </div>
        <div class="summary-card expenses">
          <h4>Total de Despesas</h4>
          <p>{{ formatarValor(dreData.total_despesas) }}</p>
        </div>
        <div class="summary-card balance">
          <h4>Lucro Líquido</h4>
          <p>{{ formatarValor(dreData.lucro_liquido) }}</p>
        </div>
      </div>

      <div class="details-grid">
        <div class="details-card">
          <h3>Receitas por Categoria</h3>
          <ul>
            <li v-for="(item, index) in dreData.receitas_por_categoria" :key="`receita-${index}`">
              <span>{{ item.categoria__nome || 'Sem Categoria' }}</span>
              <strong>{{ formatarValor(item.total) }}</strong>
            </li>
          </ul>
        </div>
        <div class="details-card">
          <h3>Despesas por Categoria</h3>
          <ul>
            <li v-for="(item, index) in dreData.despesas_por_categoria" :key="`despesa-${index}`">
              <span>{{ item.categoria__nome || 'Sem Categoria' }}</span>
              <strong>{{ formatarValor(item.total) }}</strong>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import apiClient from '@/services/api';

const today = new Date();
const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
const todayStr = today.toISOString().split('T')[0];

const startDate = ref(firstDayOfMonth);
const endDate = ref(todayStr);
const dreData = ref<any>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

const formatarValor = (valor: number) => {
  if (valor === null || valor === undefined) return 'R$ 0,00';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const fetchDRE = async () => {
  isLoading.value = true;
  error.value = null;
  dreData.value = null;

  try {
    // CORREÇÃO: URL ajustada para o novo endpoint /financeiro/dre/
    const response = await apiClient.get('/v1/financeiro/dre/', {
      params: {
        start_date: startDate.value,
        end_date: endDate.value
      }
    });
    dreData.value = response.data;
  } catch (err) {
    console.error("Erro ao gerar DRE:", err);
    error.value = "Não foi possível gerar o relatório. Verifique as datas e tente novamente.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.page-container { padding: 2rem; }
.filters-card { display: flex; gap: 1rem; align-items: flex-end; background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; }
.summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
.summary-card { padding: 1.5rem; border-radius: 8px; text-align: center; color: white; }
.summary-card h4 { margin: 0 0 0.5rem 0; font-size: 1rem; }
.summary-card p { margin: 0; font-size: 2rem; font-weight: bold; }
.revenue { background-color: #28a745; }
.expenses { background-color: #dc3545; }
.balance { background-color: #007bff; }
.details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.details-card { background: white; padding: 1.5rem; border-radius: 8px; }
.details-card ul { list-style: none; padding: 0; margin: 0; }
.details-card li { display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #eee; }
</style>
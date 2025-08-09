<template>
  <div class="dre-container">
    <header class="view-header">
      <h1>Demonstração do Resultado do Exercício (DRE)</h1>
    </header>

    <div class="filter-bar">
      <div class="filter-group">
        <label for="start-date">Data de Início:</label>
        <input type="date" id="start-date" v-model="filters.startDate" class="form-control" />
      </div>
      <div class="filter-group">
        <label for="end-date">Data de Fim:</label>
        <input type="date" id="end-date" v-model="filters.endDate" class="form-control" />
      </div>
      <button @click="fetchDRE" class="btn-primary">Atualizar Relatório</button>
    </div>

    <div v-if="isLoading" class="loading-message">
      A gerar relatório DRE...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="dreData" class="dre-report">
      <div class="dre-section">
        <h2 class="dre-title">Receita Bruta</h2>
        <div class="dre-item">
          <span class="item-label">Receita Operacional Bruta</span>
          <span class="item-value">{{ formatarValor(dreData.receita_bruta_servicos.valor) }}</span>
        </div>
      </div>

      <div class="dre-section">
        <h2 class="dre-title">Despesas Operacionais</h2>
        <div class="dre-item">
          <span class="item-label">Total de Despesas Operacionais</span>
          <span class="item-value">{{ formatarValor(dreData.despesas_operacionais.valor) }}</span>
        </div>
      </div>
      
      <div class="dre-section final-result">
        <h2 class="dre-title">Lucro Líquido Antes dos Impostos</h2>
        <div class="dre-item">
          <span class="item-label">Lucro / Prejuízo Líquido</span>
          <span class="item-value">{{ formatarValor(dreData.lucro_liquido_antes_impostos.valor) }}</span>
        </div>
      </div>

    </div>
    
    <div v-if="!isLoading && !dreData" class="no-data-message">
      <p>Nenhum dado financeiro encontrado para o período.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import apiClient from '@/services/api';

const dreData = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

const filters = ref({
  startDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().substr(0, 10),
  endDate: new Date().toISOString().substr(0, 10),
});

function formatarValor(valor: number | null) {
  if (valor === null || valor === undefined) return 'R$ 0,00';
  return parseFloat(valor.toString()).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

async function fetchDRE() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/financeiro/dre/', {
      params: {
        start_date: filters.value.startDate,
        end_date: filters.value.endDate,
      },
    });
    dreData.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar relatório DRE:", err);
    error.value = 'Não foi possível carregar o relatório DRE.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchDRE();
});
</script>

<style scoped>
.dre-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.filter-bar {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 2rem;
}
.filter-group {
  display: flex;
  flex-direction: column;
}
.filter-group label {
  font-weight: bold;
  margin-bottom: 0.5rem;
}
.form-control {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.btn-primary {
  padding: 10px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.loading-message, .error-message, .no-data-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.dre-report {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.dre-section {
  margin-bottom: 1.5rem;
}
.dre-title {
  font-size: 1.2rem;
  font-weight: bold;
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
.dre-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 1rem;
  color: #495057;
}
.final-result {
  border-top: 2px solid #000;
  padding-top: 1rem;
  margin-top: 2rem;
}
.item-label {
  font-weight: 600;
}
.item-value {
  font-weight: bold;
}
</style>
<template>
  <div class="page-container">
    <header class="view-header">
      <h1>Gerir Categorias Financeiras</h1>
      <router-link to="/financeiro/categorias/nova" class="btn-primary">+ Adicionar Categoria</router-link>
    </header>

    <div v-if="isLoading" class="loading-state">A carregar categorias...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="categorias.length" class="table-wrapper">
      <table class="styled-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Tipo</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="categoria in categorias" :key="categoria.id">
            <td>{{ categoria.nome }}</td>
            <td>{{ categoria.tipo }}</td>
            <td>
              <router-link :to="`/financeiro/categorias/editar/${categoria.id}`" class="btn-edit">Editar</router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
     <div v-else-if="!isLoading" class="no-data-message">
      Nenhuma categoria encontrada.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const categorias = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchCategorias() {
  isLoading.value = true;
  try {
    // CORREÇÃO: Removido o '/api' duplicado. A chamada começa com '/v1'.
    const response = await apiClient.get('/v1/financeiro/categorias/');
    categorias.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar categorias:", err);
    error.value = 'Falha ao carregar as categorias.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchCategorias();
});
</script>

<style scoped>
.page-container { padding: 2rem; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.table-wrapper { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th, .styled-table td { padding: 12px 15px; border-bottom: 1px solid #ddd; text-align: left; }
.btn-edit { color: #007bff; text-decoration: none; }
.loading-state, .error-message, .no-data-message { text-align: center; padding: 2rem; }
.btn-primary { 
  background-color: #007bff; 
  color: white; 
  padding: 10px 15px; 
  border-radius: 5px; 
  text-decoration: none; 
  font-weight: bold;
}
</style>
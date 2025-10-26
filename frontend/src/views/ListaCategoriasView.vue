<template>
  <div class="page-container">
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
    // Endpoint original
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
.page-container {
  padding: 0; /* CORREÇÃO: Removido padding: 2rem; */
}

/* Regras .view-header e .btn-primary removidas */

.table-wrapper {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}
.styled-table {
  width: 100%;
  border-collapse: collapse;
}
.styled-table th, .styled-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}
.styled-table th {
  background-color: #f8f9fa;
  font-weight: bold;
}
.styled-table tbody tr:hover {
    background-color: #f1f3f5;
}
.loading-state, .error-message, .no-data-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.btn-edit {
  background-color: #17a2b8; /* Cor mais profissional para 'Editar' */
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9em;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-edit:hover {
    background-color: #138496;
}
</style>
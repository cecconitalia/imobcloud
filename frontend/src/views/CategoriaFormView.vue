<template>
  <div class="page-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Categoria' : 'Adicionar Nova Categoria' }}</h1>
    </header>

    <div v-if="isLoading" class="loading-state">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <form v-if="!isLoading" @submit.prevent="submitForm" class="form-card">
      <div class="form-group">
        <label for="nome">Nome da Categoria</label>
        <input type="text" id="nome" v-model="categoria.nome" required>
      </div>
      <div class="form-group">
        <label for="tipo">Tipo</label>
        <select id="tipo" v-model="categoria.tipo" required>
          <option value="RECEITA">Receita</option>
          <option value="DESPESA">Despesa</option>
        </select>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn-primary">Salvar</button>
        <router-link to="/financeiro/categorias" class="btn-secondary">Cancelar</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();
const isEditing = computed(() => !!route.params.id);

const categoria = ref({
  nome: '',
  tipo: 'RECEITA',
});
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchCategoria(id: string) {
  try {
    // CORREÇÃO: Removido o '/api' duplicado. A chamada começa com '/v1'.
    const response = await apiClient.get(`/v1/financeiro/categorias/${id}/`);
    categoria.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar categoria:", err);
    error.value = 'Falha ao carregar a categoria.';
  }
}

async function submitForm() {
  try {
    if (isEditing.value) {
      // CORREÇÃO: Removido o '/api' duplicado.
      await apiClient.put(`/v1/financeiro/categorias/${route.params.id}/`, categoria.value);
    } else {
      // CORREÇÃO: Removido o '/api' duplicado.
      await apiClient.post('/v1/financeiro/categorias/', categoria.value);
    }
    router.push('/financeiro/categorias');
  } catch (err) {
    console.error("Erro ao salvar categoria:", err);
    error.value = 'Falha ao salvar. Verifique os dados.';
  }
}

onMounted(async () => {
  if (isEditing.value) {
    await fetchCategoria(route.params.id as string);
  }
  isLoading.value = false;
});
</script>

<style scoped>
.page-container { padding: 2rem; max-width: 800px; margin: auto; }
.form-card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: .5rem; font-weight: bold; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem; }
.btn-primary { background-color: #007bff; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
.btn-secondary { background-color: #6c757d; color: white; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; }
</style>
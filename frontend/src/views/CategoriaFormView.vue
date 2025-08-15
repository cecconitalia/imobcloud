<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">{{ formTitle }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>A carregar...</p>
    </div>

    <div v-else class="form-card">
      <form @submit.prevent="submitForm">

        <div class="form-group">
          <label for="nome" class="form-label">Nome da Categoria:</label>
          <input
            type="text"
            id="nome"
            v-model="categoria.nome"
            class="form-input"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="tipo" class="form-label">Tipo:</label>
          <select id="tipo" v-model="categoria.tipo" class="form-input" required>
            <option value="RECEITA">Receita</option>
            <option value="DESPESA">Despesa</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="pai" class="form-label">Sub-categoria de (opcional):</label>
          <select id="pai" v-model="categoria.pai" class="form-input">
            <option :value="null">Nenhuma</option>
            <option
              v-for="cat in categoriasPai"
              :key="cat.id"
              :value="cat.id"
            >
              {{ cat.nome }}
            </option>
          </select>
        </div>
        
        <div class="actions">
          <button type="submit" class="submit-button" :disabled="isSubmitting">
            {{ isSubmitting ? 'A salvar...' : 'Salvar' }}
          </button>
          <router-link :to="{ name: 'lista-categorias' }" class="cancel-link">Cancelar</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

interface Categoria {
  id?: number;
  nome: string;
  tipo: string;
  pai: number | null;
}

const route = useRoute();
const router = useRouter();

const categoria = ref<Categoria>({
  nome: '',
  tipo: 'RECEITA',
  pai: null,
});

const categoriasPai = ref<Categoria[]>([]);
const isLoading = ref(false);
const isSubmitting = ref(false);

const isEditing = computed(() => !!route.params.id);
const formTitle = computed(() => isEditing.value ? 'Editar Categoria' : 'Adicionar Nova Categoria');

const fetchCategoria = async (id: number) => {
  isLoading.value = true;
  try {
    // CORREÇÃO: URL alterada para o caminho correto
    const response = await apiClient.get(`/v1/categorias/${id}/`);
    categoria.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar categoria:', err);
    alert('Falha ao carregar os dados da categoria.');
    router.push({ name: 'lista-categorias' });
  } finally {
    isLoading.value = false;
  }
};

const fetchCategoriasPai = async () => {
  try {
    // CORREÇÃO: URL alterada para o caminho correto
    const response = await apiClient.get('/v1/categorias/?tipo=PAI');
    categoriasPai.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar categorias pai:', err);
  }
};

const submitForm = async () => {
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      // CORREÇÃO: URL alterada para o caminho correto
      await apiClient.put(`/v1/categorias/${categoria.value.id}/`, categoria.value);
    } else {
      // CORREÇÃO: URL alterada para o caminho correto
      await apiClient.post('/v1/categorias/', categoria.value);
    }
    router.push({ name: 'lista-categorias' });
  } catch (err) {
    console.error('Erro ao salvar categoria:', err);
    alert('Falha ao salvar a categoria.');
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  fetchCategoriasPai();
  if (isEditing.value) {
    fetchCategoria(Number(route.params.id));
  }
});
</script>

<style scoped>
/* Estilos permanecem inalterados */
.page-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}
.header-section {
  margin-bottom: 2rem;
  text-align: center;
}
.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}
.form-card {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
.loading-state {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #555;
}
.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 1rem;
  transition: border-color 0.3s;
}
.form-input:focus {
  outline: none;
  border-color: #007bff;
}
.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}
.submit-button, .cancel-link {
  padding: 12px 24px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}
.submit-button {
  background-color: #007bff;
  color: white;
  border: none;
}
.submit-button:hover {
  background-color: #0056b3;
}
.cancel-link {
  background-color: #6c757d;
  color: white;
  border: none;
}
.cancel-link:hover {
  background-color: #5a6268;
}
</style>
<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">Gerir Categorias Financeiras</h1>
      <button @click="adicionarCategoria" class="add-button">
        + Adicionar Categoria
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>A carregar categorias...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-else class="table-card">
      <div v-if="categorias.length === 0" class="empty-state">
        <p>Nenhuma categoria cadastrada.</p>
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Tipo</th>
            <th class="actions-column">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="categoria in categorias" :key="categoria.id">
            <td>{{ categoria.nome }}</td>
            <td>
              <span :class="['status-badge', getTipoClass(categoria.tipo)]">
                {{ formatTipo(categoria.tipo) }}
              </span>
            </td>
            <td class="actions-column">
              <button @click="editarCategoria(categoria.id)" class="action-button edit-button">
                Editar
              </button>
              <button @click="excluirCategoria(categoria.id)" class="action-button delete-button">
                Excluir
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

interface Categoria {
  id: number;
  nome: string;
  tipo: string;
}

const categorias = ref<Categoria[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const router = useRouter();

const fetchCategorias = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/categorias/');
    categorias.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar categorias:', err);
    error.value = 'Falha ao carregar a lista de categorias.';
  } finally {
    isLoading.value = false;
  }
};

const adicionarCategoria = () => {
  router.push({ name: 'nova-categoria' });
};

const editarCategoria = (id: number) => {
  // CORREÇÃO: O nome da rota deve ser 'editar-categoria'
  router.push({ name: 'editar-categoria', params: { id } });
};

const excluirCategoria = async (id: number) => {
  if (confirm('Tem certeza que deseja excluir esta categoria?')) {
    try {
      await apiClient.delete(`/v1/categorias/${id}/`);
      fetchCategorias();
    } catch (err) {
      console.error('Erro ao excluir categoria:', err);
      alert('Falha ao excluir a categoria.');
    }
  }
};

const formatTipo = (tipo: string) => {
  return tipo === 'RECEITA' ? 'Receita' : 'Despesa';
};

const getTipoClass = (tipo: string) => {
  return tipo === 'RECEITA' ? 'status-receita' : 'status-despesa';
};

onMounted(fetchCategorias);
</script>

<style scoped>
.page-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.add-button {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-button:hover {
  background-color: #0056b3;
}

.loading-state, .empty-state, .error-message {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
  margin-top: 2rem;
}

.error-message {
  color: #d9534f;
  background-color: #f2dede;
  border: 1px solid #ebccd1;
  padding: 10px;
  border-radius: 4px;
}

.table-card {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.data-table thead th {
  background-color: #f8f9fa;
  color: #333;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.9rem;
}

.data-table tbody tr:hover {
  background-color: #f1f1f1;
}

.actions-column {
  text-align: right;
  white-space: nowrap;
}

.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: bold;
  margin-left: 8px;
  transition: background-color 0.3s;
}

.edit-button {
  background-color: #ffc107;
  color: #333;
}

.edit-button:hover {
  background-color: #e0a800;
}

.delete-button {
  background-color: #dc3545;
  color: white;
}

.delete-button:hover {
  background-color: #c82333;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: bold;
  color: white;
}
.status-receita { background-color: #28a745; }
.status-despesa { background-color: #dc3545; }
</style>
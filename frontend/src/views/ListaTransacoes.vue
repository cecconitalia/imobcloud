<template>
  <div class="lista-transacoes-container">
    <header class="view-header">
      <h1>Lista de Transações</h1>
      <router-link to="/financeiro/transacoes/nova" class="btn-primary">
        + Adicionar Transação
      </router-link>
    </header>

    <div class="filters-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por descrição..."
      />
      <select v-model="filterTipo">
        <option value="">Todos os Tipos</option>
        <option value="RECEITA">Receita</option>
        <option value="DESPESA">Despesa</option>
      </select>
      <select v-model="filterCategoria">
        <option value="">Todas as Categorias</option>
        <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
          {{ categoria.nome }}
        </option>
      </select>
    </div>

    <div v-if="isLoading" class="loading-message">A carregar transações...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="filteredTransacoes.length > 0">
      <thead>
        <tr>
          <th>Data</th>
          <th>Tipo</th>
          <th>Descrição</th>
          <th>Categoria</th>
          <th>Valor</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="transacao in filteredTransacoes" :key="transacao.id">
          <td>{{ formatarData(transacao.data) }}</td>
          <td>
            <span :class="['status-badge', getTipoClass(transacao.tipo)]">
              {{ transacao.tipo }}
            </span>
          </td>
          <td>{{ transacao.descricao }}</td>
          <td>{{ transacao.categoria_obj?.nome || 'N/A' }}</td>
          <td>{{ formatarValor(transacao.valor) }}</td>
          <td class="actions-cell">
            <router-link :to="`/financeiro/transacoes/editar/${transacao.id}`" class="btn-secondary">
              Editar
            </router-link>
            <button @click="handleDelete(transacao.id)" class="btn-danger">
              Excluir
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <div v-if="!isLoading && filteredTransacoes.length === 0 && !error" class="no-data-message">
      <p>Nenhuma transação encontrada.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';

const transacoes = ref<any[]>([]);
const categorias = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

const searchTerm = ref('');
const filterTipo = ref('');
const filterCategoria = ref('');

const filteredTransacoes = computed(() => {
  let list = transacoes.value;

  if (filterTipo.value) {
    list = list.filter(t => t.tipo === filterTipo.value);
  }
  if (filterCategoria.value) {
    list = list.filter(t => t.categoria === parseInt(filterCategoria.value));
  }
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    list = list.filter(t => t.descricao.toLowerCase().includes(term));
  }

  return list;
});

async function fetchData() {
  isLoading.value = true;
  try {
    const [transacoesResponse, categoriasResponse] = await Promise.all([
      apiClient.get('/v1/financeiro/transacoes/'),
      apiClient.get('/v1/financeiro/categorias/')
    ]);
    transacoes.value = transacoesResponse.data;
    categorias.value = categoriasResponse.data;
    error.value = null;
  } catch (err) {
    console.error("Erro ao buscar dados:", err);
    error.value = 'Não foi possível carregar as transações.';
  } finally {
    isLoading.value = false;
  }
}

async function handleDelete(transacaoId: number) {
  if (!window.confirm('Tem a certeza de que deseja excluir esta transação?')) {
    return;
  }
  try {
    await apiClient.delete(`/v1/financeiro/transacoes/${transacaoId}/`);
    await fetchData();
  } catch (error) {
    console.error("Erro ao excluir transação:", error);
    alert("Ocorreu um erro ao tentar excluir a transação.");
  }
}

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR');
}

function formatarValor(valor: number) {
  return parseFloat(valor.toString()).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function getTipoClass(tipo: string) {
  return tipo === 'RECEITA' ? 'status-receita' : 'status-despesa';
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.lista-transacoes-container {
  padding: 2rem;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.btn-primary, .btn-secondary {
  padding: 10px 15px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  border: none;
  cursor: pointer;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.filters-bar input,
.filters-bar select {
  flex: 1;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
th, td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
  vertical-align: middle;
}
th {
  background-color: #f2f2f2;
}
.loading-message, .no-data-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.actions-cell {
  display: flex;
  gap: 0.5rem;
}
.btn-danger {
    background-color: #dc3545;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.9em;
    border: none;
    cursor: pointer;
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
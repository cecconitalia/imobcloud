<template>
  <div class="page-container">
    <div v-if="isLoading" class="loading-state">
      <p>A carregar formas de pagamento...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-else class="table-card">
      <div v-if="formasPagamento.length === 0" class="empty-state">
        <p>Nenhuma forma de pagamento cadastrada.</p>
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Slug</th>
            <th>Ativo</th>
            <th class="actions-column">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="forma in formasPagamento" :key="forma.id">
            <td>{{ forma.nome }}</td>
            <td>{{ forma.slug }}</td>
            <td>{{ forma.ativo ? 'Sim' : 'Não' }}</td>
            <td class="actions-column">
              <button @click="editarFormaPagamento(forma.id)" class="action-button btn-edit">Editar</button>
              <button @click="excluirFormaPagamento(forma.id)" class="action-button btn-delete">Excluir</button>
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

// Interfaces (baseado na estrutura presumida do backend)
interface FormaPagamento {
    id: number;
    nome: string;
    slug: string;
    ativo: boolean;
}

const router = useRouter();
const formasPagamento = ref<FormaPagamento[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchFormasPagamento() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<FormaPagamento[]>('/v1/financeiro/formas-pagamento/');
    formasPagamento.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar formas de pagamento:", err);
    error.value = 'Não foi possível carregar as formas de pagamento.';
  } finally {
    isLoading.value = false;
  }
}

function adicionarFormaPagamento() {
    router.push({ name: 'forma-pagamento-nova' });
}

function editarFormaPagamento(id: number) {
    router.push({ name: 'forma-pagamento-editar', params: { id } });
}

async function excluirFormaPagamento(id: number) {
    if (window.confirm("Tem certeza que deseja excluir esta forma de pagamento?")) {
        try {
            await apiClient.delete(`/v1/financeiro/formas-pagamento/${id}/`);
            alert('Forma de pagamento excluída com sucesso!');
            fetchFormasPagamento(); // Recarrega a lista
        } catch (err) {
            console.error("Erro ao excluir forma de pagamento:", err);
            alert('Não foi possível excluir a forma de pagamento.');
        }
    }
}

onMounted(() => {
  fetchFormasPagamento();
});
</script>

<style scoped>
.page-container {
  padding: 0; /* CORREÇÃO: Removido padding original */
}

/* Regras .header-section, .page-title e .add-button removidas */

.loading-state, .empty-state, .error-message {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
  margin-top: 1.5rem; /* Ajustado para consistência */
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
  vertical-align: middle;
  white-space: nowrap;
}

.data-table thead th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}
.data-table tbody tr:hover {
    background-color: #f1f3f5;
}

.actions-column {
    text-align: right;
    white-space: nowrap;
}

.action-button {
    padding: 6px 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
    text-decoration: none;
    margin-left: 0.5rem;
    font-weight: 500;
    transition: background-color 0.2s;
}

.btn-edit { background-color: #17a2b8; color: white; }
.btn-edit:hover { background-color: #138496; }

.btn-delete { background-color: #dc3545; color: white; }
.btn-delete:hover { background-color: #c82333; }
</style>
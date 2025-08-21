<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">Gerir Formas de Pagamento</h1>
      <button @click="adicionarFormaPagamento" class="add-button">
        + Adicionar Forma de Pagamento
      </button>
    </div>

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
              <button @click="editarFormaPagamento(forma.id)" class="action-button edit-button">
                Editar
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

interface FormaPagamento {
  id: number;
  nome: string;
  slug: string;
  ativo: boolean;
}

const formasPagamento = ref<FormaPagamento[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const router = useRouter();

const fetchFormasPagamento = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/financeiro/formas-pagamento/');
    formasPagamento.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar formas de pagamento:', err);
    error.value = 'Falha ao carregar a lista de formas de pagamento.';
  } finally {
    isLoading.value = false;
  }
};

const adicionarFormaPagamento = () => {
  router.push({ name: 'nova-forma-pagamento' });
};

const editarFormaPagamento = (id: number) => {
  router.push({ name: 'editar-forma-pagamento', params: { id } });
};

onMounted(fetchFormasPagamento);
</script>

<style scoped>
.page-container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.page-title { font-size: 2rem; font-weight: bold; color: #333; }
.add-button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 6px; text-decoration: none; font-weight: bold; cursor: pointer; transition: background-color 0.3s; }
.add-button:hover { background-color: #0056b3; }
.loading-state, .empty-state, .error-message { text-align: center; font-size: 1.2rem; color: #666; margin-top: 2rem; }
.error-message { color: #d9534f; background-color: #f2dede; border: 1px solid #ebccd1; padding: 10px; border-radius: 4px; }
.table-card { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
.data-table thead th { background-color: #f8f9fa; color: #333; font-weight: bold; text-transform: uppercase; font-size: 0.9rem; }
.data-table tbody tr:hover { background-color: #f1f1f1; }
.actions-column { text-align: right; white-space: nowrap; }
.action-button { padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem; font-weight: bold; margin-left: 8px; transition: background-color 0.3s; }
.edit-button { background-color: #ffc107; color: #333; }
.edit-button:hover { background-color: #e0a800; }
</style>
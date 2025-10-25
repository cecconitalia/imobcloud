<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">Gerir Contas Bancárias</h1>
      <button @click="adicionarConta" class="add-button">
        + Adicionar Conta
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>A carregar contas...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-else class="table-card">
      <div class="filter-section">
        <input 
          type="text" 
          v-model="searchTerm" 
          placeholder="Pesquisar contas (nome, banco, agência)" 
          class="filter-input"
        >
        <button @click="toggleStatus" class="filter-button">
          {{ showInactive ? 'Ver Contas Ativas' : 'Ver Contas Inativas' }}
        </button>
      </div>

      <div v-if="filteredContas.length === 0" class="empty-state">
        <p>Nenhuma conta bancária encontrada.</p>
      </div>
      
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Banco</th>
            <th>Agência</th>
            <th>Número da Conta</th>
            <th>Saldo Atual</th>
            <th class="actions-column">Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="conta in filteredContas" :key="conta.id">
            <td>{{ conta.nome }}</td>
            <td>{{ conta.banco }}</td>
            <td>{{ conta.agencia }}</td>
            <td>{{ conta.numero_conta }}</td>
            <td>{{ formatCurrency(conta.saldo_atual) }}</td>
            <td class="actions-column">
              <button @click="editarConta(conta.id)" class="action-button edit-button">
                Editar
              </button>
              <button @click="inativarConta(conta.id)" class="action-button delete-button">
                Inativar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';

interface Conta {
  id: number;
  nome: string;
  banco: string;
  agencia: string;
  numero_conta: string;
  saldo_atual: number;
  ativo: boolean;
}

const contas = ref<Conta[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const searchTerm = ref('');
const router = useRouter();
const showInactive = ref(false);

const fetchContas = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const url = showInactive.value ? '/v1/financeiro/contas/?status=inativo' : '/v1/financeiro/contas/';
    const response = await api.get(url);
    contas.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar contas:', err);
    error.value = 'Falha ao carregar as contas bancárias.';
  } finally {
    isLoading.value = false;
  }
};

const toggleStatus = () => {
  showInactive.value = !showInactive.value;
  fetchContas();
};

const adicionarConta = () => {
  router.push({ name: 'conta-nova' });
};

const editarConta = (id: number) => {
  router.push({ name: 'conta-editar', params: { id } });
};

const inativarConta = async (id: number) => {
  if (confirm('Tem certeza que deseja inativar esta conta?')) {
    try {
      await api.patch(`/v1/financeiro/contas/${id}/`, { ativo: false });
      fetchContas();
    } catch (err) {
      console.error('Erro ao inativar conta:', err);
      alert('Falha ao inativar a conta.');
    }
  }
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

const filteredContas = computed(() => {
  if (!searchTerm.value) {
    return contas.value;
  }
  const term = searchTerm.value.toLowerCase();
  return contas.value.filter(conta => 
    conta.nome.toLowerCase().includes(term) ||
    conta.banco.toLowerCase().includes(term) ||
    conta.agencia.toLowerCase().includes(term) ||
    conta.numero_conta.toLowerCase().includes(term)
  );
});

onMounted(fetchContas);
</script>

<style scoped>
.page-container {
  max-width: 1000px;
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

.add-button, .filter-button {
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

.add-button:hover, .filter-button:hover {
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

.filter-section {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-input {
  flex-grow: 1;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.filter-input:focus {
  outline: none;
  border-color: #007bff;
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
</style>
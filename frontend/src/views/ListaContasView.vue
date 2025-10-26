<template>
  <div class="page-container">
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
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="conta in filteredContas" :key="conta.id">
            <td>{{ conta.nome }}</td>
            <td>{{ conta.banco }}</td>
            <td>{{ conta.agencia }}</td>
            <td>{{ conta.conta }}</td>
            <td>{{ formatarValor(conta.saldo_atual) }}</td>
            <td>{{ conta.is_active ? 'Ativa' : 'Inativa' }}</td>
            <td class="actions-cell">
              <button @click="editarConta(conta.id)" class="btn-action btn-edit">Editar</button>
              <button @click="excluirConta(conta.id)" class="btn-action btn-delete">Excluir</button>
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
import apiClient from '@/services/api';

// Interfaces
interface Conta {
    id: number;
    nome: string;
    banco: string;
    agencia: string;
    conta: string;
    saldo_atual: number;
    is_active: boolean;
}

const router = useRouter();
const contas = ref<Conta[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const showInactive = ref(false); // Filtro para mostrar inativas ou não

async function fetchContas() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Conta[]>('/v1/financeiro/contas/');
    contas.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contas:", err);
    error.value = 'Não foi possível carregar as contas bancárias.';
  } finally {
    isLoading.value = false;
  }
}

const filteredContas = computed(() => {
    let filtered = contas.value;

    // Filtra por status (ativo/inativo)
    if (!showInactive.value) {
        filtered = filtered.filter(conta => conta.is_active);
    }
    
    // Filtro por termo de busca
    if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase();
        filtered = filtered.filter(conta =>
            conta.nome.toLowerCase().includes(term) ||
            conta.banco.toLowerCase().includes(term) ||
            conta.agencia.includes(term) ||
            conta.conta.includes(term)
        );
    }

    return filtered;
});


function toggleStatus() {
    showInactive.value = !showInactive.value;
}

function formatarValor(valor: number): string {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function adicionarConta() {
    router.push({ name: 'conta-nova' });
}

function editarConta(id: number) {
    router.push({ name: 'conta-editar', params: { id } });
}

async function excluirConta(id: number) {
    if (window.confirm("Tem certeza que deseja excluir esta conta? Esta ação não pode ser desfeita.")) {
        try {
            await apiClient.delete(`/v1/financeiro/contas/${id}/`);
            alert('Conta excluída com sucesso!');
            fetchContas(); // Recarrega a lista
        } catch (err) {
            console.error("Erro ao excluir conta:", err);
            alert('Não foi possível excluir a conta.');
        }
    }
}

onMounted(() => {
    fetchContas();
});
</script>

<style scoped>
.page-container {
  padding: 0; /* CORREÇÃO: Removido padding: 2rem; */
}

/* Regras do Header removidas */

.loading-state, .error-message, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
  background-color: #fff;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}
.error-message {
    color: #dc3545;
    background-color: #f8d7da;
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
  flex-wrap: wrap; /* Permite quebra de linha */
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center; /* Alinha verticalmente */
}

.filter-input {
  flex: 1 1 250px; /* Garante que o input de pesquisa ocupe mais espaço */
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.filter-button {
    padding: 10px 15px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    transition: background-color 0.3s;
}
.filter-button:hover {
    background-color: #0056b3;
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

.actions-cell {
    text-align: right;
    white-space: nowrap;
}

.btn-action {
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
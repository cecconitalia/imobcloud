<template>
  <div class="users-container">
    <div class="filters-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por nome, email, CRECI..."
        @input="applyFilters"
      />
      <select v-model="filterCargo" @change="applyFilters">
        <option value="">Todos os Cargos</option>
        <option value="ADMIN">Administrador</option>
        <option value="CORRETOR">Corretor</option>
      </select>
    </div>

    <div v-if="isLoading" class="loading-message">A carregar utilizadores...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="filteredUsers.length > 0">
      <thead>
        <tr>
          <th>Nome Completo</th>
          <th>Nome de Utilizador</th>
          <th>Email</th>
          <th>CRECI</th>
          <th>Telefone</th>
          <th>Cargo</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in filteredUsers" :key="user.id">
          <td>{{ user.first_name }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.perfil?.creci || 'N/A' }}</td>
          <td>{{ user.perfil?.telefone || 'N/A' }}</td>
          <td>{{ user.perfil?.cargo || 'N/A' }}</td>
          <td class="actions-cell">
            <router-link :to="`/corretores/editar/${user.id}`" class="btn-secondary">
              Editar
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!isLoading && filteredUsers.length === 0 && !error" class="no-data-message">
      <p>Nenhum utilizador encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';

const users = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterCargo = ref('');

// A lista de utilizadores é filtrada dinamicamente
const filteredUsers = computed(() => {
  let filteredList = users.value;

  if (filterCargo.value) {
    filteredList = filteredList.filter(user => user.perfil?.cargo === filterCargo.value);
  }

  if (searchTerm.value) {
    const searchLower = searchTerm.value.toLowerCase();
    filteredList = filteredList.filter(user =>
      user.first_name.toLowerCase().includes(searchLower) ||
      user.email.toLowerCase().includes(searchLower) ||
      user.perfil?.creci?.toLowerCase().includes(searchLower)
    );
  }

  return filteredList;
});

async function fetchUsers() {
  isLoading.value = true;
  error.value = null; // Limpa erro antes de tentar
  try {
    // Endpoint que o código original utilizava
    const response = await apiClient.get('/v1/corretores/');
    users.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar utilizadores:", err);
    error.value = 'Não foi possível carregar a lista de utilizadores.';
  } finally {
    isLoading.value = false;
  }
}

function applyFilters() {
  // A reatividade do `computed` já trata a filtragem
}

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.users-container {
  padding: 0; /* CORREÇÃO: Removido padding: 2rem; */
}
/* Regras .view-header e .btn-primary removidas */

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  background-color: #fff;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
th, td {
  border-bottom: 1px solid #e9ecef;
  padding: 1rem;
  text-align: left;
  vertical-align: middle;
  white-space: nowrap;
}
th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}
tr:hover {
    background-color: #f1f3f5;
}
.actions-cell {
    text-align: right; /* Alinha o botão à direita */
    min-width: 120px; /* Garante espaço */
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.9em;
    border: none;
    cursor: pointer;
    transition: background-color 0.2s;
}
.btn-secondary:hover {
    background-color: #5a6268;
}

.loading-message, .error-message, .no-data-message {
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
    border: 1px solid #f5c6cb;
}
</style>
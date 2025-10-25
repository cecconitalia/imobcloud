<template>
  <div class="users-container">
    <header class="view-header">
      <h1>Gerir Utilizadores</h1>
      <router-link to="/corretores/novo" class="btn-primary">
        + Adicionar Novo
      </router-link>
    </header>

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
  try {
    // CORREÇÃO: URL corrigida, o prefixo 'core/' foi removido
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
  padding: 2rem;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  border: none;
  cursor: pointer;
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
.btn-secondary {
    background-color: #6c757d;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.9em;
    border: none;
    cursor: pointer;
}
</style>
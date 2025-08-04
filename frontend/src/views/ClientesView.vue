<template>
  <div class="clientes-container">
    <header class="view-header">
      <h1>Meus Clientes</h1>
      <router-link to="/clientes/novo" class="btn-primary">
        + Adicionar Cliente
      </router-link>
    </header>

    <div class="search-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por nome, CPF/CNPJ, email..."
        @input="fetchClientes"
      />
    </div>

    <div v-if="isLoading">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="clientes.length > 0">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Email</th>
          <th>Telefone</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="cliente in clientes" :key="cliente.id">
          <td>{{ cliente.nome_completo }}</td>
          <td>{{ cliente.email }}</td>
          <td>{{ cliente.telefone }}</td>
          <td class="actions-cell">
            <router-link :to="`/clientes/editar/${cliente.id}`" class="btn-secondary">
              Editar
            </router-link>
            <button @click="handleInativar(cliente.id)" class="btn-danger">
              Inativar
            </button>
          </td>
        </tr>
      </tbody>
    </table>

     <div v-if="!isLoading && clientes.length === 0 && !error">
      <p>Nenhum cliente encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const clientes = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// ## ESTADO PARA O TERMO DE PESQUISA ADICIONADO ##
const searchTerm = ref('');

// ## FUNÇÃO DE BUSCA ATUALIZADA PARA INCLUIR A PESQUISA ##
async function fetchClientes() {
  isLoading.value = true;
  try {
    const params = {
      search: searchTerm.value, // Adiciona o parâmetro de pesquisa ao pedido
    };
    const response = await apiClient.get('/v1/clientes/clientes/', { params });
    clientes.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar clientes:", err);
    error.value = 'Não foi possível carregar os clientes.';
  } finally {
    isLoading.value = false;
  }
}

// Lógica onMounted (INTACTA)
onMounted(() => {
  fetchClientes();
});

// Lógica handleInativar (INTACTA)
async function handleInativar(clienteId: number) {
  if (!window.confirm('Tem a certeza de que deseja inativar este cliente?')) {
    return;
  }
  try {
    await apiClient.delete(`/v1/clientes/clientes/${clienteId}/`);
    clientes.value = clientes.value.filter(cliente => cliente.id !== clienteId);
  } catch (error) {
    console.error("Erro ao inativar cliente:", error);
    alert("Ocorreu um erro ao tentar inativar o cliente.");
  }
}
</script>

<style scoped>
/* Estilos podem ser reutilizados */
.clientes-container {
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
/* ## ESTILO PARA A BARRA DE PESQUISA ADICIONADO ## */
.search-bar {
  margin-bottom: 1.5rem;
}
.search-bar input {
  width: 100%;
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
  padding: 8px;
  text-align: left;
  vertical-align: middle;
}
th {
  background-color: #f2f2f2;
}
.error-message {
  color: red;
}
.actions-cell {
  display: flex;
  gap: 0.5rem;
}
.btn-secondary, .btn-danger {
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9em;
  border: none;
  cursor: pointer;
}
.btn-secondary { background-color: #6c757d; }
.btn-danger { background-color: #dc3545; }
</style>
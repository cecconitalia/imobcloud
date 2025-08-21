<template>
  <div class="clientes-container">
    <header class="view-header">
      <h1>Meus Clientes</h1>
      <router-link to="/clientes/novo" class="btn-primary">
        + Adicionar Cliente
      </router-link>
    </header>

    <div class="filters-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por nome, email, cpf..."
      />
    </div>

    <div v-if="isLoading" class="loading-message">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="clientes.length > 0" class="clientes-grid">
      <div v-for="cliente in filteredClientes" :key="cliente.id" class="cliente-card">
        <div class="cliente-info">
          <h3 class="cliente-nome">{{ cliente.nome_completo }}</h3>
          <p class="cliente-contato">{{ cliente.email }}</p>
          <p class="cliente-contato">{{ cliente.telefone }}</p>
        </div>
        <div class="cliente-actions">
          <router-link :to="`/clientes/editar/${cliente.id}`" class="btn-action edit-btn">
            <i class="fas fa-edit"></i>
            <span>Editar</span>
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="!isLoading && clientes.length === 0 && !error" class="no-data-message">
      <p>Nenhum cliente encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

const clientes = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');

let debounceTimeout: number | undefined = undefined;

const filteredClientes = computed(() => {
  if (!searchTerm.value) {
    return clientes.value;
  }
  const term = searchTerm.value.toLowerCase();
  return clientes.value.filter(cliente => 
    cliente.nome_completo.toLowerCase().includes(term) ||
    cliente.email.toLowerCase().includes(term) ||
    cliente.cpf_cnpj?.toLowerCase().includes(term)
  );
});

async function fetchClientes() {
  isLoading.value = true;
  try {
    const params: { [key: string]: string } = {};
    if (searchTerm.value) {
      params.search = searchTerm.value;
    }
    // A CORREÇÃO ESTÁ AQUI: URL alterada para o endpoint correto
    const response = await apiClient.get('/v1/clientes/', { params });
    clientes.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar clientes:", err);
    error.value = 'Não foi possível carregar os clientes.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchClientes();
});

watch(searchTerm, () => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }
  debounceTimeout = setTimeout(() => {
    fetchClientes();
  }, 500);
});
</script>

<style scoped>
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
.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.filters-bar input {
  flex: 1;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
.clientes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.cliente-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.cliente-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}
.cliente-info {
  margin-bottom: 1rem;
}
.cliente-nome {
  font-size: 1.25rem;
  font-weight: bold;
  margin: 0 0 0.5rem 0;
}
.cliente-contato {
  margin: 0;
  color: #6c757d;
}
.cliente-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
}
.btn-action {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  padding: 8px 12px;
  border-radius: 4px;
  text-decoration: none;
  color: #6c757d;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.btn-action:hover {
  background-color: #e9ecef;
}
.edit-btn:hover {
  background-color: #ffc107;
  color: #333;
}
.loading-message, .no-data-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
</style>
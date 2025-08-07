<template>
  <div class="imoveis-container">
    <header class="view-header">
      <h1>Meus Imóveis</h1>
      <router-link to="/imoveis/novo" class="btn-primary">
        + Adicionar Imóvel
      </router-link>
    </header>

    <div class="search-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por endereço, cidade..."
        @input="fetchImoveis"
      />
    </div>

    <div v-if="isLoading">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="imoveis.length > 0">
      <thead>
        <tr>
          <th>Endereço</th>
          <th>Tipo</th>
          <th>Status</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="imovel in imoveis" :key="imovel.id">
          <td>{{ imovel.endereco }}</td>
          <td>{{ imovel.tipo }}</td>
          <td>{{ imovel.status }}</td>
          <td class="actions-cell">
            <router-link :to="`/imoveis/editar/${imovel.id}`" class="btn-secondary">
              Editar
            </router-link>
            <router-link v-if="userIsAdmin" :to="{ name: 'imovel-imagens', params: { id: imovel.id } }" class="btn-info">
              Imagens
            </router-link>
            <button v-if="userIsAdmin" @click="handleInativar(imovel.id)" class="btn-danger">
              Inativar
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!isLoading && !imoveis.length">
      <p>Nenhum imóvel encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';

const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const userCargo = ref('');

// LÓGICA DE VERIFICAÇÃO DE ADMIN MAIS ROBUSTA
const userIsAdmin = computed(() => {
  const cargo = localStorage.getItem('userCargo');
  return cargo === 'ADMIN';
});

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const params = {
      search: searchTerm.value,
    };
    const response = await apiClient.get('/v1/imoveis/imoveis/', { params });
    imoveis.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchImoveis();
  userCargo.value = localStorage.getItem('userCargo') || '';
});

async function handleInativar(imovelId: number) {
  if (!window.confirm('Tem a certeza de que deseja inativar este imóvel? Ele não aparecerá mais nas listas.')) {
    return;
  }
  try {
    await apiClient.delete(`/v1/imoveis/imoveis/${imovelId}/`);
    imoveis.value = imoveis.value.filter(imovel => imovel.id !== imovelId);
  } catch (error) {
    console.error("Erro ao inativar imóvel:", error);
    alert("Ocorreu um erro ao tentar inativar o imóvel.");
  }
}
</script>

<style scoped>
/* Estilos permanecem os mesmos */
.imoveis-container {
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
  flex-wrap: wrap;
  gap: 0.5rem;
}
.btn-secondary, .btn-danger, .btn-info {
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9em;
  border: none;
  cursor: pointer;
}
.btn-secondary {
  background-color: #6c757d;
}
.btn-danger {
  background-color: #dc3545;
}
.btn-info {
  background-color: #17a2b8;
}
</style>
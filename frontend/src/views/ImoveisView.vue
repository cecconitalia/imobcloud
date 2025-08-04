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
            <router-link :to="`/imoveis/${imovel.id}/imagens`" class="btn-info">
              Imagens
            </router-link>
            <button @click="handleInativar(imovel.id)" class="btn-danger">
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
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// ESTADO PARA O TERMO DE PESQUISA (NOVO)
const searchTerm = ref('');

// FUNÇÃO DE BUSCA ATUALIZADA PARA INCLUIR A LÓGICA DE PESQUISA
async function fetchImoveis() {
  isLoading.value = true;
  try {
    const params = {
      search: searchTerm.value, // Adiciona o parâmetro 'search' ao pedido
    };
    // O pedido GET agora inclui os parâmetros de pesquisa
    const response = await apiClient.get('/v1/imoveis/imoveis/', { params });
    imoveis.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis.';
  } finally {
    isLoading.value = false;
  }
}

// LÓGICA onMounted (INTACTA)
onMounted(() => {
  fetchImoveis();
});

// LÓGICA handleInativar (INTACTA)
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
/* ESTILO PARA A BARRA DE PESQUISA (NOVO) */
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
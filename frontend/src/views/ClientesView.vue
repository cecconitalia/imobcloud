<template>
  <div class="clientes-container">
    <header class="view-header">
      <h1>Gerir Clientes</h1>
      <router-link to="/clientes/novo" class="btn-primary">
        <i class="fas fa-plus"></i> Novo Cliente
      </router-link>
    </header>

    <div class="search-and-filter-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por nome, email, cpf..."
        class="search-input"
      />
    </div>

    <div v-if="isLoading" class="loading-message">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="clientes.length > 0" class="clientes-grid">
      <div 
        v-for="cliente in filteredClientes" 
        :key="cliente.id" 
        class="cliente-card"
        @click="editCliente(cliente.id)"
      >
        <div class="cliente-profile-pic">
          <img v-if="cliente.foto_perfil" :src="cliente.foto_perfil" alt="Foto de Perfil" class="profile-img"/>
          <i v-else class="fas fa-user-circle profile-icon"></i>
        </div>
        <div class="cliente-info">
          <h3 class="cliente-nome">{{ cliente.nome_completo }}</h3>
          <p class="cliente-contato">{{ cliente.email }}</p>
          <p class="cliente-contato">{{ cliente.telefone }}</p>
        </div>
        <div class="cliente-actions">
          <router-link :to="`/clientes/editar/${cliente.id}`" class="btn-action edit-btn" @click.stop>
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
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

const router = useRouter();

const clientes = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');

async function fetchClientes() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/clientes/');
    clientes.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar clientes:", err);
    error.value = 'Não foi possível carregar os clientes.';
  } finally {
    isLoading.value = false;
  }
}

const filteredClientes = computed(() => {
  if (!searchTerm.value) {
    return clientes.value;
  }
  const search = searchTerm.value.toLowerCase();
  return clientes.value.filter(cliente =>
    cliente.nome_completo?.toLowerCase().includes(search) ||
    cliente.email?.toLowerCase().includes(search) ||
    cliente.cpf_cnpj?.toLowerCase().includes(search)
  );
});

function goToCreateCliente() {
  router.push({ name: 'cliente-novo' });
}

function editCliente(id: number) {
  router.push({ name: 'cliente-editar', params: { id } });
}

onMounted(() => {
  fetchClientes();
});
</script>

<style scoped>
.clientes-container {
  padding: 2rem;
  background-color: #f4f7f9;
  min-height: calc(100vh - 80px);
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 1.5rem;
}
.view-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}
.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-primary:hover {
  background-color: #0056b3;
}
.search-and-filter-bar {
  margin-bottom: 2rem;
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1rem;
  box-sizing: border-box;
}
.loading-message, .no-data-message, .error-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.clientes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}
.cliente-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center; /* Centraliza o conteúdo */
  text-align: center; /* Centraliza o texto */
  cursor: pointer;
}
.cliente-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}
.cliente-profile-pic {
  width: 80px; /* Tamanho da imagem */
  height: 80px; /* Tamanho da imagem */
  border-radius: 50%; /* Torna a imagem circular */
  overflow: hidden;
  margin-bottom: 1rem;
  background-color: #e9ecef; /* Cor de fundo para o ícone */
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px solid #007bff; /* Borda para destaque */
}
.profile-img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Garante que a imagem preencha o círculo */
}
.profile-icon {
  font-size: 40px; /* Tamanho do ícone de fallback */
  color: #6c757d;
}
.cliente-info {
  margin-bottom: 1rem;
}
.cliente-nome {
  font-size: 1.1rem;
  font-weight: bold;
  margin: 0 0 0.5rem 0;
  color: #333;
}
.cliente-contato {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}
.cliente-actions {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  width: 100%; /* Ocupa a largura total para alinhar o botão */
}
.btn-action {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 8px 12px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background-color 0.2s, color 0.2s;
  border: 1px solid #e9ecef;
  color: #6c757d;
  background-color: #f8f9fa;
}
.btn-action:hover {
  background-color: #e9ecef;
}
</style>
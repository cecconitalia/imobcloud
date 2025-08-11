<template>
  <div class="imoveis-container">
    <header class="view-header">
      <h1>Meus Imóveis</h1>
      <router-link to="/imoveis/novo" class="btn-primary">
        + Adicionar Imóvel
      </router-link>
    </header>

    <div class="filters-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por endereço, cidade..."
      />
      <select v-model="filterStatus">
        <option value="">Todos os Status</option>
        <option value="A_VENDA">À Venda</option>
        <option value="PARA_ALUGAR">Para Alugar</option>
        <option value="VENDIDO">Vendido</option>
        <option value="ALUGADO">Alugado</option>
        <option value="EM_CONSTRUCAO">Em Construção</option>
        <option value="DESATIVADO">Desativado</option>
      </select>
    </div>

    <div v-if="isLoading" class="loading-message">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="imoveis.length > 0" class="imoveis-grid">
      <div v-for="imovel in imoveis" :key="imovel.id" class="imovel-card">
        <img
          :src="getPrincipalImage(imovel.imagens)"
          :alt="imovel.titulo_anuncio"
          class="imovel-image"
        />
        <div class="imovel-info">
          <div class="imovel-header">
            <h3 class="imovel-title">{{ imovel.endereco }}</h3>
            <span :class="['status-badge', getStatusClass(imovel.status)]">
              {{ formatStatus(imovel.status) }}
            </span>
          </div>
          <p class="imovel-details">{{ imovel.cidade }} - {{ imovel.estado }}</p>
          <div class="imovel-actions">
            <router-link :to="`/imoveis/editar/${imovel.id}`" class="btn-action">
              <i class="fas fa-edit"></i>
              <span>Editar</span>
            </router-link>
            <router-link v-if="userIsAdmin" :to="{ name: 'imovel-imagens', params: { id: imovel.id } }" class="btn-action">
              <i class="fas fa-images"></i>
              <span>Imagens</span>
            </router-link>
            <button v-if="userIsAdmin" @click="handleInativar(imovel.id)" class="btn-action danger">
              <i class="fas fa-trash"></i>
              <span>Inativar</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!isLoading && !imoveis.length && !error" class="no-data-message">
      <p>Nenhum imóvel encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';
// É necessário instalar o Font Awesome para os ícones
// npm install --save-dev @fortawesome/fontawesome-free
import '@fortawesome/fontawesome-free/css/all.css';

const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterStatus = ref('');
const userIsAdmin = computed(() => localStorage.getItem('userCargo') === 'ADMIN');

let debounceTimeout: number | undefined = undefined;

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const params: { [key: string]: string } = {};
    if (searchTerm.value) {
      params.search = searchTerm.value;
    }
    if (filterStatus.value) {
      params.status = filterStatus.value;
    }
    const response = await apiClient.get('/v1/imoveis/imoveis/', { params });
    imoveis.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis.';
  } finally {
    isLoading.value = false;
  }
}

function getPrincipalImage(imagens: any[]) {
  if (!imagens || imagens.length === 0) {
    return 'https://via.placeholder.com/400x250.png?text=Sem+Imagem';
  }
  const principal = imagens.find(img => img.principal);
  return principal ? principal.imagem : imagens[0].imagem;
}

function getStatusClass(status: string) {
  switch (status) {
    case 'A_VENDA':
    case 'PARA_ALUGAR':
      return 'status-ativo';
    case 'VENDIDO':
    case 'ALUGADO':
      return 'status-concluido';
    case 'EM_CONSTRUCAO':
      return 'status-pendente';
    case 'DESATIVADO':
      return 'status-inativo';
    default:
      return '';
  }
}

function formatStatus(status: string) {
    return status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

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

onMounted(() => {
  fetchImoveis();
});

// Watchers para monitorar as mudanças nos filtros e chamar a API
watch(filterStatus, () => {
    fetchImoveis();
});

watch(searchTerm, () => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }
  debounceTimeout = setTimeout(() => {
    fetchImoveis();
  }, 500); // Espera 500ms para o usuário parar de digitar
});
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
.imoveis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.imovel-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}
.imovel-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}
.imovel-image {
  width: 100%;
  height: 200px; /* Altura fixa para consistência */
  object-fit: cover;
}
.imovel-info {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.imovel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.imovel-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: #343a40;
}
.imovel-details {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0 0 1rem 0;
}
.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  white-space: nowrap;
}
.status-ativo { background-color: #28a745; }
.status-concluido { background-color: #007bff; }
.status-pendente { background-color: #ffc107; color: #333; }
.status-inativo { background-color: #6c757d; }

.imovel-actions {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
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
.btn-action i {
    font-size: 1rem;
}
.btn-action:hover {
  background-color: #e9ecef;
}
.btn-action.danger {
  color: #dc3545;
  border-color: #dc3545;
}
.btn-action.danger:hover {
  background-color: #dc3545;
  color: white;
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
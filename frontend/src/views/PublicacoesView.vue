<template>
  <div class="publicacoes-container">
    <header class="view-header">
      <h1>Central de Publicações com IA</h1>
      <p>Selecione um imóvel abaixo para gerar e publicar conteúdo para as suas redes sociais.</p>
    </header>

    <div class="filters-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por endereço, código..."
      />
    </div>

    <div v-if="isLoading" class="loading-message">A carregar imóveis...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="filteredImoveis.length > 0" class="imoveis-list">
      <table class="table">
        <thead>
          <tr>
            <th>Imóvel</th>
            <th>Endereço</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="imovel in filteredImoveis" :key="imovel.id">
            <td>
              <div class="imovel-info">
                <img :src="getPrincipalImage(imovel.imagens)" :alt="imovel.titulo_anuncio" class="imovel-thumbnail">
                <div>
                  <strong>{{ imovel.titulo_anuncio }}</strong>
                  <small>Cód: {{ imovel.codigo_referencia }}</small>
                </div>
              </div>
            </td>
            <td>{{ imovel.endereco }}, {{ imovel.cidade }}</td>
            <td><span :class="['status-badge', getStatusClass(imovel.status)]">{{ formatStatus(imovel.status) }}</span></td>
            <td>
              <button @click="openModal(imovel)" class="btn-primary">
                <i class="fas fa-rocket"></i> Criar Publicação
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!isLoading && filteredImoveis.length === 0" class="no-data-message">
      <p>Nenhum imóvel encontrado com os filtros atuais.</p>
    </div>
  </div>

  <PublicacaoModal
    v-if="selectedImovel"
    :imovel-id="selectedImovel.id"
    @close="closeModal"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import PublicacaoModal from '@/components/PublicacaoModal.vue';
import '@fortawesome/fontawesome-free/css/all.css';

const imoveis = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const selectedImovel = ref<any | null>(null);

async function fetchImoveis() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/imoveis/');
    imoveis.value = response.data.filter((imovel: any) => imovel.status !== 'DESATIVADO');
  } catch (err) {
    console.error("Erro ao buscar imóveis:", err);
    error.value = 'Não foi possível carregar os imóveis.';
  } finally {
    isLoading.value = false;
  }
}

const filteredImoveis = computed(() => {
  if (!searchTerm.value) {
    return imoveis.value;
  }
  return imoveis.value.filter(imovel =>
    imovel.titulo_anuncio.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    imovel.endereco.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    imovel.codigo_referencia.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

function getPrincipalImage(imagens: any[]) {
  if (!imagens || imagens.length === 0) {
    return 'https://via.placeholder.com/100x60.png?text=Sem+Foto';
  }
  const principal = imagens.find(img => img.principal);
  return principal ? principal.imagem : imagens[0].imagem;
}

function getStatusClass(status: string) {
    if (!status) return 'status-inativo';
    const s = status.toLowerCase();
    if (s.includes('venda') || s.includes('alugar')) return 'status-ativo';
    if (s.includes('vendido') || s.includes('alugado')) return 'status-concluido';
    if (s.includes('construcao')) return 'status-pendente';
    return 'status-inativo';
}

function formatStatus(status: string) {
    return status ? status.replace(/_/g, ' ') : 'N/A';
}

function openModal(imovel: any) {
  selectedImovel.value = imovel;
}

function closeModal() {
  selectedImovel.value = null;
}

onMounted(() => {
  fetchImoveis();
});
</script>

<style scoped>
.publicacoes-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.view-header p {
    color: #6c757d;
}
.filters-bar {
  margin-bottom: 1.5rem;
}
.filters-bar input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.imoveis-list {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow-x: auto;
}
.table {
  width: 100%;
  border-collapse: collapse;
}
.table th, .table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}
.imovel-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.imovel-info div {
    display: flex;
    flex-direction: column;
}
.imovel-info small {
    color: #6c757d;
    font-size: 0.8em;
}
.imovel-thumbnail {
  width: 100px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
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
.loading-message, .no-data-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message { color: red; }
</style>
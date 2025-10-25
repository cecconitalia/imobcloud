<template>
  <div class="page-container">
    <header class="view-header">
      <h1>Gestão de Contratos</h1>
      <router-link to="/contratos/novo" class="btn-primary">
        <i class="fas fa-plus"></i> Adicionar Contrato
      </router-link>
    </header>

    <div class="filters-bar">
      <div class="search-wrapper">
        <i class="fas fa-search"></i>
        <input
          type="text"
          v-model="searchTerm"
          placeholder="Pesquisar por imóvel, inquilino, proprietário..."
        />
      </div>
      <div class="filter-groups">
        <select v-model="filterStatus">
          <option value="">Todos os Status</option>
          <option value="Ativo">Ativo</option>
          <option value="Pendente">Pendente</option>
          <option value="Concluído">Concluído</option>
          <option value="Rescindido">Rescindido</option>
          <option value="Inativo">Inativo</option>
        </select>
        <select v-model="filterTipo">
          <option value="">Todos os Tipos</option>
          <option value="Venda">Venda</option>
          <option value="Aluguel">Aluguel</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="loading-message">
        <div class="spinner"></div>
        A carregar contratos...
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!isLoading && filteredContratos.length > 0" class="content-grid">
      <div v-for="contrato in filteredContratos" :key="contrato.id" class="data-card" @click="goToContrato(contrato.id)">
        <div class="card-header">
          <div class="imovel-info">
            <strong class="imovel-titulo">{{ contrato.imovel?.titulo_anuncio || 'Imóvel não especificado' }}</strong>
            <span class="imovel-endereco">{{ contrato.imovel?.logradouro || 'Endereço não disponível' }}</span>
          </div>
          <div class="card-actions" @click.stop>
            <button @click="visualizarContrato(contrato.id)" class="btn-action view-btn" title="Visualizar">
              <i class="fas fa-eye"></i>
            </button>
            <router-link :to="`/contratos/editar/${contrato.id}`" class="btn-action edit-btn" title="Editar">
              <i class="fas fa-edit"></i>
            </router-link>
            <button v-if="userCargo === 'ADMIN'" @click="handleInativar(contrato.id)" class="btn-action delete-btn" title="Inativar">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>

        <div class="card-body">
          <div class="info-item">
            <i class="fas fa-user-tie icon"></i>
            <div>
              <span>Proprietário</span>
              <strong>{{ contrato.proprietario?.nome_completo || 'N/A' }}</strong>
            </div>
          </div>
          <div class="info-item">
            <i class="fas fa-user icon"></i>
            <div>
              <span>Inquilino / Comprador</span>
              <strong>{{ contrato.inquilino?.nome_completo || 'N/A' }}</strong>
            </div>
          </div>
        </div>

        <div class="card-footer">
          <div class="footer-info">
              <span :class="['status-badge', getTipoClass(contrato.tipo_contrato)]">
                {{ contrato.tipo_contrato }}
              </span>
              <span class="date-info">
                <i class="fas fa-calendar-alt"></i> {{ new Date(contrato.data_inicio).toLocaleDateString('pt-BR') }}
              </span>
          </div>
          <span :class="['status-badge', getStatusClass(contrato.status_contrato)]">
            {{ contrato.status_contrato }}
          </span>
        </div>
      </div>
    </div>
    
    <div v-if="!isLoading && filteredContratos.length === 0 && !error" class="no-data-message">
      <i class="fas fa-file-contract icon-large"></i>
      <p>Nenhum contrato encontrado para os filtros selecionados.</p>
    </div>

    <!-- Modal para visualização do contrato -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">Visualização do Contrato</h3>
          <button @click="showModal = false" class="modal-close-btn">&times;</button>
        </div>
        <div v-if="loadingModal" class="modal-loading-message">
          <div class="spinner"></div>
          Carregando conteúdo do contrato...
        </div>
        <div v-else-if="modalError" class="modal-error-message">
          {{ modalError }}
        </div>
        <div v-else class="modal-body" v-html="contratoHtml"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';
import { useToast } from 'vue-toast-notification';

const router = useRouter(); 
const toast = useToast();

const contratos = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterTipo = ref('');
const filterStatus = ref('');
const userCargo = ref('');

// Variáveis para a modal de visualização
const showModal = ref(false);
const contratoHtml = ref('');
const loadingModal = ref(false);
const modalError = ref('');


const filteredContratos = computed(() => {
  return contratos.value.filter(c => {
    const term = searchTerm.value.toLowerCase();
    const matchesSearch = !term || 
      c.imovel?.titulo_anuncio?.toLowerCase().includes(term) ||
      c.imovel?.logradouro?.toLowerCase().includes(term) ||
      c.inquilino?.nome_completo?.toLowerCase().includes(term) ||
      c.proprietario?.nome_completo?.toLowerCase().includes(term);
    
    const matchesTipo = !filterTipo.value || c.tipo_contrato === filterTipo.value;
    const matchesStatus = !filterStatus.value || c.status_contrato === filterStatus.value;
    
    return matchesSearch && matchesTipo && matchesStatus;
  });
});

async function fetchContratos() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/contratos/');
    contratos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contratos:", err);
    error.value = 'Não foi possível carregar os contratos.';
    toast.error(error.value);
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchContratos();
  userCargo.value = localStorage.getItem('userCargo') || '';
});

async function handleInativar(contratoId: number) {
  if (!window.confirm('Tem a certeza de que deseja inativar este contrato? Esta ação não pode ser desfeita.')) {
    return;
  }
  try {
    await apiClient.delete(`/v1/contratos/${contratoId}/`);
    contratos.value = contratos.value.filter(contrato => contrato.id !== contratoId);
    toast.success('Contrato inativado com sucesso.');
  } catch (err) {
    console.error("Erro ao inativar contrato:", err);
    toast.error("Ocorreu um erro ao tentar inativar o contrato.");
  }
}

function goToContrato(contratoId: number) {
  router.push({ path: `/contratos/editar/${contratoId}` });
}

function getTipoClass(tipo: string) {
  return tipo === 'Venda' ? 'tipo-venda' : 'tipo-aluguel';
}

function getStatusClass(status: string) {
  switch (status) {
    case 'Ativo': return 'status-ativo';
    case 'Pendente': return 'status-pendente';
    case 'Concluído': return 'status-concluido';
    case 'Rescindido':
    case 'Inativo': return 'status-inativo';
    default: return 'status-default';
  }
}

async function visualizarContrato(id: number) {
  showModal.value = true;
  loadingModal.value = true;
  modalError.value = '';
  try {
    const response = await apiClient.get(`/v1/contratos/${id}/get-html/`);
    contratoHtml.value = response.data;
  } catch (err) {
    modalError.value = 'Não foi possível carregar o conteúdo do contrato.';
    toast.error(modalError.value);
  } finally {
    loadingModal.value = false;
  }
}
</script>

<style scoped>
/* =================================== */
/* LAYOUT PADRÃO - INÍCIO */
/* =================================== */

.page-container {
  padding: 2rem;
  max-width: 1800px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

h1 {
  font-size: 2rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #007bff;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.btn-primary:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
}

.filters-bar {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}
.search-wrapper {
  position: relative;
  flex: 1 1 400px;
}
.search-wrapper i {
  position: absolute;
  top: 50%;
  left: 15px;
  transform: translateY(-50%);
  color: #adb5bd;
}
.filters-bar input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  font-size: 1rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  box-sizing: border-box;
}
.filter-groups {
  display: flex;
  gap: 1rem;
  flex: 1 1 auto;
}
.filters-bar select {
  width: 100%;
  padding: 12px 15px;
  font-size: 1rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  box-sizing: border-box;
  flex: 1;
}

/* GRID DE CONTEÚDO PADRONIZADO */
.content-grid {
  display: grid;
  gap: 1.5rem;
  /* MUDANÇA PRINCIPAL ABAIXO */
  /* Força 4 colunas em telas extra largas */
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

@media (min-width: 1600px) {
    .content-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}

/* CARD DE DADOS PADRONIZADO */
.data-card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.07);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  cursor: pointer;
}
.data-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.card-body {
  padding: 1rem;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.info-item .icon {
  font-size: 1.2rem;
  color: #007bff;
  width: 25px;
  text-align: center;
}
.info-item div {
  display: flex;
  flex-direction: column;
}
.info-item span {
  font-size: 0.75rem;
  color: #6c757d;
}
.info-item strong {
  font-size: 0.9rem;
  font-weight: 600;
  color: #212529;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}
.footer-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.date-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}
.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background-color: #f1f3f5;
  border: none;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-action i {
  font-size: 0.85rem;
}
.edit-btn:hover { background-color: #ffc107; color: white; }
.delete-btn:hover { background-color: #dc3545; color: white; }
.view-btn:hover { background-color: #17a2b8; color: white;}

/* =================================== */
/* LAYOUT PADRÃO - FIM */
/* =================================== */

/* Estilos Específicos da Página de Contratos */
.imovel-titulo {
  font-weight: 600;
  font-size: 1rem;
  color: #343a40;
}
.imovel-endereco {
  font-size: 0.8rem;
  color: #6c757d;
}

/* Badges */
.status-badge {
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}
.tipo-venda { background-color: #6f42c1; }
.tipo-aluguel { background-color: #fd7e14; }
.status-ativo { background-color: #28a745; }
.status-pendente { background-color: #ffc107; color: #333; }
.status-concluido { background-color: #17a2b8; }
.status-inativo { background-color: #dc3545; }
.status-default { background-color: #6c757d; }

/* MENSAGENS DE ESTADO */
.loading-message, .no-data-message, .error-message {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}
.no-data-message .icon-large {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #ced4da;
}
.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
}
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estilos para a Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-container {
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 900px;
  max-height: 90%;
  overflow-y: auto;
  position: relative;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}
.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #212529;
}
.modal-close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6c757d;
  cursor: pointer;
  transition: color 0.2s;
}
.modal-close-btn:hover {
  color: #dc3545;
}
.modal-body {
  white-space: pre-wrap; /* Mantém a formatação do texto, como quebras de linha */
  font-family: 'Inter', sans-serif;
  color: #333;
  line-height: 1.6;
}
</style>

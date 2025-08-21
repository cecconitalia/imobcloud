<template>
  <div class="contratos-container">
    <header class="view-header">
      <h1>Meus Contratos</h1>
      <router-link to="/contratos/novo" class="btn-primary">
        + Adicionar Contrato
      </router-link>
    </header>

    <div class="filters-bar">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="Pesquisar por imóvel, cliente..."
      />
      <select v-model="filterTipo">
        <option value="">Todos os Tipos</option>
        <option value="Venda">Venda</option>
        <option value="Aluguel">Aluguel</option>
      </select>
    </div>

    <div v-if="isLoading" class="loading-message">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="contratos-info" v-if="!isLoading && contratos.length > 0">
      <p class="total-count">Total de Contratos: <strong>{{ contratos.length }}</strong></p>
      <table class="contratos-table">
        <thead>
          <tr>
            <th>Imóvel</th>
            <th>Tipo</th>
            <th>Inquilino</th>
            <th>Proprietário</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contrato in filteredContratos" :key="contrato.id">
            <td>
              <strong class="imovel-titulo">{{ contrato.imovel?.titulo_anuncio || contrato.imovel?.endereco || 'N/A' }}</strong>
              <span class="imovel-endereco">{{ contrato.imovel?.endereco || 'N/A' }}</span>
            </td>
            <td>
              <span :class="['status-badge', getTipoClass(contrato.tipo_contrato)]">
                {{ contrato.tipo_contrato }}
              </span>
            </td>
            <td>{{ contrato.inquilino?.nome_completo || 'N/A' }}</td>
            <td>{{ contrato.proprietario?.nome_completo || 'N/A' }}</td>
            <td>
              <span :class="['status-badge', getStatusClass(contrato.status_contrato)]">
                {{ contrato.status_contrato }}
              </span>
            </td>
            <td class="actions-cell">
              <router-link :to="`/contratos/editar/${contrato.id}`" class="btn-action edit-btn">
                <i class="fas fa-edit"></i>
              </router-link>
              <button v-if="userCargo === 'ADMIN'" @click="handleInativar(contrato.id)" class="btn-action delete-btn">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-if="!isLoading && contratos.length === 0 && !error" class="no-data-message">
      <p>Nenhum contrato encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

const contratos = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterTipo = ref('');
const userCargo = ref('');

const filteredContratos = computed(() => {
  let filteredList = contratos.value;
  
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filteredList = filteredList.filter(c => 
      c.imovel?.endereco?.toLowerCase().includes(term) ||
      c.inquilino?.nome_completo?.toLowerCase().includes(term) ||
      c.proprietario?.nome_completo?.toLowerCase().includes(term)
    );
  }

  if (filterTipo.value) {
    filteredList = filteredList.filter(c => c.tipo_contrato === filterTipo.value);
  }

  return filteredList;
});

async function fetchContratos() {
  isLoading.value = true;
  try {
    const params = {
      search: searchTerm.value,
      tipo_contrato: filterTipo.value
    };
    const response = await apiClient.get('/v1/contratos/', { params });
    contratos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contratos:", err);
    error.value = 'Não foi possível carregar os contratos.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchContratos();
  userCargo.value = localStorage.getItem('userCargo') || '';
});

async function handleInativar(contratoId: number) {
  if (!window.confirm('Tem a certeza de que deseja inativar este contrato?')) {
    return;
  }
  try {
    await apiClient.delete(`/v1/contratos/${contratoId}/`);
    contratos.value = contratos.value.filter(contrato => contrato.id !== contratoId);
  } catch (error) {
    console.error("Erro ao inativar contrato:", error);
    alert("Ocorreu um erro ao tentar inativar o contrato.");
  }
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
    default: return '';
  }
}
</script>

<style scoped>
.contratos-container {
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

.contratos-info {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow-x: auto;
}
.total-count {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #6c757d;
}

.contratos-table {
  width: 100%;
  border-collapse: collapse;
}
.contratos-table th, .contratos-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}
.contratos-table th {
  background-color: #f8f9fa;
  font-weight: bold;
}

.imovel-titulo {
  font-weight: bold;
  display: block;
}
.imovel-endereco {
  font-size: 0.8em;
  color: #6c757d;
  display: block;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  white-space: nowrap;
}
.tipo-venda { background-color: #007bff; }
.tipo-aluguel { background-color: #28a745; }
.status-ativo { background-color: #17a2b8; }
.status-pendente { background-color: #ffc107; color: #333; }
.status-concluido { background-color: #28a745; }
.status-inativo { background-color: #dc3545; }

.actions-cell {
  display: flex;
  gap: 0.5rem;
}
.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #6c757d;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-action i {
    font-size: 1rem;
}
.edit-btn:hover { background-color: #ffc107; color: #333; }
.delete-btn:hover { background-color: #dc3545; color: white; }

.loading-message, .no-data-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
</style>
<template>
  <div class="page-container">
    
    <div v-if="isLoadingStats" class="loading-message stats-loading">
      <div class="spinner small"></div>
    </div>
    <div v-if="!isLoadingStats && dashboardData" class="dashboard-grid">
      <div class="stat-card">
        <h3>Total de Contratos</h3>
        <p>{{ dashboardData.total_contratos }}</p>
      </div>
      <div class="stat-card stat-ativo">
        <h3>Ativos</h3>
        <p>{{ dashboardData.total_ativos }}</p>
      </div>
      <div class="stat-card">
        <h3>Aluguéis Ativos (Mensal)</h3>
        <p>{{ formatCurrency(dashboardData.valor_total_alugueis_ativos) }}</p>
      </div>
      <div class="stat-card">
        <h3>Vendas (Em Andamento)</h3>
        <p>{{ formatCurrency(dashboardData.valor_total_vendas_ativas) }}</p>
      </div>
    </div>

    <div class="filters-bar card">
        <div class="filters-container">
          <div class="filter-group">
            <i class="fas fa-search filter-icon"></i>
            <input 
              type="text" 
              v-model="filtro" 
              placeholder="Filtrar por imóvel, inquilino..."
              class="form-control with-icon"
            />
          </div>
          <div class="filter-group">
            <i class="fas fa-filter filter-icon"></i>
            <select v-model="filtroStatus" class="form-select with-icon">
              <option value="">Todos os Status</option>
              <option value="RASCUNHO">Rascunho</option>
              <option value="ATIVO">Ativo</option>
              <option value="CONCLUIDO">Concluído</option>
              <option value="RESCINDIDO">Rescindido</option>
              <option value="CANCELADO">Cancelado</option>
            </select>
          </div>
          <div class="filter-group">
             <i class="fas fa-file-alt filter-icon"></i>
            <select v-model="filtroTipo" class="form-select with-icon">
              <option value="">Todos os Tipos</option>
              <option value="VENDA">Venda</option>
              <option value="ALUGUEL">Aluguel</option>
            </select>
          </div>
        </div>
        <router-link :to="{ name: 'contrato-novo' }" class="btn btn-primary btn-novo-contrato">
          <i class="fas fa-plus"></i> Novo Contrato
        </router-link>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      A carregar contratos...
    </div>
    <div v-else-if="error" class="error-message card">{{ error }}</div>
    <div v-else-if="filteredContratos.length === 0" class="empty-state card">
      Nenhum contrato encontrado com os filtros selecionados.
    </div>

    <div v-else class="contratos-grid">
      <div 
        v-for="contrato in filteredContratos" 
        :key="contrato.id" 
        :class="['contrato-card', getStatusClass(contrato.status_contrato)]"
      >
        
        <div class="card-header">
          <span :class="['status-badge', getStatusClass(contrato.status_contrato)]">
            {{ formatStatus(contrato.status_contrato) }}
          </span>
          <span class="tipo-badge">{{ contrato.tipo_contrato === 'VENDA' ? 'Venda' : 'Aluguel' }}</span>
        </div>
        
        <div class="card-body">
          <div class="card-item-principal">
            <span class="text-primary">{{ contrato.imovel_detalhes?.titulo_anuncio || 'N/A' }}</span>
            <span class="text-small">{{ contrato.imovel_detalhes?.endereco_completo || 'Endereço não disponível' }}</span>
          </div>
          
          <div class="card-info-row">
            <i class="fas fa-user icon-blue"></i>
            <div>
              <label v-if="contrato.tipo_contrato === 'VENDA'">Comprador</label>
              <label v-else>Inquilino</label>
              <span>{{ contrato.inquilino_detalhes?.nome_display || 'N/A' }}</span>
            </div>
          </div>

          <div class="card-info-row">
            <i class="fas fa-user-tie icon-grey"></i>
            <div>
              <label>Proprietário</label>
              <span>{{ contrato.proprietario_detalhes?.nome_display || 'N/A' }}</span>
            </div>
          </div>
          
          <div class="card-info-row">
             <i class="fas fa-dollar-sign icon-green"></i>
             <div>
                <label>Valor</label>
                <span class="text-bold-valor">{{ contrato.valor_display }}</span>
             </div>
          </div>
        </div>
        
        <div class="card-actions">
          
          <button
            v-if="contrato.status_contrato === 'RASCUNHO'"
            @click="handleAtivarContrato(contrato)"
            :disabled="isProcessingId === contrato.id"
            class="btn-action btn-ativar"
            title="Ativar Contrato (Gera o financeiro)"
          >
            <i v-if="isProcessingId === contrato.id" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-play"></i> Ativar
          </button>

          <button 
            v-if="contrato.tipo_contrato === 'ALUGUEL' && (contrato.status_contrato === 'ATIVO' || contrato.status_contrato === 'CONCLUIDO')"
            @click="abrirModalFinanceiro(contrato)" 
            class="btn-action btn-financeiro" 
            title="Ver Detalhes Financeiros"
          >
            <i class="fas fa-dollar-sign"></i> Financeiro
          </button>

          <button @click="editarContrato(contrato.id)" class="btn-action btn-edit" title="Editar Dados (Status, Datas...)">
            <i class="fas fa-edit"></i> Editar
          </button>
          <button @click="editarDocumento(contrato.id)" class="btn-action btn-edit-doc" title="Editar Documento (Texto)">
            <i class="fas fa-file-signature"></i> Documento
          </button>
          <button 
            @click="handleVisualizarPDF(contrato.id)" 
            :disabled="isProcessingId === contrato.id"
            class="btn-action btn-pdf" 
            title="Visualizar PDF"
          >
            <i v-if="isProcessingId === contrato.id" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-file-pdf"></i>
          </button>
          <button @click="handleDelete(contrato.id)" class="btn-action btn-delete" title="Excluir Contrato">
            <i class="fas fa-trash-alt"></i>
          </button>
        </div>
      </div>
    </div>

    <ModalFinanceiroContrato
        v-if="showModalFinanceiro && contratoSelecionado"
        :contrato="contratoSelecionado"
        @close="fecharModalFinanceiro"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { formatCurrency } from '@/utils/formatters'; 
import ModalFinanceiroContrato from '@/components/ContratoFinanceiro.vue';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';


// --- Interfaces ---
interface DetalhesPessoa {
  id: number;
  nome_display: string;
  documento?: string;
}
interface DetalhesImovel { 
  id: number; 
  logradouro: string; 
  endereco_completo: string;
  titulo_anuncio?: string; 
}
interface Contrato {
  id: number;
  tipo_contrato: 'VENDA' | 'ALUGUEL';
  imovel_detalhes: DetalhesImovel;
  proprietario_detalhes: DetalhesPessoa;
  inquilino_detalhes: DetalhesPessoa | null;
  data_inicio: string;
  data_fim?: string | null;
  data_assinatura: string | null;
  status_contrato: 'RASCUNHO' | 'ATIVO' | 'CONCLUIDO' | 'RESCINDIDO' | 'CANCELADO';
  valor_display: string;
  financeiro_gerado: boolean;
}
interface DashboardStats {
  total_contratos: number;
  total_ativos: number;
  total_rascunho: number;
  total_concluidos: number;
  valor_total_vendas_ativas: number;
  valor_total_alugueis_ativos: number;
}

const router = useRouter();
const toast = useToast(); 

// --- Refs de Estado ---
const contratos = ref<Contrato[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const filtro = ref('');
const filtroStatus = ref('');
const filtroTipo = ref(''); 
const isProcessingId = ref<number | null>(null);
const dashboardData = ref<DashboardStats | null>(null);
const isLoadingStats = ref(true);
const showModalFinanceiro = ref(false);
const contratoSelecionado = ref<Contrato | null>(null);


// --- Funções de API ---

async function fetchDashboardStats() {
  try {
    isLoadingStats.value = true;
    const response = await apiClient.get('/v1/contratos/dashboard-stats/');
    dashboardData.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar estatísticas do dashboard:', err);
  } finally {
    isLoadingStats.value = false;
  }
}

async function fetchContratos() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Contrato[]>('/v1/contratos/');
    contratos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contratos:", err);
    error.value = "Não foi possível carregar os contratos.";
  } finally {
    isLoading.value = false;
  }
}

async function handleDelete(contratoId: number) {
  if (window.confirm('Tem certeza que deseja excluir este contrato? Esta ação marcará o contrato como excluído (Soft Delete).')) {
    try {
      await apiClient.delete(`/v1/contratos/${contratoId}/`);
      contratos.value = contratos.value.filter(c => c.id !== contratoId);
      fetchDashboardStats();
    } catch (err: any) {
      console.error('Erro ao excluir contrato:', err);
      if (err.response && err.response.data && err.response.data.error) {
        alert(`Erro: ${err.response.data.error}`);
      } else {
        alert('Não foi possível excluir o contrato.');
      }
    }
  }
}

async function handleVisualizarPDF(contratoId: number) {
  if (isProcessingId.value !== null) return; 
  isProcessingId.value = contratoId;
  
  try {
    const response = await apiClient.get(
      `/v1/contratos/${contratoId}/visualizar-pdf/`,
      { responseType: 'blob' }
    );
    const file = new Blob([response.data], { type: 'application/pdf' });
    const fileURL = URL.createObjectURL(file);
    window.open(fileURL, '_blank');
    setTimeout(() => URL.revokeObjectURL(fileURL), 10000);

  } catch (error: any) {
    console.error('Erro ao visualizar PDF:', error.response?.data || error);
    alert("Falha ao gerar o PDF.");
  } finally {
    isProcessingId.value = null;
  }
}

async function handleAtivarContrato(contrato: Contrato) {
    if (isProcessingId.value !== null) return;

    const confirmacao = window.confirm(
        "Tem certeza que deseja ATIVAR este contrato?\n\nO financeiro será gerado automaticamente."
    );
    
    if (!confirmacao) return;

    isProcessingId.value = contrato.id;
    try {
        const response = await apiClient.post(`/v1/contratos/${contrato.id}/ativar/`);
        
        toast.success("Contrato ativado com sucesso!");
        
        const index = contratos.value.findIndex(c => c.id === contrato.id);
        if (index !== -1) {
             contratos.value[index] = response.data;
        }
        fetchDashboardStats(); 
        
    } catch (error: any) {
        console.error("Erro ao ativar contrato:", error.response?.data || error);
        const errorMsg = error.response?.data?.error || error.response?.data?.status_contrato || "Falha ao ativar o contrato.";
        toast.error(errorMsg, { duration: 5000 });
    } finally {
        isProcessingId.value = null;
    }
}


// --- Funções de Navegação ---

function editarContrato(id: number) {
  router.push({ name: 'contrato-editar', params: { id } });
}

function editarDocumento(id: number) {
  // ==========================================================
  // === CORREÇÃO: Usando a rota 'contrato-editar-documento'  ===
  // === do seu ficheiro router/index.ts                    ===
  // ==========================================================
  router.push({ name: 'contrato-editar-documento', params: { id } });
}

// --- Funções do Modal ---
function abrirModalFinanceiro(contrato: Contrato) {
    contratoSelecionado.value = contrato;
    showModalFinanceiro.value = true;
    // document.body.style.overflow = 'hidden'; // O componente do Modal deve tratar disto
}

function fecharModalFinanceiro() {
    showModalFinanceiro.value = false;
    contratoSelecionado.value = null;
    // document.body.style.overflow = ''; // O componente do Modal deve tratar disto
}

// --- Funções Computadas e Helpers ---

const filteredContratos = computed(() => {
  return contratos.value.filter(contrato => {
    const searchLower = filtro.value.toLowerCase().trim();
    
    const matchSearch = !searchLower ||
      (contrato.imovel_detalhes?.titulo_anuncio?.toLowerCase() || '').includes(searchLower) ||
      (contrato.imovel_detalhes?.endereco_completo?.toLowerCase() || '').includes(searchLower) ||
      (contrato.inquilino_detalhes?.nome_display?.toLowerCase() || '').includes(searchLower) ||
      (contrato.proprietario_detalhes?.nome_display?.toLowerCase() || '').includes(searchLower);

    const matchStatus = !filtroStatus.value || contrato.status_contrato === filtroStatus.value;
    const matchTipo = !filtroTipo.value || contrato.tipo_contrato === filtroTipo.value;

    return matchSearch && matchStatus && matchTipo;
  });
});

function formatarData(data: string | null | undefined): string {
  if (!data) return '';
  try {
    return format(parseISO(data), 'dd/MM/yyyy', { locale: ptBR });
  } catch {
    return 'Inválida';
  }
}

const formatStatus = (status: Contrato['status_contrato']) => {
  switch (status) {
    case 'RASCUNHO': return 'Rascunho';
    case 'ATIVO': return 'Ativo';
    case 'CONCLUIDO': return 'Concluído';
    case 'RESCINDIDO': return 'Rescindido';
    case 'CANCELADO': return 'Cancelado';
    default: return status;
  }
};

const getStatusClass = (status: Contrato['status_contrato']) => {
  switch (status) {
    case 'ATIVO': return 'status-ativo';
    case 'RASCUNHO': return 'status-rascunho';
    case 'CONCLUIDO': return 'status-concluido';
    case 'RESCINDIDO': return 'status-rescindido';
    case 'CANCELADO': return 'status-cancelado';
    default: return 'status-default';
  }
};


onMounted(() => {
  fetchContratos();
  fetchDashboardStats();
});
</script>

<style scoped>
/* ================================================== */
/* ESTILOS GERAIS DA VIEW (Layout e Cabeçalho) */
/* ================================================== */
.page-container {
  padding-top: 0;
  margin-top: 0;
}
.view-header {
  /* (Ocultado a pedido) */
  display: none; 
}
.btn-primary {
  background-color: #007bff; color: white;
  padding: 0.6rem 1.2rem; border-radius: 6px; text-decoration: none;
  font-weight: 500; display: inline-flex; align-items: center;
  gap: 0.5rem; border: none; cursor: pointer;
  transition: background-color 0.2s ease;
}
.btn-primary:hover { background-color: #0056b3; }

/* ================================================== */
/* ESTILOS DO DASHBOARD (Inalterado) */
/* ================================================== */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.stat-card {
  background-color: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}
.stat-card h3 {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  text-transform: uppercase;
}
.stat-card p {
  font-size: 1.75rem;
  font-weight: 700;
  color: #212529;
  margin: 0;
}
.stat-card.stat-ativo p { color: #198754; }
.stat-card.stat-rascunho p { color: #6c757d; }
.stats-loading { padding: 2rem; }
.spinner.small {
  width: 20px;
  height: 20px;
  border-width: 3px;
}

/* ================================================== */
/* ESTILOS DOS FILTROS (Melhorados) */
/* ================================================== */
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}
.filters-bar {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.filters-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  flex-grow: 1;
}
.filter-group {
  position: relative;
  flex-grow: 1;
  min-width: 220px;
}
.filter-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #adb5bd;
  font-size: 0.9rem;
}
.form-control.with-icon,
.form-select.with-icon {
  padding-left: 38px;
  height: 40px;
  width: 100%;
  border-radius: 6px;
  border: 1px solid #ced4da;
  background-color: #fff;
  font-size: 0.9rem;
}
.form-select.with-icon {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px 12px;
}
.btn-novo-contrato {
  white-space: nowrap; /* Impede que o botão quebre a linha */
}

/* ================================================== */
/* ESTILOS DE GRELHA E CARDS (Layout 4 Colunas) */
/* ================================================== */
.contratos-grid {
  display: grid;
  grid-template-columns: 1fr; /* 1 coluna (Mobile) */
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .contratos-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 colunas (Tablet) */
  }
}

@media (min-width: 1200px) {
  .contratos-grid {
    grid-template-columns: repeat(3, 1fr); /* 3 colunas (Desktop) */
  }
}

@media (min-width: 1600px) {
  .contratos-grid {
    grid-template-columns: repeat(4, 1fr); /* 4 colunas (Desktop Largo) */
  }
}

.contrato-card {
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border-left-width: 5px; 
  border-left-style: solid;
}
.contrato-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
}

/* Cores da Borda de Status */
.status-ativo { border-left-color: #198754; }
.status-rascunho { border-left-color: #6c757d; }
.status-concluido { border-left-color: #0d6efd; }
.status-rescindido, .status-cancelado { border-left-color: #dc3545; }
.status-default { border-left-color: #e9ecef; }


/* Cabeçalho do Card (Status e Tipo) */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1.2rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}
.status-badge {
  padding: 4px 10px; border-radius: 12px; font-size: 0.75rem;
  font-weight: bold; text-transform: uppercase;
}
.status-ativo { background-color: #d1e7dd; color: #0f5132; }
.status-rascunho { background-color: #e9ecef; color: #495057; }
.status-concluido { background-color: #cce5ff; color: #004085; }
.status-rescindido, .status-cancelado { background-color: #f8d7da; color: #721c24; }
.status-default { background-color: #e9ecef; color: #495057; }

.tipo-badge {
  font-size: 0.8rem; font-weight: 500; color: #495057;
  background-color: #e9ecef; padding: 3px 8px; border-radius: 4px;
}

/* Corpo do Card (Imóvel e Partes) */
.card-body {
  padding: 1.2rem;
  flex-grow: 1;
}
.card-item-principal {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.25rem;
}
.card-item-principal .text-primary {
  font-size: 1.15rem;
  font-weight: 600;
  color: #212529; 
  line-height: 1.3;
}
.card-item-principal .text-small {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.4;
}

.card-info-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 1rem;
}
.card-info-row i {
  font-size: 0.9rem;
  margin-top: 5px;
  width: 16px;
  text-align: center;
}
.card-info-row .icon-blue { color: #0d6efd; }
.card-info-row .icon-grey { color: #6c757d; }
.card-info-row .icon-green { color: #198754; }

.card-info-row div {
  display: flex;
  flex-direction: column;
}
.card-info-row label {
  font-size: 0.75rem;
  color: #6c757d;
  margin-bottom: 2px;
  text-transform: uppercase;
  font-weight: 500;
}
.card-info-row span {
  font-size: 0.95rem;
  font-weight: 600;
  color: #343a40;
}
.card-info-row .text-bold-valor {
  font-size: 1rem;
  font-weight: 700;
  color: #198754;
}


/* Rodapé do Card (Ações) */
.card-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end; 
  gap: 0.5rem;
  padding: 0.8rem 1.2rem;
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
}

/* ================================================== */
/* === CORREÇÃO: Estilo dos Botões (flex-grow removido) */
/* ================================================== */
.btn-action {
  background: none;
  border: 1px solid #ced4da;
  padding: 6px 10px; 
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  color: #495057;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  /* flex-grow: 1; */ /* <-- REMOVIDO para tamanhos naturais */
  justify-content: center;
}
.btn-action:hover:not(:disabled) {
  background-color: #e9ecef;
  border-color: #adb5bd;
}
.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-action i {
  font-size: 0.9em;
  /* Margem zero para botões só de ícone */
  margin-right: 0.2rem; 
}
/* Estilo para botões só de ícone (PDF e Excluir) */
.btn-pdf, .btn-delete {
  padding: 6px 9px; /* Padding horizontal menor */
}
.btn-pdf i, .btn-delete i {
  margin-right: 0; /* Remove margem do ícone */
}


/* Cores específicas dos botões */
.btn-ativar { color: #198754; border-color: #198754; }
.btn-ativar:hover:not(:disabled) { background-color: #198754; color: white; }

.btn-financeiro { color: #0d6efd; border-color: #0d6efd; }
.btn-financeiro:hover:not(:disabled) { background-color: #0d6efd; color: white; }

.btn-edit { color: #007bff; border-color: #007bff; }
.btn-edit:hover:not(:disabled) { background-color: #007bff; color: white; }

.btn-edit-doc { color: #fd7e14; border-color: #fd7e14; }
.btn-edit-doc:hover:not(:disabled) { background-color: #fd7e14; color: white; }

.btn-pdf { color: #6c757d; border-color: #6c757d; }
.btn-pdf:hover:not(:disabled) { background-color: #6c757d; color: white; }

.btn-delete { color: #dc3545; border-color: #dc3545; }
.btn-delete:hover:not(:disabled) { background-color: #dc3545; color: white; }


/* Mensagens de Estado */
.loading-message, .error-message, .empty-state {
  text-align: center; padding: 3rem; color: #6c757d;
  font-size: 1.1rem;
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

/* ================================================== */
/* === ESTILOS GLOBAIS DO MODAL (Restaurados)       === */
/* ================================================== */
:global(body.modal-open) {
  overflow: hidden;
}
/* O componente ModalFinanceiroContrato.vue é responsável 
   pelos seus próprios estilos internos (overlay, container, etc.) */
</style>
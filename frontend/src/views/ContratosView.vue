<template>
  <div class="page-container">
    
    <div v-if="isLoadingStats" class="loading-message stats-loading">
      <div class="spinner small"></div>
    </div>
    <div v-if="!isLoadingStats && dashboardData" class="dashboard-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-file-contract"></i></div>
        <div class="stat-info">
            <h3>Total de Contratos</h3>
            <p>{{ dashboardData.total_contratos }}</p>
        </div>
      </div>
      <div class="stat-card stat-ativo">
        <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
        <div class="stat-info">
            <h3>Ativos</h3>
            <p>{{ dashboardData.total_ativos }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-hand-holding-usd"></i></div>
        <div class="stat-info">
            <h3>Aluguéis (Mensal)</h3>
            <p>{{ formatCurrency(dashboardData.valor_total_alugueis_ativos) }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-comments-dollar"></i></div>
        <div class="stat-info">
            <h3>Vendas (Volume)</h3>
            <p>{{ formatCurrency(dashboardData.valor_total_vendas_ativas) }}</p>
        </div>
      </div>
    </div>

    <div class="search-and-filter-bar">
      <input 
        type="text" 
        v-model="filtro" 
        placeholder="Buscar por imóvel, inquilino..." 
        class="search-input"
      />
      
      <div class="filter-group">
        <label for="status">Status:</label>
        <select id="status" v-model="filtroStatus">
          <option value="">Todos</option>
          <option value="RASCUNHO">Rascunho</option>
          <option value="ATIVO">Ativo</option>
          <option value="CONCLUIDO">Concluído</option>
          <option value="RESCINDIDO">Rescindido</option>
          <option value="CANCELADO">Cancelado</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="tipo">Tipo:</label>
        <select id="tipo" v-model="filtroTipo">
          <option value="">Todos</option>
          <option value="VENDA">Venda</option>
          <option value="ALUGUEL">Aluguel</option>
        </select>
      </div>

      <router-link :to="{ name: 'contrato-novo' }" class="btn-add">
        <i class="fas fa-plus"></i> <span class="mobile-hide">Novo Contrato</span>
      </router-link>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      A carregar contratos...
    </div>
    <div v-else-if="error" class="error-message card">{{ error }}</div>
    <div v-else-if="filteredContratos.length === 0" class="empty-state card">
      <div class="empty-icon"><i class="fas fa-folder-open"></i></div>
      <p>Nenhum contrato encontrado com os filtros selecionados.</p>
    </div>

    <div v-else class="contratos-grid">
      <div 
        v-for="contrato in filteredContratos" 
        :key="contrato.id" 
        :class="['contrato-card', getStatusClass(contrato.status_contrato)]"
      >
        <div class="card-top-bar">
           <div class="badges-left">
               <span class="contrato-id">#{{ contrato.id }}</span>
               <span :class="['tipo-badge', contrato.tipo_contrato === 'VENDA' ? 'tipo-venda' : 'tipo-aluguel']">
                  {{ contrato.tipo_contrato === 'VENDA' ? 'Venda' : 'Aluguel' }}
               </span>
           </div>
           <div class="badges-right">
               <span :class="['status-pill', getStatusClass(contrato.status_contrato)]">
                  <i :class="getStatusIcon(contrato.status_contrato)"></i>
                  {{ formatStatus(contrato.status_contrato) }}
               </span>
           </div>
        </div>
        
        <div class="card-body">
          <div class="imovel-section">
             <h4 class="imovel-title" :title="contrato.imovel_detalhes?.titulo_anuncio">
                {{ contrato.imovel_detalhes?.titulo_anuncio || 'Imóvel sem título' }}
             </h4>
             <p class="imovel-address">
                <i class="fas fa-map-marker-alt text-muted"></i> 
                {{ contrato.imovel_detalhes?.endereco_completo || 'Endereço não disponível' }}
             </p>
          </div>

          <div class="datas-grid" v-if="contrato.data_inicio">
             <div class="data-col">
                <span class="data-label">Início</span>
                <div class="data-value text-success">
                    <i class="fas fa-hourglass-start"></i> {{ formatarData(contrato.data_inicio) }}
                </div>
             </div>
             <div class="data-divider"></div>
             <div class="data-col">
                <span class="data-label">Término</span>
                <div class="data-value" :class="contrato.data_fim ? 'text-danger' : 'text-muted'">
                    <i class="fas fa-hourglass-end"></i> {{ contrato.data_fim ? formatarData(contrato.data_fim) : 'Indeterminado' }}
                </div>
             </div>
          </div>
          <div class="datas-grid empty-dates" v-else>
              <span class="text-muted"><i class="far fa-clock"></i> Datas não definidas</span>
          </div>

          <div class="pessoas-container">
              <div class="pessoa-row">
                 <div class="pessoa-avatar avatar-proprietario">
                    <i class="fas fa-user-shield"></i>
                 </div>
                 <div class="pessoa-info">
                    <span class="pessoa-role role-proprietario">Proprietário</span>
                    <span class="pessoa-name" :title="contrato.proprietario_detalhes?.nome_display">
                        {{ contrato.proprietario_detalhes?.nome_display || '—' }}
                    </span>
                 </div>
              </div>
              
              <div class="pessoa-row">
                 <div class="pessoa-avatar avatar-inquilino">
                    <i class="fas fa-user"></i>
                 </div>
                 <div class="pessoa-info">
                    <span class="pessoa-role role-inquilino">
                        {{ contrato.tipo_contrato === 'VENDA' ? 'Comprador' : 'Inquilino' }}
                    </span>
                    <span class="pessoa-name" :title="contrato.inquilino_detalhes?.nome_display">
                        {{ contrato.inquilino_detalhes?.nome_display || '—' }}
                    </span>
                 </div>
              </div>
          </div>
        </div>
        
        <div class="valor-footer">
           <span class="valor-label">Valor do Contrato</span>
           <span class="valor-amount">{{ contrato.valor_display }}</span>
        </div>

        <div class="card-actions">
          <div class="actions-left">
            <button
                v-if="contrato.status_contrato === 'RASCUNHO'"
                @click="handleAtivarContrato(contrato)"
                :disabled="isProcessingId === contrato.id"
                class="btn-pill btn-ativar"
            >
                <i v-if="isProcessingId === contrato.id" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-play"></i> Ativar
            </button>

            <button 
                v-if="contrato.tipo_contrato === 'ALUGUEL' && (contrato.status_contrato === 'ATIVO' || contrato.status_contrato === 'CONCLUIDO')"
                @click="abrirModalFinanceiro(contrato)" 
                class="btn-pill btn-financeiro" 
            >
                <i class="fas fa-coins"></i> Financeiro
            </button>
          </div>

          <div class="actions-right">
              <button @click="editarDocumento(contrato.id)" class="btn-mini" title="Editar Texto do Contrato">
                <i class="fas fa-file-signature"></i>
              </button>
              <button 
                @click="handleVisualizarPDF(contrato.id)" 
                :disabled="isProcessingId === contrato.id"
                class="btn-mini" 
                title="Visualizar PDF"
              >
                <i v-if="isProcessingId === contrato.id" class="fas fa-spinner fa-spin"></i>
                <i v-else class="fas fa-file-pdf"></i>
              </button>
              <button @click="editarContrato(contrato.id)" class="btn-mini" title="Editar Dados">
                <i class="fas fa-pen"></i>
              </button>
              <button @click="handleDelete(contrato.id)" class="btn-mini btn-delete-mini" title="Excluir">
                <i class="fas fa-trash"></i>
              </button>
          </div>
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

// ==========================================================
// === CORREÇÃO: Função de Exclusão com DUPLO ALERTA    ===
// ==========================================================
async function handleDelete(contratoId: number) {
  // 1º ALERTA: Confirmação padrão
  if (window.confirm('Tem certeza que deseja excluir este contrato?')) {
      
      // 2º ALERTA: Aviso de IRREVERSIBILIDADE
      if (window.confirm('ATENÇÃO: Esta ação é IRREVERSÍVEL. O contrato desaparecerá da lista e todo o financeiro pendente será cancelado. Deseja realmente continuar?')) {
          try {
            await apiClient.delete(`/v1/contratos/${contratoId}/`);
            contratos.value = contratos.value.filter(c => c.id !== contratoId);
            fetchDashboardStats();
            toast.success("Contrato excluído com sucesso.");
          } catch (err: any) {
            console.error('Erro ao excluir contrato:', err);
            const msg = err.response?.data?.error || 'Não foi possível excluir o contrato.';
            toast.error(msg);
          }
      }
  }
}
// ==========================================================

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
    toast.error("Falha ao gerar o PDF.");
  } finally {
    isProcessingId.value = null;
  }
}

async function handleAtivarContrato(contrato: Contrato) {
    if (isProcessingId.value !== null) return;
    const confirmacao = window.confirm("Tem certeza que deseja ATIVAR este contrato?\n\nO financeiro será gerado automaticamente.");
    if (!confirmacao) return;
    isProcessingId.value = contrato.id;
    try {
        const response = await apiClient.post(`/v1/contratos/${contrato.id}/ativar/`);
        toast.success("Contrato ativado com sucesso!");
        const index = contratos.value.findIndex(c => c.id === contrato.id);
        if (index !== -1) { contratos.value[index] = response.data; }
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
function editarContrato(id: number) { router.push({ name: 'contrato-editar', params: { id } }); }
function editarDocumento(id: number) { router.push({ name: 'contrato-editar-documento', params: { id } }); }

// --- Funções do Modal ---
function abrirModalFinanceiro(contrato: Contrato) { contratoSelecionado.value = contrato; showModalFinanceiro.value = true; }
function fecharModalFinanceiro() { showModalFinanceiro.value = false; contratoSelecionado.value = null; }

// --- Computados e Formatadores ---
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
  if (!data) return '—';
  try { return format(parseISO(data), 'dd/MM/yy', { locale: ptBR }); } catch { return 'Inválida'; }
}

const formatStatus = (status: string) => {
  switch (status) {
    case 'RASCUNHO': return 'Rascunho';
    case 'ATIVO': return 'Ativo';
    case 'CONCLUIDO': return 'Concluído';
    case 'RESCINDIDO': return 'Rescindido';
    case 'CANCELADO': return 'Cancelado';
    default: return status;
  }
};

const getStatusClass = (status: string) => {
  switch (status) {
    case 'ATIVO': return 'status-ativo';
    case 'RASCUNHO': return 'status-rascunho';
    case 'CONCLUIDO': return 'status-concluido';
    case 'RESCINDIDO': return 'status-rescindido';
    case 'CANCELADO': return 'status-cancelado';
    default: return 'status-default';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'ATIVO': return 'fas fa-check-circle';
    case 'RASCUNHO': return 'fas fa-pencil-alt';
    case 'CONCLUIDO': return 'fas fa-flag-checkered';
    case 'RESCINDIDO': return 'fas fa-ban';
    case 'CANCELADO': return 'fas fa-times-circle';
    default: return 'fas fa-info-circle';
  }
};

onMounted(() => { fetchContratos(); fetchDashboardStats(); });
</script>

<style scoped>
/* ================================================== */
/* 1. Layout Geral */
/* ================================================== */
.page-container { padding: 0; }

/* ================================================== */
/* 2. Dashboard Stats */
/* ================================================== */
.dashboard-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem; margin-bottom: 2rem;
}
.stat-card {
  background-color: #fff; border: none; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04); display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s ease;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-icon {
    width: 50px; height: 50px; border-radius: 12px; background-color: #e7f1ff; color: #0d6efd;
    display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
}
.stat-ativo .stat-icon { background-color: #d1e7dd; color: #198754; }
.stat-info h3 { font-size: 0.8rem; color: #6c757d; font-weight: 600; margin: 0; text-transform: uppercase; }
.stat-info p { font-size: 1.5rem; font-weight: 700; color: #212529; margin: 0; }
.stat-ativo p { color: #198754; }

/* ================================================== */
/* 3. Filtros (PRESERVADOS) */
/* ================================================== */
.search-and-filter-bar {
  display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;
  align-items: center; background-color: transparent; padding: 0; box-shadow: none;
}
.search-input {
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 350px; box-sizing: border-box; font-family: system-ui, sans-serif;
}
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { font-weight: 500; color: #555; white-space: nowrap; }
.filter-group select {
  padding: 8px 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 0.95rem;
  background-color: #f8f9fa; min-width: 120px; font-family: system-ui, sans-serif;
}
.btn-add {
  background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 5px;
  cursor: pointer; font-weight: bold; transition: background-color 0.3s ease; font-size: 0.95rem;
  display: flex; align-items: center; gap: 0.5rem; margin-left: auto; width: auto; text-decoration: none;
  font-family: system-ui, sans-serif;
}
.btn-add:hover { background-color: #0056b3; }
.mobile-hide { display: inline; }
@media (max-width: 768px) {
  .search-and-filter-bar { flex-direction: column; align-items: stretch; }
  .search-input { max-width: 100%; }
  .filter-group { flex-direction: column; align-items: stretch; }
  .btn-add { margin-left: 0; justify-content: center; }
}

/* ================================================== */
/* 4. Grid de Contratos */
/* ================================================== */
.contratos-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.contrato-card {
  background-color: #fff; border-radius: 12px; border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); display: flex; flex-direction: column;
  transition: all 0.3s ease; position: relative; overflow: hidden;
}
.contrato-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.08); }

/* Header (Status/Type) */
.card-top-bar {
    padding: 0.85rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f0f2f5; background: #fff;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.contrato-id {
    font-size: 0.75rem; font-weight: 800; color: #6b7280;
    background: #f3f4f6; padding: 3px 8px; border-radius: 6px;
}

/* Badges & Colors */
.tipo-badge {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    padding: 3px 8px; border-radius: 6px; color: #6b7280; background-color: #f9fafb; border: 1px solid #e5e7eb;
}
.status-pill {
    padding: 0.35em 0.85em; border-radius: 50px; font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 5px;
}
/* Status Colors (Pastel + Strong Text) */
.status-ativo { background-color: #dcfce7; color: #166534; }
.status-rascunho { background-color: #f1f5f9; color: #475569; }
.status-concluido { background-color: #dbeafe; color: #1e40af; }
.status-rescindido, .status-cancelado { background-color: #fee2e2; color: #991b1b; }


/* Body */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }

/* Imovel Info */
.imovel-section { padding: 1.25rem 1.25rem 0.75rem; }
.imovel-title {
    font-size: 1.05rem; font-weight: 700; color: #111827; margin: 0 0 0.25rem 0;
    line-height: 1.4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.imovel-address {
    font-size: 0.85rem; color: #6b7280; margin: 0;
    display: flex; align-items: center; gap: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Dates (Timeline) */
.datas-grid {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 1.25rem; background-color: #f8fafc; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
}
.data-col { display: flex; flex-direction: column; gap: 2px; }
.data-label { font-size: 0.65rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; }
.data-value { font-size: 0.85rem; font-weight: 600; color: #374151; display: flex; align-items: center; gap: 6px; }
.data-divider { width: 1px; height: 24px; background-color: #e2e8f0; }
.empty-dates { justify-content: center; color: #9ca3af; font-size: 0.85rem; }
.text-success { color: #10b981; }
.text-danger { color: #ef4444; }

/* Pessoas Grid */
.pessoas-container { padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.pessoa-row { display: flex; align-items: center; gap: 0.85rem; }

.pessoa-avatar {
    width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0;
}
/* Colors for Roles */
.avatar-proprietario { background-color: #f3e8ff; color: #9333ea; } /* Purple */
.role-proprietario { color: #9333ea; }

.avatar-inquilino { background-color: #e0f2fe; color: #0284c7; } /* Blue */
.role-inquilino { color: #0284c7; }

.pessoa-info { display: flex; flex-direction: column; overflow: hidden; }
.pessoa-role { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1px; }
.pessoa-name { font-size: 0.9rem; color: #1f2937; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }


/* Footer Values */
.valor-footer {
    margin-top: auto; padding: 0.85rem 1.25rem;
    display: flex; justify-content: space-between; align-items: center;
    background-color: #111827; color: #fff; /* Dark contrast footer for value */
}
.valor-label { font-size: 0.75rem; color: #9ca3af; font-weight: 500; text-transform: uppercase; }
.valor-amount { font-size: 1.1rem; font-weight: 700; color: #fff; }


/* Actions */
.card-actions {
    padding: 0.85rem 1.25rem; background-color: #fff;
    display: flex; justify-content: space-between; align-items: center; gap: 1rem;
}
.actions-left { display: flex; gap: 0.5rem; }
.actions-right { display: flex; gap: 0.25rem; }

/* Action Buttons */
.btn-pill {
    border: none; border-radius: 6px; padding: 0.4rem 0.85rem; font-size: 0.8rem; font-weight: 600;
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
}
.btn-ativar { background-color: #d1fae5; color: #065f46; }
.btn-ativar:hover { background-color: #a7f3d0; }
.btn-financeiro { background-color: #eff6ff; color: #1e40af; }
.btn-financeiro:hover { background-color: #dbeafe; }

.btn-mini {
    width: 32px; height: 32px; border-radius: 6px; border: 1px solid transparent; background: transparent;
    color: #9ca3af; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s;
}
.btn-mini:hover { background-color: #f3f4f6; color: #374151; }
.btn-delete-mini:hover { background-color: #fee2e2; color: #dc2626; }

/* Utils */
.text-muted { color: #9ca3af; }
.loading-message, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #6c757d; }
.empty-icon { font-size: 3rem; color: #dee2e6; margin-bottom: 1rem; }
.spinner {
  border: 3px solid #e9ecef; border-top: 3px solid #0d6efd; border-radius: 50%;
  width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
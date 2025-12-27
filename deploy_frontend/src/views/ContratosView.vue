<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Gestão</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Contratos</span>
           </nav>
           
           <h1>Gerenciar Contratos</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="refreshData" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading || isLoadingStats }"></i>
            </button>
            
            <router-link :to="{ name: 'contrato-novo' }" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Novo Contrato
            </router-link>
        </div>
      </div>
    </header>

    <div class="kpi-grid" v-if="dashboardData">
      <div class="kpi-card blue" :class="{ active: filtroStatus === '' }" @click="filtroStatus = ''">
        <div class="kpi-content">
          <span class="kpi-value">{{ dashboardData.total_contratos }}</span>
          <span class="kpi-label">Total de Contratos</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-file-contract"></i></div>
      </div>

      <div class="kpi-card green" :class="{ active: filtroStatus === 'ATIVO' }" @click="filtroStatus = 'ATIVO'">
        <div class="kpi-content">
          <span class="kpi-value">{{ dashboardData.total_ativos }}</span>
          <span class="kpi-label">Contratos Ativos</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-check-circle"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value text-compact">{{ formatCurrency(dashboardData.valor_total_alugueis_ativos) }}</span>
          <span class="kpi-label">Aluguéis (Mensal)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-hand-holding-usd"></i></div>
      </div>

      <div class="kpi-card orange">
        <div class="kpi-content">
          <span class="kpi-value text-compact">{{ formatCurrency(dashboardData.valor_total_vendas_ativas) }}</span>
          <span class="kpi-label">Vendas (Volume)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-comments-dollar"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filtro" 
              placeholder="Buscar por imóvel, inquilino..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Status</label>
          <select v-model="filtroStatus" class="form-control">
            <option value="">Todos</option>
            <option value="RASCUNHO">Rascunho</option>
            <option value="ATIVO">Ativo</option>
            <option value="CONCLUIDO">Concluído</option>
            <option value="RESCINDIDO">Rescindido</option>
            <option value="CANCELADO">Cancelado</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Tipo</label>
          <select v-model="filtroTipo" class="form-control">
            <option value="">Todos</option>
            <option value="VENDA">Venda</option>
            <option value="ALUGUEL">Aluguel</option>
          </select>
        </div>

        <div class="filter-group small-btn">
            <label>&nbsp;</label>
            <button @click="clearFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Carregando contratos...</p>
    </div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="filteredContratos.length === 0" class="empty-state">
      <i class="fas fa-folder-open empty-icon"></i>
      <p>Nenhum contrato encontrado com os filtros selecionados.</p>
    </div>

    <div v-else class="contratos-grid">
      <div 
        v-for="contrato in filteredContratos" 
        :key="contrato.id" 
        class="contrato-card"
        :class="getBorderClass(contrato.status_contrato)"
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
                    <i class="fas fa-play-circle"></i> {{ formatarData(contrato.data_inicio) }}
                </div>
             </div>
             <div class="data-divider"></div>
             <div class="data-col">
                <span class="data-label">Término</span>
                <div class="data-value" :class="contrato.data_fim ? 'text-danger' : 'text-muted'">
                    <i class="fas fa-stop-circle"></i> {{ contrato.data_fim ? formatarData(contrato.data_fim) : 'Indeterminado' }}
                </div>
             </div>
          </div>
          <div class="datas-grid empty-dates" v-else>
              <span class="text-muted"><i class="far fa-clock"></i> Datas não definidas</span>
          </div>

          <div class="pessoas-container">
              <div class="pessoa-row">
                 <div class="pessoa-avatar avatar-proprietario">
                    <i class="fas fa-user-tie"></i>
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
                <i v-else class="fas fa-check"></i> Ativar
            </button>

            <button 
                v-if="contrato.tipo_contrato === 'ALUGUEL' && (contrato.status_contrato === 'ATIVO' || contrato.status_contrato === 'CONCLUIDO')"
                @click="abrirModalFinanceiro(contrato)" 
                class="btn-pill btn-financeiro" 
            >
                <i class="fas fa-dollar-sign"></i> Financeiro
            </button>
          </div>

          <div class="actions-right">
              <button @click="editarDocumento(contrato.id)" class="btn-mini" title="Editar Texto do Contrato">
                <i class="fas fa-file-contract"></i>
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
              <button @click="editarContrato(contrato.id)" class="btn-mini btn-edit" title="Editar Dados">
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

function refreshData() {
    fetchContratos();
    fetchDashboardStats();
}

function clearFilters() {
    filtro.value = '';
    filtroStatus.value = '';
    filtroTipo.value = '';
}

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

const getBorderClass = (status: string) => {
    if (status === 'ATIVO') return 'border-ativo';
    return '';
}

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

onMounted(() => { refreshData(); });
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (PADRONIZADO) */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA (PADRONIZADO) */
.page-header { margin-bottom: 2rem; }
.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Fino (PADRONIZADO) */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer; text-decoration: none;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15);
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* KPI GRID (PADRONIZADO) */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; position: relative; overflow: hidden;
  cursor: pointer;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-value.text-compact { font-size: 1.3rem; font-weight: 600; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }

.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }

.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }

.kpi-card.purple.active { background-color: #faf5ff; border-color: #9333ea; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR (PADRONIZADO) */
.toolbar-row {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}

.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 160px; }
.search-group { flex: 2; min-width: 260px; }
.small-btn { flex: 0 0 auto; min-width: auto; }
.filter-group label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }

.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }

.form-control {
  width: 100%; padding: 0.5rem 0.8rem; font-size: 0.85rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 38px; box-sizing: border-box; transition: all 0.2s;
}
.input-with-icon .form-control { padding-left: 2.2rem; }
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.btn-clear {
    width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc;
    border-radius: 6px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #fee2e2; color: #ef4444; border-color: #fca5a5; }

/* GRID DE CONTRATOS */
.contratos-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.contrato-card {
  background-color: #fff; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column;
  transition: all 0.2s ease; position: relative; overflow: hidden;
}
.contrato-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }
.border-ativo { border-left: 4px solid #10b981; }

/* Card Header */
.card-top-bar {
    padding: 0.8rem 1rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f1f5f9; background: #fff;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.contrato-id {
    font-size: 0.7rem; font-weight: 700; color: #64748b;
    background: #f1f5f9; padding: 2px 6px; border-radius: 4px;
}
.tipo-badge {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    padding: 2px 6px; border-radius: 4px; border: 1px solid #e2e8f0; color: #475569;
}
.status-pill {
    padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 4px;
}
.status-ativo { background-color: #dcfce7; color: #166534; }
.status-rascunho { background-color: #f1f5f9; color: #475569; }
.status-concluido { background-color: #e0f2fe; color: #1e40af; }
.status-rescindido, .status-cancelado { background-color: #fee2e2; color: #991b1b; }

/* Card Body */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }

.imovel-section { padding: 1rem 1rem 0.5rem; }
.imovel-title {
    font-size: 0.95rem; font-weight: 600; color: #1e293b; margin: 0 0 0.25rem 0;
    line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.imovel-address {
    font-size: 0.8rem; color: #64748b; margin: 0;
    display: flex; align-items: center; gap: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.datas-grid { 
    display: flex; align-items: center; justify-content: space-between; 
    padding: 0.5rem 1rem; background-color: #f8fafc; 
    border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; 
}
.data-col { display: flex; flex-direction: column; gap: 1px; }
.data-label { font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.data-value { font-size: 0.75rem; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 5px; }
.data-divider { width: 1px; height: 20px; background-color: #e2e8f0; }
.empty-dates { justify-content: center; font-size: 0.8rem; color: #94a3b8; }
.text-success { color: #16a34a; }
.text-danger { color: #dc2626; }

.pessoas-container { padding: 0.8rem 1rem; display: flex; flex-direction: column; gap: 0.8rem; }
.pessoa-row { display: flex; align-items: center; gap: 0.75rem; }
.pessoa-avatar {
    width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; flex-shrink: 0;
}
.avatar-proprietario { background-color: #f3e8ff; color: #9333ea; }
.role-proprietario { color: #9333ea; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1px; }
.avatar-inquilino { background-color: #e0f2fe; color: #0284c7; }
.role-inquilino { color: #0284c7; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1px; }
.pessoa-info { display: flex; flex-direction: column; overflow: hidden; }
.pessoa-name { font-size: 0.85rem; color: #334155; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Footer */
.valor-footer {
    margin-top: auto; padding: 0.6rem 1rem; display: flex; justify-content: space-between; align-items: center;
    background-color: #1e293b; color: #fff;
}
.valor-label { font-size: 0.7rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.valor-amount { font-size: 1rem; font-weight: 700; color: #fff; }

/* Actions */
.card-actions {
    padding: 0.75rem 1rem; background-color: #fff;
    display: flex; justify-content: space-between; align-items: center; gap: 1rem;
}
.actions-left { display: flex; gap: 0.5rem; }
.actions-right { display: flex; gap: 0.25rem; }

.btn-pill {
    border: none; border-radius: 4px; padding: 0.35rem 0.75rem; font-size: 0.75rem; font-weight: 600;
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
}
.btn-ativar { background-color: #dcfce7; color: #166534; }
.btn-ativar:hover { background-color: #bbf7d0; }
.btn-financeiro { background-color: #eff6ff; color: #1e40af; }
.btn-financeiro:hover { background-color: #dbeafe; }

.btn-mini {
    width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent;
    color: #94a3b8; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; font-size: 0.8rem;
}
.btn-mini:hover { background-color: #f1f5f9; color: #334155; }
.btn-delete-mini:hover { background-color: #fef2f2; color: #ef4444; }
.btn-edit:hover { background-color: #eff6ff; color: #2563eb; }

.text-muted { color: #94a3b8; }
.loading-state, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.empty-icon { font-size: 2.5rem; color: #e2e8f0; margin-bottom: 1rem; }
.spinner {
  border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%;
  width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .filter-group, .search-group { width: 100%; }
}
</style>
<template>
  <div class="page-container">
    <div class="view-header">
      <h1>Gestão de Contratos</h1>
      <router-link :to="{ name: 'contrato-novo' }" class="btn btn-primary">
        <i class="fas fa-plus"></i> Adicionar Contrato
      </router-link>
    </div>
    <div class="filters-bar card">
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
          <option value="ATIVO">Ativo</option>
          <option value="PENDENTE">Pendente</option>
          <option value="CONCLUIDO">Concluído</option>
          <option value="RESCINDIDO">Rescindido</option>
          <option value="INATIVO">Inativo</option>
        </select>
        <select v-model="filterTipo">
          <option value="">Todos os Tipos</option>
          <option value="VENDA">Venda</option>
          <option value="ALUGUEL">Aluguel</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      A carregar contratos...
    </div>
    <div v-if="error" class="error-message card">{{ error }}</div>

    <div v-if="filteredContratos.length > 0 && !isLoading" class="contratos-grid">
      <div v-for="contrato in filteredContratos" :key="contrato.id" class="contrato-card">
        <div class="card-header">
          <span :class="['status-badge', getStatusClass(contrato.status_contrato)]">{{ formatStatus(contrato.status_contrato) }}</span>
          <span class="tipo-badge">{{ contrato.tipo_contrato === 'VENDA' ? 'Venda' : 'Aluguel' }}</span>
        </div>
        
        <div class="card-body">
            <p><strong>Imóvel:</strong> {{ contrato.imovel_detalhes?.titulo_anuncio || contrato.imovel_detalhes?.logouro || 'N/A' }}</p>
            <p>
              <strong>{{ contrato.parte_principal_label }}:</strong> 
              {{ contrato.inquilino_detalhes?.nome_display || 'N/A' }}
            </p>
            <p><strong>Proprietário:</strong> {{ contrato.proprietario_detalhes?.nome_display || 'N/A' }}</p>
            <p><strong>Data Início:</strong> {{ formatarData(contrato.data_inicio) }}</p>
            <p><strong>Data Fim:</strong> {{ formatarData(contrato.data_fim) || 'Indeterminado' }}</p>
              <p><strong>Valor:</strong> {{ contrato.valor_display }}</p>
            <p>
                <strong>Financeiro:</strong> 
                <span :class="['status-badge', getFinanceiroStatusClass(contrato)]">
                    {{ getFinanceiroStatusText(contrato) }}
                </span>
            </p>
        </div>

        <div class="card-actions">
          
          <button
            v-if="contrato.status_contrato === 'PENDENTE'"
            @click="handleAtivarContrato(contrato)"
            :disabled="isProcessingId === contrato.id"
            class="btn-action btn-ativar"
            title="Ativar Contrato (Gera o financeiro automaticamente)"
          >
            <i v-if="isProcessingId === contrato.id" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-play"></i> Ativar
          </button>
          
          <button
            v-if="contrato.tipo_contrato === 'ALUGUEL'"
            @click="handleGerarFinanceiro(contrato.id)"
            :disabled="isProcessingId === contrato.id"
            :class="['btn-action', contrato.financeiro_gerado ? 'btn-success' : 'btn-warning']"
            :title="getGerarFinanceiroButtonText(contrato)"
          >
            <i v-if="isProcessingId === contrato.id" class="fas fa-spinner fa-spin"></i>
            <i v-else :class="contrato.financeiro_gerado ? 'fas fa-check' : 'fas fa-sync-alt'"></i>
            {{ contrato.financeiro_gerado ? 'Regerar' : 'Gerar' }}
          </button>
          
          <button @click="abrirModalFinanceiro(contrato)" class="btn-action btn-financeiro" title="Ver Detalhes Financeiros">
            <i class="fas fa-dollar-sign"></i> Financeiro
          </button>
          
          <button @click="verContrato(contrato.id)" class="btn-action btn-view"><i class="fas fa-eye"></i> Ver</button>
          
          <button 
            @click="handleVisualizarPDF(contrato.id)" 
            :disabled="isProcessingId === contrato.id"
            class="btn-action btn-pdf" 
            title="Visualizar PDF"
          >
            <i v-if="isProcessingId === contrato.id" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-file-pdf"></i> PDF
          </button>
          
          <button
            @click="editarDocumento(contrato.id)"
            class="btn-action btn-edit-doc"
            title="Editar Documento"
          >
            <i class="fas fa-file-signature"></i> Editar Doc.
          </button>
          
          <button @click="editarContrato(contrato.id)" class="btn-action btn-edit"><i class="fas fa-edit"></i> Editar</button>
          <button @click="excluirContrato(contrato.id)" class="btn-action btn-delete"><i class="fas fa-trash-alt"></i> Excluir</button>
        </div>
      </div>
    </div>
    <div v-else-if="!isLoading && !error" class="empty-state card">
      Nenhum contrato encontrado com os filtros selecionados.
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
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import ModalFinanceiroContrato from '@/components/ContratoFinanceiro.vue';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';


// Interface atualizada para corresponder aos dados aninhados
interface ClienteDetalhes { 
  id: number; 
  nome_display: string; 
}
interface ImovelDetalhes { 
  id: number; 
  logouro: string; 
  titulo_anuncio?: string; 
}
interface Contrato {
  id: number;
  tipo_contrato: 'VENDA' | 'ALUGUEL';
  // O frontend espera objetos aninhados:
  imovel_detalhes: ImovelDetalhes;
  proprietario_detalhes: ClienteDetalhes;
  inquilino_detalhes: ClienteDetalhes | null;
  data_inicio: string;
  data_fim?: string | null;
  status_contrato: 'ATIVO' | 'PENDENTE' | 'CONCLUIDO' | 'RESCINDIDO' | 'INATIVO';
  // E também espera estes campos para exibição:
  parte_principal_label: string;
  valor_display: string;
  financeiro_gerado: boolean;
}

const router = useRouter();
const contratos = ref<Contrato[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterStatus = ref('');
const filterTipo = ref('');

const toast = useToast();
const isProcessingId = ref<number | null>(null);

// Estado do Modal Financeiro
const showModalFinanceiro = ref(false);
const contratoSelecionado = ref<Contrato | null>(null);

const filteredContratos = computed(() => {
  return contratos.value.filter(contrato => {
    const searchLower = searchTerm.value.toLowerCase();
    
    // A lógica de busca já estava correta, usando os campos aninhados
    const matchSearch = !searchLower ||
      (contrato.imovel_detalhes?.titulo_anuncio?.toLowerCase() || '').includes(searchLower) ||
      (contrato.imovel_detalhes?.logouro?.toLowerCase() || '').includes(searchLower) ||
      (contrato.inquilino_detalhes?.nome_display?.toLowerCase() || '').includes(searchLower) ||
      (contrato.proprietario_detalhes?.nome_display?.toLowerCase() || '').includes(searchLower);

    const matchStatus = !filterStatus.value || contrato.status_contrato === filterStatus.value;
    const matchTipo = !filterTipo.value || contrato.tipo_contrato === filterTipo.value;

    return matchSearch && matchStatus && matchTipo;
  });
});


async function fetchContratos() {
  isLoading.value = true;
  error.value = null;
  try {
    // A API '/v1/contratos/' (GET) usará o ContratoListSerializer (corrigido)
    const response = await apiClient.get<Contrato[]>('/v1/contratos/');
    contratos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contratos:", err);
    error.value = "Não foi possível carregar os contratos.";
  } finally {
    isLoading.value = false;
  }
}

function formatarData(data: string | null | undefined): string {
  if (!data) return '';
  try {
    return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
  } catch {
    return 'Inválida';
  }
}

function formatStatus(status: string): string {
    const map: { [key: string]: string } = {
        'ATIVO': 'Ativo', 'PENDENTE': 'Pendente', 'CONCLUIDO': 'Concluído',
        'RESCINDIDO': 'Rescindido', 'INATIVO': 'Inativo',
    };
    return map[status] || status;
}

function getStatusClass(status: string): string {
    switch(status) {
        case 'ATIVO': return 'status-ativo';
        case 'PENDENTE': return 'status-pendente';
        case 'CONCLUIDO': return 'status-concluido';
        case 'RESCINDIDO': return 'status-rescindido';
        case 'INATIVO': return 'status-inativo';
        default: return '';
    }
}

function getFinanceiroStatusText(contrato: Contrato): string {
    if (contrato.tipo_contrato === 'VENDA') return 'Transação Única';
    return contrato.financeiro_gerado ? 'Gerado' : 'Pendente';
}

function getFinanceiroStatusClass(contrato: Contrato): string {
    if (contrato.tipo_contrato === 'VENDA') return 'status-financeiro-venda';
    return contrato.financeiro_gerado ? 'status-financeiro-gerado' : 'status-financeiro-pendente';
}

function getGerarFinanceiroButtonText(contrato: Contrato): string {
    return contrato.financeiro_gerado ? 'Financeiro já gerado! (Regerar)' : 'Gerar Financeiro (Manual)';
}

// (Função do PDF da etapa anterior)
async function handleVisualizarPDF(contratoId: number) {
  if (isProcessingId.value !== null) return; 
  isProcessingId.value = contratoId;
  
  try {
    toast.info('Gerando PDF... Por favor, aguarde.', { duration: 2000, position: 'top-right' });
    
    const response = await apiClient.get(
      `/v1/contratos/${contratoId}/visualizar-pdf/`,
      {
        responseType: 'blob' 
      }
    );
    const file = new Blob([response.data], { type: 'application/pdf' });
    const fileURL = URL.createObjectURL(file);
    window.open(fileURL, '_blank');
    setTimeout(() => URL.revokeObjectURL(fileURL), 10000);

  } catch (error: any) {
    console.error('Erro ao visualizar PDF:', error.response?.data || error);
    const errorMsg = error.response?.data?.error || "Falha ao gerar o PDF.";
    toast.error(errorMsg, { duration: 5000, position: 'top-right' });
  } finally {
    isProcessingId.value = null;
  }
}

async function handleAtivarContrato(contrato: Contrato) {
    if (isProcessingId.value !== null) return;

    const confirmacao = window.confirm(
        "Tem certeza que deseja ATIVAR este contrato?\n\nO financeiro será gerado automaticamente se for um contrato de aluguel e ainda não tiver sido gerado."
    );
    
    if (!confirmacao) return;

    isProcessingId.value = contrato.id;
    try {
        const response = await apiClient.post(`/v1/contratos/${contrato.id}/ativar/`);
        toast.success(response.data.status || "Contrato ativado com sucesso!");
        
        contrato.status_contrato = 'ATIVO';
        if (contrato.tipo_contrato === 'ALUGUEL') {
            contrato.financeiro_gerado = true;
        }
        
    } catch (error: any) {
        console.error("Erro ao ativar contrato:", error.response?.data || error);
        const errorMsg = error.response?.data?.error || "Falha ao ativar o contrato.";
        toast.error(errorMsg, { duration: 5000 });
    } finally {
        isProcessingId.value = null;
    }
}

async function handleGerarFinanceiro(contratoId: number) {
  if (isProcessingId.value !== null) return; 

  const contratoAtual = contratos.value.find(c => c.id === contratoId);
  const isRegerar = contratoAtual?.financeiro_gerado;
  
  const confirmacao = window.confirm(
    isRegerar ? 
    "Atenção! Você está prestes a REGERAR o financeiro. Isto irá APAGAR todas as parcelas PENDENTES deste contrato e criar novas.\n\nContas PAGO/ATRASADO serão mantidas.\n\nDeseja continuar?" :
    "Atenção! Isto irá gerar todas as parcelas de aluguel para este contrato.\n\nDeseja continuar?"
  );
  
  if (!confirmacao) {
    return;
  }

  isProcessingId.value = contratoId;
  try {
    const response = await apiClient.post(`/v1/contratos/${contratoId}/gerar-financeiro/`);
    toast.success(response.data.status || "Financeiro gerado com sucesso!");
    
    const contratoIndex = contratos.value.findIndex(c => c.id === contratoId);
    if (contratoIndex !== -1) {
        contratos.value[contratoIndex].financeiro_gerado = true;
    }
    
  } catch (error: any) {
    console.error("Erro ao gerar financeiro:", error.response?.data || error);
    const errorMsg = error.response?.data?.error || "Falha ao gerar financeiro.";
    toast.error(errorMsg, { duration: 5000 });
  } finally {
    isProcessingId.value = null;
  }
}

function verContrato(id: number) {
    // O botão "Ver" agora leva para o formulário de DADOS (como o editar)
    router.push({ name: 'contrato-editar', params: { id } });
}

// ==========================================================
// ================== NOVA FUNÇÃO ADICIONADA ================
// ==========================================================
function editarDocumento(id: number) {
  // Esta função leva para a NOVA tela de edição de HTML
  router.push({ name: 'contrato-editar-documento', params: { id } });
}
// ==========================================================

function editarContrato(id: number) {
  // Esta é a edição do FORMULÁRIO (dados do contrato)
  router.push({ name: 'contrato-editar', params: { id } });
}

async function excluirContrato(id: number) {
  if (window.confirm("Tem certeza de que deseja excluir este contrato? Esta ação não pode ser desfeita e excluirá os pagamentos associados.")) {
    isProcessingId.value = id; // Bloqueia botões durante a exclusão
    try {
      await apiClient.delete(`/v1/contratos/${id}/`);
      toast.success('Contrato excluído com sucesso!');
      fetchContratos();
    } catch (err) {
      console.error("Erro ao excluir contrato:", err);
      toast.error('Não foi possível excluir o contrato.');
    } finally {
      isProcessingId.value = null;
    }
  }
}


// Funções do Modal Financeiro
function abrirModalFinanceiro(contrato: Contrato) {
    contratoSelecionado.value = contrato;
    showModalFinanceiro.value = true;
    document.body.style.overflow = 'hidden';
}

function fecharModalFinanceiro() {
    showModalFinanceiro.value = false;
    contratoSelecionado.value = null;
    document.body.style.overflow = '';
}


onMounted(fetchContratos);
</script>

<style scoped>
.page-container {
  padding: 0; 
}

/* ================================================== */
/* ESTILOS DE VISIBILIDADE DO MODAL (MUITO IMPORTANTES!) */
/* ================================================== */
:global(.modal-overlay) {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); display: flex;
  justify-content: center; align-items: center; z-index: 1050;
}
:global(.modal-container) { 
  background: #fff; padding: 2rem; border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 90%; max-width: 700px; 
  max-height: 90vh; overflow-y: auto; position: relative;
}
:global(.modal-close-button) { 
    position: absolute; top: 1rem; right: 1rem; background: none; border: none;
    font-size: 1.5rem; cursor: pointer; color: #6c757d; line-height: 1;
}

/* ================================================== */
/* ESTILOS GERAIS DA VIEW (mantidos) */
/* ================================================== */

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}
.view-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #333;
}

.btn-primary {
  background-color: #007bff; color: white;
  padding: 0.6rem 1.2rem; border-radius: 6px; text-decoration: none;
  font-weight: 500; display: inline-flex; align-items: center;
  gap: 0.5rem; border: none; cursor: pointer;
  transition: background-color 0.2s ease;
}
.btn-primary:hover { background-color: #0056b3; }

.card {
    background: white; padding: 1.5rem; border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 1.5rem;
}

.filters-bar {
  display: flex; flex-wrap: wrap; align-items: center; gap: 1rem 1.5rem; 
}
.search-wrapper {
  position: relative; flex: 1 1 300px; min-width: 250px;
}
.search-wrapper i {
  position: absolute; left: 12px; top: 50%;
  transform: translateY(-50%); color: #adb5bd;
}
.search-wrapper input {
  width: 100%; padding: 10px 10px 10px 35px; border: 1px solid #ced4da;
  border-radius: 6px; font-size: 0.9rem; box-sizing: border-box; 
}
.filter-groups {
  display: flex; gap: 1rem; flex-wrap: wrap; flex-grow: 1; 
}
.filter-groups select {
  padding: 10px; border: 1px solid #ced4da; border-radius: 6px;
  font-size: 0.9rem; background-color: #fff; flex: 1 1 150px; min-width: 150px;
}
.loading-message, .error-message, .empty-state {
  text-align: center; padding: 2rem; color: #6c757d;
}
.spinner {
  border: 4px solid #f3f3f3; border-top: 4px solid #007bff; border-radius: 50%;
  width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.contratos-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem;
}
.contrato-card {
  background-color: #fff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.07);
  overflow: hidden; display: flex; flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.contrato-card:hover {
    transform: translateY(-4px); box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.8rem 1.2rem; background-color: #f8f9fa; border-bottom: 1px solid #e9ecef;
}
.status-badge {
    padding: 4px 10px; border-radius: 12px; font-size: 0.75rem;
    font-weight: bold; color: white; text-transform: uppercase;
}
.status-ativo { background-color: #198754; }
.status-pendente { background-color: #ffc107; color: #333; }
.status-concluido { background-color: #0d6efd; }
.status-rescindido { background-color: #dc3545; }
.status-inativo { background-color: #6c757d; }

.status-financeiro-pendente { background-color: #ffc107; color: #333; font-weight: 600; }
.status-financeiro-gerado { background-color: #198754; color: white; }
.status-financeiro-venda { background-color: #0d6efd; color: white; font-size: 0.7rem; }

.tipo-badge {
    font-size: 0.8rem; font-weight: 500; color: #495057;
    background-color: #e9ecef; padding: 3px 8px; border-radius: 4px;
}
.card-body {
  padding: 1.2rem; flex-grow: 1;
}
.card-body p { margin: 0 0 0.6rem 0; font-size: 0.9rem; color: #495057; }
.card-body p strong { color: #212529; margin-right: 5px; }

.card-actions {
  display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 0.5rem;
  padding: 0.8rem 1.2rem; border-top: 1px solid #e9ecef; background-color: #f8f9fa;
}

.btn-action {
    background: none; border: 1px solid transparent; padding: 6px 10px;
    border-radius: 5px; cursor: pointer; font-size: 0.8rem; font-weight: 500;
    transition: background-color 0.2s, color 0.2s, border-color 0.2s;
    display: inline-flex; align-items: center; gap: 0.4rem;
}
.btn-action i { font-size: 0.9em; }

.btn-action:disabled {
  opacity: 0.6; cursor: not-allowed; background-color: #e9ecef;
  color: #6c757d; border-color: #ced4da;
}

/* Estilo para o novo botão ATIVAR */
.btn-ativar { border-color: #198754; color: #198754; background-color: #d1e7dd; }
.btn-ativar:hover:not(:disabled) { background-color: #198754; color: white; }

.btn-warning { border: 1px solid #ffc107; background-color: #ffc107; color: #212529; }
.btn-warning:hover:not(:disabled) { background-color: #e0a800; color: #212529; border-color: #e0a800; }
.btn-success { border: 1px solid #198754; background-color: #198754; color: white; }
.btn-success:hover:not(:disabled) { background-color: #157347; color: white; border-color: #157347; }
.btn-view { border-color: #6c757d; color: #6c757d; }
.btn-view:hover { background-color: #6c757d; color: white; }
.btn-edit { border-color: #0d6efd; color: #0d6efd; }
.btn-edit:hover { background-color: #0d6efd; color: white; }
.btn-financeiro { border-color: #198754; color: #198754; }
.btn-financeiro:hover { background-color: #198754; color: white; }
.btn-delete { border-color: #dc3545; color: #dc3545; }
.btn-delete:hover { background-color: #dc3545; color: white; }

.btn-pdf { border-color: #0d6efd; color: #0d6efd; } 
.btn-pdf:hover:not(:disabled) { background-color: #0d6efd; color: white; }

/* ========================================================== */
/* ==================== ESTILO ADICIONADO =================== */
/* ========================================================== */
.btn-edit-doc { border-color: #ffc107; color: #212529; } /* Amarelo */
.btn-edit-doc:hover:not(:disabled) { background-color: #e0a800; color: #212529; border-color: #e0a800; }
/* ========================================================== */
</style>
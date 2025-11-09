<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <button class="modal-close-button" @click="$emit('close')">&times;</button>
      
      <h2 class="modal-title">Detalhes Financeiros do Contrato #{{ contrato.id }}</h2>
      <p class="modal-subtitle">Imóvel: {{ contrato.imovel_detalhes?.titulo_anuncio || contrato.imovel_detalhes?.logradouro }}</p>
      <p class="modal-subtitle">Inquilino: {{ contrato.inquilino_detalhes?.nome_display }}</p>

      <div v-if="isLoadingPagamentos" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i> Carregando parcelas...
      </div>
      
      <div v-else-if="error" class="error-state">
        Erro ao carregar pagamentos: {{ error }}
      </div>

      <div v-else-if="pagamentos.length === 0" class="empty-state">
        Nenhuma parcela gerada para este contrato.
      </div>
      
      <div v-else class="pagamentos-list">
        <div v-for="pagamento in pagamentos" :key="pagamento.id" class="pagamento-item card">
          <div class="item-details">
            <p><strong>Vencimento:</strong> {{ formatarData(pagamento.data_vencimento) }}</p>
            <p><strong>Valor:</strong> {{ formatarMoeda(pagamento.valor) }}</p>
            <p>
                <strong>Status:</strong>
                <span :class="['status-badge', getPagamentoStatusClass(pagamento.status)]">
                    {{ formatarStatusPagamento(pagamento.status) }}
                </span>
            </p>
            <p v-if="pagamento.data_pagamento"><strong>Data Pag.:</strong> {{ formatarData(pagamento.data_pagamento) }}</p>
          </div>
          
          <div class="item-actions">
            <button 
              v-if="pagamento.status !== 'PAGO'"
              @click="marcarComoPago(pagamento.id)"
              :disabled="isProcessingId === pagamento.id"
              class="btn-action btn-success"
            >
              <i v-if="isProcessingId === pagamento.id" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-check"></i> Marcar Pago
            </button>
            
            <button 
              v-if="pagamento.status === 'PAGO'"
              @click="gerarRecibo(pagamento.id)"
              class="btn-action btn-info"
              :disabled="isProcessingId === pagamento.id"
            >
              <i class="fas fa-file-pdf"></i> Recibo
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api'; 
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useToast } from 'vue-toast-notification';

const props = defineProps({
  contrato: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['close']);

// Tipagens simplificadas do Contrato e Pagamento
interface IContrato {
    id: number;
    imovel_detalhes: { titulo_anuncio: string, logradouro: string };
    inquilino_detalhes: { nome_display: string };
}
interface IPagamento {
    id: number;
    valor: string;
    data_vencimento: string;
    data_pagamento: string | null;
    status: 'PENDENTE' | 'PAGO' | 'ATRASADO' | 'CANCELADO';
}

const pagamentos = ref<IPagamento[]>([]);
const isLoadingPagamentos = ref(false);
const error = ref<string | null>(null);
const isProcessingId = ref<number | null>(null);
const toast = useToast();

const contrato = props.contrato as IContrato;

// --- Funções de Formatação ---

function formatarData(data: string | null | undefined): string {
  if (!data) return 'N/A';
  try {
    return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
  } catch {
    return 'Inválida';
  }
}

function formatarMoeda(valor: string | number): string {
    const num = typeof valor === 'string' ? parseFloat(valor) : valor;
    if (isNaN(num)) return 'R$ 0,00';
    return `R$ ${num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatarStatusPagamento(status: string): string {
    const map: { [key: string]: string } = {
        'PENDENTE': 'Pendente', 'PAGO': 'Pago', 'ATRASADO': 'Atrasado', 'CANCELADO': 'Cancelado',
    };
    return map[status] || status;
}

function getPagamentoStatusClass(status: string): string {
    switch(status) {
        case 'PAGO': return 'status-pago';
        case 'PENDENTE': return 'status-pendente';
        case 'ATRASADO': return 'status-atrasado';
        case 'CANCELADO': return 'status-cancelado';
        default: return '';
    }
}


// --- Funções de API ---

async function fetchPagamentos() {
  isLoadingPagamentos.value = true;
  error.value = null;
  try {
    // Chama o endpoint customizado do ContratoViewSet: /v1/contratos/{id}/pagamentos/
    const response = await apiClient.get(`/v1/contratos/${contrato.id}/pagamentos/`);
    pagamentos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar pagamentos:", err);
    error.value = "Não foi possível carregar as parcelas.";
  } finally {
    isLoadingPagamentos.value = false;
  }
}

async function marcarComoPago(pagamentoId: number) {
  const pagamento = pagamentos.value.find(p => p.id === pagamentoId);
  const vencimento = pagamento ? formatarData(pagamento.data_vencimento) : 'N/A';

  if (!window.confirm(`Confirmar baixa do pagamento com vencimento em ${vencimento}?`)) return;
  
  isProcessingId.value = pagamentoId;
  try {
    // Chama o endpoint customizado do PagamentoViewSet: /v1/pagamentos/{id}/marcar-pago/
    const response = await apiClient.post(`/v1/pagamentos/${pagamentoId}/marcar-pago/`, {});
    
    toast.success('Pagamento baixado com sucesso!');
    fetchPagamentos(); // Recarrega a lista para atualizar o status
  } catch (error: any) {
    const errorMsg = error.response?.data?.status || 'Falha ao marcar como pago.';
    console.error("Erro ao marcar como pago:", errorMsg);
    toast.error(errorMsg);
  } finally {
    isProcessingId.value = null;
  }
}

async function gerarRecibo(pagamentoId: number) {
  isProcessingId.value = pagamentoId;
  try {
    // Chama a View personalizada para gerar o PDF: /v1/pagamentos/{id}/recibo/
    const response = await apiClient.get(`/v1/pagamentos/${pagamentoId}/recibo/`, {
      responseType: 'blob' // Importante para receber o arquivo PDF
    });
    
    // Cria um URL temporário para o blob e abre em nova janela
    const fileURL = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    window.open(fileURL, '_blank');

    toast.info('Recibo gerado e aberto em nova aba.');
  } catch (error) {
    console.error("Erro ao gerar recibo:", error);
    toast.error('Não foi possível gerar o recibo.');
  } finally {
    isProcessingId.value = null;
  }
}

onMounted(fetchPagamentos);

</script>

<style scoped>
/* Os estilos globais do Modal estão no ContratosView.vue. */

.modal-container { 
  max-width: 800px !important;
}

.modal-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; color: #007bff; }
.modal-subtitle { font-size: 1rem; color: #6c757d; margin-bottom: 0.5rem; }

.loading-state, .error-state, .empty-state {
    text-align: center;
    padding: 2rem;
    font-size: 1.1rem;
    color: #6c757d;
}
.error-state {
    color: #dc3545;
    background-color: #f8d7da;
    border-radius: 6px;
}

.pagamentos-list {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.pagamento-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border: 1px solid #e9ecef;
    border-left: 5px solid #007bff; /* Linha de destaque */
    background-color: #fff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    border-radius: 6px;
}

.item-details p {
    margin: 0;
    font-size: 0.95rem;
    color: #495057;
}

.item-details p strong {
    color: #212529;
    margin-right: 5px;
}

.status-badge {
    padding: 4px 10px; border-radius: 12px; font-size: 0.75rem;
    font-weight: bold; color: white; text-transform: uppercase;
    display: inline-block;
    margin-left: 5px;
}
.status-pago { background-color: #198754; }
.status-pendente { background-color: #ffc107; color: #333; }
.status-atrasado { background-color: #dc3545; }
.status-cancelado { background-color: #6c757d; }

.item-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-action {
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: opacity 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

.btn-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-success { background-color: #198754; color: white; }
.btn-info { background-color: #0d6efd; color: white; }
</style>
<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <button @click="closeModal" class="modal-close-button">&times;</button>
      
      <div class="modal-header">
        <div>
            <h3>Financeiro do Contrato (Aluguel)</h3>
            <p>
              Locatário: <strong>{{ contrato.inquilino_detalhes?.nome_display || 'N/A' }}</strong><br>
              Imóvel: <strong>{{ contrato.imovel_detalhes?.titulo_anuncio || 'N/A' }}</strong>
            </p>
        </div>
        
        <button @click="fetchPagamentos" :disabled="isLoading" class="btn btn-refresh" title="Atualizar Pagamentos">
           <i :class="['fas fa-sync-alt', { 'fa-spin': isLoading }]"></i>
           <span v-if="isLoading">Atualizando...</span>
           <span v-else>Atualizar</span>
        </button>
      </div>
      
      <div class="modal-body">
        <div v-if="isLoading" class="loading-message">
          <div class="spinner"></div>
          Carregando pagamentos...
        </div>
        
        <div v-else-if="error" class="error-message">
          Erro ao carregar dados: {{ error }}
        </div>
        
        <div v-else-if="pagamentos.length === 0" class="empty-message">
          Nenhuma parcela gerada para este contrato.
        </div>
        
        <div v-else class="tabela-pagamentos">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Vencimento</th>
                <th>Valor</th>
                <th>Status</th>
                <th>Data Pagamento</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(pag, index) in pagamentos" :key="pag.id">
                <td>{{ index + 1 }}</td>
                <td>{{ formatarData(pag.data_vencimento) }}</td>
                <td>{{ formatCurrency(pag.valor) }}</td>
                <td>
                  <span :class="['status-badge', getStatusClass(pag.status)]">
                    {{ pag.status }}
                  </span>
                </td>
                <td>{{ formatarData(pag.data_pagamento) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="closeModal" class="btn btn-secondary">Fechar</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, PropType, onBeforeUnmount } from 'vue';
import apiClient from '@/services/api';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { formatCurrency } from '@/utils/formatters'; 


// --- Interfaces ---

interface DetalhesPessoa {
  nome_display: string;
}
interface DetalhesImovel { 
  titulo_anuncio: string;
}

// Interface do Contrato (recebida via Prop)
interface Contrato {
  id: number;
  imovel_detalhes: DetalhesImovel;
  inquilino_detalhes: DetalhesPessoa;
}

// Interface para os pagamentos que vamos buscar
interface Pagamento {
  id: number;
  data_vencimento: string;
  valor: number;
  status: 'PENDENTE' | 'PAGO' | 'ATRASADO' | 'CANCELADO';
  data_pagamento: string | null;
}

// --- Props e Emits ---
const props = defineProps({
  contrato: {
    type: Object as PropType<Contrato>,
    required: true
  }
});

const emit = defineEmits(['close']);

// --- Estado Local ---
const pagamentos = ref<Pagamento[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

// --- Funções ---
async function fetchPagamentos() {
  isLoading.value = true;
  error.value = null;
  try {
    // A API que criamos: /api/v1/contratos/{id}/pagamentos/
    const response = await apiClient.get(`/v1/contratos/${props.contrato.id}/pagamentos/`);
    pagamentos.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar pagamentos:", err);
    error.value = err.response?.data?.error || "Não foi possível carregar os detalhes financeiros.";
  } finally {
    isLoading.value = false;
  }
}

function closeModal() {
  emit('close');
}

function formatarData(data: string | null | undefined): string {
  if (!data) return '—';
  try {
    return format(parseISO(data), 'dd/MM/yyyy', { locale: ptBR });
  } catch {
    return 'Inválida';
  }
}

function getStatusClass(status: Pagamento['status']) {
  switch (status) {
    case 'PAGO': return 'status-pago';
    case 'PENDENTE': return 'status-pendente';
    case 'ATRASADO': return 'status-atrasado';
    case 'CANCELADO': return 'status-cancelado';
    default: return 'status-default';
  }
}

onMounted(() => {
  fetchPagamentos();
  document.body.style.overflow = 'hidden';
});

onBeforeUnmount(() => {
  document.body.style.overflow = '';
});
</script>

<style scoped>
/* Overlay do Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
  padding: 1rem;
}

/* Container do Modal */
.modal-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex; 
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #212529;
}
.modal-header p {
  margin: 0.25rem 0 0;
  font-size: 0.9rem;
  color: #6c757d;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex-grow: 1;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
  display: flex;
  justify-content: flex-end;
}

.modal-close-button {
  position: absolute;
  top: 0.75rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.75rem;
  font-weight: 600;
  cursor: pointer;
  color: #adb5bd;
  line-height: 1;
  padding: 0.5rem;
  z-index: 1060; 
}
.modal-close-button:hover {
  color: #495057;
}

/* Tabela de Pagamentos */
.tabela-pagamentos {
  width: 100%;
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.9rem;
  white-space: nowrap;
}
th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}
td {
  color: #212529;
}
tr:last-child td {
  border-bottom: none;
}

/* Status Badges */
.status-badge {
  padding: 0.25em 0.6em;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}
.status-pago { background-color: #d1e7dd; color: #0f5132; }
.status-pendente { background-color: #ffedcc; color: #664d03; }
.status-atrasado { background-color: #f8d7da; color: #721c24; }
.status-cancelado { background-color: #e9ecef; color: #495057; }
.status-default { background-color: #e9ecef; color: #495057; }

/* Mensagens */
.loading-message, .empty-message, .error-message {
  text-align: center;
  padding: 2rem;
  font-size: 1rem;
  color: #6c757d;
}
.error-message {
  color: #dc3545;
}
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Botões */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}
.btn-secondary {
  background-color: #6c757d;
  border-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
.btn-refresh {
    background-color: #0d6efd;
    border-color: #0d6efd;
    color: white;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 8px 12px;
}
.btn-refresh:hover:not(:disabled) {
    background-color: #0a58ca;
}
.btn-refresh:disabled {
    opacity: 0.6;
}
</style>
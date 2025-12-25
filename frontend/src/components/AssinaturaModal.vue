<script setup lang="ts">
/**
 * IMOBCLOUD - MODAL DE COLETA DE ASSINATURA (RESPONSIVO)
 * Atualização: 
 * - Layout responsivo com scroll interno (evita quebra em telas pequenas).
 * - Ajuste de grid para os botões de seleção.
 * - Melhoria na experiência mobile.
 */
import { ref, onMounted, watch, nextTick } from 'vue';
import { VueSignaturePad } from 'vue-signature-pad';

interface AssinanteOption {
  label: string;
  value: string;
  signed?: boolean;
}

const props = defineProps({
    titulo: { type: String, default: '' },
    termo: { type: String, default: '' },
    enderecoImovel: { type: String, default: '' },
    isSaving: { type: Boolean, default: false },
    assinantesDisponiveis: { 
      type: Array as () => AssinanteOption[], 
      default: () => [] 
    }
});

const emit = defineEmits(['close', 'save']);

const signaturePad = ref<any>(null);
const userInteracted = ref(false);
const tipoSelecionado = ref<string>('');

// Lógica de seleção automática
onMounted(() => {
  autoSelect();
  resizeCanvas(); // Garante que o canvas tenha o tamanho correto ao abrir
});

watch(() => props.assinantesDisponiveis, () => {
  autoSelect();
});

function autoSelect() {
  if (props.assinantesDisponiveis.length === 1) {
    tipoSelecionado.value = props.assinantesDisponiveis[0].value;
  }
}

function resizeCanvas() {
    nextTick(() => {
        if (signaturePad.value) {
            signaturePad.value.resizeCanvas();
        }
    });
}

function startSigning() {
    userInteracted.value = true;
}

function limpar() {
    signaturePad.value.clearSignature();
    userInteracted.value = false;
}

function salvar() {
  if (props.assinantesDisponiveis.length > 0 && !tipoSelecionado.value) {
    alert("Por favor, selecione quem está assinando.");
    return;
  }

  const { isEmpty, data } = signaturePad.value.saveSignature();
  if (isEmpty) {
    alert("Por favor, é necessário assinar antes de confirmar.");
    return;
  }
  
  emit('save', { signatureData: data, tipoAssinante: tipoSelecionado.value });
}
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      
      <div class="modal-header">
          <h3><i class="fas fa-file-signature"></i> {{ titulo || 'Assinatura' }}</h3>
          <button class="btn-close" @click="$emit('close')"><i class="fas fa-times"></i></button>
      </div>
      
      <div class="modal-body">
          
          <div class="form-group" v-if="assinantesDisponiveis.length > 0">
            <label class="label-assinante">Quem está assinando?</label>
            <div class="signer-options-grid">
              <button 
                v-for="op in assinantesDisponiveis" 
                :key="op.value"
                class="signer-btn"
                :class="{ 
                  'selected': tipoSelecionado === op.value,
                  'signed': op.signed
                }"
                @click="tipoSelecionado = op.value"
              >
                <div class="icon-wrapper">
                    <i class="fas fa-check-circle icon-signed" v-if="op.signed"></i>
                    <i class="far fa-user icon-default" v-else></i>
                </div>
                
                <div class="text-wrapper">
                    <span class="btn-label">{{ op.label }}</span>
                    <span class="btn-status signed-text" v-if="op.signed && tipoSelecionado !== op.value">
                        <i class="fas fa-check"></i> Assinado
                    </span>
                    <span class="btn-status redo-text" v-else-if="op.signed && tipoSelecionado === op.value">
                        <i class="fas fa-redo"></i> Refazer
                    </span>
                </div>
                
                <div class="selection-indicator" v-if="tipoSelecionado === op.value">
                    <i class="fas fa-pen"></i>
                </div>
              </button>
            </div>
          </div>

          <div class="termo-container">
            <p class="termo-texto" v-if="termo">{{ termo }}</p>
            <p class="termo-texto" v-else>
                Visita ao imóvel: <strong>{{ enderecoImovel }}</strong>.
            </p>
          </div>

          <div class="signature-section">
            <div class="signature-wrapper">
                <VueSignaturePad 
                    width="100%" 
                    height="100%" 
                    ref="signaturePad" 
                    :options="{ penColor: '#000', backgroundColor: 'rgb(248,250,252)' }" 
                />
                <div class="overlay-hint" v-if="!userInteracted" @click="startSigning">
                    <i class="fas fa-pen-alt"></i> Toque para assinar
                </div>
            </div>
            <div class="signature-tools">
                <button @click="limpar" class="btn-link-danger"><i class="fas fa-eraser"></i> Limpar</button>
            </div>
          </div>
      </div>

      <div class="modal-actions">
        <button @click="$emit('close')" class="btn-secondary">Cancelar</button>
        <button @click="salvar" class="btn-primary" :disabled="isSaving">
            <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
            <span v-else>Confirmar</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay { 
    position: fixed; top:0; left:0; right:0; bottom:0; 
    background: rgba(0,0,0,0.6); z-index: 1050;
    display:flex; justify-content:center; align-items:center; 
    backdrop-filter: blur(3px);
    padding: 10px; /* Espaço nas bordas em mobile */
}

/* Estrutura Flexível do Modal */
.modal-content { 
    background: white; 
    border-radius: 16px; 
    width: 100%; 
    max-width: 500px; /* Largura máxima desktop */
    max-height: 90vh; /* Altura máxima viewport */
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    display: flex; 
    flex-direction: column; /* Cabeçalho e Rodapé fixos, Corpo rola */
    overflow: hidden;
}

.modal-header {
    padding: 1rem 1.25rem; 
    border-bottom: 1px solid #e2e8f0;
    display: flex; justify-content: space-between; align-items: center;
    background-color: #f8fafc;
    flex-shrink: 0;
}
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; font-weight: 700; display: flex; align-items: center; gap: 0.5rem; }
.btn-close { background: none; border: none; cursor: pointer; font-size: 1.25rem; color: #94a3b8; transition: color 0.2s;}
.btn-close:hover { color: #ef4444; }

/* Corpo com Scroll */
.modal-body { 
    padding: 1.25rem; 
    overflow-y: auto; /* Permite scroll se o conteúdo for grande */
    flex: 1; /* Ocupa o espaço restante */
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

/* --- Botões de Seleção --- */
.label-assinante { display: block; font-weight: 700; color: #334155; margin-bottom: 0.75rem; font-size: 0.9rem; text-align: center; }

.signer-options-grid {
  display: flex;
  flex-direction: column; /* Mobile first: empilhado */
  gap: 0.75rem;
}

.signer-btn {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 0.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  position: relative;
  text-align: left;
}

.signer-btn:hover { background-color: #f8fafc; border-color: #cbd5e1; }
.signer-btn.signed { background-color: #f0fdf4; border-color: #86efac; }
.signer-btn.selected { border-color: #3b82f6; background-color: #eff6ff; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3); z-index: 2; }

.icon-wrapper {
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 50%; background: #f1f5f9; flex-shrink: 0;
}
.signer-btn.signed .icon-wrapper { background: #dcfce7; }
.signer-btn.selected .icon-wrapper { background: #dbeafe; }

.icon-signed { color: #16a34a; font-size: 1.2rem; }
.icon-default { color: #94a3b8; font-size: 1.1rem; }
.signer-btn.selected .icon-default { color: #2563eb; }

.text-wrapper { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.btn-label { font-weight: 600; color: #334155; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.signer-btn.signed .btn-label { color: #166534; }
.signer-btn.selected .btn-label { color: #1e40af; }

.btn-status { font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.025em; margin-top: 2px; }
.signed-text { color: #16a34a; }
.redo-text { color: #d97706; }

.selection-indicator { color: #3b82f6; font-size: 0.9rem; }

/* --- Termos --- */
.termo-container {
    background: #f8fafc; padding: 0.75rem; border-radius: 8px; border: 1px solid #f1f5f9;
}
.termo-texto { font-size: 0.85rem; color: #64748b; margin: 0; line-height: 1.5; text-align: justify; }

/* --- Área da Assinatura --- */
.signature-section {
    display: flex; flex-direction: column; gap: 0.5rem; flex: 1; min-height: 180px;
}

.signature-wrapper { 
    border: 2px dashed #cbd5e1; 
    border-radius: 12px; 
    position: relative; 
    overflow: hidden; 
    background: #f8fafc;
    flex: 1; /* Ocupa espaço disponível vertical */
    min-height: 160px; /* Garante altura mínima */
}

.overlay-hint {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.7); color: #64748b; font-weight: 600; font-size: 0.9rem;
    cursor: pointer; gap: 8px;
    transition: opacity 0.2s;
}
.overlay-hint:hover { background: rgba(255,255,255,0.5); color: #3b82f6; }

.signature-tools { display: flex; justify-content: flex-end; }
.btn-link-danger {
    background: none; border: none; color: #ef4444; cursor: pointer;
    font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; gap: 0.25rem;
    padding: 0.25rem 0.5rem; border-radius: 4px;
}
.btn-link-danger:hover { background: #fef2f2; }

/* --- Rodapé --- */
.modal-actions { 
    padding: 1rem 1.25rem; 
    border-top: 1px solid #e2e8f0; 
    display: flex; justify-content: flex-end; gap: 0.75rem; 
    background-color: #f8fafc;
    flex-shrink: 0;
}

.btn-secondary, .btn-primary {
    padding: 0.75rem 1.5rem; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; font-size: 0.9rem;
    transition: all 0.2s;
}
.btn-secondary { background: white; border: 1px solid #e2e8f0; color: #64748b; }
.btn-secondary:hover { background: #f1f5f9; color: #334155; }

.btn-primary { background: #2563eb; color: white; display: flex; align-items: center; gap: 0.5rem; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);}
.btn-primary:hover { background: #1d4ed8; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

/* --- Ajustes Mobile (Telas muito pequenas) --- */
@media (max-width: 480px) {
    .modal-content { 
        height: 100%; /* Ocupa tela toda se necessário */
        max-height: 100%; 
        border-radius: 0; 
    }
    .modal-body { padding: 1rem; }
    .signer-btn { padding: 0.6rem; }
    .btn-label { font-size: 0.85rem; }
    .signature-wrapper { min-height: 200px; /* Mais espaço para o dedo */ }
    .modal-actions { padding: 0.75rem 1rem; }
    .btn-primary, .btn-secondary { flex: 1; justify-content: center; } /* Botões expandidos */
}
</style>
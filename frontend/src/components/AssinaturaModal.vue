<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
          <h3><i class="fas fa-file-signature"></i> {{ titulo || 'Coletar Assinatura' }}</h3>
          <button class="btn-close" @click="$emit('close')"><i class="fas fa-times"></i></button>
      </div>
      
      <div class="modal-body">
          <p class="termo-texto" v-if="termo">
            {{ termo }}
          </p>
          <p class="termo-texto" v-else>
            Declaro que visitei o imóvel situado em:
            <strong>{{ enderecoImovel || 'Endereço não disponível' }}</strong>, 
            apresentado pela imobiliária, nesta data.
          </p>

          <div class="signature-wrapper">
            <VueSignaturePad 
                width="100%" 
                height="200px" 
                ref="signaturePad" 
                :options="{ penColor: '#000', backgroundColor: 'rgb(245,245,245)' }" 
            />
            <div class="overlay-hint" v-if="!userInteracted" @click="startSigning">
                <i class="fas fa-pen-alt"></i> Toque aqui para assinar
            </div>
          </div>
          <button @click="limpar" class="btn-link-danger"><i class="fas fa-eraser"></i> Limpar assinatura</button>
      </div>

      <div class="modal-actions">
        <button @click="$emit('close')" class="btn-secondary">Cancelar</button>
        <button @click="salvar" class="btn-primary" :disabled="isSaving">
            <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
            <span v-else>Confirmar e Salvar</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { VueSignaturePad } from 'vue-signature-pad';

// Adicionadas props 'titulo' e 'termo'
const props = defineProps({
    titulo: { type: String, default: '' },
    termo: { type: String, default: '' },
    enderecoImovel: { type: String, default: '' },
    isSaving: { type: Boolean, default: false }
});

const emit = defineEmits(['close', 'save']);

const signaturePad = ref<any>(null);
const userInteracted = ref(false);

function startSigning() {
    userInteracted.value = true;
}

function limpar() {
    signaturePad.value.clearSignature();
    userInteracted.value = false;
}

function salvar() {
  const { isEmpty, data } = signaturePad.value.saveSignature();
  if (isEmpty) {
    alert("Por favor, é necessário assinar antes de confirmar.");
    return;
  }
  emit('save', data);
}
</script>

<style scoped>
.modal-overlay { 
    position: fixed; top:0; left:0; right:0; bottom:0; 
    background: rgba(0,0,0,0.6); z-index: 1000;
    display:flex; justify-content:center; align-items:center; 
    backdrop-filter: blur(2px);
}
.modal-content { 
    background: white; border-radius: 12px; width: 90%; max-width: 500px; 
    box-shadow: 0 10px 25px rgba(0,0,0,0.2); overflow: hidden;
    display: flex; flex-direction: column;
}
.modal-header {
    padding: 1rem 1.5rem; border-bottom: 1px solid #eee;
    display: flex; justify-content: space-between; align-items: center;
    background-color: #f8f9fa;
}
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #333; }
.btn-close { background: none; border: none; cursor: pointer; font-size: 1.2rem; color: #666; }

.modal-body { padding: 1.5rem; }
.termo-texto { font-size: 0.9rem; color: #555; margin-bottom: 1rem; line-height: 1.5; text-align: justify; }

.signature-wrapper { 
    border: 2px dashed #ccc; border-radius: 8px; position: relative; 
    overflow: hidden; margin-bottom: 0.5rem;
}
.overlay-hint {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.8); color: #666; font-weight: bold;
    cursor: pointer; gap: 8px;
}

.btn-link-danger {
    background: none; border: none; color: #dc3545; cursor: pointer;
    font-size: 0.85rem; text-decoration: underline; padding: 0;
}

.modal-actions { 
    padding: 1rem 1.5rem; border-top: 1px solid #eee; 
    display: flex; justify-content: flex-end; gap: 10px; 
    background-color: #f8f9fa;
}
.btn-secondary, .btn-primary {
    padding: 0.6rem 1.2rem; border-radius: 6px; border: none; cursor: pointer; font-weight: 600;
}
.btn-secondary { background: #e9ecef; color: #333; }
.btn-primary { background: #007bff; color: white; display: flex; align-items: center; gap: 8px;}
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
</style>
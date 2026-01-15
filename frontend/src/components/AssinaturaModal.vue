<template>
  <div class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in" @click.self="fechar">
    <div class="bg-white w-full max-w-[500px] rounded-xl shadow-2xl flex flex-col overflow-hidden animate-scale-in">
      
      <div class="bg-slate-50 px-5 py-4 border-b border-slate-100 flex justify-between items-center">
          <h3 class="text-base font-bold text-slate-800 m-0 flex items-center gap-2">
              <div class="i-fas-file-signature text-blue-600" />
              {{ titulo || 'Coleta de Assinatura' }}
          </h3>
          <button @click="fechar" class="w-8 h-8 flex items-center justify-center rounded-full text-slate-400 hover:bg-slate-200 hover:text-red-500 transition-colors cursor-pointer border-none bg-transparent">
              <div class="i-fas-times text-lg" />
          </button>
      </div>
      
      <div class="p-5 flex flex-col gap-4 bg-white">
          
          <div class="bg-blue-50 border border-blue-100 rounded-lg p-3">
            <p class="text-sm text-blue-800 m-0 text-center font-medium leading-relaxed">
                {{ enderecoImovel || 'Confirmo a realização da visita aos imóveis selecionados.' }}
            </p>
          </div>

          <div class="flex flex-col gap-2">
            <label class="text-xs font-bold text-slate-500 uppercase tracking-wide">Assine abaixo:</label>
            <div class="relative border-2 border-dashed border-slate-300 rounded-xl bg-slate-50 overflow-hidden h-[220px] touch-none transition-colors hover:border-blue-300 group">
                <VueSignaturePad 
                    width="100%" 
                    height="100%" 
                    ref="signaturePad" 
                    :options="{ penColor: '#1e293b', backgroundColor: 'transparent' }" 
                />
                
                <div v-if="!userInteracted" class="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40 group-hover:opacity-60 transition-opacity">
                    <span class="text-slate-400 font-medium flex items-center gap-2">
                        <div class="i-fas-pen-alt" /> Desenhe sua assinatura aqui
                    </span>
                </div>
            </div>
            
            <div class="flex justify-end">
                <button @click="limpar" class="text-xs font-semibold text-red-500 hover:text-red-700 bg-transparent border-none cursor-pointer flex items-center gap-1 py-1">
                    <div class="i-fas-eraser" /> Limpar assinatura
                </button>
            </div>
          </div>
      </div>

      <div class="p-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-3">
        <button @click="fechar" class="px-4 py-2.5 rounded-lg text-sm font-medium text-slate-600 bg-white border border-slate-200 hover:bg-slate-100 transition-colors cursor-pointer">
            Cancelar
        </button>
        <button @click="salvar" class="px-6 py-2.5 rounded-lg text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-sm hover:shadow transition-all cursor-pointer flex items-center gap-2 border-none disabled:opacity-70 disabled:cursor-not-allowed" :disabled="isSaving">
            <div v-if="isSaving" class="i-fas-spinner animate-spin" />
            <div v-else class="i-fas-check" />
            <span>{{ isSaving ? 'Salvando...' : 'Confirmar Assinatura' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { VueSignaturePad } from 'vue-signature-pad';

const props = defineProps({
    titulo: { type: String, default: '' },
    enderecoImovel: { type: String, default: '' },
    isSaving: { type: Boolean, default: false }
});

const emit = defineEmits(['close', 'save']);

const signaturePad = ref<any>(null);
const userInteracted = ref(false);

onMounted(() => {
    resizeCanvas();
});

function resizeCanvas() {
    nextTick(() => {
        if (signaturePad.value) {
            signaturePad.value.resizeCanvas();
            // Adiciona listener para detectar interação
            const canvas = signaturePad.value.$el;
            canvas.addEventListener('mousedown', () => userInteracted.value = true);
            canvas.addEventListener('touchstart', () => userInteracted.value = true);
        }
    });
}

function limpar() {
    signaturePad.value.clearSignature();
    userInteracted.value = false;
}

function fechar() {
    emit('close');
}

function salvar() {
  const { isEmpty, data } = signaturePad.value.saveSignature();
  if (isEmpty) {
    alert("Por favor, faça sua assinatura antes de confirmar.");
    return;
  }
  emit('save', data); // Envia base64 da imagem
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
.animate-scale-in { animation: scaleIn 0.2s ease-out; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
</style>
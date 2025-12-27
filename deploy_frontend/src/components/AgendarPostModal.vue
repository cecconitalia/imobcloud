<template>
  <Transition name="modal-fade">
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal-container">
        
        <header class="modal-header">
          <div class="header-title">
            <i class="fab fa-instagram text-gradient"></i>
            <h2>Nova Publicação</h2>
          </div>
          <button @click="close" class="btn-close" title="Fechar"><i class="fas fa-times"></i></button>
        </header>

        <div class="modal-body">
          <div class="editor-column">
            
            <div class="form-section">
              <div class="section-header">
                <label>Selecionar Mídia (Carrossel)</label>
                <span class="badge-count">{{ selectedImages.length }} selecionadas</span>
              </div>
              
              <div v-if="imovelImagens.length > 0" class="image-grid">
                <div 
                  v-for="img in imovelImagens" 
                  :key="img.id" 
                  class="image-item"
                  :class="{ 'is-selected': selectedImages.includes(img.id) }"
                  @click="toggleImage(img.id)"
                >
                  <img :src="img.imagem" alt="Foto do imóvel">
                  <div class="selection-overlay">
                    <div class="checkbox-circle">
                      <span v-if="selectedImages.includes(img.id)">{{ selectedImages.indexOf(img.id) + 1 }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state"><i class="fas fa-images"></i><p>Sem imagens disponíveis.</p></div>
            </div>

            <div class="form-section">
              <div class="section-header">
                <label>Legenda</label>
                <button 
                  @click="gerarTextoIA" 
                  :disabled="loadingIA || cooldown > 0" 
                  class="btn-ai"
                  :class="{ 'btn-disabled': cooldown > 0 }"
                >
                  <i v-if="loadingIA" class="fas fa-circle-notch fa-spin"></i>
                  <i v-else-if="cooldown > 0" class="fas fa-hourglass-half"></i>
                  <i v-else class="fas fa-magic"></i>
                  
                  <span v-if="loadingIA"> Escrevendo...</span>
                  <span v-else-if="cooldown > 0"> Aguarde {{ cooldown }}s</span>
                  <span v-else> Gerar com IA</span>
                </button>
              </div>
              <div class="textarea-wrapper">
                <textarea v-model="textoPost" rows="5" placeholder="Escreva uma legenda..."></textarea>
                <div class="char-count">{{ textoPost.length }} caracteres</div>
              </div>
            </div>

            <div class="form-section schedule-section">
              <div class="switch-container">
                <label class="switch">
                  <input type="checkbox" v-model="publicarAgora">
                  <span class="slider round"></span>
                </label>
                <span class="switch-label">Publicar Imediatamente</span>
              </div>

              <div v-if="!publicarAgora" class="date-picker-container">
                <label>Data e Hora de Agendamento</label>
                <div class="input-icon-wrapper">
                  <i class="far fa-calendar-alt"></i>
                  <input type="datetime-local" v-model="dataAgendamento">
                </div>
                <p class="help-text">O post será agendado para este horário.</p>
              </div>
            </div>

          </div>

          <div class="preview-column">
            <div class="phone-mockup">
              <div class="phone-notch"></div>
              <div class="instagram-feed">
                <div class="insta-header">
                  <div class="user-info">
                    <div class="avatar-circle"></div>
                    <span class="username">sua_imobiliaria</span>
                  </div>
                  <i class="fas fa-ellipsis-h"></i>
                </div>
                <div class="insta-image-container">
                  <img v-if="previewImage" :src="previewImage" class="insta-main-image">
                  <div v-else class="image-placeholder">
                    <i class="fas fa-camera"></i><span>Selecione uma foto</span>
                  </div>
                  <div v-if="selectedImages.length > 1" class="photo-tag">1/{{ selectedImages.length }}</div>
                </div>
                <div class="insta-actions">
                  <div class="left-actions"><i class="far fa-heart"></i><i class="far fa-comment"></i><i class="far fa-paper-plane"></i></div>
                  <i class="far fa-bookmark"></i>
                </div>
                <div class="insta-caption-area">
                  <div class="caption-text">
                    <span class="username">sua_imobiliaria</span>
                    <span v-if="textoPost" class="caption-content">{{ textoPost }}</span>
                    <span v-else class="caption-placeholder">Sua legenda aparecerá aqui...</span>
                  </div>
                </div>
              </div>
            </div>
            <p class="preview-label">Pré-visualização</p>
          </div>
        </div>

        <footer class="modal-footer">
          <button @click="close" class="btn-cancel">Cancelar</button>
          <button 
            @click="confirmar" 
            :disabled="isSubmitting"
            class="btn-confirm"
            :class="{'btn-instant': publicarAgora}"
          >
            <i v-if="isSubmitting" class="fas fa-circle-notch fa-spin"></i>
            <span v-else>
               <i v-if="publicarAgora" class="fas fa-rocket"></i>
               <i v-else class="fas fa-calendar-check"></i>
               {{ publicarAgora ? 'Publicar Agora' : 'Confirmar Agendamento' }}
            </span>
          </button>
        </footer>

      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import api from '../services/api';

const props = defineProps({ isOpen: Boolean, imovel: Object });
const emit = defineEmits(['close', 'success']);

const textoPost = ref('');
const dataAgendamento = ref('');
const publicarAgora = ref(false);
const imovelImagens = ref<any[]>([]);
const selectedImages = ref<number[]>([]);
const loadingIA = ref(false);
const isSubmitting = ref(false);

// NOVO: Variável para o timer de resfriamento
const cooldown = ref(0);

watch(() => props.imovel, async (newImovel) => {
  if (newImovel && newImovel.id) {
    if (newImovel.imagens && newImovel.imagens.length > 0) {
        imovelImagens.value = newImovel.imagens;
        initSelection();
    } else {
        try {
            const response = await api.get(`/v1/imoveis/${newImovel.id}/`); 
            imovelImagens.value = response.data.imagens || []; 
            initSelection();
        } catch (e) {
            imovelImagens.value = [];
        }
    }
  }
}, { immediate: true });

function initSelection() {
    selectedImages.value = [];
    textoPost.value = '';
    publicarAgora.value = false;
    if (imovelImagens.value.length > 0) {
        selectedImages.value.push(imovelImagens.value[0].id);
    }
}

const previewImage = computed(() => {
  if (selectedImages.value.length === 0) return null;
  const firstId = selectedImages.value[0];
  const img = imovelImagens.value.find(i => i.id === firstId);
  return img ? img.imagem : null;
});

function toggleImage(id: number) {
  const index = selectedImages.value.indexOf(id);
  if (index === -1) selectedImages.value.push(id);
  else selectedImages.value.splice(index, 1);
}

// Inicia o contador regressivo
function startCooldown() {
  cooldown.value = 15; // 15 segundos de espera
  const timer = setInterval(() => {
    cooldown.value--;
    if (cooldown.value <= 0) clearInterval(timer);
  }, 1000);
}

async function gerarTextoIA() {
  if (!props.imovel) return;
  if (cooldown.value > 0) return; // Impede clique se estiver em cooldown

  loadingIA.value = true;
  try {
    const response = await api.post('/v1/publicacoes/gerar-texto/', { imovel_id: props.imovel.id });
    textoPost.value = response.data.texto_sugerido;
  } catch (error: any) {
    // Se der erro 429, avisamos especificamente
    if (error.response && error.response.status === 429) {
       alert("Muitas tentativas! O sistema entrou em pausa automática.");
       cooldown.value = 30; // Penalidade maior se já deu erro
    } else {
       alert("Erro na IA: " + (error.response?.data?.error || "Verifique o servidor."));
    }
  } finally {
    loadingIA.value = false;
    startCooldown(); // Sempre inicia o cooldown após tentar
  }
}

async function confirmar() {
  if (selectedImages.value.length === 0) return alert("Selecione pelo menos uma imagem.");
  if (!publicarAgora.value && !dataAgendamento.value) return alert("Selecione uma data para agendar.");

  isSubmitting.value = true;
  
  let dataParaEnvio = null;

  if (!publicarAgora.value) {
      try {
          const [datePart, timePart] = dataAgendamento.value.split('T');
          dataParaEnvio = `${datePart}T${timePart}:00`; 
      } catch (e) {
          isSubmitting.value = false;
          return alert("Erro interno na formatação da data.");
      }
  }

  try {
    await api.post('/v1/publicacoes/agendar/', {
      imovel_id: props.imovel?.id,
      texto: textoPost.value,
      imagens_ids: selectedImages.value,
      publicar_agora: publicarAgora.value,
      data_agendamento: publicarAgora.value ? null : dataParaEnvio
    });
    
    alert(publicarAgora.value ? "Publicação iniciada!" : "Agendado com sucesso!");
    emit('success');
    close();
  } catch (error: any) {
    alert("Erro: " + (error.response?.data?.error || error.message));
  } finally {
    isSubmitting.value = false;
  }
}

function close() { emit('close'); }
</script>

<style scoped>
/* Mesmos estilos anteriores, com adição do botão desabilitado */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.65); backdrop-filter: blur(4px); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 1rem; }
.modal-container { background: #fff; width: 100%; max-width: 1000px; height: 90vh; max-height: 800px; border-radius: 16px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); display: flex; flex-direction: column; overflow: hidden; }
.modal-header { padding: 1.25rem 2rem; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; background: #fff; }
.header-title { display: flex; align-items: center; gap: 0.75rem; }
.header-title h2 { font-size: 1.25rem; font-weight: 700; color: #1a1a1a; margin: 0; }
.text-gradient { background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.5rem; }
.btn-close { background: none; border: none; font-size: 1.25rem; color: #8c8c8c; cursor: pointer; }
.modal-body { flex: 1; display: flex; overflow: hidden; }
.editor-column { flex: 1.2; padding: 2rem; overflow-y: auto; border-right: 1px solid #f0f0f0; display: flex; flex-direction: column; gap: 2rem; }
.preview-column { flex: 1; background: #fafafa; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; }
.form-section { display: flex; flex-direction: column; gap: 0.75rem; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.section-header label, .form-section label { font-weight: 600; color: #333; }
.badge-count { font-size: 0.8rem; background: #f3f4f6; padding: 0.2rem 0.6rem; border-radius: 12px; color: #666; }
.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 0.75rem; max-height: 220px; overflow-y: auto; padding-right: 5px; }
.image-item { position: relative; aspect-ratio: 1; border-radius: 8px; overflow: hidden; cursor: pointer; border: 2px solid transparent; transition: all 0.2s; }
.image-item img { width: 100%; height: 100%; object-fit: cover; }
.image-item.is-selected { border-color: #0095f6; }
.selection-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.1); display: flex; align-items: flex-start; justify-content: flex-end; padding: 6px; }
.checkbox-circle { width: 22px; height: 22px; border-radius: 50%; border: 2px solid #fff; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75rem; font-weight: 700; }
.image-item.is-selected .checkbox-circle { background: #0095f6; border-color: #fff; }

/* Estilo do botão IA */
.btn-ai { font-size: 0.8rem; color: #833ab4; background: #fdf2ff; border: 1px solid #f3e5f5; padding: 0.4rem 0.8rem; border-radius: 20px; cursor: pointer; display: flex; align-items: center; gap: 6px; font-weight: 600; transition: all 0.2s; }
.btn-ai:hover:not(:disabled) { background: #f3e5f5; transform: scale(1.02); }
.btn-ai:disabled { opacity: 0.7; cursor: not-allowed; background: #f5f5f5; color: #999; border-color: #eee; }

textarea { width: 100%; padding: 1rem; border: 1px solid #e0e0e0; border-radius: 8px; font-family: inherit; font-size: 0.95rem; resize: vertical; background: #fafafa; }
.char-count { text-align: right; font-size: 0.75rem; color: #999; margin-top: 4px; }
.input-icon-wrapper { position: relative; display: flex; align-items: center; }
.input-icon-wrapper i { position: absolute; left: 12px; color: #888; }
.input-icon-wrapper input { width: 100%; padding: 0.75rem 0.75rem 0.75rem 2.5rem; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa; }
.help-text { font-size: 0.8rem; color: #888; margin-top: 0.2rem; }
.modal-footer { padding: 1.5rem 2rem; border-top: 1px solid #f0f0f0; display: flex; justify-content: flex-end; gap: 1rem; background: #fff; }
.btn-cancel { padding: 0.6rem 1.5rem; border: 1px solid #d9d9d9; background: #fff; color: #555; border-radius: 6px; font-weight: 600; cursor: pointer; }
.btn-confirm { padding: 0.6rem 1.5rem; border: none; background: #0095f6; color: #fff; border-radius: 6px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }
.schedule-section { background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; }
.switch-container { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
.switch-label { font-weight: 600; color: #1e293b; }
.switch { position: relative; display: inline-block; width: 44px; height: 24px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: #10b981; }
input:checked + .slider:before { transform: translateX(20px); }
.btn-instant { background: #10b981; }
.btn-instant:hover { background: #059669; }
.phone-mockup { background: #fff; width: 320px; border-radius: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); padding: 12px; border: 8px solid #333; position: relative; }
.instagram-feed { background: #fff; height: 100%; border-radius: 20px; overflow: hidden; border: 1px solid #dbdbdb; }
.insta-header { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #efefef; }
.user-info { display: flex; align-items: center; gap: 8px; }
.avatar-circle { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(45deg, #f09433, #e6683c, #dc2743); }
.username { font-size: 0.85rem; font-weight: 600; color: #262626; }
.insta-image-container { width: 100%; aspect-ratio: 1; background: #efefef; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.insta-main-image { width: 100%; height: 100%; object-fit: cover; }
.photo-tag { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.6); color: #fff; font-size: 0.7rem; padding: 3px 8px; border-radius: 10px; }
.insta-actions { padding: 10px; display: flex; justify-content: space-between; font-size: 1.3rem; color: #262626; }
.left-actions { display: flex; gap: 14px; }
.insta-caption-area { padding: 0 10px 15px 10px; font-size: 0.85rem; }
.caption-content { margin-left: 6px; color: #262626; white-space: pre-wrap; }
.preview-label { margin-top: 1rem; font-size: 0.85rem; color: #999; font-weight: 500; }
@media (max-width: 900px) {
  .modal-body { flex-direction: column; overflow-y: auto; }
  .editor-column { border-right: none; border-bottom: 1px solid #f0f0f0; flex: none; }
  .preview-column { padding: 2rem 1rem; flex: none; }
  .modal-container { height: auto; max-height: 95vh; }
}
</style>
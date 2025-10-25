<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Estúdio de Publicação com IA</h3>
        <button @click="closeModal" class="close-button">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="isLoading" class="loading-state">
          <p>A nossa IA está a criar uma sugestão incrível para si. Aguarde...</p>
        </div>
        
        <div v-if="error" class="error-state">
          <p>Ocorreu um erro: {{ error }}</p>
          <button @click="gerarTexto" class="btn-secondary">Tentar Novamente</button>
        </div>

        <div v-if="!isLoading && !error" class="content-state">
          <div class="texto-section">
            <label for="texto-publicacao">Texto da Publicação:</label>
            <textarea id="texto-publicacao" v-model="textoEditavel" rows="12"></textarea>
            <button @click="gerarTexto" class="btn-info-outline regenerate-button">
              Gerar Nova Sugestão
            </button>
          </div>
          
          <div class="acoes-section">
            <h4>1. Selecione as Plataformas</h4>
            <div class="plataformas-section">
                <label><input type="checkbox" v-model="plataformas.facebook"> Facebook</label>
                <label><input type="checkbox" v-model="plataformas.instagram"> Instagram</label>
            </div>

            <hr>

            <h4>2. Ação Imediata</h4>
            <button @click="publicarAgora" class="btn-success" :disabled="isPublicando || isAgendando">
              {{ isPublicando ? 'A Publicar...' : 'Publicar Agora' }}
            </button>
            <p v-if="statusPublicacao" class="status-message">{{ statusPublicacao }}</p>

            <hr>

            <h4>3. Agendar Publicação</h4>
            <div class="agendamento-section">
              <label for="data_agendamento">Escolha a data e hora:</label>
              <input type="datetime-local" id="data_agendamento" v-model="dataAgendamento">
              <button @click="agendarPublicacao" class="btn-primary" :disabled="isAgendando || isPublicando || !dataAgendamento">
                {{ isAgendando ? 'A Agendar...' : 'Agendar' }}
              </button>
              <p v-if="statusAgendamento" class="status-message">{{ statusAgendamento }}</p>
            </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import apiClient from '@/services/api';

const props = defineProps({
  imovelId: {
    type: Number,
    required: true,
  }
});

const emit = defineEmits(['close']);

// Variáveis de estado existentes
const isLoading = ref(true);
const error = ref<string | null>(null);
const textoGerado = ref('');
const textoEditavel = ref('');
const plataformas = ref({
    facebook: false,
    instagram: false
});

// Variáveis de estado para Publicação
const isPublicando = ref(false);
const statusPublicacao = ref('');

// --- NOVAS VARIÁVEIS DE ESTADO PARA AGENDAMENTO ---
const isAgendando = ref(false);
const statusAgendamento = ref('');
const dataAgendamento = ref('');


watch(textoGerado, (newVal) => {
  textoEditavel.value = newVal;
});

async function gerarTexto() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.post('/v1/publicacoes/gerar-texto/', {
      imovel_id: props.imovelId
    });
    textoGerado.value = response.data.texto_sugerido;
  } catch (err: any) {
    error.value = err.response?.data?.error || "Ocorreu um erro desconhecido ao gerar o texto.";
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function publicarAgora() {
    isPublicando.value = true;
    statusPublicacao.value = '';
    const plataformasSelecionadas = Object.keys(plataformas.value).filter(p => (plataformas.value as any)[p]);

    if (plataformasSelecionadas.length === 0) {
        statusPublicacao.value = 'Erro: Selecione pelo menos uma plataforma.';
        isPublicando.value = false;
        setTimeout(() => { statusPublicacao.value = ''; }, 4000);
        return;
    }

    try {
        const response = await apiClient.post('/v1/publicacoes/publicar/', {
            imovel_id: props.imovelId,
            texto: textoEditavel.value,
            plataformas: plataformasSelecionadas
        });
        statusPublicacao.value = 'Publicado com sucesso!';
        setTimeout(() => closeModal(), 2000); // Fecha o modal após sucesso
    } catch (err: any) {
        statusPublicacao.value = `Erro ao publicar: ${err.response?.data?.error || 'Erro desconhecido'}`;
    } finally {
        isPublicando.value = false;
    }
}

// --- NOVA FUNÇÃO PARA AGENDAR ---
async function agendarPublicacao() {
    isAgendando.value = true;
    statusAgendamento.value = '';
    const plataformasSelecionadas = Object.keys(plataformas.value).filter(p => (plataformas.value as any)[p]);

    if (plataformasSelecionadas.length === 0) {
        statusAgendamento.value = 'Erro: Selecione pelo menos uma plataforma.';
        isAgendando.value = false;
        setTimeout(() => { statusAgendamento.value = ''; }, 4000);
        return;
    }
    if (!dataAgendamento.value) {
        statusAgendamento.value = 'Erro: Por favor, selecione uma data e hora.';
        isAgendando.value = false;
        setTimeout(() => { statusAgendamento.value = ''; }, 4000);
        return;
    }

    try {
        const response = await apiClient.post('/v1/publicacoes/agendar/', {
            imovel_id: props.imovelId,
            texto: textoEditavel.value,
            plataformas: plataformasSelecionadas,
            data_agendamento: dataAgendamento.value
        });
        statusAgendamento.value = 'Agendado com sucesso!';
        setTimeout(() => closeModal(), 2000); // Fecha o modal após sucesso
    } catch (err: any) {
        statusAgendamento.value = `Erro ao agendar: ${err.response?.data?.error || 'Erro desconhecido'}`;
    } finally {
        isAgendando.value = false;
    }
}


function closeModal() {
  emit('close');
}

onMounted(() => {
  gerarTexto();
});
</script>

<style scoped>
/* Estilos gerais do modal (sem alterações) */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.7); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-container { background-color: white; border-radius: 8px; width: 90%; max-width: 800px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); display: flex; flex-direction: column; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; color: #333; }
.close-button { background: none; border: none; font-size: 2rem; cursor: pointer; color: #aaa; }
.modal-body { padding: 1.5rem; min-height: 300px; }
.loading-state, .error-state { text-align: center; padding: 2rem; color: #555; }
.content-state { display: flex; gap: 2rem; }

/* Secção de texto (sem alterações) */
.texto-section { flex: 2; }
.texto-section label { display: block; margin-bottom: 0.5rem; font-weight: bold; color: #444; }
.texto-section textarea { width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; font-size: 1rem; }
.regenerate-button { margin-top: 1rem; }

/* Secção de Ações (com novas adições) */
.acoes-section {
  flex: 1;
  border-left: 1px solid #eee;
  padding-left: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.acoes-section h4 {
    margin: 0 0 0.5rem 0;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
}
hr {
    border: none;
    border-top: 1px solid #eee;
    width: 100%;
}
.plataformas-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.btn-success, .btn-primary, .btn-secondary, .btn-info-outline {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    cursor: pointer;
    border: none;
    border-radius: 4px;
}
.btn-success:disabled, .btn-primary:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
}
.status-message {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    text-align: center;
}
.agendamento-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.agendamento-section input[type="datetime-local"] {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
}
</style>
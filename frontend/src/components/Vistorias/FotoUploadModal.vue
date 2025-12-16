<template>
  <div class="modal fade" :class="{ 'show': show }" style="display: block;" tabindex="-1" v-if="show">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Upload de Fotos para Item #{{ itemId }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <p>Selecione uma ou mais fotos para anexar a este item de vistoria.</p>
          <form @submit.prevent="handleUpload">
            
            <div class="mb-3">
              <label for="photoUpload" class="form-label">Arquivos de Imagem (JPG, PNG)</label>
              <input type="file" id="photoUpload" class="form-control" ref="fileInput" multiple accept="image/*" required>
              <div class="form-text">Você pode selecionar várias fotos ao mesmo tempo.</div>
            </div>
            
            <div class="d-flex justify-content-end">
              <button type="button" class="btn btn-secondary me-2" @click="$emit('close')">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="uploading">
                <i class="fas fa-spinner fa-spin me-1" v-if="uploading"></i>
                <i class="fas fa-upload me-1" v-else></i>
                Carregar Fotos ({{ fileCount }})
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop fade show" v-if="show"></div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed } from 'vue';
import api from '@/services/api';

export default defineComponent({
  name: 'FotoUploadModal',
  props: {
    show: { type: Boolean, required: true },
    itemId: { type: Number, default: null }, // ID do Item de Vistoria
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const fileInput = ref<HTMLInputElement | null>(null);
    const uploading = ref(false);
    const fileCount = ref(0);

    // Monitora o input de arquivo para atualizar a contagem
    watch(fileInput, (input) => {
        if (input) {
            input.onchange = () => {
                fileCount.value = input.files ? input.files.length : 0;
            };
        }
    });

    const handleUpload = async () => {
      if (!props.itemId || !fileInput.value || !fileInput.value.files || fileInput.value.files.length === 0) {
        alert('Selecione pelo menos um arquivo.');
        return;
      }
      
      uploading.value = true;
      const formData = new FormData();
      
      // Adiciona o ID do Item
      formData.append('item', props.itemId.toString());
      
      // Adiciona todos os arquivos de foto ao array 'fotos'
      for (let i = 0; i < fileInput.value.files.length; i++) {
        formData.append('fotos', fileInput.value.files[i]);
      }

      try {
        // Usa o endpoint de upload em lote que definimos em app_vistorias/views.py
        await api.post('/vistorias/fotos/upload-lote/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        
        alert(`${fileInput.value.files.length} fotos carregadas com sucesso!`);
        
        // Limpa o input
        fileInput.value.value = ''; 
        fileCount.value = 0;

        emit('refresh'); // Recarrega os detalhes da Vistoria
        emit('close');
      } catch (error) {
        console.error('Erro ao fazer upload das fotos:', error);
        alert('Erro ao carregar as fotos. Verifique o tamanho dos arquivos.');
      } finally {
        uploading.value = false;
      }
    };
    
    // Reseta a contagem quando o modal é fechado/aberto
    watch(() => props.show, (newVal) => {
        if (newVal) {
            fileCount.value = 0;
        }
    });

    return {
      fileInput,
      uploading,
      fileCount,
      handleUpload,
    };
  },
});
</script>

<style scoped>
.modal { background-color: rgba(0, 0, 0, 0.5); }
</style>
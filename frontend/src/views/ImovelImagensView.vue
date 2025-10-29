<template>
  <div class="image-manager">
    <div class="upload-area">
      <input type="file" ref="fileInput" multiple @change="handleFileChange" style="display: none;" accept="image/*" />
      <div class="upload-prompt" @click="openFilePicker">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Clique para selecionar as imagens</p>
      </div>
      <button @click="uploadFiles" :disabled="!uploadQueue.length || isUploading" class="btn-upload">
        {{ isUploading ? 'A Carregar...' : `Fazer Upload (${uploadQueue.length})` }}
      </button>
    </div>

    <div v-if="isLoading" class="loading-message">
      <p>A carregar imagens...</p>
    </div>
    
    <template v-else>
      <div v-if="images.length > 0">
        <div class="info-drag">
          <i class="fas fa-info-circle"></i>
          Arraste as imagens para reordenar. A primeira imagem é sempre a principal.
        </div>
        <draggable v-model="images" @end="saveOrder" item-key="id" class="image-preview-grid">
          <template #item="{ element: image }">
            <div class="image-container" :class="{ 'is-principal': image.ordem === 0 }">
              <img :src="image.imagem" :alt="`Imagem ${image.ordem}`" class="preview-image"/>
              <div class="image-actions">
                <button @click.stop="deleteImage(image.id)" class="delete-btn" title="Excluir Imagem"><i class="fas fa-trash"></i></button>
              </div>
              <div v-if="image.ordem === 0" class="principal-badge">Principal</div>
            </div>
          </template>
        </draggable>
      </div>
      <div v-else class="no-images-message">
        <p>Nenhuma imagem cadastrada para este imóvel.</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import apiClient from '@/services/api';
import draggable from 'vuedraggable'; // Importa o componente draggable
import '@fortawesome/fontawesome-free/css/all.css'; // Importa FontAwesome

const props = defineProps({
  imovelId: {
    type: [String, Number],
    required: true
  }
});

const fileInput = ref<HTMLInputElement | null>(null);
const images = ref<any[]>([]);
const uploadQueue = ref<File[]>([]);
const isLoading = ref(true);
const isUploading = ref(false);

function openFilePicker() {
  fileInput.value?.click();
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    uploadQueue.value.push(...Array.from(target.files));
  }
}

async function uploadFiles() {
  if (!uploadQueue.value.length || isUploading.value) return;

  isUploading.value = true;
  const formData = new FormData();
  formData.append('imovel', props.imovelId.toString());
  
  uploadQueue.value.forEach(file => {
    formData.append('imagem', file);
  });

  try {
    // CORREÇÃO: O endpoint correto (baseado nos seus urls.py) é /imoveis/imagens/
    await apiClient.post('/v1/imoveis/imagens/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    uploadQueue.value = [];
    await fetchImages(); // Recarrega a lista após o sucesso
  } catch (error: any) {
    console.error("Erro ao fazer upload:", error.response?.data || error);
    alert(`Falha no upload. Erro: ${JSON.stringify(error.response?.data || error.message)}`);
  } finally {
    isUploading.value = false;
  }
}

async function fetchImages() {
  if (!props.imovelId) {
    isLoading.value = false;
    return;
  }
  isLoading.value = true;
  try {
    const response = await apiClient.get(`/v1/imoveis/${props.imovelId}/`);
    images.value = (response.data.imagens || []).sort((a: any, b: any) => a.ordem - b.ordem);
  } catch (error) {
    console.error("Erro ao carregar imagens:", error);
  } finally {
    isLoading.value = false;
  }
}

async function deleteImage(imageId: number) {
  if (confirm('Tem a certeza que deseja excluir esta imagem?')) {
    try {
      // CORREÇÃO: O endpoint correto (baseado nos seus urls.py) é /imoveis/imagens/
      await apiClient.delete(`/v1/imoveis/imagens/${imageId}/`);
      await fetchImages(); // Recarrega para refletir a exclusão e a nova imagem principal
    } catch (error) {
      console.error("Erro ao excluir imagem:", error);
      alert('Não foi possível excluir a imagem.');
    }
  }
}

async function saveOrder() {
  images.value.forEach((img, index) => {
    img.ordem = index;
    img.principal = index === 0;
  });

  const orderedIds = images.value.map(img => img.id);
  
  try {
    // CORREÇÃO: O endpoint correto (baseado nos seus urls.py) é /imoveis/imagens/reordenar/
    await apiClient.post(`/v1/imoveis/imagens/reordenar/`, { 
        ordem_ids: orderedIds,
        imovel_id: props.imovelId // Adiciona o imovel_id, como esperado pela view
    });
  } catch (error) {
    console.error("Erro ao salvar a nova ordem:", error);
    alert('Não foi possível salvar a nova ordem das imagens. A página será recarregada.');
    await fetchImages(); // Recarrega para reverter a mudança visual em caso de erro
  }
}

watch(() => props.imovelId, (newId) => {
  if (newId) fetchImages();
}, { immediate: true });

onMounted(() => {
    if (!props.imovelId) isLoading.value = false;
});
</script>

<style scoped>
.image-container {
    cursor: grab;
}
.image-manager { display: flex; flex-direction: column; gap: 1.5rem; }
.upload-area { display: flex; flex-direction: column; gap: 1rem; }
.upload-prompt { border: 2px dashed #ccc; border-radius: 8px; padding: 2rem; text-align: center; cursor: pointer; background-color: #fafafa; }
.upload-prompt i { font-size: 2rem; color: #6c757d; }
.btn-upload { background-color: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.btn-upload:disabled { background-color: #ccc; }
.info-drag { text-align: center; margin-bottom: 0.5rem; color: #6c757d; font-size: 0.9rem; }
.image-preview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
.image-container { position: relative; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border: 3px solid transparent; }
.image-container.is-principal { border-color: #007bff; }
.preview-image { width: 100%; height: 120px; object-fit: cover; display: block; }
.image-actions { position: absolute; top: 0; right: 0; background-color: rgba(0, 0, 0, 0.6); padding: 0.25rem; }
.delete-btn { background: none; border: none; color: white; cursor: pointer; font-size: 1rem; }
.principal-badge { position: absolute; bottom: 5px; left: 5px; background-color: #007bff; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
.no-images-message, .loading-message { text-align: center; color: #6c757d; padding: 2rem; }
</style>
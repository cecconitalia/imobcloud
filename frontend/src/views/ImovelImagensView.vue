<template>
  <div class="image-manager">
    <div class="upload-area">
      <file-upload
        ref="upload"
        v-model="files"
        :multiple="true"
        :drop="true"
        @input-file="handleFileChange"
        class="file-uploader">
        <div class="upload-prompt">
          <i class="fas fa-cloud-upload-alt"></i>
          <p>Arraste e solte as imagens aqui ou clique para selecionar</p>
        </div>
      </file-upload>
    </div>

    <div v-if="isLoading" class="loading-message">
      <p>A carregar imagens...</p>
    </div>
    
    <template v-else>
      <div v-if="images.length > 0">
        <div class="info-drag">
          <i class="fas fa-arrows-alt"></i>
          Arraste as imagens para reordenar. A primeira imagem é sempre a principal.
        </div>
        <draggable
          v-model="images"
          @end="saveOrder"
          item-key="id"
          class="image-preview-grid"
          :animation="200"
          ghost-class="ghost-image">
          <template #item="{ element: image }">
            <div class="image-container" :class="{ 'is-principal': image.principal }">
              <img :src="image.imagem" :alt="image.imagem" class="preview-image"/>
              <div class="image-actions">
                <button @click="setAsPrincipal(image)" class="principal-btn" title="Definir como Principal"><i class="fas fa-star"></i></button>
                <button @click="deleteImage(image.id)" class="delete-btn" title="Excluir Imagem"><i class="fas fa-trash"></i></button>
              </div>
              <div v-if="image.principal" class="principal-badge">Principal</div>
            </div>
          </template>
        </draggable>
      </div>
      <div v-else class="no-images-message">
        <p>Nenhuma imagem cadastrada para este imóvel.</p>
      </div>
    </template>

    <div v-if="uploadQueue.length > 0" class="upload-queue">
      <h4>Fila de Uploads</h4>
      <ul>
        <li v-for="file in uploadQueue" :key="file.id">
          <span>{{ file.name }}</span>
          <span v-if="file.error" class="error-text">{{ file.error }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import apiClient from '@/services/api';
import FileUpload from 'vue-upload-component';
import { VueDraggableNext as draggable } from 'vue-draggable-next';

const props = defineProps({
  imovelId: {
    type: [String, Number],
    required: true
  }
});

const files = ref([]);
const images = ref<any[]>([]);
const uploadQueue = ref<any[]>([]);
const isLoading = ref(true);

async function fetchImages() {
  if (!props.imovelId) {
    isLoading.value = false;
    images.value = [];
    return;
  }
  isLoading.value = true;
  try {
    const response = await apiClient.get(`/v1/imoveis/imoveis/${props.imovelId}/`);
    images.value = response.data.imagens || [];
  } catch (error) {
    console.error("Erro ao carregar imagens:", error);
    images.value = [];
  } finally {
    isLoading.value = false;
  }
}

async function saveOrder() {
  const orderedIds = images.value.map(img => img.id);
  try {
    await apiClient.post(`/v1/imoveis/imagens/reordenar/`, { ordem_ids: orderedIds });
    await fetchImages();
  } catch (error) {
    console.error("Erro ao salvar a nova ordem:", error);
    alert('Não foi possível salvar a nova ordem das imagens.');
  }
}

async function setAsPrincipal(imageToMove: any) {
  const imageIndex = images.value.findIndex(img => img.id === imageToMove.id);
  if (imageIndex > 0) {
    images.value.splice(imageIndex, 1);
    images.value.unshift(imageToMove);
    await saveOrder();
  }
}

async function handleUpload(file: any) {
  const formData = new FormData();
  formData.append('imagem', file.file);
  formData.append('imovel', props.imovelId.toString());

  try {
    await apiClient.post('/v1/imoveis/imagens/', formData);
    await fetchImages();
  } catch (error: any) {
    const fileInQueue = uploadQueue.value.find(f => f.id === file.id);
    if(fileInQueue) fileInQueue.error = error.response?.data?.detail || 'Falha no upload.';
  } finally {
    setTimeout(() => {
       uploadQueue.value = uploadQueue.value.filter(f => f.id !== file.id);
    }, 5000);
  }
}

function handleFileChange(newFile: any, oldFile: any) {
  if (newFile && !oldFile) {
    const fileToUpload = { id: newFile.id, name: newFile.name, file: newFile.file, error: null };
    uploadQueue.value.push(fileToUpload);
    handleUpload(fileToUpload);
  }
}

async function deleteImage(imageId: number) {
    if (confirm('Tem a certeza que deseja excluir esta imagem?')) {
        try {
            await apiClient.delete(`/v1/imoveis/imagens/${imageId}/`);
            await fetchImages();
        } catch (error) {
            console.error("Erro ao excluir imagem:", error);
            alert('Não foi possível excluir a imagem.');
        }
    }
}

watch(() => props.imovelId, (newId) => {
  if (newId) {
    fetchImages();
  }
}, { immediate: true });

onMounted(() => {
  if (props.imovelId) {
    fetchImages();
  } else {
    isLoading.value = false;
  }
});

</script>

<style scoped>
.image-manager {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.file-uploader {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  background-color: #fafafa;
  transition: all 0.2s ease-in-out;
}
.file-uploader:hover, .file-uploader.drop-active {
  border-color: #007bff;
  background-color: #f0f8ff;
}
.upload-prompt i {
  font-size: 2.5rem;
  color: #007bff;
}
.upload-prompt p {
  margin-top: 1rem;
  font-weight: 500;
  color: #555;
}
.info-drag {
  text-align: center;
  margin-bottom: 0.5rem;
  color: #6c757d;
  font-size: 0.9rem;
}
.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}
.image-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: grab;
  border: 3px solid transparent;
}
.image-container:active {
  cursor: grabbing;
}
.image-container.is-principal {
  border-color: #007bff;
}
.preview-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}
.image-actions {
  position: absolute;
  top: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  gap: 0.25rem;
  padding: 0.25rem;
  border-bottom-left-radius: 8px;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}
.image-container:hover .image-actions {
  opacity: 1;
}
.image-actions button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
}
.principal-badge {
    position: absolute;
    bottom: 5px;
    left: 5px;
    background-color: #007bff;
    color: white;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
}
.ghost-image {
  opacity: 0.5;
  background: #c8ebfb;
  border: 1px dashed #007bff;
}
.upload-queue ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.upload-queue li {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  background-color: #f7f7f7;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}
.upload-queue li span {
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9rem;
}
.error-text {
  color: #dc3545;
  font-weight: bold;
}
.no-images-message, .loading-message {
  text-align: center;
  color: #6c757d;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>
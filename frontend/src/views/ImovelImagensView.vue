<template>
  <div class="image-manager">
    <div class="upload-area">
      <input type="file" ref="fileInput" multiple @change="handleFileChange" style="display: none;" />
      <div class="upload-prompt" @click="openFilePicker">
        <i class="fas fa-cloud-upload-alt"></i>
        <p>Clique para selecionar as imagens</p>
      </div>
      <button @click="uploadFiles" :disabled="!uploadQueue.length || isUploading" class="btn-upload">
        {{ isUploading ? 'A Carregar...' : 'Fazer Upload' }} ({{ uploadQueue.length }})
      </button>
    </div>

    <div v-if="isLoading" class="loading-message">
      <p>A carregar imagens...</p>
    </div>
    
    <template v-else>
      <div v-if="images.length > 0">
        <div class="info-drag">
          <i class="fas fa-info-circle"></i>
          Utilize os botões para reordenar, definir a imagem principal e excluir.
        </div>
        <div class="image-preview-grid">
          <div v-for="(image, index) in images" :key="image.id" class="image-container" :class="{ 'is-principal': image.principal }">
            <img :src="image.imagem" :alt="image.imagem" class="preview-image"/>
            <div class="image-actions">
              <button @click.stop="setAsPrincipal(image)" class="principal-btn" title="Definir como Principal" :disabled="image.principal"><i class="fas fa-star"></i></button>
              <button @click.stop="moveImageUp(index)" class="order-btn" title="Mover para cima" :disabled="index === 0"><i class="fas fa-arrow-up"></i></button>
              <button @click.stop="moveImageDown(index)" class="order-btn" title="Mover para baixo" :disabled="index === images.length - 1"><i class="fas fa-arrow-down"></i></button>
              <button @click.stop="deleteImage(image.id)" class="delete-btn" title="Excluir Imagem"><i class="fas fa-trash"></i></button>
            </div>
            <div v-if="image.principal" class="principal-badge">Principal</div>
          </div>
        </div>
      </div>
      <div v-else class="no-images-message">
        <p>Nenhuma imagem cadastrada para este imóvel.</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import apiClient from '@/services/api';

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
    uploadQueue.value = Array.from(target.files);
  }
}

async function uploadFiles() {
  if (!uploadQueue.value.length || isUploading.value) return;

  isUploading.value = true;
  const uploadPromises = uploadQueue.value.map(file => {
    const formData = new FormData();
    formData.append('imagem', file);
    formData.append('imovel', props.imovelId.toString());
    
    // CORREÇÃO APLICADA: Apontando para o novo endpoint de imagens.
    return apiClient.post('/v1/imagens-imovel/', formData)
      .then(() => {
        console.log(`Sucesso no upload do arquivo: ${file.name}`);
      })
      .catch((error: any) => {
        console.error(`Erro ao fazer upload de ${file.name}:`, error.response?.data || error);
        alert(`Falha no upload do arquivo ${file.name}.`);
      });
  });

  await Promise.all(uploadPromises);

  uploadQueue.value = [];
  isUploading.value = false;
  await fetchImages();
}

async function fetchImages() {
  if (!props.imovelId) {
    isLoading.value = false;
    images.value = [];
    return;
  }
  isLoading.value = true;
  try {
    const response = await apiClient.get(`/v1/imoveis/${props.imovelId}/`);
    images.value = (response.data.imagens || []).filter((img: any) => img.imagem).sort((a: any, b: any) => a.ordem - b.ordem);
  } catch (error) {
    console.error("Erro ao carregar imagens:", error);
    images.value = [];
  } finally {
    isLoading.value = false;
  }
}

async function moveImageUp(index: number) {
  if (index > 0) {
    const imageToMove = images.value[index];
    images.value.splice(index, 1);
    images.value.splice(index - 1, 0, imageToMove);
    await saveOrder();
  }
}

async function moveImageDown(index: number) {
  if (index < images.value.length - 1) {
    const imageToMove = images.value[index];
    images.value.splice(index, 1);
    images.value.splice(index + 1, 0, imageToMove);
    await saveOrder();
  }
}

async function setAsPrincipal(imageToMove: any) {
  const imageIndex = images.value.findIndex(img => img.id === imageToMove.id);
  if (imageIndex > -1) {
    images.value.forEach(img => img.principal = false);
    
    const [movedImage] = images.value.splice(imageIndex, 1);
    movedImage.principal = true;
    images.value.unshift(movedImage);

    await saveOrder();
  }
}

async function deleteImage(imageId: number) {
  if (confirm('Tem a certeza que deseja excluir esta imagem?')) {
    try {
      const index = images.value.findIndex(img => img.id === imageId);
      if (index > -1) {
        const wasPrincipal = images.value[index].principal;
        
        images.value.splice(index, 1);
        
        if (wasPrincipal && images.value.length > 0) {
          images.value[0].principal = true;
        }

        // CORREÇÃO APLICADA: Apontando para o novo endpoint de imagens.
        await apiClient.delete(`/v1/imagens-imovel/${imageId}/`);
        console.log(`Imagem ${imageId} excluída com sucesso.`);
        
        if (wasPrincipal && images.value.length > 0) {
          await saveOrder();
        }
      }
    } catch (error) {
      console.error("Erro ao excluir imagem:", error);
      alert('Não foi possível excluir a imagem.');
      await fetchImages();
    }
  }
}

async function saveOrder() {
  const orderedIds = images.value.map(img => img.id);
  try {
    // CORREÇÃO APLICADA: Apontando para o novo endpoint de imagens.
    await apiClient.post(`/v1/imagens-imovel/reordenar/`, { ordem_ids: orderedIds });
    console.log("Ordem das imagens salva com sucesso.");
    // Recarrega as imagens para garantir consistência visual (opcional, mas recomendado)
    await fetchImages();
  } catch (error) {
    console.error("Erro ao salvar a nova ordem:", error);
    alert('Não foi possível salvar a nova ordem das imagens.');
    await fetchImages();
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
.upload-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.upload-prompt {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  background-color: #fafafa;
  transition: all 0.2s ease-in-out;
}
.upload-prompt:hover {
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
.btn-upload {
  background-color: #28a745;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.btn-upload:disabled {
  background-color: #a3d9b1;
  cursor: not-allowed;
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
  border: 3px solid transparent;
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
.principal-btn, .order-btn, .delete-btn {
  color: white;
  background-color: transparent;
  border: none;
  cursor: pointer;
}
.principal-btn:disabled {
  color: yellow;
  cursor: not-allowed;
}
.order-btn:disabled {
  color: #a3a3a3;
  cursor: not-allowed;
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
.no-images-message, .loading-message {
  text-align: center;
  color: #6c757d;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>
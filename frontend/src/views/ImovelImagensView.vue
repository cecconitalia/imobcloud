<template>
  <div class="imagens-container">
    <header class="view-header">
      <div>
        <h1>Gestão de Imagens</h1>
        <h2 v-if="imovel" class="sub-header">{{ imovel.endereco }}</h2>
      </div>
      <router-link to="/imoveis" class="btn-secondary">Voltar à Lista</router-link>
    </header>

    <div class="upload-section">
      <h3>Carregar Novas Imagens</h3>
      <div class="form-group">
        <label for="imagem-file">Selecionar um ou mais ficheiros</label>
        <input type="file" @change="handleFileSelect" id="imagem-file" accept="image/*" multiple />
      </div>
      <button @click="handleUpload" :disabled="!selectedFiles.length || isUploading" class="btn-primary">
        {{ isUploading ? `A carregar ${uploadProgress}...` : `Carregar ${selectedFiles.length} Imagens` }}
      </button>
    </div>

    <hr class="divider" />

    <h3>Imagens Atuais</h3>
    <div v-if="isLoading">A carregar imagens...</div>
    <div v-if="!isLoading && imagens.length === 0" class="no-images">
      Nenhuma imagem cadastrada para este imóvel.
    </div>
    <div v-else class="gallery">
      <div v-for="imagem in imagens" :key="imagem.id" class="image-card">
        <img :src="imagem.imagem" alt="Imagem do imóvel" class="image-thumbnail" />
        <div class="image-actions">
          <button @click="handleDelete(imagem.id)" class="btn-danger-small">Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const imovelId = route.params.id as string;

// Estados do componente
const imovel = ref<any>(null);
const imagens = ref<any[]>([]);
const selectedFiles = ref<File[]>([]); // Modificado para ser um array de ficheiros
const isLoading = ref(true);
const isUploading = ref(false);
const uploadProgress = ref(''); // Para feedback durante o upload

// Função para buscar os dados do imóvel e as suas imagens (sem alterações)
async function fetchImovelEImagens() {
  isLoading.value = true;
  try {
    const response = await apiClient.get(`/v1/imoveis/imoveis/${imovelId}/`);
    imovel.value = response.data;
    imagens.value = response.data.imagens || [];
  } catch (error) {
    console.error("Erro ao buscar dados do imóvel:", error);
    alert("Não foi possível carregar os dados do imóvel.");
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchImovelEImagens();
});

// MODIFICADO para lidar com múltiplos ficheiros
function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    selectedFiles.value = Array.from(target.files); // Converte o FileList para um array
  }
}

// MODIFICADO para fazer o upload de múltiplos ficheiros em sequência
async function handleUpload() {
  if (!selectedFiles.value.length) return;

  isUploading.value = true;
  const totalFiles = selectedFiles.value.length;

  // Itera sobre cada ficheiro selecionado e faz o upload
  for (let i = 0; i < totalFiles; i++) {
    const file = selectedFiles.value[i];
    uploadProgress.value = `(${i + 1}/${totalFiles})`; // Atualiza o progresso

    const formData = new FormData();
    formData.append('imagem', file);
    formData.append('imovel', imovelId);

    try {
      // Envia um pedido para cada imagem
      await apiClient.post('/v1/imoveis/imagens/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    } catch (error) {
      console.error(`Erro no upload da imagem ${file.name}:`, error);
      alert(`Ocorreu um erro ao carregar a imagem: ${file.name}. O processo foi interrompido.`);
      isUploading.value = false; // Interrompe em caso de erro
      uploadProgress.value = '';
      return;
    }
  }
  
  // Após o sucesso de todos os uploads
  isUploading.value = false;
  uploadProgress.value = '';
  selectedFiles.value = []; // Limpa a seleção de ficheiros
  (document.getElementById('imagem-file') as HTMLInputElement).value = ''; // Limpa o input visualmente

  // Atualiza a galeria com as novas imagens
  await fetchImovelEImagens();
}

// Função de eliminação (sem alterações)
async function handleDelete(imagemId: number) {
  if (!window.confirm('Tem a certeza de que deseja eliminar esta imagem?')) {
    return;
  }
  try {
    await apiClient.delete(`/v1/imoveis/imagens/${imagemId}/`);
    await fetchImovelEImagens();
  } catch (error) {
    console.error("Erro ao eliminar a imagem:", error);
    alert("Ocorreu um erro ao eliminar a imagem.");
  }
}
</script>

<style scoped>
/* Os seus estilos não precisam de ser alterados */
.imagens-container {
  padding: 2rem;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.sub-header {
  color: #6c757d;
  font-weight: normal;
  margin-top: -10px;
}
.upload-section {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.form-group {
  margin-bottom: 1rem;
}
.divider {
  border: 0;
  height: 1px;
  background-color: #dee2e6;
  margin-bottom: 2rem;
}
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
.image-card {
  position: relative;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}
.image-thumbnail {
  width: 100%;
  height: 150px;
  object-fit: cover;
  display: block;
}
.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 0.5rem;
  display: flex;
  justify-content: center;
}
.btn-primary, .btn-secondary {
  border: none; cursor: pointer; padding: 10px 15px; border-radius: 5px; text-decoration: none; font-weight: bold;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:disabled { background-color: #a0cfff; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-danger-small {
  background-color: #dc3545;
  color: white;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 0.8em;
  border-radius: 4px;
}
.no-images {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
</style>
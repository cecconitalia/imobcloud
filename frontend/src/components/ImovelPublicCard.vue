<template>
  <div class="imovel-card">
    <router-link :to="`/site/imovel/${imovel.id}`" class="image-link">
      <div class="image-carousel-container">
        <img :src="currentImage" alt="Imagem do imóvel" class="imovel-image" />
        
        <div v-if="imovel.imagens && imovel.imagens.length > 1">
          <button class="nav-btn prev" @click.stop.prevent="prevImage">&lt;</button>
          <button class="nav-btn next" @click.stop.prevent="nextImage">&gt;</button>
        </div>
      </div>
    </router-link>
    
    <div class="card-content">
      <div class="card-header-flex">
        <h3 class="card-title">{{ imovel.titulo_anuncio }}</h3>
        <p class="card-price" v-if="imovel.valor_venda || imovel.valor_aluguel">
          {{ formatarPreco(imovel) }}
        </p>
      </div>

      <div class="imovel-details-icons">
        <div class="detail-item" v-if="imovel.quartos">
          <i class="fas fa-bed"></i> {{ imovel.quartos }} Qts
        </div>
        <div class="detail-item" v-if="imovel.banheiros">
          <i class="fas fa-bath"></i> {{ imovel.banheiros }} Ban
        </div>
        <div class="detail-item" v-if="imovel.vagas_garagem">
          <i class="fas fa-car"></i> {{ imovel.vagas_garagem }} Vagas
        </div>
        <div class="detail-item" v-if="imovel.area_total">
          <i class="fas fa-ruler-combined"></i> {{ imovel.area_total }}m²
        </div>
      </div>
      
      <div class="imovel-info-group">
        <p class="imovel-location">
          <i class="fas fa-map-marker-alt"></i>
          {{ imovel.bairro || 'N/A' }}, {{ imovel.cidade }}, {{ imovel.estado }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, onMounted, watch } from 'vue';
import publicApiClient from '@/services/publicApiClient';

const props = defineProps({
  imovel: {
    type: Object,
    required: true
  }
});

const currentImageIndex = ref(0);
const currentImage = ref('');

function formatarPreco(imovel: any) {
  if (imovel.valor_venda) {
    return parseFloat(imovel.valor_venda).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  if (imovel.valor_aluguel) {
    return `${parseFloat(imovel.valor_aluguel).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}/mês`;
  }
  return 'A consultar';
}

function getImageUrl(imagemPath: string) {
  if (imagemPath.startsWith('http')) {
    return imagemPath;
  }
  const baseUrl = publicApiClient.defaults.baseURL.replace('/api', '');
  const path = imagemPath.startsWith('/') ? imagemPath : `/${imagemPath}`;
  return `${baseUrl}${path}`;
}

function updateCurrentImage() {
  const imagens = props.imovel.imagens;
  if (!imagens || imagens.length === 0) {
    currentImage.value = 'https://via.placeholder.com/400x300.png?text=Sem+imagem';
    return;
  }
  const imagemPath = imagens[currentImageIndex.value].imagem;
  currentImage.value = getImageUrl(imagemPath);
}

function nextImage() {
  const imagens = props.imovel.imagens;
  if (imagens.length <= 1) return;
  currentImageIndex.value = (currentImageIndex.value + 1) % imagens.length;
  updateCurrentImage();
}

function prevImage() {
  const imagens = props.imovel.imagens;
  if (imagens.length <= 1) return;
  currentImageIndex.value = (currentImageIndex.value - 1 + imagens.length) % imagens.length;
  updateCurrentImage();
}

onMounted(() => {
  const imagens = props.imovel.imagens;
  if (imagens && imagens.length > 0) {
    const principal = imagens.find((img: any) => img.principal);
    if (principal) {
      currentImageIndex.value = imagens.indexOf(principal);
    }
  }
  updateCurrentImage();
});

// Watch para garantir que a imagem seja atualizada quando o prop do imóvel mudar
watch(() => props.imovel, () => {
    currentImageIndex.value = 0; // Reinicia o índice ao mudar de imóvel
    updateCurrentImage();
});
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.imovel-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

.imovel-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.image-link {
  display: block;
}

.image-carousel-container {
  width: 100%;
  height: 180px;
  overflow: hidden;
  position: relative;
}

.imovel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  height: 100%;
  transition: background-color 0.2s;
  opacity: 0;
}

.image-carousel-container:hover .nav-btn {
  opacity: 1;
}

.nav-btn:hover {
  background-color: rgba(0, 0, 0, 0.8);
}

.prev {
  left: 0;
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}

.next {
  right: 0;
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}

.card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  text-align: left;
}

.card-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
}

.card-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  color: #343a40;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

.card-price {
    font-size: 1rem;
    font-weight: bold;
    color: #28a745;
    margin: 0;
    flex-shrink: 0;
    white-space: nowrap;
    margin-left: 1rem;
}

.imovel-details-icons {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 500;
}

.detail-item i {
  margin-right: 4px;
  color: var(--primary-color);
  font-size: 1em;
}

.imovel-info-group {
  margin-top: 0.5rem;
}

.imovel-location {
  font-size: 0.8rem;
  color: #6c757d;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.imovel-location i {
  color: var(--primary-color);
}
</style>
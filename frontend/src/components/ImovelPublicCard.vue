<template>
  <div class="imovel-card" @click="openDetails">
    <div class="card-image-wrapper" @mouseenter="showControls = true" @mouseleave="showControls = false">
      <img 
        :src="currentImageSrc" 
        @error="handleImageError"
        alt="Imagem do Imóvel" 
        class="card-image"
      />
      <div class="card-overlay"></div>
      
      <div v-if="orderedImages.length > 1" class="carousel-controls" :class="{ 'visible': showControls }">
        <button class="nav-btn prev" @click.stop="prevImage">
          <i class="fas fa-chevron-left"></i>
        </button>
        <button class="nav-btn next" @click.stop="nextImage">
          <i class="fas fa-chevron-right"></i>
        </button>
        
        <div class="image-counter">
          {{ currentImageIndex + 1 }} / {{ orderedImages.length }}
        </div>
      </div>

      <div class="card-badges">
        <span class="badge-status" :class="getStatusClass(imovel.status)">
          {{ formatStatus(imovel.status) }}
        </span>
        <span class="badge-id">Ref: {{ imovel.codigo_referencia }}</span>
      </div>
    </div>

    <div class="card-content">
      <div class="card-header">
        <h3 class="card-title" :title="imovel.titulo_anuncio">
          {{ imovel.titulo_anuncio || 'Imóvel sem título' }}
        </h3>
        <p class="card-location">
          <i class="fas fa-map-marker-alt"></i>
          {{ imovel.bairro || 'Bairro não informado' }}, {{ imovel.cidade || 'Cidade' }}
        </p>
      </div>

      <div class="card-specs">
        <div class="spec-item" v-if="imovel.quartos" title="Quartos">
          <i class="fas fa-bed"></i> {{ imovel.quartos }}
        </div>
        <div class="spec-item" v-if="imovel.suites" title="Suítes">
          <i class="fas fa-bath"></i> {{ imovel.suites }}
        </div>
        <div class="spec-item" v-if="imovel.vagas_garagem" title="Vagas">
          <i class="fas fa-car"></i> {{ imovel.vagas_garagem }}
        </div>
        <div class="spec-item" v-if="imovel.area_util" title="Área Útil">
          <i class="fas fa-ruler-combined"></i> {{ imovel.area_util }}m²
        </div>
      </div>

      <div class="card-footer">
        <div class="price-info">
          <small>{{ imovel.status === 'A_VENDA' ? 'Valor de Venda' : 'Valor de Aluguel' }}</small>
          <strong>{{ formattedPrice }}</strong>
        </div>
        <div class="action-arrow">
          <i class="fas fa-chevron-right"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  imovel: {
    type: Object,
    required: true
  }
});

const router = useRouter();
const imageLoadError = ref(false);
const currentImageIndex = ref(0);
const showControls = ref(false);

const orderedImages = computed(() => {
  const imgs = props.imovel.imagens || [];
  if (imgs.length === 0) return [];
  return [...imgs].sort((a: any, b: any) => (b.principal === true ? 1 : 0) - (a.principal === true ? 1 : 0));
});

const currentImageSrc = computed(() => {
  if (imageLoadError.value || orderedImages.value.length === 0) {
    return 'https://via.placeholder.com/400x300.png?text=Sem+Foto';
  }
  return orderedImages.value[currentImageIndex.value].imagem;
});

function nextImage() {
  if (orderedImages.value.length > 1) {
    currentImageIndex.value = (currentImageIndex.value + 1) % orderedImages.value.length;
  }
}

function prevImage() {
  if (orderedImages.value.length > 1) {
    currentImageIndex.value = (currentImageIndex.value - 1 + orderedImages.value.length) % orderedImages.value.length;
  }
}

function handleImageError() {
  imageLoadError.value = true;
}

function openDetails() {
  if (props.imovel && props.imovel.id) {
    router.push({ 
      name: 'public-imovel-detail', 
      params: { id: props.imovel.id } 
    });
  }
}

const formattedPrice = computed(() => {
  const val = props.imovel.valor_venda || props.imovel.valor_aluguel;
  if (!val) return 'R$ Sob Consulta';
  return parseFloat(val).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
});

function formatStatus(status: string) {
  const map: Record<string, string> = {
    'A_VENDA': 'Venda',
    'PARA_ALUGAR': 'Aluguel',
    'VENDIDO': 'Vendido',
    'ALUGADO': 'Alugado'
  };
  return map[status] || status;
}

function getStatusClass(status: string) {
  if (status === 'A_VENDA') return 'badge-blue';
  if (status === 'PARA_ALUGAR') return 'badge-green';
  if (status === 'VENDIDO' || status === 'ALUGADO') return 'badge-red';
  return 'badge-gray';
}
</script>

<style scoped>
.imovel-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border: 1px solid rgba(0,0,0,0.02);
  cursor: pointer;
  height: 100%;
  position: relative;
}

.imovel-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.card-image-wrapper {
  position: relative;
  height: 220px;
  overflow: hidden;
  background-color: #e2e8f0;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.imovel-card:hover .card-image {
  transform: scale(1.05);
}

.card-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 40%;
  background: linear-gradient(to top, rgba(0,0,0,0.5), transparent);
  pointer-events: none;
}

.carousel-controls {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 5;
}

.card-image-wrapper:hover .carousel-controls {
  opacity: 1;
}

.nav-btn {
  background: rgba(0, 0, 0, 0.3);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  backdrop-filter: blur(2px);
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #1e293b;
  transform: scale(1.1);
}

.image-counter {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  backdrop-filter: blur(2px);
  pointer-events: none;
}

.card-badges {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  z-index: 4;
  pointer-events: none;
}

.badge-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.badge-blue { background-color: #3b82f6; }
.badge-green { background-color: #10b981; }
.badge-red { background-color: #ef4444; }
.badge-gray { background-color: #6b7280; }

.badge-id {
  background: rgba(255, 255, 255, 0.9);
  color: #1e293b;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.card-content {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 600; /* Slightly reduced weight for title too */
  color: #1e293b;
  margin: 0 0 0.25rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-location {
  color: #64748b;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 300;
}

.card-specs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.spec-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: #475569;
  font-weight: 400; /* Regular weight for specs */
}
.spec-item i { color: #94a3b8; }

.card-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-info {
  display: flex;
  flex-direction: column;
}

.price-info small {
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
  font-weight: 500;
  margin-bottom: 2px;
}

/* ALTERAÇÕES AQUI: Fonte fina e menor */
.price-info strong {
  font-size: 1.15rem; /* Diminuído de 1.35rem */
  color: #0f172a;
  font-weight: 300;   /* Fonte fina (Light) */
  letter-spacing: 0px;
}

.action-arrow {
  width: 32px; /* Ligeiramente menor para combinar */
  height: 32px;
  border-radius: 50%;
  background: #f8fafc;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.imovel-card:hover .action-arrow {
  background: #3b82f6;
  color: #fff;
  transform: translateX(4px);
}
</style>
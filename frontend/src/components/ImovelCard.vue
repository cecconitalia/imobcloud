<template>
  <div class="imovel-card">
    <div class="image-container">
      <img :src="getPrincipalImage(imovel.imagens)" :alt="imovel.titulo_anuncio" class="imovel-card-image">
      <div class="card-badges">
        <span :class="['publication-badge', imovel.isPublished ? 'published' : 'not-published']">
          {{ imovel.isPublished ? 'Publicado' : 'Não Publicado' }}
        </span>
        <span :class="['status-badge', getStatusClass(imovel.status)]">
          {{ formatStatus(imovel.status) }}
        </span>
      </div>
    </div>
    
    <div class="imovel-card-body">
      <span class="price-display">R$ {{ formatPrice(imovel.valor_venda) }}</span>
      <h3 class="imovel-title">{{ imovel.titulo_anuncio }}</h3>
      <p class="imovel-address">
        <i class="fas fa-map-marker-alt"></i> {{ imovel.endereco }}
      </p>
      
      <div class="imovel-details-badges">
        <span v-if="imovel.quartos" class="detail-badge"><i class="fas fa-bed"></i> {{ imovel.quartos }}</span>
        <span v-if="imovel.banheiros" class="detail-badge"><i class="fas fa-bath"></i> {{ imovel.banheiros }}</span>
        <span v-if="imovel.vagas_garagem" class="detail-badge"><i class="fas fa-car"></i> {{ imovel.vagas_garagem }}</span>
      </div>

      <div class="card-actions">
        <button @click="$emit('open-modal')" class="btn-primary-card">
          <i class="fas fa-rocket"></i> Publicar
        </button>
        <button v-if="imovel.isPublished" @click="$emit('open-history-modal', imovel.id)" class="btn-secondary-card">
          <i class="fas fa-history"></i> Histórico
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import '@fortawesome/fontawesome-free/css/all.css';

const props = defineProps({
  imovel: {
    type: Object,
    required: true,
  },
});

const emits = defineEmits(['open-modal', 'open-history-modal']);

function formatPrice(value: number) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }).replace('R$', '').trim();
}

function getPrincipalImage(imagens: any[]) {
  if (!imagens || imagens.length === 0) {
    return 'https://via.placeholder.com/400x250.png?text=Sem+Foto';
  }
  const principal = imagens.find(img => img.principal);
  return principal ? principal.imagem : imagens[0].imagem;
}

function getStatusClass(status: string) {
  if (!status) return 'status-inativo';
  const s = status.toLowerCase();
  if (s.includes('venda') || s.includes('alugar')) return 'status-ativo';
  if (s.includes('vendido') || s.includes('alugado')) return 'status-concluido';
  if (s.includes('construcao')) return 'status-pendente';
  return 'status-inativo';
}

function formatStatus(status: string) {
  return status ? status.replace(/_/g, ' ') : 'N/A';
}
</script>

<style scoped>
.imovel-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  position: relative;
  display: flex;
  flex-direction: column;
}
.imovel-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}
.image-container {
  position: relative;
}
.imovel-card-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}
.card-badges {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}
.publication-badge, .status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  white-space: nowrap;
}
.publication-badge.published { background-color: #28a745; }
.publication-badge.not-published { background-color: #dc3545; }
.status-badge.status-ativo { background-color: #007bff; }
.status-badge.status-concluido { background-color: #6c757d; }
.status-badge.status-pendente { background-color: #ffc107; color: #333; }
.imovel-card-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.price-display {
  font-size: 1.5rem;
  font-weight: 700;
  color: #17a2b8;
  margin-bottom: 0.5rem;
}
.imovel-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #343a40;
  margin: 0;
}
.imovel-address {
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.imovel-address i {
  color: var(--secondary-color);
}
.imovel-details-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
  margin-bottom: 1.5rem;
}
.detail-badge {
  background-color: #f1f1f1;
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 0.8em;
  color: #555;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}
.detail-badge i {
  color: #007bff;
}
.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: auto;
}
.btn-primary-card, .btn-secondary-card {
  padding: 12px 15px;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  flex-grow: 1;
}
.btn-primary-card { background-color: #007bff; color: white; }
.btn-primary-card:hover { background-color: #0056b3; }
.btn-secondary-card { background-color: #e9ecef; color: #495057; }
.btn-secondary-card:hover { background-color: #d1d5db; }
</style>
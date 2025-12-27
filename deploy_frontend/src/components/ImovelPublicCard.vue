<template>
  <div class="imovel-card">
    <div class="card-image-wrapper">
      <img 
        :src="principalImage" 
        alt="Imagem do Imóvel" 
        class="card-image"
      />
      <div class="card-badges">
        <span class="badge-status" :class="getStatusClass(imovel.status)">
          {{ formatStatus(imovel.status) }}
        </span>
        <span class="badge-id">#{{ imovel.codigo_referencia }}</span>
      </div>
    </div>

    <div class="card-content">
      <h3 class="card-title" :title="imovel.titulo_anuncio">
        {{ imovel.titulo_anuncio || 'Imóvel sem título' }}
      </h3>
      
      <p class="card-location">
        <i class="fas fa-map-marker-alt"></i>
        {{ imovel.bairro }}, {{ imovel.cidade }}
      </p>

      <div class="card-specs">
        <span v-if="imovel.quartos"><i class="fas fa-bed"></i> {{ imovel.quartos }}</span>
        <span v-if="imovel.suites"><i class="fas fa-bath"></i> {{ imovel.suites }}</span>
        <span v-if="imovel.vagas_garagem"><i class="fas fa-car"></i> {{ imovel.vagas_garagem }}</span>
        <span v-if="imovel.area_util"><i class="fas fa-ruler"></i> {{ imovel.area_util }}m²</span>
      </div>

      <div class="card-price">
        <small>{{ imovel.status === 'A_VENDA' ? 'Venda' : 'Aluguel' }}</small>
        <strong>{{ formattedPrice }}</strong>
      </div>
    </div>

    <div class="card-actions">
      <button 
        @click="$emit('open-modal')" 
        class="btn-action btn-instagram"
      >
        <i class="fab fa-instagram"></i> Agendar Post
      </button>
      
      <button 
        @click="$emit('open-history-modal')" 
        class="btn-icon"
        title="Histórico de Publicações"
      >
        <i class="fas fa-history"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  imovel: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['open-modal', 'open-history-modal']);

const principalImage = computed(() => {
  if (props.imovel.imagens && props.imovel.imagens.length > 0) {
    const principal = props.imovel.imagens.find((img: any) => img.principal);
    return principal ? principal.imagem : props.imovel.imagens[0].imagem;
  }
  return 'https://via.placeholder.com/400x300.png?text=Sem+Foto';
});

const formattedPrice = computed(() => {
  const val = props.imovel.valor_venda || props.imovel.valor_aluguel;
  if (!val) return 'R$ Sob Consulta';
  return parseFloat(val).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
});

function formatStatus(status: string) {
  const map: Record<string, string> = {
    'A_VENDA': 'À Venda',
    'PARA_ALUGAR': 'Alugar',
    'VENDIDO': 'Vendido',
    'ALUGADO': 'Alugado'
  };
  return map[status] || status;
}

function getStatusClass(status: string) {
  if (status === 'A_VENDA') return 'bg-blue';
  if (status === 'PARA_ALUGAR') return 'bg-green';
  return 'bg-gray';
}
</script>

<style scoped>
.imovel-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s;
  border: 1px solid #f1f5f9;
}
.imovel-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-image-wrapper {
  position: relative;
  height: 200px;
}
.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-badges {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  gap: 8px;
}
.badge-status {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
}
.bg-blue { background-color: #3b82f6; }
.bg-green { background-color: #10b981; }
.bg-gray { background-color: #6b7280; }

.badge-id {
  background: rgba(0,0,0,0.6);
  color: #fff;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  backdrop-filter: blur(2px);
}

.card-content {
  padding: 1rem;
  flex: 1;
}
.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-location {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}
.card-location i { margin-right: 4px; }

.card-specs {
  display: flex;
  gap: 12px;
  color: #64748b;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}
.card-specs span i { color: #94a3b8; margin-right: 4px; }

.card-price {
  display: flex;
  flex-direction: column;
}
.card-price small { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; }
.card-price strong { font-size: 1.25rem; color: #0f172a; }

.card-actions {
  padding: 1rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  gap: 0.5rem;
  background: #f8fafc;
}

/* BOTÃO DE AGENDAR - O PRINCIPAL */
.btn-action {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.2s;
}
.btn-instagram {
  background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
  color: white;
}
.btn-instagram:hover { opacity: 0.9; }

.btn-icon {
  width: 40px;
  border: 1px solid #cbd5e1;
  background: white;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-icon:hover { background: #f1f5f9; color: #334155; }
</style>
<template>
  <div class="imovel-card">
    <div class="image-container">
      <img :src="imovel.imagens && imovel.imagens[0] ? imovel.imagens[0].imagem : 'https://via.placeholder.com/400x300.png?text=Sem+imagem'" alt="Imagem do imóvel" class="imovel-image" />
    </div>
    <div class="card-content">
      <h3 class="card-title">{{ imovel.titulo_anuncio || imovel.tipo }}</h3>
      
      <div class="imovel-info-group">
        <p class="imovel-info" v-if="imovel.configuracao_publica?.logradouro && imovel.logradouro">
          <i class="fas fa-map-marker-alt"></i>
          {{ imovel.logradouro }}, {{ imovel.numero }} - {{ imovel.bairro }}
        </p>
        <p class="imovel-info" v-else-if="imovel.configuracao_publica?.bairro && imovel.bairro">
          <i class="fas fa-map-marker-alt"></i>
          {{ imovel.bairro }}
        </p>
        <p class="imovel-info" v-if="imovel.configuracao_publica?.cidade && imovel.cidade">
          <i class="fas fa-city"></i>
          {{ imovel.cidade }} - {{ imovel.estado }}
        </p>
      </div>

      <div class="imovel-details">
        <span class="detail-item" v-if="imovel.configuracao_publica?.quartos && imovel.quartos">
          <i class="fas fa-bed"></i> {{ imovel.quartos }} Qts
        </span>
        <span class="detail-item" v-if="imovel.configuracao_publica?.suites && imovel.suites">
          <i class="fas fa-bath"></i> {{ imovel.suites }} Suítes
        </span>
        <span class="detail-item" v-if="imovel.configuracao_publica?.vagas_garagem && imovel.vagas_garagem">
          <i class="fas fa-car"></i> {{ imovel.vagas_garagem }} Vagas
        </span>
        <span class="detail-item" v-if="imovel.configuracao_publica?.area_total && imovel.area_total">
          <i class="fas fa-ruler-combined"></i> {{ imovel.area_total }}m²
        </span>
      </div>

      <p class="card-price" v-if="imovel.configuracao_publica?.valor_venda && imovel.valor_venda">
        R$ {{ formatCurrency(imovel.valor_venda) }}
      </p>
      <p class="card-price" v-else-if="imovel.configuracao_publica?.valor_aluguel && imovel.valor_aluguel">
        R$ {{ formatCurrency(imovel.valor_aluguel) }}/mês
      </p>

      <div class="card-actions">
        <router-link :to="`/site/imovel/${imovel.id}`" class="btn-detalhes">Ver Detalhes</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

const props = defineProps({
  imovel: {
    type: Object,
    required: true
  }
});

function formatCurrency(value: number) {
  return value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
</script>

<style scoped>
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

.image-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background-color: #f0f0f0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.imovel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #007bff;
  min-height: 48px; /* Para manter a altura consistente */
}

.imovel-info-group {
  margin-bottom: 1rem;
}

.imovel-info {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.imovel-info i {
  margin-right: 8px;
  color: #007bff;
}

.imovel-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-top: 1px solid #e9ecef;
  border-bottom: 1px solid #e9ecef;
  padding: 1rem 0;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #343a40;
}

.detail-item i {
  margin-right: 5px;
  color: #007bff;
}

.card-price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #28a745;
  margin-bottom: 1.5rem;
}

.card-actions {
  margin-top: auto;
  display: flex;
  justify-content: center;
}

.btn-detalhes {
  display: inline-block;
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.btn-detalhes:hover {
  background-color: #0056b3;
}
</style>
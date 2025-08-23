<template>
  <div class="imovel-card">
    <div class="image-container">
      <img :src="getPrincipalImage(imovel.imagens)" alt="Imagem do imóvel" class="imovel-image" />
    </div>
    <div class="card-content">
      <h3 class="card-title">{{ imovel.titulo_anuncio }}</h3>
      
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

      <p class="card-price" v-if="imovel.valor_venda">
        {{ formatarPreco(imovel.valor_venda) }}
      </p>
      <p class="card-price" v-else-if="imovel.valor_aluguel">
        {{ formatarPreco(imovel.valor_aluguel) }}/mês
      </p>

      <div class="card-actions">
        <router-link :to="`/site/imovel/${imovel.id}`" class="btn-detalhes">Ver Detalhes</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import publicApiClient from '@/services/publicApiClient';

const props = defineProps({
  imovel: {
    type: Object,
    required: true
  }
});

function formatCurrency(value: number) {
  return value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatarPreco(value: number) {
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function getPrincipalImage(imagens: any[]) {
  if (!imagens || imagens.length === 0) {
    return 'https://via.placeholder.com/400x300.png?text=Sem+imagem';
  }
  const principal = imagens.find(img => img.principal);
  const imagemPath = principal ? principal.imagem : imagens[0].imagem;
  
  // CORREÇÃO FINAL: Garante que a URL da imagem seja sempre absoluta.
  // Se o caminho já for absoluto (http/https), usa-o. Caso contrário,
  // constrói a URL completa.
  if (imagemPath.startsWith('http')) {
    return imagemPath;
  }
  
  // Remove o '/api' da base URL para ter o domínio base.
  const baseUrl = publicApiClient.defaults.baseURL.replace('/api', '');
  
  // Adiciona uma barra inicial se o caminho não a tiver, para evitar caminhos quebrados.
  const path = imagemPath.startsWith('/') ? imagemPath : `/${imagemPath}`;
  
  return `${baseUrl}${path}`;
}
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
  text-align: left;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #343a40;
}

.imovel-details-icons {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
}

.detail-item i {
  margin-right: 8px;
  color: #007bff;
  font-size: 1.1rem;
}

.imovel-info-group {
  margin-bottom: 1rem;
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
}

.imovel-location {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.imovel-location i {
  color: #007bff;
}

.card-price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #28a745;
  margin: 1rem 0;
}

.card-actions {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  text-align: right;
}

.btn-detalhes {
  display: inline-block;
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.btn-detalhes:hover {
  background-color: #0056b3;
}
</style>
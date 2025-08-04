<template>
  <div class="container">
    <div v-if="isLoading" class="loading-message">A carregar detalhes do imóvel...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="imovel" class="imovel-detail-container">
      <div class="gallery">
        <img :src="imagemPrincipal" alt="Imagem principal do imóvel" class="main-image" />
        <div class="thumbnail-grid" v-if="imovel.imagens && imovel.imagens.length > 1">
          <img
            v-for="imagem in imovel.imagens"
            :key="imagem.id"
            :src="imagem.imagem"
            alt="Thumbnail do imóvel"
            @click="setImagemPrincipal(imagem.imagem)"
            :class="{ active: imagem.imagem === imagemPrincipal }"
            class="thumbnail"
          />
        </div>
      </div>

      <div class="details">
        <h1 class="endereco">{{ imovel.endereco }}</h1>
        <p class="cidade">{{ imovel.cidade }}, {{ imovel.estado }}</p>
        <p class="preco">{{ formatarPreco(imovel) }}</p>

        <div class="caracteristicas">
          <div class="caracteristica-item" v-if="imovel.area_total">
            <span>Área Total</span>
            <strong>{{ imovel.area_total }} m²</strong>
          </div>
          <div class="caracteristica-item" v-if="imovel.quartos > 0">
            <span>Quartos</span>
            <strong>{{ imovel.quartos }}</strong>
          </div>
          <div class="caracteristica-item" v-if="imovel.banheiros > 0">
            <span>WC</span>
            <strong>{{ imovel.banheiros }}</strong>
          </div>
           <div class="caracteristica-item" v-if="imovel.vagas_garagem > 0">
            <span>Garagem</span>
            <strong>{{ imovel.vagas_garagem }}</strong>
          </div>
        </div>

        <h3 class="descricao-titulo">Descrição</h3>
        <p class="descricao-texto">{{ imovel.descricao || 'Nenhuma descrição disponível.' }}</p>
        
        <router-link to="/site" class="btn-voltar">Voltar à Lista</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import publicApiClient from '@/services/publicApiClient';

const route = useRoute();
const imovelId = route.params.id as string;

const imovel = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const imagemPrincipal = ref('');

// --- FUNÇÃO fetchImovel ATUALIZADA ---
async function fetchImovel() {
  isLoading.value = true;
  try {
    // Extrai o subdomínio da mesma forma que na página principal
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    let subdomain = null;
    if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
      subdomain = parts[0];
    }

    if (!subdomain) {
      error.value = "Endereço inválido.";
      return;
    }

    // Envia o subdomínio como um parâmetro para que o backend saiba onde procurar
    const response = await publicApiClient.get(`/v1/imoveis/imoveis/${imovelId}/`, {
      params: { subdomain: subdomain }
    });
    
    imovel.value = response.data;
    imagemPrincipal.value = getPrincipalImage(imovel.value.imagens);
  } catch (err) {
    console.error("Erro ao buscar detalhes do imóvel:", err);
    error.value = 'Não foi possível carregar os detalhes deste imóvel.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchImovel();
});

// As funções abaixo permanecem sem alterações
function setImagemPrincipal(url: string) {
  imagemPrincipal.value = url;
}

function getPrincipalImage(imagens: any[]) {
  if (!imagens || imagens.length === 0) {
    return 'https://via.placeholder.com/800x600.png?text=Sem+Imagem';
  }
  const principal = imagens.find(img => img.principal);
  return principal ? principal.imagem : imagens[0].imagem;
}

function formatarPreco(imovel: any) {
  if (imovel.finalidade === 'Venda' && imovel.valor_venda) {
    return parseFloat(imovel.valor_venda).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  if (imovel.finalidade === 'Aluguel' && imovel.valor_aluguel) {
    return `${parseFloat(imovel.valor_aluguel).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} /mês`;
  }
  return 'Valor a consultar';
}
</script>

<style scoped>
/* O seu CSS permanece sem alterações */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
.loading-message, .error-message {
  text-align: center;
  padding: 3rem;
}
.imovel-detail-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
@media (max-width: 992px) {
  .imovel-detail-container {
    grid-template-columns: 1fr;
  }
}
.main-image {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: cover;
  border-radius: 8px;
}
.thumbnail-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
  margin-top: 1rem;
}
.thumbnail {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}
.thumbnail:hover, .thumbnail.active {
  border-color: #007bff;
}
.details {
  padding-left: 1rem;
}
.endereco {
  font-size: 2rem;
  font-weight: bold;
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.cidade {
  color: #6c757d;
  font-size: 1.1rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
}
.preco {
  font-size: 2.2rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 2rem;
}
.caracteristicas {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  border-top: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  padding: 1.5rem 0;
}
.caracteristica-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.caracteristica-item span {
  font-size: 0.9rem;
  color: #6c757d;
}
.caracteristica-item strong {
  font-size: 1.2rem;
  font-weight: bold;
}
.descricao-titulo {
  margin-bottom: 0.5rem;
}
.descricao-texto {
  line-height: 1.6;
  color: #333;
}
.btn-voltar {
  display: inline-block;
  margin-top: 2rem;
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  text-decoration: none;
  border-radius: 5px;
}
</style>
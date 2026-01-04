<template>
  <div class="imovel-detail-container">
    <div v-if="isLoading" class="loading-message">A carregar detalhes do imóvel...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="imovel" class="imovel-content">
      <div class="main-column">
        <h1 class="imovel-title">{{ imovel.titulo_anuncio }}</h1>
        <p class="imovel-location">{{ imovel.logradouro }}, {{ imovel.numero }}, {{ imovel.bairro }}, {{ imovel.cidade }} - {{ imovel.estado }}</p>

        <div class="gallery">
          <img :src="principalImage" alt="Imagem principal do imóvel" class="main-image" @click="openImageModal(principalImage)">
          <div class="thumbnail-grid">
            <img v-for="imagem in imovel.imagens" :key="imagem.id" :src="imagem.imagem" @click="principalImage = imagem.imagem" :class="{ active: principalImage === imagem.imagem }" class="thumbnail">
          </div>
        </div>

        <div class="details-section">
            <h2>Destaques</h2>
            <div class="highlights-grid">
                <div class="highlight-item"><i class="fas fa-ruler-combined"></i> {{ imovel.area_util || imovel.area_construida }} m²</div>
                <div class="highlight-item"><i class="fas fa-bed"></i> {{ imovel.quartos }} Quarto(s)</div>
                <div class="highlight-item"><i class="fas fa-bath"></i> {{ imovel.suites }} Suíte(s)</div>
                <div class="highlight-item"><i class="fas fa-car"></i> {{ imovel.vagas_garagem }} Vaga(s)</div>
                <div v-if="imovel.piscina_privativa || imovel.piscina_condominio" class="highlight-item"><i class="fas fa-swimmer"></i> Piscina</div>
                <div v-if="imovel.churrasqueira_privativa || imovel.churrasqueira_condominio" class="highlight-item"><i class="fas fa-utensils"></i> Churrasqueira</div>
                <div v-if="imovel.academia" class="highlight-item"><i class="fas fa-dumbbell"></i> Academia</div>
                <div v-if="imovel.aceita_pet" class="highlight-item"><i class="fas fa-paw"></i> Aceita Pet</div>
                <div v-if="imovel.mobiliado" class="highlight-item"><i class="fas fa-couch"></i> Mobiliado</div>
            </div>
        </div>

        <div class="details-section">
          <h2>Descrição</h2>
          <p class="description-text">{{ imovel.descricao_completa || 'Descrição não disponível.' }}</p>
        </div>

        <div class="details-section">
          <h2>Características do Imóvel</h2>
          <ul class="features-list">
            <li v-if="imovel.area_util"><span>Área Útil:</span> {{ imovel.area_util }} m²</li>
            <li v-if="imovel.area_construida"><span>Área Construída:</span> {{ imovel.area_construida }} m²</li>
            <li v-if="imovel.area_total"><span>Área Total:</span> {{ imovel.area_total }} m²</li>
            <li v-if="imovel.quartos"><span>Quartos:</span> {{ imovel.quartos }}</li>
            <li v-if="imovel.suites"><span>Suítes:</span> {{ imovel.suites }}</li>
            <li v-if="imovel.banheiros"><span>Banheiros:</span> {{ imovel.banheiros }}</li>
            <li v-if="imovel.vagas_garagem"><span>Vagas de Garagem:</span> {{ imovel.vagas_garagem }}</li>
            <li v-if="imovel.ano_construcao"><span>Ano de Construção:</span> {{ imovel.ano_construcao }}</li>
            <li v-if="imovel.andar"><span>Andar:</span> {{ imovel.andar }}</li>
            <li v-if="imovel.varanda"><span>Varanda / Sacada:</span> Sim</li>
            <li v-if="imovel.ar_condicionado"><span>Ar Condicionado:</span> Sim</li>
          </ul>
        </div>

        <div class="details-section" v-if="isCondominio">
          <h2>Características do Condomínio</h2>
          <ul class="features-list">
            <li v-if="imovel.portaria_24h"><span>Portaria 24h:</span> Sim</li>
            <li v-if="imovel.elevador"><span>Elevador:</span> Sim</li>
            <li v-if="imovel.salao_festas"><span>Salão de Festas:</span> Sim</li>
            <li v-if="imovel.academia"><span>Academia:</span> Sim</li>
            <li v-if="imovel.piscina_condominio"><span>Piscina:</span> Sim</li>
            <li v-if="imovel.playground"><span>Playground:</span> Sim</li>
            <li v-if="imovel.quadra_esportiva"><span>Quadra Esportiva:</span> Sim</li>
            <li v-if="imovel.espaco_gourmet"><span>Espaço Gourmet:</span> Sim</li>
          </ul>
        </div>
      </div>

      <div class="info-sidebar">
        <div class="sidebar-box">
          <p class="imovel-ref">Ref: {{ imovel.codigo_referencia }}</p>

          <div class="price-box">
            <p class="price-label">{{ getPriceLabel(imovel) }}</p>
            <p class="imovel-price">{{ formatarPreco(imovel) }}</p>
            <p v-if="imovel.valor_condominio" class="imovel-condo">Condomínio: R$ {{ imovel.valor_condominio }}</p>
            <p v-if="imovel.valor_iptu" class="imovel-iptu">IPTU: R$ {{ imovel.valor_iptu }} (anual)</p>
          </div>

          <div class="contact-form-section">
            <h3>Fale com o corretor</h3>
            <form @submit.prevent="handleContatoSubmit">
              <input type="text" v-model="contatoForm.nome" placeholder="Seu nome" required>
              <input type="email" v-model="contatoForm.email" placeholder="Seu e-mail" required>
              <input type="tel" v-model="contatoForm.telefone" placeholder="Seu telefone *" required>
              <textarea v-model="contatoForm.mensagem" rows="4" placeholder="Olá! Tenho interesse neste imóvel e gostaria de mais informações." required></textarea>
              <button type="submit" :disabled="isSubmittingContato">
                {{ isSubmittingContato ? 'A enviar...' : 'Enviar Mensagem' }}
              </button>
              <p v-if="contatoSuccess" class="success-message">Mensagem enviada com sucesso!</p>
            </form>
          </div>
        </div>
      </div>

    </div>

    <div v-if="isModalVisible" class="image-modal-overlay" @click="closeImageModal">
      <button class="modal-nav-btn prev-btn" @click.stop="prevImage">&lt;</button>
      <div class="image-modal-content">
        <img :src="modalImageUrl" alt="Imagem ampliada do imóvel">
      </div>
      <button class="modal-nav-btn next-btn" @click.stop="nextImage">&gt;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
// --- CORREÇÃO IMPORTANTE AQUI ---
// A linha abaixo corrige o erro de build.
// Importamos 'publicApiClient' como padrão (sem chaves {}), pois é assim que ele é exportado.
import publicApiClient from '@/services/publicApiClient';

const route = useRoute();
const imovel = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const principalImage = ref('');

const isModalVisible = ref(false);
const modalImageUrl = ref('');
const currentImageIndex = ref(0);

const contatoForm = ref({
  nome: '',
  email: '',
  telefone: '',
  mensagem: 'Olá! Tenho interesse neste imóvel e gostaria de mais informações.',
  imovel: route.params.id
});
const isSubmittingContato = ref(false);
const contatoSuccess = ref(false);

const isCondominio = computed(() => {
    if (!imovel.value) return false;
    return imovel.value.portaria_24h || imovel.value.elevador || imovel.value.piscina_condominio || imovel.value.academia || imovel.value.salao_festas;
});

function openImageModal(imageUrl: string) {
  const foundIndex = imovel.value.imagens.findIndex((img: any) => img.imagem === imageUrl);
  if (foundIndex !== -1) {
    currentImageIndex.value = foundIndex;
  }
  modalImageUrl.value = imageUrl;
  isModalVisible.value = true;
}

function closeImageModal() {
  isModalVisible.value = false;
}

function nextImage() {
  const newIndex = (currentImageIndex.value + 1) % imovel.value.imagens.length;
  currentImageIndex.value = newIndex;
  modalImageUrl.value = imovel.value.imagens[newIndex].imagem;
  principalImage.value = imovel.value.imagens[newIndex].imagem;
}

function prevImage() {
  const newIndex = (currentImageIndex.value - 1 + imovel.value.imagens.length) % imovel.value.imagens.length;
  currentImageIndex.value = newIndex;
  modalImageUrl.value = imovel.value.imagens[newIndex].imagem;
  principalImage.value = imovel.value.imagens[newIndex].imagem;
}


async function fetchImovelDetail() {
  isLoading.value = true;
  try {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    let subdomain = null;
    if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
      subdomain = parts[0];
    }
    
    // Fallback para desenvolvimento
    if (subdomain === 'localhost' || !subdomain) {
        subdomain = 'estilomusical';
    }

    if (!subdomain) {
      error.value = "Site não encontrado. Aceda através de um endereço de imobiliária válido.";
      isLoading.value = false;
      return;
    }

    const params = { subdomain };
    
    // Usamos o publicApiClient que importamos corretamente
    const response = await publicApiClient.get(`/public/imoveis/${route.params.id}/`, { params });

    imovel.value = response.data;

    if (imovel.value.imagens && imovel.value.imagens.length > 0) {
      const principal = imovel.value.imagens.find((img: any) => img.principal) || imovel.value.imagens[0];
      principalImage.value = principal.imagem;
    } else {
      principalImage.value = 'https://via.placeholder.com/800x600.png?text=Sem+Imagem';
    }
  } catch (err) {
    console.error("Erro ao buscar detalhes do imóvel:", err);
    error.value = 'Não foi possível carregar os detalhes do imóvel.';
  } finally {
    isLoading.value = false;
  }
}

async function handleContatoSubmit() {
    isSubmittingContato.value = true;
    try {
        await publicApiClient.post('/public/contatos/', contatoForm.value);
        contatoSuccess.value = true;
        contatoForm.value.nome = '';
        contatoForm.value.email = '';
        contatoForm.value.telefone = '';
    } catch (error) {
        console.error("Erro ao enviar contato:", error);
        alert("Ocorreu um erro ao enviar sua mensagem. Tente novamente.");
    } finally {
        isSubmittingContato.value = false;
    }
}

onMounted(() => {
  fetchImovelDetail();
});

function getPriceLabel(imovel: any): string {
  if (imovel.status === 'A_VENDA') return 'Valor de Venda';
  if (imovel.status === 'PARA_ALUGAR') return 'Valor do Aluguel';
  return 'Valor';
}

function formatarPreco(imovel: any) {
  if (imovel.status === 'A_VENDA' && imovel.valor_venda) {
    return parseFloat(imovel.valor_venda).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
  if (imovel.status === 'PARA_ALUGAR' && imovel.valor_aluguel) {
    return `${parseFloat(imovel.valor_aluguel).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })} /mês`;
  }
  return 'A consultar';
}
</script>

<style scoped>
/* REMOVIDO: @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'); */
/* O FontAwesome agora é carregado via main.ts para evitar erros de build */

.imovel-detail-container {
  margin: 2rem auto;
  padding: 0 2rem;
}
.imovel-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2.5rem;
  align-items: flex-start;
}
.main-column {
}
.info-sidebar {
    position: sticky;
    top: 2rem;
}
.sidebar-box {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    overflow: hidden;
}
.imovel-title {
  font-size: 1.8rem; 
  font-weight: bold;
  margin-top: 0;
  margin-bottom: 0.25rem;
  line-height: 1.2;
}
.imovel-location {
  color: #6c757d;
  margin-bottom: 1.5rem;
  font-size: 1.0rem; 
}
.gallery {
  margin-bottom: 2rem;
}
.main-image {
  width: 100%;
  height: auto;
  max-height: 400px; 
  object-fit: contain; 
  background-color: #e9ecef;
  border-radius: 8px;
  margin-bottom: 1rem;
  cursor: pointer;
}
.thumbnail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.5rem;
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
.imovel-ref {
    color: #6c757d;
    font-size: 0.9rem;
    background-color: #f8f9fa;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e9ecef;
}
.price-box {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}
.price-label {
    font-size: 1rem;
    color: #6c757d;
    margin-top: 0;
}
.imovel-price {
  font-size: 2.0rem; 
  font-weight: bold;
  color: #007bff;
  margin: 0;
}
.imovel-condo, .imovel-iptu {
  margin: 0.25rem 0 0 0;
  color: #6c757d;
}
.contact-form-section {
    padding: 1.5rem;
}
.contact-form-section h3 { margin-top: 0; }
.contact-form-section form { display: flex; flex-direction: column; gap: 0.75rem; }
.contact-form-section input,
.contact-form-section textarea,
.contact-form-section button {
    width: 100%; padding: 10px; border-radius: 4px; border: 1px solid #ccc; font-size: 1rem;
}
.contact-form-section button { background-color: #28a745; color: white; font-weight: bold; cursor: pointer; }
.success-message { color: #28a745; text-align: center; font-weight: bold; }

.details-section {
  margin-bottom: 2.5rem;
}
.details-section h2 {
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 1.4rem; 
}
.description-text {
    line-height: 1.7;
    white-space: pre-wrap;
}
.highlights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1.5rem;
    text-align: center;
}
.highlight-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.highlight-item i {
    font-size: 1.6rem; 
    color: var(--primary-color);
}
.features-list {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.75rem 1.5rem;
}
.features-list li {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid var(--primary-color);
}
.features-list li span {
  font-weight: bold;
  color: #343a40;
}

.loading-message, .error-message {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
}

.image-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.image-modal-content {
  max-width: 90%;
  max-height: 90%;
}
.image-modal-content img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.modal-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  font-size: 3rem;
  cursor: pointer;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  user-select: none;
}
.prev-btn {
  left: 20px;
}
.next-btn {
  right: 20px;
}

@media (max-width: 992px) {
    .imovel-detail-container {
        padding: 0 1rem;
    }
    .imovel-content {
        display: flex;
        flex-direction: column;
    }
    .main-column {
        order: 1;
    }
    .info-sidebar {
        order: 2;
        position: static;
        width: 100%;
    }
}

@media (max-width: 576px) {
    .imovel-title {
        font-size: 1.6rem; 
    }
    .imovel-price {
        font-size: 1.8rem;
    }
    .highlights-grid, .features-list {
        grid-template-columns: 1fr 1fr;
    }
    .imovel-detail-container {
        margin-top: 1rem;
    }
}
</style>
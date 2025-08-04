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
      
      <div class="contato-section">
        <h3>Ficou interessado? Contacte-nos!</h3>

        <div v-if="contatoEnviado" class="success-message">
          A sua mensagem foi enviada com sucesso! Entraremos em contacto em breve.
        </div>

        <form v-else @submit.prevent="handleContatoSubmit" class="contato-form">
          <div class="form-group">
            <label for="nome">Nome</label>
            <input type="text" id="nome" v-model="contato.nome" required />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="contato.email" required />
          </div>
          <div class="form-group">
            <label for="telefone">Telefone (Opcional)</label>
            <input type="tel" id="telefone" v-model="contato.telefone" />
          </div>
          <div class="form-group form-group-full">
            <label for="mensagem">Mensagem</label>
            <textarea id="mensagem" v-model="contato.mensagem" rows="5" required></textarea>
          </div>
          <button type="submit" :disabled="isSubmittingContato" class="btn-submit">
            {{ isSubmittingContato ? 'A enviar...' : 'Enviar Mensagem' }}
          </button>
        </form>
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

// NOVOS ESTADOS PARA O FORMULÁRIO DE CONTATO
const contato = ref({
  imovel: 0,
  nome: '',
  email: '',
  telefone: '',
  mensagem: `Olá, tenho interesse neste imóvel (${route.params.id}) e gostaria de mais informações.`
});
const isSubmittingContato = ref(false);
const contatoEnviado = ref(false);


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
    // Atribuímos o ID do imóvel ao nosso formulário
    if (response.data) {
        contato.value.imovel = response.data.id;
    }
  } catch (err) {
    console.error("Erro ao buscar detalhes do imóvel:", err);
    error.value = 'Não foi possível carregar os detalhes deste imóvel.';
  } finally {
    isLoading.value = false;
  }
}

// NOVA FUNÇÃO PARA SUBMETER O CONTATO
async function handleContatoSubmit() {
  isSubmittingContato.value = true;
  try {
    await publicApiClient.post('/v1/imoveis/contatos/', contato.value);
    contatoEnviado.value = true; // Mostra a mensagem de sucesso
  } catch (err) {
    console.error("Erro ao enviar mensagem:", err);
    alert('Ocorreu um erro ao enviar a sua mensagem. Por favor, tente novamente.');
  } finally {
    isSubmittingContato.value = false;
  }
}

onMounted(() => {
  fetchImovel();
});

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
  gap: 2rem;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  grid-template-columns: 2fr 1fr;
  /* Adicionamos uma nova linha no grid para o formulário */
  grid-template-rows: auto auto; 
}
@media (max-width: 992px) {
  .imovel-detail-container {
    grid-template-columns: 1fr;
  }
}
.gallery {
  grid-column: 1 / 2;
  grid-row: 1 / 2;
}
.details {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
  padding-left: 1rem;
}
@media (max-width: 992px) {
  .gallery, .details {
    grid-column: 1 / -1;
  }
  .details {
    padding-left: 0;
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

/* NOVOS ESTILOS PARA O FORMULÁRIO */
.contato-section {
  grid-column: 1 / -1; /* Ocupa a largura total */
  grid-row: 2 / 3;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}
.contato-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group-full {
  grid-column: 1 / -1;
}
label {
  margin-bottom: 0.5rem;
  font-weight: 500;
}
input, textarea {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.btn-submit {
  grid-column: 1 / -1;
  background-color: #28a745;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}
.btn-submit:disabled {
  background-color: #a3d9b1;
}
.success-message {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  padding: 1rem;
  border-radius: 5px;
  text-align: center;
}
</style>
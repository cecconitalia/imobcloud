<template>
  <div class="ai-chat-search">
    <form @submit.prevent="submitSearch" class="search-form">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Descreva o imóvel que procura..."
        class="search-input"
        :disabled="isLoading"
      />
      <button type="submit" class="search-button" :disabled="isLoading">
        <span v-if="!isLoading">Buscar</span>
        <span v-else class="spinner"></span>
      </button>
    </form>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import publicApiClient from '@/services/publicApiClient'; // Usa o cliente público

const searchQuery = ref('');
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);

// Define os eventos que este componente pode emitir
const emit = defineEmits(['search-results', 'search-error']);

async function submitSearch() {
  if (!searchQuery.value.trim()) {
    errorMessage.value = 'Por favor, descreva o imóvel que procura.';
    return;
  }

  isLoading.value = true;
  errorMessage.value = null;

  try {
    // 1. Obter o subdomínio (mesma lógica usada em PublicHomeView e PublicLayout)
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    let subdomain = null;
    if (parts.length > 1 && parts[0] !== 'www') {
      subdomain = parts[0];
    }
    if (subdomain === 'localhost' || !subdomain) {
        subdomain = 'estilomusical'; // Fallback para desenvolvimento
    }

    if (!subdomain) {
        throw new Error("Não foi possível identificar a imobiliária (subdomínio).");
    }

    // 2. Montar os parâmetros da query string
    const params = { subdomain };

    // 3. Fazer a requisição POST para a URL CORRETA
    // CORREÇÃO: Removido o prefixo '/v1/' da URL.
    // O publicApiClient já tem a baseURL 'http://localhost:8000'.
    const response = await publicApiClient.post(
        '/public/imoveis/busca-ia/', // URL CORRETA, sem /v1/
        { query: searchQuery.value }, // Corpo da requisição (payload)
        { params } // Query parameters (para o subdomínio)
    );

    // 4. Emitir o evento com os resultados
    emit('search-results', response.data); // Emite { mensagem: '...', imoveis: [...] }

  } catch (err: any) {
    console.error("Erro na busca por IA:", err);
    let errorMsg = 'Ocorreu um erro ao processar a sua busca. Tente novamente.';
    if (err.response && err.response.data && err.response.data.error) {
        errorMsg = err.response.data.error; // Mostra a mensagem de erro específica da API (Gemini ou validação)
    } else if (err.message) {
        errorMsg = err.message;
    }
    errorMessage.value = errorMsg;
    emit('search-error', errorMsg); // Emite evento de erro
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.ai-chat-search {
  margin: 1.5rem 0; /* Adicionado margem superior/inferior */
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
}

.search-form {
  display: flex;
  gap: 0.5rem; /* Reduzido o espaço */
  align-items: center; /* Alinha verticalmente */
}

.search-input {
  flex-grow: 1;
  padding: 0.8rem 1rem; /* Aumentado o padding */
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:focus {
  border-color: var(--primary-color, #007bff);
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  outline: none;
}

.search-button {
  padding: 0.8rem 1.5rem; /* Aumentado o padding */
  background-color: var(--primary-color, #007bff);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s ease, opacity 0.2s ease;
  display: flex; /* Para centralizar o spinner */
  align-items: center;
  justify-content: center;
  min-width: 80px; /* Largura mínima para evitar encolhimento com spinner */
  height: 44px; /* Altura fixa igual ao input */
}

.search-button:hover:not(:disabled) {
  background-color: #0056b3; /* Cor um pouco mais escura no hover */
}

.search-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  margin-top: 0.75rem;
  font-size: 0.9rem;
  text-align: center;
}

/* Spinner animation */
.spinner {
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-left-color: #fff;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
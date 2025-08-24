<template>
  <div class="ai-chat-widget">
    <div class="chat-header">
      <i class="fas fa-microchip animated-robot"></i>
      <div class="header-text-container">
        <h3 class="animated-text">{{ dynamicHeaderText }}</h3>
        <div class="animated-tips-wrapper">
          <transition-group name="fade" mode="out-in" tag="div" class="animated-tips-container">
            <p v-for="tip in visibleTips" :key="tip" class="search-tip">{{ tip }}</p>
          </transition-group>
        </div>
      </div>
    </div>
    
    <div class="chat-input-form">
      <input type="text" v-model="currentMessage" placeholder="Descreva o imóvel que procura..." :disabled="isWaitingForAI" @keyup.enter="sendMessage" />
      <button type="button" @click="sendMessage" :disabled="!currentMessage || isWaitingForAI">
        <i v-if="isWaitingForAI" class="fas fa-spinner fa-spin"></i>
        <i v-else class="fas fa-paper-plane"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import publicApiClient from '@/services/publicApiClient';

const emit = defineEmits(['searchResults']);

const currentMessage = ref('');
const isWaitingForAI = ref(false);

const headerTexts = [
  "Agente ImobBot", 
  "Como posso ajudar?", 
  "Qual imóvel você busca?", 
  "Agente ImobBot está online"
];
const dynamicHeaderText = ref(headerTexts[0]);
let textIndex = 0;

const searchTips = [
  "Ex: 'Apartamento com 2 quartos e piscina'.",
  "Refine: '3 quartos e aceita pet'.",
  "Termos: 'móveis planejados' ou 'financiável'."
];
const visibleTips = ref([searchTips[0]]);
let tipIndex = 0;

function animateHeaderText() {
  setInterval(() => {
    textIndex = (textIndex + 1) % headerTexts.length;
    dynamicHeaderText.value = headerTexts[textIndex];
  }, 4000);
}

function animateTips() {
  setInterval(() => {
    tipIndex = (tipIndex + 1) % searchTips.length;
    visibleTips.value = [searchTips[tipIndex]];
  }, 5000);
}

onMounted(() => {
  animateHeaderText();
  animateTips();
});

async function sendMessage() {
  if (!currentMessage.value) return;

  const userText = currentMessage.value;
  currentMessage.value = '';
  isWaitingForAI.value = true;
  
  const hostname = window.location.hostname;
  const parts = hostname.split('.');
  let subdomain = null;
  if (parts.length > 1 && parts[0] !== 'www' && parts[0] !== 'localhost') {
    subdomain = parts[0];
  } else {
    subdomain = 'estilomusical'; 
  }

  try {
    const response = await publicApiClient.post(`/v1/public/imoveis/busca-ia/?subdomain=${subdomain}`, { query: userText });
    
    // CORREÇÃO: Emite a resposta completa, incluindo a mensagem da IA
    emit('searchResults', response.data);

  } catch (error: any) {
    console.error("Erro na busca por IA:", error.response?.data || error);
  } finally {
    isWaitingForAI.value = false;
  }
}
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Transição de fade para as dicas */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-leave-active {
  position: absolute;
}

.ai-chat-widget {
  width: 100%;
  max-width: 600px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  margin: 0 auto;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  min-height: 60px;
  border-radius: 12px 12px 0 0;
  gap: 1rem;
  background-color: transparent;
  color: #343a40;
}

.header-text-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Alinha o texto à esquerda */
  flex-grow: 1;
  position: relative;
  min-height: 40px; /* Garante que o container não encolha */
}

.chat-header h3 {
  margin: 0;
  font-size: 1.2rem;
  white-space: nowrap;
}

.animated-tips-wrapper {
  position: relative;
  overflow: hidden;
  width: 100%;
  min-height: 20px;
}

.animated-tips-container {
  display: flex;
}

.search-tip {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
  white-space: nowrap;
}

.animated-robot {
  font-size: 1.8rem;
  color: #007bff;
  animation: pulse 2s infinite ease-in-out;
}

.chat-input-form {
  display: flex;
  border-top: 1px solid #e9ecef;
  padding: 1rem;
  gap: 0.5rem;
  background-color: #fff;
  border-radius: 0 0 12px 12px;
}

.chat-input-form input {
  flex-grow: 1;
  border: 1px solid #ced4da;
  border-radius: 20px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.chat-input-form input:focus {
  outline: none;
  border-color: #007bff;
}

.chat-input-form button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.chat-input-form button:hover {
  background-color: #0056b3;
}

.chat-input-form button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .ai-chat-widget {
    width: 90vw;
  }
}
</style>
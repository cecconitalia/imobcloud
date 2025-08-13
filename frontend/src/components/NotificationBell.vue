<template>
  <div class="notification-bell" @click="toggleDropdown">
    <i class="fas fa-bell"></i>
    <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
    
    <div v-if="isDropdownOpen" class="notification-dropdown">
      <div v-if="isLoading" class="dropdown-item">A carregar...</div>
      <div v-else-if="notificacoes.length === 0" class="dropdown-item">Nenhuma notificação nova.</div>
      <div v-else>
        <div v-for="notificacao in notificacoes" :key="notificacao.id" class="dropdown-item" @click="handleNotificationClick(notificacao)">
          <p>{{ notificacao.mensagem }}</p>
          <small>{{ formatDistanceToNow(new Date(notificacao.data_criacao), { addSuffix: true, locale: ptBR }) }}</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Notificacao {
  id: number;
  mensagem: string;
  lida: boolean;
  data_criacao: string;
  link: string | null;
}

const isDropdownOpen = ref(false);
const notificacoes = ref<Notificacao[]>([]);
const unreadCount = ref(0);
const isLoading = ref(false);
const router = useRouter();

async function fetchNotificacoes() {
  isLoading.value = true;
  try {
    // A CORREÇÃO ESTÁ AQUI: URL corrigido para remover a palavra 'core'
    const response = await apiClient.get('/v1/corretores/minhas-notificacoes/');
    notificacoes.value = response.data;
    unreadCount.value = response.data.filter((n: Notificacao) => !n.lida).length;
  } catch (error) {
    console.error("Erro ao carregar notificações:", error);
  } finally {
    isLoading.value = false;
  }
}

async function marcarComoLida(notificacaoId: number) {
  try {
    // A CORREÇÃO ESTÁ AQUI: URL corrigido para remover a palavra 'core'
    await apiClient.post(`/v1/notificacoes/${notificacaoId}/marcar-como-lida/`);
    fetchNotificacoes(); // Recarrega as notificações
  } catch (error) {
    console.error("Erro ao marcar notificação como lida:", error);
  }
}

function handleNotificationClick(notificacao: Notificacao) {
  marcarComoLida(notificacao.id);
  if (notificacao.link) {
    router.push(notificacao.link);
  }
  isDropdownOpen.value = false;
}

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value;
  if (isDropdownOpen.value) {
    fetchNotificacoes();
  }
}

onMounted(() => {
  fetchNotificacoes();
  // Opcional: recarregar a cada minuto
  setInterval(fetchNotificacoes, 60000);
});
</script>

<style scoped>
.notification-bell {
  position: relative;
  cursor: pointer;
  color: #333;
}
.fa-bell {
  font-size: 1.5rem;
}
.notification-badge {
  position: absolute;
  top: -5px;
  right: -10px;
  background-color: red;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 0.7rem;
  font-weight: bold;
}
.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 300px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 100;
}
.dropdown-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}
.dropdown-item:last-child {
  border-bottom: none;
}
.dropdown-item p {
  margin: 0;
  font-size: 0.9rem;
}
.dropdown-item small {
  color: #999;
}
</style>
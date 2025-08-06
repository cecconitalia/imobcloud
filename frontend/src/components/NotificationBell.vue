<template>
  <div class="notification-bell" @click="toggleDropdown">
    <i class="icon-bell"></i>
    <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
    
    <div v-if="isDropdownOpen" class="notification-dropdown" @click.stop>
      <div class="dropdown-header">
        Notificações
      </div>
      <div v-if="isLoading" class="loading-message">Carregando...</div>
      <div v-else-if="notifications.length === 0" class="no-notifications">
        Nenhuma nova notificação.
      </div>
      <ul v-else class="notification-list">
        <li v-for="notification in notifications" :key="notification.id" @click="handleNotificationClick(notification)" class="notification-item">
          <p>{{ notification.mensagem }}</p>
          <small>{{ formatRelativeTime(notification.data_criacao) }}</small>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

const notifications = ref<any[]>([]);
const isLoading = ref(false);
const isDropdownOpen = ref(false);
const router = useRouter();
let intervalId: number | null = null;

const unreadCount = computed(() => notifications.value.length);

async function fetchNotifications() {
  if (document.hidden) return;

  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/core/corretores/minhas-notificacoes/');
    notifications.value = response.data;
  } catch (error) {
    console.error("Erro ao buscar notificações:", error);
  } finally {
    isLoading.value = false;
  }
}

function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value;
  if (isDropdownOpen.value) {
    fetchNotifications();
  }
}

async function handleNotificationClick(notification: any) {
  try {
    // ATUALIZADO: Chamando o endpoint correto na NotificacaoViewSet
    await apiClient.post(`/v1/core/notificacoes/${notification.id}/marcar-como-lida/`);
    
    // Remove a notificação da lista local para feedback imediato
    notifications.value = notifications.value.filter(n => n.id !== notification.id);

    if (notification.link) {
      router.push(notification.link);
    }
    
    isDropdownOpen.value = false;

  } catch (error) {
    console.error('Erro ao marcar notificação como lida:', error);
  }
}

function formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return `${Math.floor(interval)} ano(s) atrás`;
    interval = seconds / 2592000;
    if (interval > 1) return `${Math.floor(interval)} mês(es) atrás`;
    interval = seconds / 86400;
    if (interval > 1) return `${Math.floor(interval)} dia(s) atrás`;
    interval = seconds / 3600;
    if (interval > 1) return `${Math.floor(interval)} hora(s) atrás`;
    interval = seconds / 60;
    if (interval > 1) return `${Math.floor(interval)} minuto(s) atrás`;
    return "agora mesmo";
}

onMounted(() => {
  fetchNotifications();
  intervalId = window.setInterval(fetchNotifications, 60000);
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});
</script>

<style scoped>
/* Estilos permanecem os mesmos */
.notification-bell {
  position: relative;
  cursor: pointer;
  display: flex;
  align-items: center;
  height: 100%;
}
.icon-bell {
  font-size: 1.5rem;
  color: #333;
}
.notification-badge {
  position: absolute;
  top: 10px;
  right: -8px;
  background-color: #e74c3c;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 0.75rem;
  font-weight: bold;
}
.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 350px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  margin-top: 10px;
  color: #333;
  border: 1px solid #eee;
}
.dropdown-header {
  padding: 1rem;
  font-weight: bold;
  border-bottom: 1px solid #f0f0f0;
}
.loading-message, .no-notifications {
  padding: 1.5rem;
  text-align: center;
  color: #6c757d;
}
.notification-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}
.notification-item {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}
.notification-item:last-child {
  border-bottom: none;
}
.notification-item:hover {
  background-color: #f8f9fa;
}
.notification-item p {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
}
.notification-item small {
  color: #007bff;
  font-size: 0.75rem;
}
</style>
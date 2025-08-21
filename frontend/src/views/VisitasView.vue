<template>
  <div class="visitas-container">
    <header class="view-header">
      <h1>Gerir Visitas</h1>
      <router-link to="/visitas/nova" class="btn-primary">
        + Agendar Visita
      </router-link>
    </header>

    <div v-if="isLoading" class="loading-message">A carregar visitas...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="visitas.length > 0" class="visitas-list">
      <div v-for="visita in visitas" :key="visita.id" class="visita-card">
        <div class="visita-info">
          <p class="visita-data">
            <i class="fas fa-calendar-alt"></i>
            {{ formatarDataHora(visita.data_hora_visita) }}
          </p>
          <p class="visita-cliente">
            <i class="fas fa-user"></i>
            {{ visita.cliente_obj?.nome_completo || 'Cliente não informado' }}
          </p>
          <p class="visita-imovel">
            <i class="fas fa-home"></i>
            {{ visita.imovel_obj?.endereco || 'Imóvel não informado' }}
          </p>
        </div>
        <div class="visita-actions">
          <router-link :to="`/visitas/editar/${visita.id}`" class="btn-action edit-btn">
            <i class="fas fa-edit"></i>
          </router-link>
          <button @click="handleDeletar(visita.id)" class="btn-action delete-btn">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="!isLoading && visitas.length === 0 && !error" class="no-data-message">
      <p>Nenhuma visita agendada.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

const visitas = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

function formatarDataHora(dataHora: string) {
  const data = new Date(dataHora);
  return data.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
}

async function fetchVisitas() {
  isLoading.value = true;
  try {
    // AQUI ESTÁ A CORREÇÃO: URL alterada para o endpoint correto
    const response = await apiClient.get('/v1/visitas/');
    visitas.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar visitas:", err);
    error.value = 'Não foi possível carregar as visitas.';
  } finally {
    isLoading.value = false;
  }
}

async function handleDeletar(visitaId: number) {
  if (!window.confirm('Tem a certeza de que deseja deletar este agendamento?')) {
    return;
  }
  try {
    // AQUI ESTÁ A CORREÇÃO: URL alterada para o endpoint correto
    await apiClient.delete(`/v1/visitas/${visitaId}/`);
    visitas.value = visitas.value.filter(v => v.id !== visitaId);
    alert('Agendamento deletado com sucesso!');
  } catch (error) {
    console.error("Erro ao deletar agendamento:", error);
    alert("Ocorreu um erro ao tentar deletar o agendamento.");
  }
}

onMounted(() => {
  fetchVisitas();
});
</script>

<style scoped>
.visitas-container {
  padding: 2rem;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  border: none;
  cursor: pointer;
}
.loading-message, .error-message, .no-data-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.visitas-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.visita-card {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.visita-info p {
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.visita-info i {
  color: #007bff;
  width: 20px;
  text-align: center;
}
.visita-data {
  font-weight: bold;
}
.visita-actions {
  display: flex;
  gap: 0.5rem;
}
.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #6c757d;
  cursor: pointer;
  transition: background-color 0.2s;
  text-decoration: none;
}
.btn-action i {
  font-size: 1rem;
}
.edit-btn:hover {
  background-color: #ffc107;
  color: #333;
}
.delete-btn:hover {
  background-color: #dc3545;
  color: white;
}
</style>
<template>
  <div class="visitas-container">
    <header class="view-header">
      <h1>Agenda de Visitas</h1>
      <router-link to="/visitas/nova" class="btn-primary">
        + Agendar Nova Visita
      </router-link>
    </header>

    <div v-if="isLoading">A carregar visitas...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="visitas.length > 0">
      <thead>
        <tr>
          <th>Imóvel</th>
          <th>Cliente</th>
          <th>Data e Hora</th>
          <th>Status</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="visita in visitas" :key="visita.id">
          <td>{{ visita.imovel_obj?.endereco || 'N/A' }}</td>
          <td>{{ visita.cliente_obj?.nome_completo || 'N/A' }}</td>
          <td>{{ formatarData(visita.data_hora) }}</td>
          <td>{{ visita.status }}</td>
          <td class="actions-cell">
            <router-link :to="`/visitas/editar/${visita.id}`" class="btn-secondary">
              Editar
            </router-link>
            <button v-if="userCargo === 'ADMIN'" @click="handleCancelar(visita.id)" class="btn-danger">
              Cancelar
            </button>
          </td>
        </tr>
      </tbody>
    </table>
     <div v-if="!isLoading && visitas.length === 0 && !error">
      <p>Nenhuma visita encontrada.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const visitas = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const userCargo = ref(''); // NOVO: Estado para guardar o cargo do utilizador

async function fetchVisitas() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/clientes/visitas/');
    visitas.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar visitas:", err);
    error.value = 'Não foi possível carregar a agenda de visitas.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchVisitas();
  // NOVO: Lê o cargo do localStorage quando a página é carregada
  userCargo.value = localStorage.getItem('userCargo') || '';
});

async function handleCancelar(visitaId: number) {
  if (!window.confirm('Tem a certeza de que deseja cancelar esta visita?')) {
    return;
  }
  try {
    await apiClient.patch(`/v1/clientes/visitas/${visitaId}/`, { status: 'Cancelada' });
    await fetchVisitas();
  } catch (error) {
    console.error("Erro ao cancelar visita:", error);
    alert("Ocorreu um erro ao tentar cancelar a visita.");
  }
}

function formatarData(data: string) {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  };
  return new Date(data).toLocaleString('pt-BR', options);
}
</script>

<style scoped>
/* Estilos podem ser reutilizados de outras views */
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
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
  vertical-align: middle;
}
th {
  background-color: #f2f2f2;
}
.error-message {
  color: red;
}
.actions-cell {
  display: flex;
  gap: 0.5rem;
}
.btn-secondary, .btn-danger {
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9em;
  border: none;
  cursor: pointer;
}
.btn-secondary { background-color: #6c757d; }
.btn-danger { background-color: #dc3545; }
</style>
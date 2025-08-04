<template>
  <div class="contactos-container">
    <header class="view-header">
      <h1>Contactos Recebidos</h1>
    </header>

    <div v-if="isLoading" class="loading-message">Carregando contactos...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="contactos.length > 0">
      <thead>
        <tr>
          <th>Imóvel</th>
          <th>Nome</th>
          <th>Email</th>
          <th>Telefone</th>
          <th>Mensagem</th>
          <th>Data</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="contacto in contactos" :key="contacto.id">
          <td>{{ contacto.imovel_obj?.endereco || 'N/A' }} ({{ contacto.imovel_obj?.tipo || 'N/A' }})</td>
          <td>{{ contacto.nome }}</td>
          <td>{{ contacto.email }}</td>
          <td>{{ contacto.telefone || 'Não informado' }}</td>
          <td>{{ contacto.mensagem }}</td>
          <td>{{ formatarData(contacto.data_contato) }}</td>
          <td class="actions-cell">
            <button class="btn-secondary" @click="handleResponder(contacto)">Responder</button>
            <button class="btn-info" @click="handleArquivar(contacto)">Arquivar</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!isLoading && contactos.length === 0 && !error" class="no-data-message">
      <p>Nenhum contacto encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const contactos = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchContactos() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/imoveis/contatos/');
    contactos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contactos:", err);
    error.value = 'Não foi possível carregar os contactos.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchContactos();
});

function formatarData(data: string) {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  };
  return new Date(data).toLocaleString('pt-BR', options);
}

// Funções de ação (apenas de exemplo)
function handleResponder(contacto: any) {
  alert(`Ação de responder para ${contacto.email}.`);
}

function handleArquivar(contacto: any) {
  alert(`Ação de arquivar o contacto de ${contacto.nome}.`);
  // Futuramente, você pode implementar a lógica para marcar o contacto como "arquivado" no backend.
}
</script>

<style scoped>
.contactos-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
th, td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
  vertical-align: middle;
}
th {
  background-color: #f2f2f2;
}
.loading-message, .no-data-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
  text-align: center;
  padding: 2rem;
}
.actions-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.btn-secondary, .btn-info {
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9em;
  border: none;
  cursor: pointer;
}
.btn-secondary {
  background-color: #6c757d;
}
.btn-info {
  background-color: #17a2b8;
}
</style>
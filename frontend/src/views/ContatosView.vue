<template>
  <div class="contatos-container">
    <header class="view-header">
      <h1>Contatos Recebidos</h1>
    </header>

    <div v-if="isLoading" class="loading-message">Carregando contatos...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="contatos.length > 0">
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
        <tr v-for="contato in contatos" :key="contato.id">
          <td>{{ contato.imovel_obj?.endereco || 'N/A' }} ({{ contato.imovel_obj?.tipo || 'N/A' }})</td>
          <td>{{ contato.nome }}</td>
          <td>{{ contato.email }}</td>
          <td>{{ contato.telefone || 'Não informado' }}</td>
          <td>{{ contato.mensagem }}</td>
          <td>{{ formatarData(contato.data_contato) }}</td>
          <td class="actions-cell">
            <button class="btn-secondary" @click="handleResponder(contato)">Responder</button>
            <button class="btn-info" @click="handleArquivar(contato)">Arquivar</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!isLoading && contatos.length === 0 && !error" class="no-data-message">
      <p>Nenhum contato encontrado.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const contatos = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchContatos() {
  isLoading.value = true;
  try {
    // CORREÇÃO: URL alterada para o caminho correto
    const response = await apiClient.get('/v1/contatos/');
    contatos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contatos:", err);
    error.value = 'Não foi possível carregar os contatos.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchContatos();
});

function formatarData(data: string) {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  };
  return new Date(data).toLocaleString('pt-BR', options);
}

// Funções de ação (apenas de exemplo)
function handleResponder(contato: any) {
  alert(`Ação de responder para ${contato.email}.`);
}

function handleArquivar(contato: any) {
  if (!window.confirm(`Tem a certeza de que deseja arquivar o contato de ${contato.nome}?`)) {
    return;
  }
  try {
    // CORREÇÃO: URL alterada para o caminho correto
    apiClient.post(`/v1/contatos/${contato.id}/arquivar/`).then(() => {
        contatos.value = contatos.value.filter(c => c.id !== contato.id);
    });
  } catch(err) {
    alert(`Ocorreu um erro ao arquivar o contato de ${contato.nome}.`);
  }
}
</script>

<style scoped>
.contatos-container {
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
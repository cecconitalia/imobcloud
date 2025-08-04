<template>
  <div class="contratos-container">
    <header class="view-header">
      <h1>Meus Contratos</h1>
      <router-link to="/contratos/novo" class="btn-primary">
        + Adicionar Contrato
      </router-link>
    </header>

    <div v-if="isLoading">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <table v-if="contratos.length > 0">
      <thead>
        <tr>
          <th>Imóvel</th>
          <th>Cliente</th>
          <th>Tipo</th>
          <th>Status</th>
          <th>Ações</th> </tr>
      </thead>
      <tbody>
        <tr v-for="contrato in contratos" :key="contrato.id">
          <td>{{ contrato.imovel_obj?.endereco || 'N/A' }}</td>
          <td>{{ contrato.cliente_obj?.nome_completo || 'N/A' }}</td>
          <td>{{ contrato.tipo_contrato }}</td>
          <td>{{ contrato.status_contrato }}</td>
          <td class="actions-cell">
            <router-link :to="`/contratos/editar/${contrato.id}`" class="btn-secondary">
              Editar
            </router-link>
            <button @click="handleInativar(contrato.id)" class="btn-danger">
              Inativar
            </button>
          </td>
        </tr>
      </tbody>
    </table>
     <div v-if="!isLoading && contratos.length === 0 && !error">
      <p>Nenhum contrato cadastrado ainda.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const contratos = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchContratos() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/contratos/contratos/');
    contratos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contratos:", err);
    error.value = 'Não foi possível carregar os contratos.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchContratos();
});

// ## LÓGICA DE INATIVAÇÃO ADICIONADA ##
async function handleInativar(contratoId: number) {
  if (!window.confirm('Tem a certeza de que deseja inativar este contrato?')) {
    return;
  }

  try {
    // Chama o endpoint DELETE. O backend irá interpretar isto como uma inativação.
    await apiClient.delete(`/v1/contratos/contratos/${contratoId}/`);

    // Remove o contrato da lista no frontend para uma atualização instantânea da UI.
    contratos.value = contratos.value.filter(contrato => contrato.id !== contratoId);
  } catch (error) {
    console.error("Erro ao inativar contrato:", error);
    alert("Ocorreu um erro ao tentar inativar o contrato.");
  }
}
</script>

<style scoped>
/* Estilos podem ser reutilizados */
.contratos-container {
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
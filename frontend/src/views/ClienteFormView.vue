<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Cliente' : 'Adicionar Novo Cliente' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do cliente...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="cliente-form">
      <div class="form-group">
        <label for="nome_completo">Nome Completo</label>
        <input type="text" id="nome_completo" v-model="cliente.nome_completo" required />
      </div>
      <div class="form-group">
        <label for="cpf_cnpj">CPF ou CNPJ</label>
        <input type="text" id="cpf_cnpj" v-model="cliente.cpf_cnpj" required />
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" v-model="cliente.email" required />
      </div>
      <div class="form-group">
        <label for="telefone">Telefone</label>
        <input type="tel" id="telefone" v-model="cliente.telefone" required />
      </div>

      <div class="form-group full-width">
        <label for="preferencias">Preferências do Imóvel (opcional)</label>
        <textarea id="preferencias" v-model="cliente.preferencias_imovel" rows="4"></textarea>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Guardando...' : 'Guardar Cliente' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();

// Determina se estamos em modo de edição com base no parâmetro 'id' do URL
const clienteId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!clienteId.value);

const cliente = ref({
  nome_completo: '',
  cpf_cnpj: '',
  email: '',
  telefone: '',
  preferencias_imovel: '',
});

// Controlo de estados da UI
const isLoadingData = ref(false);
const isSubmitting = ref(false);

// Função para buscar os dados de um cliente existente
async function fetchClienteData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/clientes/clientes/${clienteId.value}/`);
      cliente.value = response.data; // Preenche o formulário com os dados da API
    } catch (error) {
      console.error("Erro ao buscar dados do cliente:", error);
      alert("Não foi possível carregar os dados do cliente para edição.");
      router.push({ name: 'clientes' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

// Quando o componente é montado, verifica se precisa de buscar dados
onMounted(() => {
  fetchClienteData();
});

// Função de submissão que agora lida com criar (POST) e editar (PUT)
async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      // MODO EDIÇÃO: Usa o método PUT para atualizar o cliente existente
      await apiClient.put(`/v1/clientes/clientes/${clienteId.value}/`, cliente.value);
    } else {
      // MODO CRIAÇÃO: Usa o método POST para criar um novo cliente
      await apiClient.post('/v1/clientes/clientes/', cliente.value);
    }
    router.push({ name: 'clientes' }); // Redireciona para a lista após o sucesso
  } catch (error) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o cliente. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'clientes' });
}
</script>

<style scoped>
/* Estilos podem ser reutilizados de outros formulários */
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.cliente-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; flex: 1 1 calc(50% - 1.5rem); }
.form-group.full-width { flex-basis: 100%; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.loading-message { text-align: center; padding: 2rem; }
</style>
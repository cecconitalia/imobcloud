<template>
  <div class="form-container">
    <header class="view-header">
      <h1>Adicionar Nova Oportunidade</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="oportunidade-form">
      <div class="form-group full-width">
        <label for="titulo">Título da Oportunidade</label>
        <input type="text" id="titulo" v-model="oportunidade.titulo" placeholder="Ex: Venda do apartamento X para o cliente Y" required />
      </div>

      <div class="form-group">
        <label for="cliente">Cliente</label>
        <select id="cliente" v-model="oportunidade.cliente" required>
          <option disabled value="">Selecione um cliente</option>
          <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
            {{ cliente.nome_completo }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="imovel">Imóvel de Interesse (opcional)</label>
        <select id="imovel" v-model="oportunidade.imovel">
          <option :value="null">Nenhum</option>
          <option v-for="imovel in imoveis" :key="imovel.id" :value="imovel.id">
            {{ imovel.endereco }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="valor_estimado">Valor Estimado (R$)</label>
        <input type="number" step="0.01" id="valor_estimado" v-model="oportunidade.valor_estimado" />
      </div>

      <div class="form-group">
        <label for="responsavel">Corretor Responsável</label>
        <select id="responsavel" v-model="oportunidade.responsavel">
          <option :value="null">Ninguém</option>
          <option v-for="corretor in corretores" :key="corretor.id" :value="corretor.id">
            {{ corretor.username }}
          </option>
        </select>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A Guardar...' : 'Criar Oportunidade' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';

const router = useRouter();

// Estado para o formulário
const oportunidade = ref({
  titulo: '',
  cliente: '',
  imovel: null,
  valor_estimado: null,
  responsavel: null,
  fase: 'LEAD'
});

// Estados para carregar dados dos dropdowns
const clientes = ref<any[]>([]);
const imoveis = ref<any[]>([]);
const corretores = ref<any[]>([]); // NOVO: Estado para a lista de corretores
const isLoadingData = ref(true);
const isSubmitting = ref(false);

// ATUALIZADO: Busca agora também os corretores
async function fetchDropdownData() {
  isLoadingData.value = true;
  try {
    const [clientesResponse, imoveisResponse, corretoresResponse] = await Promise.all([
      apiClient.get('/v1/clientes/clientes/'),
      apiClient.get('/v1/imoveis/imoveis/'),
      apiClient.get('/v1/core/corretores/') // NOVO: Chamada ao novo endpoint
    ]);
    clientes.value = clientesResponse.data;
    imoveis.value = imoveisResponse.data;
    corretores.value = corretoresResponse.data; // NOVO: Guardar os corretores
  } catch (error) {
    console.error("Erro ao carregar dados para o formulário:", error);
    alert('Não foi possível carregar os dados necessários para o formulário.');
  } finally {
    isLoadingData.value = false;
  }
}

onMounted(() => {
  fetchDropdownData();
});

// Lida com a submissão do formulário
async function handleSubmit() {
  isSubmitting.value = true;
  try {
    await apiClient.post('/v1/clientes/oportunidades/', oportunidade.value);
    router.push({ name: 'funil-vendas' });
  } catch (error) {
    console.error("Erro ao criar oportunidade:", error.response?.data || error);
    alert('Ocorreu um erro ao criar a oportunidade. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'funil-vendas' });
}
</script>

<style scoped>
/* Estilos podem ser reutilizados de outros formulários */
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.oportunidade-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; flex: 1 1 calc(50% - 1.5rem); }
.form-group.full-width { flex-basis: 100%; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, select { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.loading-message { text-align: center; padding: 2rem; }
</style>
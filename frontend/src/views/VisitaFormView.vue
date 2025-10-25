<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Agendamento' : 'Agendar Nova Visita' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados para o agendamento...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="visita-form">
      <div class="form-group">
        <label for="cliente">Cliente</label>
        <select id="cliente" v-model="visita.cliente" required>
          <option disabled :value="null">Selecione um cliente</option>
          <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
            {{ cliente.nome_completo }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="imovel">Imóvel</label>
        <select id="imovel" v-model="visita.imovel" required>
          <option disabled :value="null">Selecione um imóvel</option>
          <option v-for="imovel in imoveis" :key="imovel.id" :value="imovel.id">
            {{ imovel.endereco }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="data_hora_visita">Data e Hora da Visita</label>
        <input type="datetime-local" id="data_hora_visita" v-model="visita.data_hora_visita" required />
      </div>
      
      <div class="form-group full-width">
        <label for="observacoes">Observações (opcional)</label>
        <textarea id="observacoes" v-model="visita.observacoes" rows="4"></textarea>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Guardando...' : 'Guardar Agendamento' }}
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

const visitaId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!visitaId.value);

const visita = ref({
  cliente: null as number | null,
  imovel: null as number | null,
  data_hora_visita: '',
  observacoes: '',
});

const clientes = ref<any[]>([]);
const imoveis = ref<any[]>([]);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchDropdownData() {
  try {
    const [clientesResponse, imoveisResponse] = await Promise.all([
      apiClient.get('/v1/clientes/'),
      apiClient.get('/v1/imoveis/')
    ]);
    clientes.value = clientesResponse.data;
    imoveis.value = imoveisResponse.data;
  } catch (error) {
    console.error("Erro ao carregar dados para o formulário:", error);
    alert('Não foi possível carregar os imóveis e clientes.');
  }
}

async function fetchVisitaData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      // AQUI ESTÁ A CORREÇÃO: URL alterada para o endpoint correto
      const response = await apiClient.get(`/v1/visitas/${visitaId.value}/`);
      visita.value = { 
        ...response.data,
        cliente: response.data.cliente?.id || null,
        imovel: response.data.imovel?.id || null,
      };
    } catch (error) {
      console.error("Erro ao buscar dados da visita:", error);
      alert("Não foi possível carregar os dados da visita para edição.");
      router.push({ name: 'visitas' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

onMounted(async () => {
  isLoadingData.value = true;
  await fetchDropdownData();
  await fetchVisitaData();
  isLoadingData.value = false;
});

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      // AQUI ESTÁ A CORREÇÃO: URL alterada para o endpoint correto
      await apiClient.put(`/v1/visitas/${visitaId.value}/`, visita.value);
    } else {
      // AQUI ESTÁ A CORREÇÃO: URL alterada para o endpoint correto
      await apiClient.post('/v1/visitas/', visita.value);
    }
    router.push({ name: 'visitas' });
  } catch (error: any) {
    console.error("Erro ao guardar o agendamento:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o agendamento. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'visitas' });
}
</script>

<style scoped>
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.visita-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; flex: 1 1 calc(50% - 1.5rem); }
.form-group.full-width { flex-basis: 100%; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, select, textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.loading-message { text-align: center; padding: 2rem; }
</style>
<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Oportunidade' : 'Adicionar Nova Oportunidade' }}</h1>
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
        <label for="fonte">Fonte do Lead</label>
        <select id="fonte" v-model="oportunidade.fonte">
          <option :value="null">Não informada</option>
          <option value="SITE">Site</option>
          <option value="INDICACAO">Indicação</option>
          <option value="ANUNCIO">Anúncio Online</option>
          <option value="CLIENTE_ANTIGO">Cliente Antigo</option>
          <option value="OUTRO">Outro</option>
        </select>
      </div>

      <div class="form-group">
        <label for="probabilidade">Probabilidade de Fechamento (%)</label>
        <input type="number" id="probabilidade" v-model="oportunidade.probabilidade" min="0" max="100" />
      </div>
      <div class="form-group">
        <label for="data_proximo_contato">Data do Próximo Contato</label>
        <input type="date" id="data_proximo_contato" v-model="oportunidade.data_proximo_contato" />
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

      <div v-if="oportunidade.fase === 'PERDIDO'" class="form-group full-width">
        <label for="motivo_perda">Motivo da Perda</label>
        <textarea id="motivo_perda" v-model="oportunidade.motivo_perda" rows="3" placeholder="Descreva por que este negócio foi perdido..."></textarea>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A Guardar...' : (isEditing ? 'Guardar Alterações' : 'Criar Oportunidade') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const router = useRouter();
const route = useRoute();

const oportunidadeId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!oportunidadeId.value);

// ATUALIZADO: Adicionados os novos campos com valores padrão
const oportunidade = ref({
  titulo: '',
  cliente: '',
  imovel: null,
  valor_estimado: null,
  responsavel: null,
  fase: 'LEAD',
  // Novos campos
  fonte: null,
  probabilidade: 10,
  data_proximo_contato: null,
  motivo_perda: ''
});

const clientes = ref<any[]>([]);
const imoveis = ref<any[]>([]);
const corretores = ref<any[]>([]);
const isLoadingData = ref(true);
const isSubmitting = ref(false);

async function fetchData() {
  isLoadingData.value = true;
  try {
    // Busca os dados dos dropdowns
    const [clientesResponse, imoveisResponse, corretoresResponse] = await Promise.all([
      apiClient.get('/v1/clientes/clientes/'),
      apiClient.get('/v1/imoveis/imoveis/'),
      apiClient.get('/v1/core/corretores/')
    ]);
    clientes.value = clientesResponse.data;
    imoveis.value = imoveisResponse.data;
    corretores.value = corretoresResponse.data;

    // Se estiver a editar, busca os dados da oportunidade
    if (isEditing.value) {
      const oportunidadeResponse = await apiClient.get(`/v1/clientes/oportunidades/${oportunidadeId.value}/`);
      oportunidade.value = oportunidadeResponse.data;
    }

  } catch (error) {
    console.error("Erro ao carregar dados:", error);
    alert('Não foi possível carregar os dados necessários.');
  } finally {
    isLoadingData.value = false;
  }
}

onMounted(() => {
  fetchData();
});

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/clientes/oportunidades/${oportunidadeId.value}/`, oportunidade.value);
    } else {
      await apiClient.post('/v1/clientes/oportunidades/', oportunidade.value);
    }
    router.push({ name: 'funil-vendas' });
  } catch (error) {
    console.error("Erro ao guardar oportunidade:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar a oportunidade. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'funil-vendas' });
}
</script>

<style scoped>
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.oportunidade-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
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
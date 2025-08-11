<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Contrato' : 'Adicionar Novo Contrato' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do contrato...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="contrato-form">
      <div class="form-group">
        <label for="imovel">Imóvel</label>
        <select id="imovel" v-model="contrato.imovel" required>
          <option disabled value="">Selecione um imóvel</option>
          <option v-for="imovel in imoveis" :key="imovel.id" :value="imovel.id">
            {{ imovel.endereco }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="cliente">Cliente</label>
        <select id="cliente" v-model="contrato.cliente" required>
          <option disabled value="">Selecione um cliente</option>
          <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
            {{ cliente.nome_completo }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="tipo_contrato">Tipo de Contrato</label>
        <select id="tipo_contrato" v-model="contrato.tipo_contrato" required>
          <option value="Venda">Venda</option>
          <option value="Aluguel">Aluguel</option>
        </select>
      </div>
       <div class="form-group">
        <label for="status_contrato">Status do Contrato</label>
        <select id="status_contrato" v-model="contrato.status_contrato" required>
          <option value="Ativo">Ativo</option>
          <option value="Concluído">Concluído</option>
          <option value="Rescindido">Rescindido</option>
          <option value="Pendente">Pendente</option>
        </select>
      </div>

      <div class="form-group">
        <label for="data_inicio">Data de Início</label>
        <input type="date" id="data_inicio" v-model="contrato.data_inicio" required />
      </div>
      <div class="form-group">
        <label for="data_fim">Data de Fim</label>
        <input type="date" id="data_fim" v-model="contrato.data_fim" />
      </div>

       <div class="form-group">
        <label for="data_assinatura">Data de Assinatura</label>
        <input type="date" id="data_assinatura" v-model="contrato.data_assinatura" required />
      </div>
      <div class="form-group">
        <label for="valor_total">Valor Total (R$)</label>
        <input type="number" step="0.01" id="valor_total" v-model="contrato.valor_total" required />
      </div>
      
      <div class="form-group full-width">
        <label for="condicoes_pagamento">Condições de Pagamento</label>
        <textarea id="condicoes_pagamento" v-model="contrato.condicoes_pagamento" rows="4" required></textarea>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Guardando...' : 'Guardar Contrato' }}
        </button>
      </div>
    </form>

    <ContratoFinanceiro
      v-if="isEditing && contrato.tipo_contrato === 'Aluguel'"
      :contrato="contrato"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import ContratoFinanceiro from '@/components/ContratoFinanceiro.vue';

const route = useRoute();
const router = useRouter();

const contratoId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!contratoId.value);

const contrato = ref({
  imovel: '',
  cliente: '',
  tipo_contrato: 'Venda',
  data_inicio: '',
  data_fim: '',
  data_assinatura: '',
  condicoes_pagamento: '',
  valor_total: null,
  status_contrato: 'Ativo',
  pagamentos: []
});

const imoveis = ref<any[]>([]);
const clientes = ref<any[]>([]);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchDropdownData() {
  try {
    const [imoveisResponse, clientesResponse] = await Promise.all([
      apiClient.get('/v1/imoveis/imoveis/'),
      apiClient.get('/v1/clientes/clientes/')
    ]);
    imoveis.value = imoveisResponse.data;
    clientes.value = clientesResponse.data;
  } catch (error) {
    console.error("Erro ao carregar dados para o formulário:", error);
    alert('Não foi possível carregar os imóveis e clientes.');
  }
}

async function fetchContratoData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/contratos/contratos/${contratoId.value}/`);
      contrato.value = response.data;
    } catch (error) {
      console.error("Erro ao buscar dados do contrato:", error);
      alert("Não foi possível carregar os dados do contrato para edição.");
      router.push({ name: 'contratos' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

onMounted(async () => {
  isLoadingData.value = true;
  await fetchDropdownData();
  await fetchContratoData();
  isLoadingData.value = false;
});

// ATUALIZADO: A função de submissão agora limpa os dados antes de enviar
async function handleSubmit() {
  isSubmitting.value = true;
  
  // Prepara um objeto "limpo" apenas com os campos que o backend espera
  const payload = {
    imovel: contrato.value.imovel,
    cliente: contrato.value.cliente,
    tipo_contrato: contrato.value.tipo_contrato,
    data_inicio: contrato.value.data_inicio,
    data_fim: contrato.value.data_fim,
    data_assinatura: contrato.value.data_assinatura,
    valor_total: contrato.value.valor_total,
    condicoes_pagamento: contrato.value.condicoes_pagamento,
    status_contrato: contrato.value.status_contrato,
  };

  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/contratos/contratos/${contratoId.value}/`, payload);
    } else {
      await apiClient.post('/v1/contratos/contratos/', payload);
    }
    router.push({ name: 'contratos' });
  } catch (error) {
    console.error("Erro ao guardar o contrato:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o contrato. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'contratos' });
}
</script>

<style scoped>
/* Os seus estilos continuam os mesmos */
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.contrato-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
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
<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Contrato' : 'Adicionar Novo Contrato' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do contrato...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="contrato-form">
      <div class="tabs">
        <button type="button" @click="activeTab = 'dados'" :class="{ active: activeTab === 'dados' }">Dados Principais</button>
        <button type="button" @click="activeTab = 'valores'" :class="{ active: activeTab === 'valores' }">Valores e Informações</button>
      </div>

      <div class="tab-content">
        <div v-show="activeTab === 'dados'" class="form-grid">
          <div class="form-group">
            <label for="imovel">Imóvel</label>
            <v-select
              id="imovel"
              label="titulo_anuncio"
              :options="imoveis"
              v-model="contrato.imovel"
              placeholder="Pesquise por um imóvel..."
              :reduce="option => option.id"
              required
            ></v-select>
          </div>

          <div class="form-group">
            <label for="inquilino">Inquilino / Comprador</label>
            <v-select
              id="inquilino"
              label="nome_completo"
              :options="clientes"
              v-model="contrato.inquilino"
              placeholder="Pesquise por um cliente..."
              :reduce="option => option.id"
              :required="contrato.tipo_contrato === 'Aluguel'"
            ></v-select>
          </div>
          
          <div class="form-group">
            <label for="proprietario">Proprietário / Vendedor</label>
            <v-select
              id="proprietario"
              label="nome_completo"
              :options="clientes"
              v-model="contrato.proprietario"
              placeholder="Pesquise por um cliente..."
              :reduce="option => option.id"
              :required="contrato.tipo_contrato === 'Aluguel'"
            ></v-select>
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
            <label for="data_assinatura">Data de Assinatura</label>
            <input type="date" id="data_assinatura" v-model="contrato.data_assinatura" required />
          </div>

          <div class="form-group">
            <label for="data_inicio">Data de Início da Vigência</label>
            <input type="date" id="data_inicio" v-model="contrato.data_inicio" required />
          </div>

          <div v-if="contrato.tipo_contrato === 'Aluguel'" class="form-group">
            <label for="duracao_meses">Duração (meses)</label>
            <input type="number" id="duracao_meses" v-model="contrato.duracao_meses" min="1" required />
          </div>

          <div class="form-group">
            <label for="data_fim">Data de Fim da Vigência</label>
            <input type="date" id="data_fim" v-model="contrato.data_fim" />
          </div>
        </div>

        <div v-show="activeTab === 'valores'" class="form-grid">
          <div class="form-group">
            <label for="valor_total">Valor Total (Venda) ou Mensal (Aluguel) (R$)</label>
            <input type="number" step="0.01" id="valor_total" v-model="contrato.valor_total" required />
          </div>
          
          <div class="form-group full-width">
            <label for="formas_pagamento">Formas de Pagamento Aceitas</label>
            <v-select
                id="formas_pagamento"
                multiple
                :options="formasPagamento"
                label="nome"
                v-model="contrato.formas_pagamento"
                placeholder="Selecione uma ou mais opções"
                :reduce="option => option.id"
            ></v-select>
          </div>
          
          <div class="form-group full-width">
            <label for="informacoes_adicionais">Informações Adicionais (Opcional)</label>
            <textarea id="informacoes_adicionais" v-model="contrato.informacoes_adicionais" rows="4"></textarea>
          </div>
        </div>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Guardando...' : 'Guardar Contrato' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const route = useRoute();
const router = useRouter();

const contratoId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!contratoId.value);
const activeTab = ref('dados');

// ==========================================================================================
// <<< CORREÇÃO APLICADA NO OBJETO DO CONTRATO >>>
const criarContratoVazio = () => ({
  id: null as number | null,
  imovel: null as number | null,
  inquilino: null as number | null,
  proprietario: null as number | null,
  tipo_contrato: 'Venda',
  data_inicio: '',
  data_assinatura: new Date().toISOString().split('T')[0],
  data_fim: '',
  duracao_meses: 12,
  valor_total: null,
  status_contrato: 'Ativo',
  pagamentos: [],
  formas_pagamento: [] as number[],
  informacoes_adicionais: '', // 'condicoes_pagamento' foi removido e este adicionado
});
// ==========================================================================================

const contrato = ref(criarContratoVazio());

const imoveis = ref<any[]>([]);
const clientes = ref<any[]>([]);
const formasPagamento = ref<any[]>([]);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchDropdownData() {
  try {
    const [imoveisResponse, clientesResponse, formasPagamentoResponse] = await Promise.all([
      apiClient.get('/v1/imoveis/'),
      apiClient.get('/v1/clientes/'),
      apiClient.get('/v1/financeiro/formas-pagamento/')
    ]);
    imoveis.value = imoveisResponse.data;
    clientes.value = clientesResponse.data;
    formasPagamento.value = formasPagamentoResponse.data;
  } catch (error) {
    console.error("Erro ao carregar dados para o formulário:", error);
    alert('Não foi possível carregar os imóveis, clientes e formas de pagamento.');
  }
}

async function fetchContratoData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/contratos/${contratoId.value}/`);
      const formasPagamentoIds = response.data.formas_pagamento.map((fp: any) => fp.id);
      
      contrato.value = {
        ...criarContratoVazio(),
        ...response.data,
        id: response.data.id,
        imovel: response.data.imovel?.id || null,
        inquilino: response.data.inquilino?.id || null,
        proprietario: response.data.proprietario?.id || null,
        formas_pagamento: formasPagamentoIds,
      };
    } catch (error) {
      console.error("Erro ao buscar dados do contrato:", error);
      alert("Não foi possível carregar os dados do contrato para edição.");
      router.push({ name: 'contratos' });
    } finally {
      isLoadingData.value = false;
    }
  } else {
    contrato.value = criarContratoVazio();
  }
}

watch(() => route.params.id, () => {
    fetchContratoData();
}, { immediate: true });

onMounted(async () => {
  isLoadingData.value = true;
  await fetchDropdownData();
  await fetchContratoData();
  isLoadingData.value = false;
});

watch(() => contrato.value.data_inicio, (novaData) => {
  if (novaData && contrato.value.tipo_contrato === 'Aluguel' && contrato.value.duracao_meses) {
    const dataInicio = new Date(novaData);
    dataInicio.setMonth(dataInicio.getMonth() + contrato.value.duracao_meses);
    contrato.value.data_fim = dataInicio.toISOString().split('T')[0];
  }
});

watch(() => contrato.value.duracao_meses, (novaDuracao) => {
  if (contrato.value.data_inicio && contrato.value.tipo_contrato === 'Aluguel' && novaDuracao) {
    const dataInicio = new Date(contrato.value.data_inicio);
    dataInicio.setMonth(dataInicio.getMonth() + novaDuracao);
    contrato.value.data_fim = dataInicio.toISOString().split('T')[0];
  }
});

async function handleSubmit() {
  isSubmitting.value = true;
  
  // ==========================================================================================
  // <<< CORREÇÃO APLICADA NO PAYLOAD DE ENVIO >>>
  const payload = {
    imovel: contrato.value.imovel,
    inquilino: contrato.value.inquilino,
    proprietario: contrato.value.proprietario,
    tipo_contrato: contrato.value.tipo_contrato,
    data_inicio: contrato.value.data_inicio,
    data_fim: contrato.value.data_fim,
    duracao_meses: contrato.value.duracao_meses,
    data_assinatura: contrato.value.data_assinatura,
    valor_total: contrato.value.valor_total,
    status_contrato: contrato.value.status_contrato,
    formas_pagamento: contrato.value.formas_pagamento,
    informacoes_adicionais: contrato.value.informacoes_adicionais,
  };
  // ==========================================================================================

  try {
    let response;
    if (isEditing.value) {
      response = await apiClient.put(`/v1/contratos/${contratoId.value}/`, payload);
    } else {
      response = await apiClient.post('/v1/contratos/', payload);
    }
    if (!isEditing.value && response && response.data?.id) {
        router.push({ name: 'contrato-editar', params: { id: response.data.id } });
    } else {
        router.push({ name: 'contratos' });
    }
  } catch (error: any) {
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
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.tabs { display: flex; border-bottom: 2px solid #ccc; margin-bottom: 1.5rem; width: 100%; }
.tabs button { padding: 10px 20px; border: none; background: none; cursor: pointer; font-size: 1rem; font-weight: 500; color: #6c757d; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tabs button.active { color: #007bff; border-bottom-color: #007bff; font-weight: bold; }
.tab-content { width: 100%; }
.contrato-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; width: 100%;}
.form-group { display: flex; flex-direction: column; }
.form-group.full-width { grid-column: 1 / -1; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, select, textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.loading-message { text-align: center; padding: 2rem; }
:deep(.vs__dropdown-toggle) {
    padding: 6px;
}
</style>
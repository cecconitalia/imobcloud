<template>
  <div class="page-container-form">
    <form @submit.prevent="handleSubmit" class="form-card">
      <div class="form-header">
        <h2>{{ isEditing ? 'Editar Contrato' : 'Novo Contrato' }}</h2>
        <router-link :to="{ name: 'contratos' }" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i> Voltar para Lista
        </router-link>
      </div>

      <div v-if="isLoading" class="loading-message">
        <div class="spinner"></div>
        A carregar dados...
      </div>

      <div v-if="!isLoading">
        <fieldset class="form-section">
          <legend>Partes do Contrato</legend>
          <div class="form-grid-2col">
            <div class="form-group">
              <label for="proprietario">Proprietário / Locador *</label>
              <v-select
                id="proprietario"
                v-model="contrato.proprietario_id"
                :options="proprietarioOptions" 
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione o proprietário (lista filtrada)"
                :clearable="false"
              ></v-select>
            </div>

            <div class="form-group">
              <label for="inquilino">{{ tipoContratoLabel.outraParte }} *</label>
              <v-select
                id="inquilino"
                v-model="contrato.inquilino_id"
                :options="clienteOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione o inquilino/comprador (lista completa)"
                :clearable="false"
              ></v-select>
            </div>
            
            <div class="form-group" v-if="contrato.tipo_contrato === 'ALUGUEL'">
              <label for="fiadores">Fiadores</label>
              <v-select
                id="fiadores"
                v-model="contrato.fiadores"
                :options="clienteOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione um ou mais fiadores (lista completa)"
                multiple
              ></v-select>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>Objeto (Imóvel)</legend>
          <div class="form-group">
            <label for="imovel">Imóvel *</label>
            <v-select
              id="imovel"
              v-model="contrato.imovel_id"
              :options="imovelOptions"
              :reduce="(option) => option.value"
              label="label"
              placeholder="Selecione um proprietário primeiro"
              :clearable="false"
              :disabled="!contrato.proprietario_id || isCarregandoImoveis"
            >
              <template #no-options>
                <span v-if="!contrato.proprietario_id">Selecione um proprietário para carregar os imóveis.</span>
                <span v-else>Nenhum imóvel encontrado para este proprietário.</span>
              </template>
            </v-select>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>Termos e Valores</legend>
          <div class="form-grid-3col">
            <div class="form-group">
              <label for="tipo_contrato">Tipo de Contrato *</label>
              <v-select
                id="tipo_contrato"
                v-model="contrato.tipo_contrato"
                :options="opcoesTipoContrato"
                :clearable="false"
              ></v-select>
            </div>
            
            <div class="form-group">
              <label for="status_contrato">Status do Contrato *</label>
              <v-select
                id="status_contrato"
                v-model="contrato.status_contrato"
                :options="opcoesStatusContrato"
                :clearable="false"
              ></v-select>
            </div>

            <div class="form-group">
              <label for="data_assinatura">Data da Assinatura</label>
              <input type="date" id="data_assinatura" v-model="contrato.data_assinatura" />
            </div>

            <div class="form-group">
              <label for="data_inicio">Data de Início *</label>
              <input type="date" id="data_inicio" v-model="contrato.data_inicio" required />
            </div>

            <div class="form-group" v-if="contrato.tipo_contrato === 'ALUGUEL'">
              <label for="duracao_meses">Duração (meses) *</label>
              <input type="number" id="duracao_meses" v-model.number="contrato.duracao_meses" placeholder="Ex: 30" />
            </div>
            
            <div class="form-group" v-if="contrato.tipo_contrato === 'ALUGUEL'">
              <label for="data_fim">Data de Fim</label>
              <input type="date" id="data_fim" v-model="contrato.data_fim" />
            </div>

            <div class="form-group" v-if="contrato.tipo_contrato === 'ALUGUEL'">
              <label for="aluguel">Valor do Aluguel (R$) *</label>
              <input
                type="text"
                id="aluguel"
                v-model.lazy="contrato.aluguel_formatado"
                v-money="moneyConfig"
                class="form-input-money"
              />
            </div>
            
            <div class="form-group" v-if="contrato.tipo_contrato === 'VENDA'">
              <label for="valor_total">Valor Total da Venda (R$) *</label>
              <input
                type="text"
                id="valor_total"
                v-model.lazy="contrato.valor_total_formatado"
                v-money="moneyConfig"
                class="form-input-money"
              />
            </div>
            
            <div class="form-group form-group-span-2" v-if="contrato.tipo_contrato === 'VENDA'">
              <label for="formas_pagamento">Formas de Pagamento (Venda)</label>
              <v-select
                id="formas_pagamento"
                v-model="contrato.formas_pagamento"
                :options="formaPagamentoOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione as formas de pagamento"
                multiple
              ></v-select>
            </div>
            
          </div>
        </fieldset>
        
        <fieldset class="form-section">
          <legend>Cláusulas Personalizadas e Observações</legend>
            <div class="form-group">
              <label>Cláusulas Adicionais</label>
              <QuillEditor
                theme="snow"
                v-model:content="contrato.conteudo_personalizado"
                contentType="html"
                placeholder="Insira aqui cláusulas extras, observações ou termos que devem constar no PDF do contrato."
                style="height: 250px; background-color: white;"
              />
            </div>
            
          <div class="form-group" style="margin-top: 5rem;">
            <label for="informacoes_adicionais">Observações Internas (Não sai no contrato)</label>
            <textarea
              id="informacoes_adicionais"
              v-model="contrato.informacoes_adicionais"
              rows="4"
              placeholder="Anotações para controle interno..."
            ></textarea>
          </div>
        </fieldset>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="isSaving || isLoading">
          <span v-if="isSaving"><i class="fas fa-spinner fa-spin"></i> Salvando...</span>
          <span v-else><i class="fas fa-save"></i> Salvar Contrato</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient from '@/services/api';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

// Importação de componentes ricos
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';

// Importação do v-money3
import money from 'v-money3';
const vMoney = money.directive; 

// Utilitário de data (usado no watch)
import { addMonths } from 'date-fns';

// Interfaces
interface ContratoFormData {
  id?: number;
  tipo_contrato: 'ALUGUEL' | 'VENDA';
  status_contrato: 'PENDENTE' | 'ATIVO' | 'CONCLUIDO' | 'RESCINDIDO' | 'INATIVO';
  imovel_id: number | null;
  inquilino_id: number | null;
  proprietario_id: number | null;
  fiadores: number[]; // M2M
  formas_pagamento: number[]; // M2M
  
  valor_total_formatado: string; 
  aluguel_formatado: string;     

  duracao_meses: number | null;
  data_inicio: string;
  data_fim: string | null;
  data_assinatura: string | null;
  conteudo_personalizado: string;
  informacoes_adicionais: string;
}

interface SelectOption {
  label: string;
  value: number;
}

// Configurações e Estado
const router = useRouter();
const route = useRoute();
const toast = useToast();

const contrato = ref<ContratoFormData>({
  tipo_contrato: 'ALUGUEL',
  status_contrato: 'PENDENTE',
  imovel_id: null,
  inquilino_id: null,
  proprietario_id: null,
  fiadores: [],
  formas_pagamento: [],
  
  valor_total_formatado: '', 
  aluguel_formatado: '',

  duracao_meses: 30,
  data_inicio: new Date().toISOString().split('T')[0],
  data_fim: null,
  data_assinatura: null,
  conteudo_personalizado: '',
  informacoes_adicionais: '',
});

// Listas de dados separadas
const clienteOptions = ref<SelectOption[]>([]); 
const proprietarioOptions = ref<SelectOption[]>([]); 
const formaPagamentoOptions = ref<SelectOption[]>([]);
const imovelOptions = ref<SelectOption[]>([]); 

const isLoading = ref(true);
const isSaving = ref(false);
const isCarregandoImoveis = ref(false); 
const isEditing = computed(() => !!route.params.id);


// Opções Estáticas
const opcoesTipoContrato = ['ALUGUEL', 'VENDA'];
const opcoesStatusContrato = ['PENDENTE', 'ATIVO', 'CONCLUIDO', 'RESCINDIDO', 'INATIVO'];

// Configuração do v-money3
const moneyConfig = {
  decimal: ',',
  thousands: '.',
  prefix: 'R$ ',
  suffix: '',
  precision: 2,
  masked: false,
};

// Labels dinâmicos
const tipoContratoLabel = computed(() => {
  if (contrato.value.tipo_contrato === 'VENDA') {
    return { outraParte: 'Comprador' };
  }
  return { outraParte: 'Inquilino' };
});

// ******************************************************************
// FUNÇÃO-CHAVE: Converte a string de dinheiro em número
// ******************************************************************
const parseMoney = (value: string | number | null | undefined): number | null => {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === 'number') {
    return isNaN(value) ? null : value;
  }
  
  const numericString = String(value)
    .replace('R$', '')
    .replace(/\./g, '')  // Remove separador de milhar
    .replace(',', '.')  // Substitui vírgula decimal
    .trim();
    
  if (numericString === "") {
    return null;
  }
    
  const parsed = parseFloat(numericString);
  if (parsed === 0) return 0;
  
  return isNaN(parsed) ? null : parsed;
};


// Limpa campos incompatíveis ao trocar o tipo de contrato
watch(() => contrato.value.tipo_contrato, (newType) => {
  if (newType === 'VENDA') {
    contrato.value.aluguel_formatado = '';
    contrato.value.duracao_meses = null;
    contrato.value.data_fim = null;
    contrato.value.fiadores = [];
  } else {
    contrato.value.valor_total_formatado = '';
    contrato.value.formas_pagamento = [];
    contrato.value.duracao_meses = 30; // Valor padrão
  }
});

// Lógica de carregamento de Imóveis por Proprietário
watch(() => contrato.value.proprietario_id, (newPropId, oldPropId) => {
  if (oldPropId) {
    contrato.value.imovel_id = null;
  }
  
  imovelOptions.value = [];
  
  if (newPropId) {
    loadImoveis(newPropId);
  }
});

function loadImoveis(proprietarioId: number) {
  isCarregandoImoveis.value = true;
  return apiClient.get<SelectOption[]>(`/v1/imoveis/lista-simples/?proprietario_id=${proprietarioId}`)
    .then(response => {
      imovelOptions.value = response.data; 
    })
    .catch(error => {
      console.error("Erro ao carregar imóveis do proprietário:", error);
      toast.error("Não foi possível carregar os imóveis deste proprietário.");
    })
    .finally(() => {
      isCarregandoImoveis.value = false;
    });
}

// Carregamento inicial de dados (Clientes, Proprietários, Formas de Pagamento)
async function loadDropdownData() {
  try {
    const [todosClientesRes, proprietariosRes, formasRes] = await Promise.all([
      apiClient.get('/v1/clientes/lista-simples/'), 
      apiClient.get('/v1/clientes/lista_proprietarios/'), 
      apiClient.get('/v1/financeiro/formas-pagamento/')
    ]);
    
    clienteOptions.value = todosClientesRes.data.map((cli: any) => ({
      label: `${cli.nome_display} (${cli.documento || 'N/D'})`,
      value: cli.id,
    }));
    
    proprietarioOptions.value = proprietariosRes.data.map((cli: any) => ({
      label: `${cli.nome_display} (${cli.documento || 'N/D'})`,
      value: cli.id,
    }));
    
    formaPagamentoOptions.value = formasRes.data.map((fp: any) => ({
        label: fp.nome,
        value: fp.id
    }));
    
  } catch (error) { 
    console.error("Erro ao carregar dados para dropdowns:", error);
    toast.error("Falha ao carregar opções do formulário.");
  }
}


async function loadContrato(id: string | string[]) {
   try {
    const { data } = await apiClient.get(`/v1/contratos/${id}/`);
    
    const proprietarioId = data.proprietario_detalhes?.id || data.proprietario;
    if (proprietarioId) {
        await loadImoveis(proprietarioId);
    }
    
    contrato.value = {
      ...data, 
      id: data.id,
      imovel_id: data.imovel_detalhes?.id || data.imovel,
      inquilino_id: data.inquilino_detalhes?.id || data.inquilino,
      proprietario_id: proprietarioId,
      fiadores: data.fiadores || [], 
      formas_pagamento: data.formas_pagamento || [],
      
      aluguel_formatado: data.aluguel || '', 
      valor_total_formatado: data.valor_total || '',
      
      duracao_meses: data.duracao_meses || 30,
      data_inicio: data.data_inicio ? data.data_inicio.split('T')[0] : '',
      data_fim: data.data_fim ? data.data_fim.split('T')[0] : null,
      data_assinatura: data.data_assinatura ? data.data_assinatura.split('T')[0] : null,
      conteudo_personalizado: data.conteudo_personalizado || '',
      informacoes_adicionais: data.informacoes_adicionais || '',
    };
    
  } catch (error) {
    console.error("Erro ao carregar contrato:", error);
    toast.error("Não foi possível carregar os dados do contrato.");
    router.push({ name: 'contratos' });
  }
}

// Watcher para calcular Data de Fim automaticamente para ALUGUEL
watch([() => contrato.value.data_inicio, () => contrato.value.duracao_meses, () => contrato.value.tipo_contrato], ([novaDataInicio, novaDuracao, novoTipo]) => {
  if (novoTipo === 'ALUGUEL' && novaDataInicio && novaDuracao && novaDuracao > 0) {
    try {
        const dataInicio = new Date(novaDataInicio + 'T00:00:00'); 
        const dataFimCalculada = addMonths(dataInicio, novaDuracao);
        
        contrato.value.data_fim = dataFimCalculada.toISOString().split('T')[0];
    } catch (e) {
        contrato.value.data_fim = null;
    }
  } else if (novoTipo === 'VENDA') {
    contrato.value.duracao_meses = null;
  }
}, { immediate: true });


onMounted(async () => {
  isLoading.value = true;
  await loadDropdownData(); 
  if (isEditing.value) {
    await loadContrato(route.params.id as string); 
  }
  isLoading.value = false;
});

// Ação de Salvar
async function handleSubmit() {
  if (isSaving.value) return;
  isSaving.value = true;

  const tipoContratoUpper = contrato.value.tipo_contrato ? contrato.value.tipo_contrato.toUpperCase() : null;
  const statusContratoUpper = contrato.value.status_contrato ? contrato.value.status_contrato.toUpperCase() : null;

  const payload = {
      tipo_contrato: tipoContratoUpper,
      status_contrato: statusContratoUpper,
      imovel: contrato.value.imovel_id,
      inquilino: contrato.value.inquilino_id,
      proprietario: contrato.value.proprietario_id,
      fiadores: contrato.value.fiadores,
      formas_pagamento: contrato.value.formas_pagamento,
      
      // Converte a string formatada "R$ 1.200,00" para o número 1200.00
      valor_total: parseMoney(contrato.value.valor_total_formatado),
      aluguel: parseMoney(contrato.value.aluguel_formatado),
      
      duracao_meses: contrato.value.duracao_meses,
      data_inicio: contrato.value.data_inicio,
      data_fim: contrato.value.data_fim || null,
      data_assinatura: contrato.value.data_assinatura || null,
      conteudo_personalizado: contrato.value.conteudo_personalizado,
      informacoes_adicionais: contrato.value.informacoes_adicionais,
  };
  
  if (!payload.imovel || !payload.inquilino || !payload.proprietario) {
      toast.error("Proprietário, Inquilino/Comprador e Imóvel são obrigatórios.");
      isSaving.value = false;
      return;
  }

  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/contratos/${route.params.id}/`, payload);
      toast.success("Contrato atualizado com sucesso!");
      // CORREÇÃO: Redireciona para a lista após ATUALIZAR
      router.push({ name: 'contratos' }); 
    } else {
      const response = await apiClient.post('/v1/contratos/', payload);
      toast.success("Contrato criado com sucesso!");
      // CORREÇÃO: Redireciona para a lista após CRIAR (comportamento seguro)
      // Se você quiser redirecionar para a edição, precisará que o backend retorne o ID.
      // Por enquanto, voltamos para a lista.
      router.push({ name: 'contratos' });
    }
    
  } catch (error: any) {
    console.error("Erro ao salvar contrato:", error.response?.data || error);
    
    let errorMsg = "Ocorreu uma falha desconhecida ao salvar.";

    if (error.response && error.response.data) {
        const errors = error.response.data;
        
        if (errors.status_contrato && Array.isArray(errors.status_contrato)) {
            errorMsg = errors.status_contrato[0];
        } else if (errors.non_field_errors && Array.isArray(errors.non_field_errors)) {
            errorMsg = errors.non_field_errors[0];
        } else if (typeof errors === 'object' && errors !== null) {
            const firstErrorKey = Object.keys(errors)[0];
            if (Array.isArray(errors[firstErrorKey])) {
                errorMsg = `Erro no campo '${firstErrorKey}': ${errors[firstErrorKey][0]}`;
            } else {
                 errorMsg = `Erro(s) de validação: ${JSON.stringify(errors)}`;
            }
        } else if (typeof errors === 'string') {
             errorMsg = errors;
        }
    }
    
    toast.error(errorMsg, { duration: 7000 });
    
  } finally {
    isSaving.value = false;
  }
}
</script>

<style scoped>
/* Importar CSS do v-select e Quill */
@import 'vue-select/dist/vue-select.css';
@import '@vueup/vue-quill/dist/vue-quill.snow.css'; 

/* Estilos Globais da Página */
.page-container-form {
  max-width: 1000px;
  margin: 1rem auto;
  padding: 0 1rem;
}

.form-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 2rem;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}
.form-header h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #333;
}

/* Estilos de Botões */
.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0056b3;
}
.btn-primary:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}


/* Seções do Formulário */
.form-section {
  border: none;
  padding: 0;
  margin-bottom: 2rem;
}
.form-section legend {
  font-size: 1.2rem;
  font-weight: 600;
  color: #0056b3;
  margin-bottom: 1rem;
  padding: 0;
}

/* Grid Layout */
.form-grid-2col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}
.form-grid-3col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

/* Grupos de Formulário */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.form-group-span-2 {
  grid-column: span 2;
}

.form-group label {
  font-weight: 500;
  color: #495057;
}
.form-group input[type="text"],
.form-group input[type="date"],
.form-group input[type="number"],
.form-group textarea,
.form-group .form-input-money {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box; 
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}
.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

/* Estilização do v-select */
:deep(.vs__dropdown-toggle) {
  padding: 6px 8px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  background: white;
}
:deep(.vs__search:focus) {
  outline: none;
}
:deep(.vs--open .vs__dropdown-toggle) {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}
:deep(.vs__selected) {
  padding: 2px 6px;
  background-color: #e0eafc;
  border-color: #007bff;
  color: #004a99;
}
:deep(.vs__clear), :deep(.vs__open-indicator) {
  fill: #6c757d;
}

/* Ações do Formulário */
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

/* Loading */
.loading-message {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
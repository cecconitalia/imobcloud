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
          <div class="form-grid-3col">
            <div class="form-group">
              <label for="tipo">Tipo de Contrato *</label>
              <select id="tipo" v-model="contrato.tipo_contrato" :disabled="isEditing && contrato.status_contrato !== 'PENDENTE'" @change="handleTipoChange">
                <option value="ALUGUEL">Aluguel</option>
                <option value="VENDA">Venda</option>
              </select>
            </div>
            
            <div class="form-group" v-if="proprietarioOptions.length || contrato.proprietario !== null">
              <label for="proprietario">Proprietário / Locador *</label>
              <v-select
                id="proprietario"
                v-model="contrato.proprietario"
                :options="proprietarioOptions" 
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione o proprietário"
                :clearable="false"
              ></v-select>
            </div>
            <div v-else class="form-group"><input type="text" disabled placeholder="Carregando Proprietários..." /></div>


            <div class="form-group" v-if="todosClientesOptions.length">
              <label for="inquilino">{{ tipoContratoLabel.outraParte }} *</label>
              <v-select
                id="inquilino"
                v-model="contrato.inquilino"
                :options="todosClientesOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione a outra parte"
                :clearable="false"
              ></v-select>
            </div>
            <div v-else class="form-group"><input type="text" disabled :placeholder="`Carregando ${tipoContratoLabel.outraParte}s...`" /></div>
          </div>
          
          <div class="form-group" v-if="imovelOptions.length || contrato.imovel !== null">
            <label for="imovel">Imóvel *</label>
            <v-select
              id="imovel"
              v-model="contrato.imovel"
              :options="imovelOptions"
              :reduce="(option) => option.value"
              label="label"
              placeholder="Selecione o Imóvel"
              :clearable="false"
            ></v-select>
          </div>
          <div v-else class="form-group"><input type="text" disabled placeholder="Carregando Imóveis..." /></div>
        </fieldset>

        <fieldset v-if="contrato.tipo_contrato === 'ALUGUEL'" class="form-section">
          <legend>Termos do Aluguel</legend>
          <div class="form-grid-3col">
            <div class="form-group">
              <label for="aluguel">Valor do Aluguel (Mensal) *</label>
              <MoneyInput v-model.number="contrato.aluguel" class="form-input-money" required />
            </div>

            <div class="form-group">
              <label for="duracao_meses">Duração (meses) *</label>
              <input type="number" id="duracao_meses" v-model.number="contrato.duracao_meses" required min="1">
            </div>

            <div class="form-group">
              <label for="taxa_adm">Taxa Adm. (%)</label>
              <input type="number" id="taxa_adm" v-model.number="contrato.taxa_administracao_percentual" step="0.01" min="0" max="100">
              <p class="help-text">Usada no cálculo do repasse ao proprietário.</p>
            </div>
          </div>
          
          <div class="form-grid-2col">
            <div class="form-group">
              <label for="data_primeiro_vencimento">Data do 1º Vencimento *</label>
              <input type="date" id="data_primeiro_vencimento" v-model="contrato.data_primeiro_vencimento" required>
              <p class="help-text">A primeira parcela será gerada com esta data.</p>
            </div>
          </div>
        </fieldset>

        <fieldset v-if="contrato.tipo_contrato === 'VENDA'" class="form-section">
          <legend>Termos da Venda e Comissão</legend>
          <div class="form-grid-3col">
            <div class="form-group">
              <label for="valor_total">Valor Total da Venda *</label>
              <MoneyInput v-model.number="contrato.valor_total" class="form-input-money" @change="calcularComissaoInicial" required />
            </div>

            <div class="form-group">
              <label for="comissao_venda_percentual">% Comissão (Base)</label>
              <input type="number" id="comissao_venda_percentual" v-model.number="contrato.comissao_venda_percentual" @input="calcularComissaoInicial" step="0.01" min="0" max="100">
            </div>
            
            <div class="form-group">
              <label for="valor_comissao_acordado">Valor Acordado Comissão (R$) *</label>
              <MoneyInput v-model.number="contrato.valor_comissao_acordado" class="form-input-money" required />
              <p class="help-text">Este valor será lançado em Contas a Receber.</p>
            </div>
          </div>
          
          <div class="form-grid-2col">
            <div class="form-group">
                <label for="data_vencimento_venda">Data Venc. Comissão/Quitação *</label>
                <input type="date" id="data_vencimento_venda" v-model="contrato.data_vencimento_venda" required>
                <p class="help-text">Data para o lançamento da comissão (Contas a Receber).</p>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>Datas e Detalhes Adicionais</legend>
          <div class="form-grid-3col">
            <div class="form-group">
              <label for="data_inicio">Data de Início *</label>
              <input type="date" id="data_inicio" v-model="contrato.data_inicio" required>
            </div>
            <div class="form-group">
              <label for="data_assinatura">Data de Assinatura *</label>
              <input type="date" id="data_assinatura" v-model="contrato.data_assinatura" required>
            </div>
            <div class="form-group">
              <label for="data_fim">Data de Término (Opcional)</label>
              <input type="date" id="data_fim" v-model="contrato.data_fim">
            </div>
          </div>
          
          <div class="form-grid-2col">
            <div class="form-group" v-if="todosClientesOptions.length">
                <label for="fiadores">Fiadores (Opcional)</label>
                <v-select
                  id="fiadores"
                  v-model="contrato.fiadores"
                  :options="todosClientesOptions"
                  :reduce="(option) => option.value"
                  label="label"
                  placeholder="Selecione um ou mais fiadores"
                  multiple
                ></v-select>
            </div>
            <div v-else class="form-group"><input type="text" disabled placeholder="Carregando Fiadores..." /></div>

            <div class="form-group">
                <label for="status_contrato">Status do Contrato *</label>
                <select id="status_contrato" v-model="contrato.status_contrato" required>
                  <option value="PENDENTE">Pendente</option>
                  <option value="ATIVO">Ativo</option>
                  <option value="CONCLUIDO">Concluído</option>
                  <option value="RESCINDIDO">Rescindido</option>
                  <option value="INATIVO">Inativo</option>
                </select>
                <p class="help-text">Ao salvar como ATIVO, o financeiro será gerado/lançado.</p>
            </div>
          </div>
          
          <div class="form-group">
            <label for="informacoes_adicionais">Informações Adicionais</label>
            <textarea id="informacoes_adicionais" v-model="contrato.informacoes_adicionais"></textarea>
          </div>
        </fieldset>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Salvando...' : (isEditing ? 'Atualizar Contrato' : 'Criar Contrato') }}
          </button>
          <button type="button" @click="router.push({ name: 'contratos' })" class="btn btn-light">
            Cancelar
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import vSelect from 'vue-select';
import MoneyInput from '@/components/MoneyInput.vue'; 
import { format } from 'date-fns';

// TIPAGEM BASE
interface ClienteOption { label: string; value: number; }
interface ImovelOption { label: string; value: number; }

interface ContratoData {
  id?: number;
  imobiliaria?: number;
  tipo_contrato: 'ALUGUEL' | 'VENDA' | '';
  status_contrato: 'PENDENTE' | 'ATIVO' | 'CONCLUIDO' | 'RESCINDIDO' | 'INATIVO';
  
  imovel: number | null;
  inquilino: number | null;
  proprietario: number | null;
  fiadores: number[];
  
  // Dados de Aluguel
  aluguel: number | null;
  duracao_meses: number | null;
  taxa_administracao_percentual: number;
  data_primeiro_vencimento: string | null; 
  
  // Dados de Venda/Comissão
  valor_total: number | null;
  comissao_venda_percentual: number; 
  valor_comissao_acordado: number | null; 
  data_vencimento_venda: string | null; 

  data_inicio: string | null;
  data_fim: string | null;
  data_assinatura: string | null;
  informacoes_adicionais: string | null;
  conteudo_personalizado: string | null;
  formas_pagamento: number[];
}

const route = useRoute();
const router = useRouter();
const isEditing = ref(!!route.params.id);
const contratoId = route.params.id as string;

// Definição inicial do Contrato
const contrato = ref<ContratoData>({
  tipo_contrato: 'ALUGUEL',
  status_contrato: 'PENDENTE',
  imovel: null,
  inquilino: null,
  proprietario: null,
  fiadores: [],
  aluguel: null,
  duracao_meses: 12,
  taxa_administracao_percentual: 10.00,
  data_primeiro_vencimento: null,
  
  valor_total: null,
  comissao_venda_percentual: 6.00,
  valor_comissao_acordado: null,
  data_vencimento_venda: null,

  data_inicio: format(new Date(), 'yyyy-MM-dd'),
  data_fim: null,
  data_assinatura: format(new Date(), 'yyyy-MM-dd'),
  informacoes_adicionais: null,
  conteudo_personalizado: null,
  formas_pagamento: []
});

// LISTAS FILTRADAS
const todosClientesOptions = ref<ClienteOption[]>([]); // Lista completa para Inquilino/Fiadores
const proprietarioOptions = ref<ClienteOption[]>([]); // Lista filtrada por tipo de contrato
const imovelOptions = ref<ImovelOption[]>([]); // Lista filtrada por tipo de contrato E proprietário

const isSubmitting = ref(false);
const isLoading = ref(true); 
const error = ref<string | null>(null);

// ===============================================
// LÓGICA COMPUTADA E HELPERS
// ===============================================

const tipoContratoLabel = computed(() => {
  if (contrato.value.tipo_contrato === 'VENDA') {
    return { principal: 'Comprador', outraParte: 'Comprador' }; 
  }
  return { principal: 'Inquilino', outraParte: 'Inquilino' };
});

const calcularComissaoInicial = () => {
  if (contrato.value.tipo_contrato === 'VENDA' && contrato.value.valor_total && contrato.value.comissao_venda_percentual) {
    const valorTotal = Number(contrato.value.valor_total);
    const percentual = Number(contrato.value.comissao_venda_percentual);
    
    if (!isNaN(valorTotal) && !isNaN(percentual)) {
        contrato.value.valor_comissao_acordado = parseFloat((valorTotal * (percentual / 100)).toFixed(2));
    } else {
        contrato.value.valor_comissao_acordado = null;
    }
  }
};

const handleTipoChange = () => {
    // Ao mudar o tipo, resetar o Proprietário e Imóvel para forçar nova seleção
    contrato.value.proprietario = null;
    contrato.value.imovel = null;
    
    calcularComissaoInicial();

    if (contrato.value.tipo_contrato === 'ALUGUEL') {
        contrato.value.valor_total = null;
        contrato.value.valor_comissao_acordado = null;
        contrato.value.comissao_venda_percentual = 6.00;
        contrato.value.data_vencimento_venda = null;
    } else if (contrato.value.tipo_contrato === 'VENDA') {
        contrato.value.aluguel = null;
        contrato.value.duracao_meses = null;
        contrato.value.taxa_administracao_percentual = 0.00;
        contrato.value.data_primeiro_vencimento = null;
    }
};

// ===============================================
// FUNÇÕES DE DADOS E SUBMISSÃO
// ===============================================

async function fetchInitialDependencies() {
  try {
    // 1. Fetch Lista Completa de Clientes (para Inquilino/Fiadores)
    const clientesRes = await apiClient.get('/v1/clientes/lista-simples/');
    
    todosClientesOptions.value = clientesRes.data.map((c: any) => ({
      label: c.nome_display || c.nome,
      value: c.id,
    }));
  } catch (err) {
    console.error('Erro ao carregar lista de clientes para Inquilino/Fiadores:', err);
    error.value = 'Não foi possível carregar a lista de clientes para Inquilino/Fiadores.';
  }
}

async function fetchProprietarioOptions(tipo: 'ALUGUEL' | 'VENDA' | '') {
    if (!tipo) return;
    const finalidade = tipo === 'VENDA' ? 'A_VENDA' : 'PARA_ALUGAR';
    
    try {
        // Fetch: Proprietários filtrados pela finalidade
        const proprietarioRes = await apiClient.get('/v1/clientes/lista-proprietarios/', { params: { finalidade: finalidade } });
        proprietarioOptions.value = proprietarioRes.data.map((c: any) => ({ label: c.nome_display || c.nome, value: c.id, }));
    } catch (err) {
        console.error('Erro ao carregar lista de Proprietários filtrada:', err);
        proprietarioOptions.value = []; 
    }
}

async function fetchImovelOptions(tipo: 'ALUGUEL' | 'VENDA' | '', proprietarioId: number | null) {
  if (!tipo) return;

  const finalidade = tipo === 'VENDA' ? 'A_VENDA' : 'PARA_ALUGAR';
  
  // Parâmetros base para Imóveis: Filtra por finalidade E proprietário (se selecionado)
  const imovelParams: Record<string, any> = { finalidade: finalidade };
  if (proprietarioId) {
      imovelParams.proprietario_id = proprietarioId;
  }
  
  try {
    // Fetch: Imóveis filtrados por finalidade E proprietário
    const imovelRes = await apiClient.get('/v1/imoveis/lista-simples/', { params: imovelParams });
    imovelOptions.value = imovelRes.data; 

  } catch (err) {
    console.error('Erro ao carregar Imóveis filtrados:', err);
    imovelOptions.value = [];
  }
}

async function fetchContrato() {
  try {
    const response = await apiClient.get(`/v1/contratos/${contratoId}/`); 
    const data = response.data;
    
    contrato.value = {
        ...data,
        fiadores: data.fiadores.map((f: any) => f.id) || [], 
        
        taxa_administracao_percentual: parseFloat(data.taxa_administracao_percentual) || 10.00,
        comissao_venda_percentual: parseFloat(data.comissao_venda_percentual) || 6.00,
        
        aluguel: data.aluguel ? parseFloat(data.aluguel) : null,
        valor_total: data.valor_total ? parseFloat(data.valor_total) : null,
        valor_comissao_acordado: data.valor_comissao_acordado ? parseFloat(data.valor_comissao_acordado) : null,

        // Garante que o ID do objeto aninhado (na leitura) seja usado
        proprietario: data.proprietario?.id || data.proprietario, 
        inquilino: data.inquilino?.id || data.inquilino,
        imovel: data.imovel?.id || data.imovel,
    };
    
  } catch (err) {
    console.error('Erro ao carregar contrato:', err);
    error.value = 'Não foi possível carregar os dados do contrato.';
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  error.value = null;

  try {
    const payload = { ...contrato.value };
    
    // 1. Limpeza de dados (Garantir null para campos não usados)
    if (payload.tipo_contrato === 'ALUGUEL') {
        payload.valor_total = null;
        payload.comissao_venda_percentual = 0.00; 
        payload.valor_comissao_acordado = null;
        payload.data_vencimento_venda = null;
    } else { // Venda
        payload.aluguel = null;
        payload.duracao_meses = null;
        payload.taxa_administracao_percentual = 0.00;
        payload.data_primeiro_vencimento = null;
    }

    // 2. Envio para API
    if (isEditing.value) {
      await apiClient.put(`/v1/contratos/${contratoId}/`, payload);
      alert('Contrato atualizado com sucesso!');
    } else {
      await apiClient.post('/v1/contratos/', payload);
      alert('Contrato criado com sucesso!');
    }
    router.push({ name: 'contratos' });

  } catch (err: any) {
    console.error('Erro ao salvar contrato:', err.response?.data || err);
    
    if (err.response && err.response.status === 400 && err.response.data) {
        const apiError = err.response.data;
        if (apiError.status_contrato) {
            error.value = apiError.status_contrato[0];
        } else if (apiError.non_field_errors) {
            error.value = apiError.non_field_errors[0];
        } else {
            const firstErrorKey = Object.keys(apiError)[0];
            error.value = `Erro no campo ${firstErrorKey}: ${apiError[firstErrorKey][0]}`;
        }
    } else {
        error.value = 'Ocorreu um erro ao comunicar com o servidor. Tente novamente.';
    }

  } finally {
    isSubmitting.value = false;
  }
}

// ===============================================
// WATCHERS E MOUNTED (Gatilhos de Carregamento)
// ===============================================

// Watcher 1: Dispara a busca de Proprietários e Imóveis filtrados ao mudar o Tipo de Contrato
watch(() => contrato.value.tipo_contrato, (newTipo) => {
    // 1. Recarrega lista de Proprietários
    fetchProprietarioOptions(newTipo); 
    
    // 2. Recarrega a lista de Imóveis (filtrados pelo TIPO e pelo Proprietário ATUAL)
    fetchImovelOptions(newTipo, contrato.value.proprietario);
}, { immediate: false }); 

// Watcher 2: Dispara a busca de Imóveis filtrados ao mudar o Proprietário
watch(() => contrato.value.proprietario, (newProprietarioId, oldProprietarioId) => {
    // 1. **CORREÇÃO: Reseta o Imóvel ao mudar o Proprietário**
    // Só reseta se o ID realmente mudou, evitando resets desnecessários na carga
    if (newProprietarioId !== oldProprietarioId) {
      contrato.value.imovel = null;
    }
    
    // 2. Apenas recarrega a lista de Imóveis (o tipo de contrato já está definido)
    fetchImovelOptions(contrato.value.tipo_contrato, newProprietarioId);
}, { immediate: false });


onMounted(async () => {
  isLoading.value = true;
  // 1. Carrega todas as dependências básicas (Clientes para Inquilino/Fiadores)
  await fetchInitialDependencies();
  
  // 2. Se estiver editando, carrega os dados do contrato PRIMEIRO
  if (isEditing.value) {
    await fetchContrato();
  }
  
  // 3. Carrega as listas filtradas com base no estado inicial (novo ou editado)
  await fetchProprietarioOptions(contrato.value.tipo_contrato);
  await fetchImovelOptions(contrato.value.tipo_contrato, contrato.value.proprietario);
  
  // 4. Finaliza o loading
  if (!error.value) {
    isLoading.value = false; 
  }
});
</script>

<style scoped>
/* Estilos mantidos do código anterior (semântica e cores) */
.page-container-form {
    padding: 0;
}
.form-card {
    background: white; 
    padding: 20px 30px; 
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    max-width: 1000px;
    margin: 1rem auto;
}
.form-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}
.form-header h2 {
    font-size: 1.6rem;
    margin: 0;
}
.form-section {
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 20px;
    background-color: #fcfcfc;
}
.form-section legend {
    font-size: 1.1rem;
    font-weight: 600;
    color: #495057;
    padding: 0 10px;
    width: auto;
    margin-left: -5px;
}
.form-grid-3col {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 15px;
}
.form-grid-2col {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 15px;
}
.form-group {
    display: flex;
    flex-direction: column;
}
label {
    font-weight: 600;
    margin-bottom: 5px;
    color: #495057;
    font-size: 0.85rem;
}
input[type="text"], input[type="number"], input[type="date"], select, .form-group textarea, .form-group .form-input-money {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-size: 0.9rem;
    box-sizing: border-box; 
    transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group textarea {
    resize: vertical;
    min-height: 80px;
}
.help-text {
    font-size: 0.75rem;
    color: #6c757d;
    margin-top: 5px;
}

/* Estilos para v-select (mantidos) */
:deep(.vs__dropdown-toggle) {
  padding: 6px 8px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  background: white;
  min-height: 38px;
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
  background-color: #e9ecef;
  border-color: #e9ecef;
  color: #495057;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* Botões */
.form-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}
.btn {
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.3s;
    text-decoration: none;
}
.btn-primary {
    background-color: #007bff;
    color: white;
    border: none;
}
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary, .btn-light {
    background-color: #f8f9fa;
    color: #495057;
    border: 1px solid #ced4da;
}
.btn-secondary:hover, .btn-light:hover { background-color: #e2e6ea; }

/* Mensagens de estado */
.loading-message, .error-message {
    text-align: center;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 15px;
}
.loading-message {
    background-color: #e9f5ff;
    color: #007bff;
}
.error-message {
    background-color: #f8d7da;
    color: #dc3545;
    border: 1px solid #f5c6cb;
}
.spinner { /* Placeholder para spinner, se necessário */
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border-left-color: #007bff;
    display: inline-block;
    vertical-align: middle;
    margin-right: 8px;
    animation: spin 1s ease infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .form-grid-3col, .form-grid-2col {
    grid-template-columns: 1fr;
  }
}
</style>
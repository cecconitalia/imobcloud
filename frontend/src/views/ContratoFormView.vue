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
      
      <div v-if="error" class="error-message" role="alert">
        <strong>Erro:</strong> {{ error }}
      </div>
      <div v-if="!isLoading">
        
        <fieldset class="form-section">
          <legend>Partes do Contrato</legend>
          <div class="form-grid-3col">
            <div class="form-group">
              <label for="tipo">Tipo de Contrato *</label>
              <select id="tipo" v-model="contrato.tipo_contrato" :disabled="isEditing && contrato.status_contrato !== 'RASCUNHO'" @change="handleTipoChange">
                <option value="ALUGUEL">Aluguel</option>
                <option value="VENDA">Venda</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="proprietario">Proprietário / Locador *</label>
              <v-select
                id="proprietario"
                v-model="contrato.proprietario"
                :options="proprietarioOptions" 
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione o proprietário"
                :clearable="false"
                :disabled="!contrato.tipo_contrato || (!proprietarioOptions.length && !isEditing && !isLoadingProprietarios)"
              ></v-select>
              <p v-if="isLoadingProprietarios" class="help-text-loading">Carregando proprietários...</p>
              <p v-else-if="!contrato.tipo_contrato" class="help-text">Selecione o Tipo de Contrato primeiro.</p>
              <p v-else-if="!proprietarioOptions.length && !isEditing" class="help-text">Nenhum proprietário com imóveis disponíveis para esta finalidade.</p>
            </div>


            <div class="form-group">
              <label for="inquilino">{{ tipoContratoLabel.outraParte }} *</label>
              <v-select
                id="inquilino"
                v-model="contrato.inquilino"
                :options="todosClientesOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione a outra parte"
                :clearable="false"
                :disabled="!todosClientesOptions.length"
              ></v-select>
              <p v-if="!todosClientesOptions.length" class="help-text-loading">Carregando clientes...</p>
            </div>
          </div>
          
          <div class="form-grid-2col">
            <div class="form-group">
              <label for="imovel">Imóvel *</label>
              <v-select
                id="imovel"
                v-model="contrato.imovel"
                :options="imovelOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione o Imóvel"
                :clearable="false"
                :disabled="!contrato.proprietario || (!imovelOptions.length && !isEditing && !isLoadingImoveis)"
              ></v-select>
              <p v-if="isLoadingImoveis" class="help-text-loading">Carregando imóveis...</p>
              <p v-else-if="!contrato.proprietario" class="help-text">Selecione um Proprietário primeiro.</p>
              <p v-else-if="!imovelOptions.length" class="help-text">Nenhum imóvel disponível encontrado para este proprietário.</p>
            </div>
            
            <div class="form-group">
              <label for="modelo_contrato">Modelo de Documento</label>
              <v-select
                id="modelo_contrato"
                v-model="contrato.modelo_utilizado"
                :options="modeloContratoOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Selecione o modelo"
                :clearable="true"
                :disabled="!contrato.tipo_contrato || isLoadingModelos"
              ></v-select>
              <p v-if="isLoadingModelos" class="help-text-loading">Carregando modelos...</p>
              <p v-else-if="!contrato.tipo_contrato" class="help-text">Selecione o Tipo de Contrato.</p>
              <p v-else class="help-text">
                (Opcional) Se não selecionar, o modelo padrão da imobiliária será usado.
              </p>
            </div>
          </div>

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
              <MoneyInput 
                v-model.number="contrato.valor_total" 
                class="form-input-money" 
                @change="calcularComissaoValor" 
                required 
              />
            </div>
            
            <div class="form-group">
              <label for="comissao_venda_percentual">% Comissão (Base)</label>
              <input 
                type="number" 
                id="comissao_venda_percentual" 
                v-model.number="contrato.comissao_venda_percentual" 
                @input="calcularComissaoValor" 
                step="0.01" min="0" max="100"
              >
            </div>
            
            <div class="form-group">
              <label for="valor_comissao_acordado">Valor Acordado Comissão (R$) *</label>
              <MoneyInput 
                v-model.number="contrato.valor_comissao_acordado" 
                class="form-input-money" 
                @change="calcularPercentualComissao"
                required 
              />
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
              <input 
                type="date" 
                id="data_inicio" 
                v-model="contrato.data_inicio" 
                :disabled="contrato.tipo_contrato === 'VENDA'"
                required
              >
              <p v-if="contrato.tipo_contrato === 'VENDA'" class="help-text">Será a mesma da Data de Assinatura.</p>
            </div>
            <div class="form-group">
              <label for="data_assinatura">Data de Assinatura *</label>
              <input 
                type="date" 
                id="data_assinatura" 
                v-model="contrato.data_assinatura"
                @change="handleDataAssinaturaChange" 
                required
              >
            </div>
            <div class="form-group" v-if="contrato.tipo_contrato === 'ALUGUEL'">
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
                <select 
                  id="status_contrato" 
                  v-model="contrato.status_contrato" 
                  required 
                  :disabled="contrato.tipo_contrato === 'VENDA' && contrato.status_contrato !== 'RASCUNHO'"
                >
                  <option value="RASCUNHO">Rascunho</option>
                  
                  <option value="ATIVO">Ativo</option>
                  
                  <option v-if="isEditing" value="RESCINDIDO">Rescindido</option>
                  <option v-if="isEditing" value="CONCLUIDO">Concluído</option>
                  <option v-if="isEditing" value="CANCELADO">Cancelado</option>
                </select>
                
                <p class="help-text" v-if="contrato.tipo_contrato === 'VENDA' && contrato.status_contrato === 'ATIVO'">
                    Contrato de Venda finalizado. Status bloqueado.
                </p>
                <p class="help-text" v-else-if="!isEditing">
                    Recomendado iniciar como Rascunho.
                </p>
                <p class="help-text" v-else>
                    Alterar para ATIVO gera o financeiro.
                </p>
            </div>
            </div>
          <div class="form-group">
            <label for="informacoes_adicionais">Informações Adicionais / Condições de Pagamento (Venda)</label>
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
interface ModeloContratoOption { label: string; value: number; padrao: boolean; } 
interface ImovelOption { 
  label: string; 
  value: number; 
  aluguel: number | null;
  venda: number | null;
}

interface ContratoData {
  id?: number;
  imobiliaria?: number;
  tipo_contrato: 'ALUGUEL' | 'VENDA' | '';
  status_contrato: 'RASCUNHO' | 'ATIVO' | 'CONCLUIDO' | 'RESCINDIDO' | 'CANCELADO';
  
  modelo_utilizado: number | null; 
  
  imovel: number | null;
  inquilino: number | null;
  proprietario: number | null; 
  fiadores: number[];
  
  aluguel: number | null;
  duracao_meses: number | null;
  taxa_administracao_percentual: number;
  data_primeiro_vencimento: string | null; 
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

interface ProprietarioSerializerResponse {
  id: number;
  nome_display: string;
}
interface ModeloContratoResponse {
  id: number;
  nome: string;
  padrao: boolean;
  tipo_contrato: 'ALUGUEL' | 'VENDA';
}

const route = useRoute();
const router = useRouter();
const isEditing = ref(!!route.params.id);
const contratoId = route.params.id as string;

// Definição inicial do Contrato
const contrato = ref<ContratoData>({
  tipo_contrato: 'ALUGUEL',
  status_contrato: 'RASCUNHO',
  
  modelo_utilizado: null, 
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
const todosClientesOptions = ref<ClienteOption[]>([]); 
const proprietarioOptions = ref<ClienteOption[]>([]); 
const imovelOptions = ref<ImovelOption[]>([]); 
const modeloContratoOptions = ref<ModeloContratoOption[]>([]); 

const selectedProprietario = ref<ClienteOption | null>(null);
const selectedImovel = ref<ImovelOption | null>(null);
const selectedModelo = ref<ModeloContratoOption | null>(null); 

const isSubmitting = ref(false);
const isLoading = ref(true); 
const isLoadingProprietarios = ref(false); 
const isLoadingImoveis = ref(false); 
const isLoadingModelos = ref(false); 
const error = ref<string | null>(null);

const tipoContratoLabel = computed(() => {
  if (contrato.value.tipo_contrato === 'VENDA') {
    return { principal: 'Comprador', outraParte: 'Comprador' }; 
  }
  return { principal: 'Inquilino', outraParte: 'Inquilino' };
});

// =======================================================================
// === NOVAS FUNÇÕES DE CÁLCULO (Bidirecionais)                        ===
// =======================================================================

const calcularComissaoValor = () => {
  if (contrato.value.tipo_contrato === 'VENDA' && contrato.value.valor_total) {
    const valorTotal = Number(contrato.value.valor_total);
    const percentual = Number(contrato.value.comissao_venda_percentual);
    
    if (!isNaN(valorTotal) && !isNaN(percentual)) {
        contrato.value.valor_comissao_acordado = parseFloat((valorTotal * (percentual / 100)).toFixed(2));
    }
  }
};

const calcularPercentualComissao = () => {
    if (contrato.value.tipo_contrato === 'VENDA' && contrato.value.valor_total && contrato.value.valor_comissao_acordado) {
        const valorTotal = Number(contrato.value.valor_total);
        const valorComissao = Number(contrato.value.valor_comissao_acordado);
        
        if (!isNaN(valorTotal) && !isNaN(valorComissao) && valorTotal > 0) {
            contrato.value.comissao_venda_percentual = parseFloat(((valorComissao / valorTotal) * 100).toFixed(2));
        }
    }
};
// =======================================================================

const handleDataAssinaturaChange = () => {
  if (contrato.value.tipo_contrato === 'VENDA') {
    contrato.value.data_inicio = contrato.value.data_assinatura;
  }
}
const handleTipoChange = () => {
    contrato.value.proprietario = null;
    contrato.value.imovel = null;
    contrato.value.modelo_utilizado = null;
    proprietarioOptions.value = [];
    imovelOptions.value = [];
    modeloContratoOptions.value = []; 
    
    // Reseta valores ao mudar o tipo
    if (contrato.value.tipo_contrato === 'ALUGUEL') {
        contrato.value.valor_total = null;
        contrato.value.valor_comissao_acordado = null;
        contrato.value.comissao_venda_percentual = 6.00;
        contrato.value.data_vencimento_venda = null;
        contrato.value.taxa_administracao_percentual = 10.00; 
        contrato.value.duracao_meses = 12;
    } else if (contrato.value.tipo_contrato === 'VENDA') {
        contrato.value.aluguel = null;
        contrato.value.duracao_meses = null;
        contrato.value.taxa_administracao_percentual = 0.00;
        contrato.value.data_primeiro_vencimento = null;
        contrato.value.data_fim = null;
        contrato.value.data_inicio = contrato.value.data_assinatura;
        // Inicializa cálculo se houver dados residuais
        calcularComissaoValor();
    }
};

async function fetchInitialDependencies() {
  try {
    const clientesRes = await apiClient.get('/v1/clientes/lista-simples/');
    todosClientesOptions.value = clientesRes.data.map((c: any) => ({
      label: c.nome_display,
      value: c.id,
    }));
  } catch (err) {
    console.error('Erro ao carregar lista de clientes para Inquilino/Fiadores:', err);
    error.value = 'Não foi possível carregar a lista de clientes para Inquilino/Fiadores.';
  }
}

async function fetchProprietarioOptions(tipo: 'ALUGUEL' | 'VENDA' | '') {
    if (!tipo) return;
    isLoadingProprietarios.value = true;
    const status_filter = tipo === 'VENDA' ? 'A_VENDA' : 'PARA_ALUGAR';
    const params = { finalidade: status_filter }; 
    try {
        const proprietarioRes = await apiClient.get('/v1/clientes/lista-proprietarios/', { params: params });
        const options: ClienteOption[] = proprietarioRes.data.map((c: ProprietarioSerializerResponse) => ({
            label: c.nome_display,
            value: c.id,
        }));
        if (isEditing.value && selectedProprietario.value) {
            const exists = options.some(opt => opt.value === selectedProprietario.value!.value);
            if (!exists) {
                options.unshift(selectedProprietario.value);
            }
        }
        proprietarioOptions.value = options;
    } catch (err) {
        console.error('Erro ao carregar lista de Proprietários filtrada:', err);
        if (isEditing.value && selectedProprietario.value) {
             proprietarioOptions.value = [selectedProprietario.value];
        } else {
             proprietarioOptions.value = []; 
        }
    } finally {
        isLoadingProprietarios.value = false;
    }
}

async function fetchImovelOptions(tipo: 'ALUGUEL' | 'VENDA' | '', proprietarioId: number | null) {
  if (!tipo || !proprietarioId) { 
      imovelOptions.value = [];
      return;
  }
  isLoadingImoveis.value = true;
  
  const statusImovel = tipo === 'VENDA' ? 'A_VENDA' : 'PARA_ALUGAR';
  const imovelParams: Record<string, any> = { 
      status: statusImovel, 
      proprietario: proprietarioId, 
  };
  
  try {
    const imovelRes = await apiClient.get('/v1/imoveis/lista-simples/', { params: imovelParams });
    const options: ImovelOption[] = imovelRes.data.map((i: any) => ({
        label: `#${i.codigo_referencia} - ${i.titulo_anuncio || i.logradouro}`,
        value: i.id,
        aluguel: i.valor_aluguel,
        venda: i.valor_venda
    }));

    if (isEditing.value && selectedImovel.value) {
         if (contrato.value.proprietario === proprietarioId) {
            const exists = options.some(opt => opt.value === selectedImovel.value!.value);
            if (!exists) {
                options.unshift(selectedImovel.value);
            }
         }
    }
    imovelOptions.value = options;
  } catch (err) {
    console.error('Erro ao carregar Imóveis filtrados:', err);
     if (isEditing.value && selectedImovel.value && contrato.value.proprietario === proprietarioId) {
         imovelOptions.value = [selectedImovel.value];
     } else {
         imovelOptions.value = [];
     }
  } finally {
    isLoadingImoveis.value = false;
  }
}

async function fetchModeloContratoOptions(tipo: 'ALUGUEL' | 'VENDA' | '') {
  if (!tipo) {
    modeloContratoOptions.value = [];
    return;
  }
  isLoadingModelos.value = true;
  try {
    const response = await apiClient.get('/v1/modelos-contrato/', {
      params: { tipo_contrato: tipo }
    });
    const options: ModeloContratoOption[] = response.data.map((m: ModeloContratoResponse) => ({
      label: m.padrao ? `${m.nome} (Padrão)` : m.nome,
      value: m.id,
      padrao: m.padrao,
    }));
    if (isEditing.value && selectedModelo.value) {
      const exists = options.some(opt => opt.value === selectedModelo.value!.value);
      if (!exists) {
        options.unshift(selectedModelo.value);
      }
    }
    modeloContratoOptions.value = options;
    if (!isEditing.value) {
        const padrao = options.find(o => o.padrao);
        if (padrao) {
            contrato.value.modelo_utilizado = padrao.value;
        }
    }
  } catch (err) {
    console.error('Erro ao carregar Modelos de Contrato:', err);
    if (isEditing.value && selectedModelo.value) {
      modeloContratoOptions.value = [selectedModelo.value];
    } else {
      modeloContratoOptions.value = [];
    }
  } finally {
    isLoadingModelos.value = false;
  }
}

async function fetchContrato() {
  try {
    const response = await apiClient.get(`/v1/contratos/${contratoId}/`); 
    const data = response.data;

    // ==========================================================
    // === REGRA DE NEGÓCIO: BLOQUEIO DE ACESSO À EDIÇÃO      ===
    // ==========================================================
    // Bloqueia apenas se for VENDA e estiver ATIVO. 
    // Contratos de ALUGUEL podem ser editados.
    if (data.status_contrato === 'ATIVO' && data.tipo_contrato === 'VENDA') {
        alert("Este contrato de Venda já está ATIVO e finalizado. Não é possível editá-lo.\nVocê será redirecionado para a lista.");
        router.push({ name: 'contratos' });
        return;
    }
    // ==========================================================

    const fiadorIds = (data.fiadores || []).map((f: any) => (typeof f === 'object' ? f.id : f));
    if (data.proprietario_detalhes) {
      selectedProprietario.value = {
        label: data.proprietario_detalhes.nome_display,
        value: data.proprietario_detalhes.id
      };
    }
    if (data.imovel_detalhes) {
      selectedImovel.value = data.imovel_detalhes;
    }
    if (data.modelo_utilizado) {
        selectedModelo.value = {
            label: data.modelo_utilizado.padrao ? `${data.modelo_utilizado.nome} (Padrão)` : data.modelo_utilizado.nome,
            value: data.modelo_utilizado.id,
            padrao: data.modelo_utilizado.padrao
        };
    }
    contrato.value = {
        ...data,
        fiadores: fiadorIds,
        taxa_administracao_percentual: parseFloat(data.taxa_administracao_percentual) || 10.00,
        comissao_venda_percentual: parseFloat(data.comissao_venda_percentual) || 6.00,
        aluguel: data.aluguel ? parseFloat(data.aluguel) : null,
        valor_total: data.valor_total ? parseFloat(data.valor_total) : null,
        valor_comissao_acordado: data.valor_comissao_acordado ? parseFloat(data.valor_comissao_acordado) : null,
        proprietario: data.proprietario_detalhes?.id || data.proprietario, 
        inquilino: data.inquilino_detalhes?.id || data.inquilino,
        imovel: data.imovel_detalhes?.id || data.imovel,
        modelo_utilizado: data.modelo_utilizado?.id || null, 
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
    if (payload.tipo_contrato === 'ALUGUEL') {
        payload.valor_total = null;
        payload.valor_comissao_acordado = null;
        payload.data_vencimento_venda = null;
    } else { 
        payload.aluguel = null;
        payload.duracao_meses = null;
        payload.data_primeiro_vencimento = null;
        payload.data_fim = null;
    }
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
        if (apiError.modelo_utilizado) {
             error.value = `Modelo: ${apiError.modelo_utilizado[0]}`;
        }
        else if (apiError.imovel) {
             error.value = `Imóvel: ${apiError.imovel[0]}`;
        } else if (apiError.proprietario) {
             error.value = `Proprietario: ${apiError.proprietario[0]}`;
        } else if (apiError.status_contrato) {
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

watch(() => contrato.value.tipo_contrato, (newTipo, oldTipo) => {
    fetchProprietarioOptions(newTipo); 
    fetchModeloContratoOptions(newTipo); 
    if (oldTipo !== undefined && !isLoading.value) { 
      contrato.value.proprietario = null;
      contrato.value.imovel = null;
    }
    imovelOptions.value = [];
}, { immediate: true }); 

watch(() => contrato.value.proprietario, (newProprietarioId, oldProprietarioId) => {
    if (oldProprietarioId !== undefined && newProprietarioId !== oldProprietarioId && !isLoading.value) {
       contrato.value.imovel = null;
    }
    if (contrato.value.tipo_contrato) {
        fetchImovelOptions(contrato.value.tipo_contrato, newProprietarioId);
    } else {
        imovelOptions.value = [];
    }
}, { immediate: true }); 

watch(
  [() => contrato.value.imovel, () => imovelOptions.value], 
  ([newImovelId, newOptions]) => {
    if (!newImovelId || !newOptions.length) {
      return;
    }
    if (isLoading.value && isEditing.value) {
      return;
    }
    const selectedImovel = newOptions.find(o => o.value === newImovelId);
    if (selectedImovel) {
      if (contrato.value.tipo_contrato === 'ALUGUEL') {
        if (!contrato.value.aluguel) {
            contrato.value.aluguel = selectedImovel.aluguel ? parseFloat(String(selectedImovel.aluguel)) : null;
        }
      } 
      else if (contrato.value.tipo_contrato === 'VENDA') {
        if (!contrato.value.valor_total) {
            contrato.value.valor_total = selectedImovel.venda ? parseFloat(String(selectedImovel.venda)) : null;
        }
        // Recalcula a comissão inicial com base no valor do imóvel selecionado
        calcularComissaoValor();
      }
    }
  }
);

onMounted(async () => {
  isLoading.value = true;
  error.value = null;
  
  await fetchInitialDependencies(); 
  
  if (isEditing.value) {
    await fetchContrato(); 
    
    if (contrato.value.tipo_contrato) {
        await fetchProprietarioOptions(contrato.value.tipo_contrato);
        await fetchModeloContratoOptions(contrato.value.tipo_contrato);
    }
    if (contrato.value.tipo_contrato && contrato.value.proprietario) {
        await fetchImovelOptions(contrato.value.tipo_contrato, contrato.value.proprietario);
    }

  } else {
    handleDataAssinaturaChange();
    await fetchProprietarioOptions(contrato.value.tipo_contrato);
    await fetchModeloContratoOptions(contrato.value.tipo_contrato);
  }
  
  if (!error.value) {
    isLoading.value = false; 
  }
});
</script>

<style scoped>
/* (Estilos CSS inalterados) */
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
input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
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
.help-text-loading {
    font-size: 0.75rem;
    color: #007bff;
    margin-top: 5px;
}
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
.loading-message {
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
    color: #721c24;
    border: 1px solid #f5c6cb;
    padding: 10px 15px;
    border-radius: 6px;
    margin-bottom: 20px;
    font-size: 0.9rem;
}
.spinner {
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
<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
             <span>Gestão</span> 
             <i class="fas fa-chevron-right separator"></i> 
             <router-link :to="{ name: 'contratos' }">Contratos</router-link>
             <i class="fas fa-chevron-right separator"></i>
             <span class="active">{{ isEditing ? 'Editar' : 'Novo' }}</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Contrato' : 'Novo Contrato' }}</h1>
        </div>
      </div>
    </header>

    <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando dados do contrato...</p>
    </div>

    <div v-else-if="error" class="error-banner">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ error }}</span>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="main-content-grid">
      
      <div class="left-column">
        <div class="card form-card">
            
            <div class="form-section">
                <h3 class="section-title">
                    <i class="fas fa-users"></i> Partes do Contrato
                </h3>
                
                <div class="form-grid">
                    <div class="form-group full-width">
                        <label>Tipo de Contrato <span class="req">*</span></label>
                        <div class="tipo-toggle">
                            <label class="radio-label" :class="{ active: contrato.tipo_contrato === 'ALUGUEL' }">
                                <input type="radio" value="ALUGUEL" v-model="contrato.tipo_contrato" :disabled="isEditing && contrato.status_contrato !== 'RASCUNHO'" @change="handleTipoChange">
                                <i class="fas fa-key"></i> Aluguel
                            </label>
                            <label class="radio-label" :class="{ active: contrato.tipo_contrato === 'VENDA' }">
                                <input type="radio" value="VENDA" v-model="contrato.tipo_contrato" :disabled="isEditing && contrato.status_contrato !== 'RASCUNHO'" @change="handleTipoChange">
                                <i class="fas fa-handshake"></i> Venda
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Proprietário / Locador <span class="req">*</span></label>
                        <v-select
                            v-model="contrato.proprietario"
                            :options="proprietarioOptions" 
                            :reduce="(option: any) => option.value"
                            label="label"
                            placeholder="Selecione..."
                            :clearable="false"
                            :disabled="!contrato.tipo_contrato || isLoadingProprietarios"
                            class="style-chooser"
                        >
                            <template #no-options>
                                <span v-if="isLoadingProprietarios">Carregando...</span>
                                <span v-else>Nenhum proprietário encontrado.</span>
                            </template>
                        </v-select>
                        <small v-if="!contrato.proprietario && contrato.tipo_contrato" class="help-text">Necessário para carregar imóveis.</small>
                    </div>

                    <div class="form-group">
                        <label>{{ tipoContratoLabel.outraParte }} <span class="req">*</span></label>
                        <v-select
                            v-model="contrato.inquilino"
                            :options="todosClientesOptions"
                            :reduce="(option: any) => option.value"
                            label="label"
                            placeholder="Selecione..."
                            :clearable="false"
                            :disabled="!todosClientesOptions.length"
                            class="style-chooser"
                        ></v-select>
                    </div>

                    <div class="form-group full-width">
                        <label>Imóvel <span class="req">*</span></label>
                        <v-select
                            v-model="contrato.imovel"
                            :options="imovelOptions"
                            :reduce="(option: any) => option.value"
                            label="label"
                            placeholder="Selecione o Imóvel"
                            :clearable="false"
                            :disabled="!contrato.proprietario || isLoadingImoveis"
                            class="style-chooser"
                        >
                            <template #no-options>
                                <span v-if="isLoadingImoveis">Carregando...</span>
                                <span v-else-if="!contrato.proprietario">Selecione o proprietário primeiro.</span>
                                <span v-else>Nenhum imóvel disponível.</span>
                            </template>
                        </v-select>
                    </div>
                </div>
            </div>

            <div v-if="contrato.tipo_contrato === 'ALUGUEL'" class="form-section">
                <h3 class="section-title">
                    <i class="fas fa-hand-holding-usd"></i> Termos do Aluguel
                </h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Valor Mensal <span class="req">*</span></label>
                        <MoneyInput v-model.number="contrato.aluguel" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Duração (meses) <span class="req">*</span></label>
                        <div class="input-wrapper">
                            <i class="fas fa-hourglass-half input-icon"></i>
                            <input type="number" v-model.number="contrato.duracao_meses" min="1" class="form-input has-icon">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Taxa Adm. (%)</label>
                        <div class="input-wrapper">
                            <i class="fas fa-percent input-icon"></i>
                            <input type="number" v-model.number="contrato.taxa_administracao_percentual" step="0.01" min="0" max="100" class="form-input has-icon">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>1º Vencimento <span class="req">*</span></label>
                        <div class="input-wrapper">
                            <i class="far fa-calendar-alt input-icon"></i>
                            <input type="date" v-model="contrato.data_primeiro_vencimento" class="form-input has-icon">
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="contrato.tipo_contrato === 'VENDA'" class="form-section">
                <h3 class="section-title">
                    <i class="fas fa-handshake"></i> Termos da Venda
                </h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Valor da Venda <span class="req">*</span></label>
                        <MoneyInput 
                            v-model.number="contrato.valor_total" 
                            class="form-input" 
                            @change="calcularComissaoValor" 
                        />
                    </div>
                    <div class="form-group">
                        <label>Data Previsão Pagto. <span class="req">*</span></label>
                        <div class="input-wrapper">
                            <i class="far fa-calendar-alt input-icon"></i>
                            <input type="date" v-model="contrato.data_vencimento_venda" class="form-input has-icon">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>% Comissão</label>
                        <div class="input-wrapper">
                            <i class="fas fa-percent input-icon"></i>
                            <input 
                                type="number" 
                                v-model.number="contrato.comissao_venda_percentual" 
                                @input="calcularComissaoValor" 
                                step="0.01" min="0" max="100"
                                class="form-input has-icon"
                            >
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Valor Comissão (R$) <span class="req">*</span></label>
                        <MoneyInput 
                            v-model.number="contrato.valor_comissao_acordado" 
                            class="form-input" 
                            @change="calcularPercentualComissao"
                        />
                    </div>
                </div>
            </div>

            <div class="form-section compact-section">
                <h3 class="section-title">
                    <i class="far fa-clock"></i> Vigência e Detalhes
                </h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Data Início <span class="req">*</span></label>
                        <div class="input-wrapper">
                            <i class="far fa-calendar-check input-icon"></i>
                            <input 
                                type="date" 
                                v-model="contrato.data_inicio" 
                                :disabled="contrato.tipo_contrato === 'VENDA'"
                                class="form-input has-icon"
                            >
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Data Assinatura <span class="req">*</span></label>
                        <div class="input-wrapper">
                            <i class="fas fa-file-signature input-icon"></i>
                            <input 
                                type="date" 
                                v-model="contrato.data_assinatura"
                                @change="handleDataAssinaturaChange" 
                                class="form-input has-icon"
                            >
                        </div>
                    </div>
                    <div class="form-group" v-if="contrato.tipo_contrato === 'ALUGUEL'">
                        <label>Data Término</label>
                        <div class="input-wrapper">
                            <i class="far fa-calendar-times input-icon"></i>
                            <input type="date" v-model="contrato.data_fim" @change="handleDataFimChange" class="form-input has-icon">
                        </div>
                    </div>
                    
                    <div class="form-group full-width" v-if="todosClientesOptions.length">
                        <label>Fiadores</label>
                        <v-select
                            v-model="contrato.fiadores"
                            :options="todosClientesOptions"
                            :reduce="(option: any) => option.value"
                            label="label"
                            placeholder="Selecione..."
                            multiple
                            class="style-chooser"
                        ></v-select>
                    </div>

                    <div class="form-group full-width">
                        <label>Informações Adicionais</label>
                        <textarea v-model="contrato.informacoes_adicionais" class="form-textarea" rows="3" placeholder="Observações importantes..."></textarea>
                    </div>
                </div>
            </div>

            <div class="form-actions-footer">
                <router-link :to="{ name: 'contratos' }" class="btn-secondary">Cancelar</router-link>
                <button type="submit" class="btn-primary" :disabled="isSubmitting">
                    <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
                    <span v-else>{{ isEditing ? 'Salvar Contrato' : 'Criar Contrato' }}</span>
                </button>
            </div>

        </div>
      </div>

      <div class="right-column">
          
          <div class="card info-card">
             <div class="widget-header">
                 <h3 class="widget-title"><i class="fas fa-file-alt"></i> Status</h3>
             </div>
             <div class="form-group">
                <select 
                  v-model="contrato.status_contrato" 
                  :disabled="contrato.tipo_contrato === 'VENDA' && contrato.status_contrato !== 'RASCUNHO'"
                  class="form-select status-select"
                  :class="getStatusClass(contrato.status_contrato)"
                >
                  <option value="RASCUNHO">Rascunho</option>
                  <option value="ATIVO">Ativo</option>
                  <option v-if="isEditing" value="RESCINDIDO">Rescindido</option>
                  <option v-if="isEditing" value="CONCLUIDO">Concluído</option>
                  <option v-if="isEditing" value="CANCELADO">Cancelado</option>
                </select>
                <small class="helper-text-widget" v-if="contrato.status_contrato === 'ATIVO'">
                    Contrato vigente e gerando financeiro.
                </small>
                <small class="helper-text-widget" v-if="contrato.status_contrato === 'RASCUNHO'">
                    Rascunho não gera financeiro.
                </small>
             </div>
          </div>

          <div class="card info-card">
             <div class="widget-header">
                 <h3 class="widget-title"><i class="fas fa-stamp"></i> Configuração</h3>
             </div>
             <div class="form-group">
                <label>Modelo de Documento</label>
                <v-select
                    v-model="contrato.modelo_utilizado"
                    :options="modeloContratoOptions"
                    :reduce="(option: any) => option.value"
                    label="label"
                    placeholder="Padrão do sistema"
                    :clearable="true"
                    :disabled="!contrato.tipo_contrato || isLoadingModelos"
                    class="style-chooser"
                ></v-select>
                <small class="helper-text-widget">Define o template para impressão.</small>
             </div>
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
import 'vue-select/dist/vue-select.css';
import MoneyInput from '@/components/MoneyInput.vue'; 
import { format } from 'date-fns';

// --- INTERFACES ---
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
  tipo_contrato: 'ALUGUEL' | 'VENDA' | '';
  status_contrato: string;
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
  formas_pagamento: number[];
}

const route = useRoute();
const router = useRouter();
const isEditing = ref(!!route.params.id);
const contratoId = route.params.id as string;

// Estado do Contrato
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
  formas_pagamento: []
});

// Listas para Selects
const todosClientesOptions = ref<ClienteOption[]>([]); 
const proprietarioOptions = ref<ClienteOption[]>([]); 
const imovelOptions = ref<ImovelOption[]>([]); 
const modeloContratoOptions = ref<ModeloContratoOption[]>([]); 

// Estados de Carregamento
const isSubmitting = ref(false);
const isLoading = ref(true); 
const isLoadingProprietarios = ref(false); 
const isLoadingImoveis = ref(false); 
const isLoadingModelos = ref(false); 
const error = ref<string | null>(null);

const tipoContratoLabel = computed(() => {
  return contrato.value.tipo_contrato === 'VENDA' 
    ? { principal: 'Comprador', outraParte: 'Comprador' } 
    : { principal: 'Inquilino', outraParte: 'Inquilino' };
});

// --- SMART SYNC DATAS (RESTAURADO) ---

const addMonths = (dateStr: string, months: number): string => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  d.setMonth(d.getMonth() + months);
  return d.toISOString().split('T')[0];
};

const diffMonths = (startStr: string, endStr: string): number => {
  if (!startStr || !endStr) return 0;
  const start = new Date(startStr);
  const end = new Date(endStr);
  let months = (end.getFullYear() - start.getFullYear()) * 12;
  months -= start.getMonth();
  months += end.getMonth();
  return months <= 0 ? 0 : months;
};

// 1. Mudou Início ou Duração -> Recalcula Fim
watch(
  [() => contrato.value.data_inicio, () => contrato.value.duracao_meses],
  ([newInicio, newDuracao]) => {
    if (newInicio && newDuracao && contrato.value.tipo_contrato === 'ALUGUEL') {
       contrato.value.data_fim = addMonths(newInicio, Number(newDuracao));
    }
  }
);

// 2. Mudou Fim (evento manual) -> Recalcula Duração
const handleDataFimChange = () => {
  if (contrato.value.data_inicio && contrato.value.data_fim) {
    const meses = diffMonths(contrato.value.data_inicio, contrato.value.data_fim);
    contrato.value.duracao_meses = meses;
  }
};

// --- LÓGICA DE NEGÓCIO ---

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

const handleDataAssinaturaChange = () => {
  if (contrato.value.tipo_contrato === 'VENDA') {
    contrato.value.data_inicio = contrato.value.data_assinatura;
  }
}

const handleTipoChange = () => {
    contrato.value.proprietario = null;
    contrato.value.imovel = null;
    contrato.value.modelo_utilizado = null;
    
    if (contrato.value.tipo_contrato === 'ALUGUEL') {
        contrato.value.valor_total = null;
        contrato.value.duracao_meses = 12;
    } else {
        contrato.value.aluguel = null;
        contrato.value.data_inicio = contrato.value.data_assinatura;
        calcularComissaoValor();
    }
};

const getStatusClass = (status: string) => {
    switch (status) {
        case 'ATIVO': return 'status-active';
        case 'RASCUNHO': return 'status-draft';
        case 'CONCLUIDO': return 'status-done';
        case 'CANCELADO': return 'status-cancelled';
        default: return '';
    }
};

// --- FETCH FUNCTIONS ---

async function fetchInitialDependencies() {
  try {
    const clientesRes = await apiClient.get('/v1/clientes/lista-simples/');
    todosClientesOptions.value = clientesRes.data.map((c: any) => ({
      label: c.nome_display,
      value: c.id,
    }));
  } catch (err) {
    console.error('Erro clientes:', err);
  }
}

async function fetchProprietarioOptions(tipo: string) {
    if (!tipo) return;
    isLoadingProprietarios.value = true;
    const params = { finalidade: tipo === 'VENDA' ? 'A_VENDA' : 'PARA_ALUGAR' }; 
    try {
        const res = await apiClient.get('/v1/clientes/lista-proprietarios/', { params });
        proprietarioOptions.value = res.data.map((c: any) => ({
            label: c.nome_display,
            value: c.id,
        }));
    } catch (err) {
        console.error('Erro proprietários:', err);
    } finally {
        isLoadingProprietarios.value = false;
    }
}

async function fetchImovelOptions(tipo: string, proprietarioId: number | null) {
  if (!tipo || !proprietarioId) { 
      imovelOptions.value = [];
      return;
  }
  isLoadingImoveis.value = true;
  const params = { 
      status: tipo === 'VENDA' ? 'A_VENDA' : 'PARA_ALUGAR', 
      proprietario: proprietarioId, 
  };
  try {
    const res = await apiClient.get('/v1/imoveis/lista-simples/', { params });
    imovelOptions.value = res.data.map((i: any) => ({
        label: `#${i.codigo_referencia} - ${i.titulo_anuncio || i.logradouro}`,
        value: i.id,
        aluguel: i.valor_aluguel,
        venda: i.valor_venda
    }));
  } catch (err) {
    console.error('Erro imóveis:', err);
  } finally {
    isLoadingImoveis.value = false;
  }
}

async function fetchModeloContratoOptions(tipo: string) {
  if (!tipo) return;
  isLoadingModelos.value = true;
  try {
    const res = await apiClient.get('/v1/modelos-contrato/', { params: { tipo_contrato: tipo } });
    modeloContratoOptions.value = res.data.map((m: any) => ({
      label: m.padrao ? `${m.nome} (Padrão)` : m.nome,
      value: m.id,
      padrao: m.padrao,
    }));
    
    if (!isEditing.value && !contrato.value.modelo_utilizado) {
        const padrao = modeloContratoOptions.value.find(o => o.padrao);
        if (padrao) contrato.value.modelo_utilizado = padrao.value;
    }
  } catch (err) {
    console.error('Erro modelos:', err);
  } finally {
    isLoadingModelos.value = false;
  }
}

async function fetchContrato() {
  try {
    const response = await apiClient.get(`/v1/contratos/${contratoId}/`); 
    const data = response.data;

    if (data.status_contrato === 'ATIVO' && data.tipo_contrato === 'VENDA') {
        alert("Contrato de Venda finalizado. Edição bloqueada.");
        router.push({ name: 'contratos' });
        return;
    }

    if (data.tipo_contrato) {
        await fetchProprietarioOptions(data.tipo_contrato);
        await fetchModeloContratoOptions(data.tipo_contrato);
    }
    if (data.tipo_contrato && (data.proprietario || data.proprietario_detalhes?.id)) {
        const propId = data.proprietario_detalhes?.id || data.proprietario;
        await fetchImovelOptions(data.tipo_contrato, propId);
    }

    contrato.value = {
        ...data,
        fiadores: (data.fiadores || []).map((f: any) => (typeof f === 'object' ? f.id : f)),
        taxa_administracao_percentual: parseFloat(data.taxa_administracao_percentual) || 0,
        comissao_venda_percentual: parseFloat(data.comissao_venda_percentual) || 0,
        aluguel: data.aluguel ? parseFloat(data.aluguel) : null,
        valor_total: data.valor_total ? parseFloat(data.valor_total) : null,
        valor_comissao_acordado: data.valor_comissao_acordado ? parseFloat(data.valor_comissao_acordado) : null,
        proprietario: data.proprietario_detalhes?.id || data.proprietario, 
        inquilino: data.inquilino_detalhes?.id || data.inquilino,
        imovel: data.imovel_detalhes?.id || data.imovel,
        modelo_utilizado: data.modelo_utilizado?.id || data.modelo_utilizado || null, 
    };

  } catch (err) {
    console.error('Erro ao carregar contrato:', err);
    error.value = 'Não foi possível carregar os dados do contrato.';
  }
}

// --- WATCHERS ---

watch(() => contrato.value.tipo_contrato, (newTipo, oldTipo) => {
    if (isLoading.value && isEditing.value) return;
    
    if (newTipo) {
        fetchProprietarioOptions(newTipo);
        fetchModeloContratoOptions(newTipo);
    }
    if (oldTipo && newTipo !== oldTipo && !isLoading.value) {
        contrato.value.proprietario = null;
        contrato.value.imovel = null;
    }
});

watch(() => contrato.value.proprietario, (newProp, oldProp) => {
    if (isLoading.value && isEditing.value) return;

    if (newProp && contrato.value.tipo_contrato) {
        fetchImovelOptions(contrato.value.tipo_contrato, newProp);
    } else {
        imovelOptions.value = [];
    }
    
    if (oldProp && newProp !== oldProp && !isLoading.value) {
        contrato.value.imovel = null;
    }
});

watch(() => contrato.value.imovel, (newImovelId) => {
    if (!newImovelId || isLoading.value) return; 
    
    const selected = imovelOptions.value.find(o => o.value === newImovelId);
    if (selected) {
        if (contrato.value.tipo_contrato === 'ALUGUEL' && !contrato.value.aluguel) {
            contrato.value.aluguel = selected.aluguel ? parseFloat(String(selected.aluguel)) : null;
        } else if (contrato.value.tipo_contrato === 'VENDA' && !contrato.value.valor_total) {
            contrato.value.valor_total = selected.venda ? parseFloat(String(selected.venda)) : null;
            calcularComissaoValor();
        }
    }
});

// --- SUBMIT ---

async function handleSubmit() {
  if (!contrato.value.proprietario || !contrato.value.imovel || !contrato.value.inquilino) {
      alert("Por favor, preencha as partes do contrato (Proprietário, Imóvel e Cliente).");
      return;
  }

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
    console.error('Erro submit:', err);
    if (err.response?.data) {
        const errors = err.response.data;
        const firstKey = Object.keys(errors)[0];
        const msg = Array.isArray(errors[firstKey]) ? errors[firstKey][0] : errors[firstKey];
        error.value = `Erro no campo ${firstKey}: ${msg}`;
    } else {
        error.value = 'Erro ao salvar. Verifique sua conexão.';
    }
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(async () => {
  isLoading.value = true;
  await fetchInitialDependencies();
  
  if (isEditing.value) {
    await fetchContrato();
  } else {
    if (contrato.value.tipo_contrato) {
        await fetchProprietarioOptions(contrato.value.tipo_contrato);
        await fetchModeloContratoOptions(contrato.value.tipo_contrato);
    }
  }
  
  isLoading.value = false;
});
</script>

<style scoped>
/* =========================================================
   1. GERAL & LAYOUT
   ========================================================= */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  display: flex; flex-direction: column;
}

.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
.breadcrumb a:hover { color: #2563eb; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.main-content-grid { 
    display: grid; grid-template-columns: 1fr 320px; gap: 1.5rem; align-items: start; 
}
@media (max-width: 1100px) { .main-content-grid { grid-template-columns: 1fr; } }

/* =========================================================
   2. CARDS & SEÇÕES
   ========================================================= */
.card {
  background-color: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
  padding: 1.5rem; border: 1px solid #e5e7eb;
}
.form-card { min-height: 400px; }
.info-card { padding: 1.2rem; margin-bottom: 1rem; border-left: 3px solid #e5e7eb; }

.form-section { margin-bottom: 2rem; }
.section-title {
    font-size: 1rem; color: #1f2937; margin-bottom: 1.2rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9; font-weight: 600; display: flex; align-items: center; gap: 0.6rem;
}
.section-title i { color: #2563eb; font-size: 0.9rem; }
.compact-section { margin-bottom: 0; }

/* Grid de Campos */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 500; font-size: 0.85rem; color: #4b5563; }
.req { color: #ef4444; }

/* Inputs */
.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; font-size: 0.85rem; pointer-events: none; }

.form-input, .form-select, .form-textarea {
    width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.9rem; transition: all 0.2s; background-color: #fff; box-sizing: border-box; color: #1f2937;
    height: 40px;
}
.form-input.has-icon { padding-left: 2.2rem; }
.form-input:focus, .form-select:focus, .form-textarea:focus { 
    border-color: #3b82f6; outline: none; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
.form-input:disabled { background-color: #f3f4f6; cursor: not-allowed; color: #9ca3af; }
.form-textarea { resize: vertical; min-height: 80px; font-family: inherit; height: auto; }

/* Select Status Especial */
.status-select { font-weight: 600; }
.status-active { color: #16a34a; border-color: #86efac; background-color: #f0fdf4; }
.status-draft { color: #64748b; border-color: #e2e8f0; background-color: #f8fafc; }
.status-done { color: #2563eb; border-color: #bfdbfe; background-color: #eff6ff; }
.status-cancelled { color: #ef4444; border-color: #fecaca; background-color: #fef2f2; }

/* Widget Styles */
.widget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f1f5f9; }
.widget-title { font-size: 0.9rem; font-weight: 600; margin: 0; color: #374151; }
.helper-text-widget { font-size: 0.75rem; color: #9ca3af; margin-top: 0.3rem; font-style: italic; display: block; }

/* Toggle Tipo Contrato */
.tipo-toggle { display: flex; gap: 1rem; padding: 0.5rem; background: #f9fafb; border-radius: 8px; border: 1px solid #f3f4f6; width: fit-content; }
.radio-label {
    padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; color: #6b7280; font-size: 0.9rem; font-weight: 500; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem;
}
.radio-label:hover { background: #e5e7eb; }
.radio-label.active { background: white; color: #2563eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-weight: 600; }
.radio-label input { display: none; }

/* Footer Actions */
.form-actions-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f1f5f9; }
.btn-primary, .btn-secondary { padding: 0.5rem 1.2rem; border-radius: 6px; border: none; font-weight: 500; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; text-decoration: none; }
.btn-primary { background-color: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.1); }
.btn-primary:hover { background-color: #1d4ed8; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-secondary { background-color: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.btn-secondary:hover { background-color: #f1f5f9; border-color: #cbd5e1; color: #334155; }

/* Loading & Error */
.loading-state { text-align: center; padding: 4rem; color: #64748b; }
.error-banner { 
    background-color: #fef2f2; border: 1px solid #fecaca; color: #991b1b; 
    padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem; 
    display: flex; align-items: center; gap: 0.8rem; font-size: 0.9rem;
}
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Estilização v-select para match com form-input */
:deep(.style-chooser .vs__dropdown-toggle) {
    height: 40px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; padding: 0 0 4px 0;
}
:deep(.style-chooser.vs--open .vs__dropdown-toggle) { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }
:deep(.style-chooser .vs__search::placeholder) { color: #9ca3af; font-size: 0.9rem; margin-left: 6px; }
:deep(.style-chooser .vs__selected) { font-size: 0.9rem; color: #1f2937; margin-top: 6px; margin-left: 6px; }
:deep(.style-chooser.vs--disabled .vs__dropdown-toggle) { background-color: #f3f4f6; cursor: not-allowed; }

@media (max-width: 1024px) { .page-container { padding: 1rem; } }
@media (max-width: 640px) { .form-grid { grid-template-columns: 1fr; } }
</style>
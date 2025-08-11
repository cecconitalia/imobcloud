<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">{{ formTitle }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>A carregar dados...</p>
    </div>

    <div v-else class="form-card">
      <form @submit.prevent="submitForm">
        
        <div class="form-row">
          <div class="form-group">
            <label for="tipo" class="form-label">Tipo:</label>
            <select id="tipo" v-model="transacao.tipo" class="form-input" required>
              <option disabled value="">Selecione o tipo</option>
              <option value="RECEITA">Receita</option>
              <option value="DESPESA">Despesa</option>
            </select>
          </div>

          <div class="form-group">
            <label for="status" class="form-label">Status:</label>
            <select id="status" v-model="transacao.status" class="form-input" required>
              <option value="PENDENTE">Pendente</option>
              <option value="PAGO">Pago</option>
              <option value="ATRASADO">Atrasado</option>
              <option value="CANCELADO">Cancelado</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="descricao" class="form-label">Descrição:</label>
          <input type="text" id="descricao" v-model="transacao.descricao" class="form-input" required>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="valor" class="form-label">Valor:</label>
            <input type="number" id="valor" v-model.number="transacao.valor" class="form-input" required step="0.01">
          </div>
          <div class="form-group">
            <label for="data_vencimento" class="form-label">Data de Vencimento:</label>
            <input type="date" id="data_vencimento" v-model="transacao.data_vencimento" class="form-input" required>
          </div>
          <div class="form-group">
            <label for="data_pagamento" class="form-label">Data de Pagamento (Opcional):</label>
            <input type="date" id="data_pagamento" v-model="transacao.data_pagamento" class="form-input">
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="conta_bancaria" class="form-label">Conta Bancária:</label>
            <select id="conta_bancaria" v-model="transacao.conta_bancaria" class="form-input" required>
              <option disabled value="">Selecione uma conta</option>
              <option v-for="conta in contasBancarias" :key="conta.id" :value="conta.id">
                {{ conta.nome }} - {{ conta.banco }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="categoria" class="form-label">Categoria:</label>
            <select id="categoria" v-model="transacao.categoria" class="form-input" required>
              <option disabled value="">Selecione uma categoria</option>
              <option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">
                {{ categoria.nome }} ({{ categoria.tipo }})
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Imóvel (Opcional):</label>
          <input
            type="text"
            v-model="imovelSearchTerm"
            placeholder="Pesquisar imóvel por título"
            class="form-input"
            @focus="showImovelList = true"
            @blur="hideImovelList"
          />
          <ul v-show="showImovelList && filteredImoveis.length > 0" class="imovel-results">
            <li
              v-for="imovel in filteredImoveis"
              :key="imovel.id"
              @mousedown.prevent="selectImovel(imovel)"
            >
              {{ imovel.titulo_anuncio }}
            </li>
          </ul>
          <div v-if="transacao.imovel" class="selected-imovel">
            Imóvel Selecionado: <span>{{ getImovelTitle(transacao.imovel) }}</span>
            <button @click="clearImovel" type="button" class="clear-button">x</button>
          </div>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="actions">
          <button type="submit" class="submit-button">{{ submitButtonText }}</button>
          <button @click="router.back()" type="button" class="cancel-link">Cancelar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';

interface Transacao {
  id?: number;
  tipo: 'RECEITA' | 'DESPESA' | '';
  valor: number;
  descricao: string;
  conta_bancaria: number | null;
  categoria: number | null;
  imovel: number | null;
  data_vencimento: string;
  data_pagamento: string | null;
  status: 'PENDENTE' | 'PAGO' | 'ATRASADO' | 'CANCELADO';
}
interface ContaBancaria { id: number; nome: string; banco: string; }
interface Categoria { id: number; nome: string; tipo: 'RECEITA' | 'DESPESA'; }
interface Imovel { id: number; titulo_anuncio: string; }

const route = useRoute();
const router = useRouter();

const transacao = ref<Transacao>({
  tipo: '',
  valor: 0,
  descricao: '',
  conta_bancaria: null,
  categoria: null,
  imovel: null,
  data_vencimento: new Date().toISOString().split('T')[0],
  data_pagamento: null,
  status: 'PENDENTE',
});

const contasBancarias = ref<ContaBancaria[]>([]);
const categorias = ref<Categoria[]>([]);
const imoveis = ref<Imovel[]>([]);
const imovelSearchTerm = ref('');
const showImovelList = ref(false);
const isLoading = ref(false);
const error = ref<string | null>(null);

const isEditing = computed(() => !!route.params.id);

// --- LÓGICA INTELIGENTE PARA O FORMULÁRIO ---
const isPaymentMode = computed(() => {
  // O modo de pagamento é ativado se estivermos editando uma conta que está pendente ou atrasada
  return isEditing.value && (transacao.value.status === 'PENDENTE' || transacao.value.status === 'ATRASADO');
});

const formTitle = computed(() => {
  if (isPaymentMode.value) {
    return transacao.value.tipo === 'RECEITA' ? 'Confirmar Recebimento' : 'Confirmar Pagamento';
  }
  return isEditing.value ? 'Editar Transação' : 'Adicionar Nova Transação';
});

const submitButtonText = computed(() => {
  if (isPaymentMode.value) {
    return 'Confirmar e Marcar como Pago';
  }
  return 'Salvar';
});
// --- FIM DA LÓGICA INTELIGENTE ---

const fetchData = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const [contasResponse, categoriasResponse, imoveisResponse] = await Promise.all([
      api.get('/v1/financeiro/contas/'),
      api.get('/v1/financeiro/categorias/'),
      api.get('/v1/imoveis/imoveis/'),
    ]);
    contasBancarias.value = contasResponse.data;
    categorias.value = categoriasResponse.data;
    imoveis.value = imoveisResponse.data.results || imoveisResponse.data;

    if (isEditing.value) {
      const id = Number(route.params.id);
      const transacaoResponse = await api.get(`/v1/financeiro/transacoes/${id}/`);
      transacao.value = transacaoResponse.data;

      if (transacao.value.imovel) {
        const imovelSelecionado = imoveis.value.find(i => i.id === transacao.value.imovel);
        if (imovelSelecionado) {
          imovelSearchTerm.value = imovelSelecionado.titulo_anuncio;
        }
      }
      
      // Se estamos em modo de pagamento e ainda não há data, preenchemos com hoje.
      if (isPaymentMode.value && !transacao.value.data_pagamento) {
        transacao.value.data_pagamento = new Date().toISOString().split('T')[0];
      }
    }
  } catch (err) {
    console.error('Erro ao carregar dados:', err);
    error.value = 'Falha ao carregar dados. Verifique a conexão com a API.';
  } finally {
    isLoading.value = false;
  }
};

const submitForm = async () => {
  try {
    const payload = { ...transacao.value };
    
    // Limpeza de dados antes do envio
    if (!payload.imovel) payload.imovel = null;
    if (!payload.categoria) payload.categoria = null;
    
    // Lógica para atualizar o status com base na data de pagamento
    if (payload.data_pagamento) {
        payload.status = 'PAGO';
    } else if (payload.status === 'PAGO') {
        // Se o usuário remover a data de pagamento, a conta volta a ser pendente
        payload.status = 'PENDENTE';
    }
    
    if (isEditing.value) {
      await api.put(`/v1/financeiro/transacoes/${transacao.value.id}/`, payload);
    } else {
      await api.post('/v1/financeiro/transacoes/', payload);
    }
    router.back(); // Volta para a página anterior (ContasPendentes ou ListaTransacoes)
  } catch (err: any) {
    console.error('Erro ao salvar transação:', err);
    if (err.response && err.response.data) {
      error.value = JSON.stringify(err.response.data);
    } else {
      error.value = 'Falha ao salvar a transação. Verifique os dados e tente novamente.';
    }
  }
};

const filteredImoveis = computed(() => {
  if (!imovelSearchTerm.value || getImovelTitle(transacao.value.imovel) === imovelSearchTerm.value) {
    return imoveis.value;
  }
  const term = imovelSearchTerm.value.toLowerCase();
  return imoveis.value.filter(imovel => imovel.titulo_anuncio.toLowerCase().includes(term));
});

const selectImovel = (imovel: Imovel) => {
  transacao.value.imovel = imovel.id;
  imovelSearchTerm.value = imovel.titulo_anuncio;
  showImovelList.value = false;
};

const getImovelTitle = (id: number | null) => {
  const imovel = imoveis.value.find(i => i.id === id);
  return imovel ? imovel.titulo_anuncio : '';
};

const clearImovel = () => {
  transacao.value.imovel = null;
  imovelSearchTerm.value = '';
};

const hideImovelList = () => {
  setTimeout(() => {
    if (!document.activeElement?.closest('.imovel-results')) {
      showImovelList.value = false;
    }
  }, 100);
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
/* Os seus estilos estão corretos e foram mantidos */
.form-row { display: flex; gap: 1.5rem; }
.form-row .form-group { flex: 1; }
.page-container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
.header-section { margin-bottom: 2rem; text-align: center; }
.page-title { font-size: 2rem; font-weight: bold; color: #333; }
.form-card { background-color: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
.loading-state { text-align: center; font-size: 1.2rem; color: #666; }
.form-group { margin-bottom: 1.5rem; position: relative; }
.form-label { display: block; font-weight: bold; margin-bottom: 0.5rem; color: #555; }
.form-input { width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 1rem; transition: border-color 0.3s; }
.form-input:focus { outline: none; border-color: #007bff; }
.imovel-results { position: absolute; width: 100%; max-height: 200px; overflow-y: auto; background-color: white; border: 1px solid #ccc; border-top: none; z-index: 10; border-radius: 0 0 6px 6px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); list-style-type: none; padding: 0; margin: 0; }
.imovel-results li { padding: 10px 12px; cursor: pointer; }
.imovel-results li:hover { background-color: #f1f1f1; }
.selected-imovel { margin-top: 10px; padding: 8px 12px; background-color: #e2f0ff; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
.clear-button { background-color: #dc3545; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; font-size: 0.8rem; cursor: pointer; }
.actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem; }
.submit-button, .cancel-link { padding: 12px 24px; border-radius: 6px; text-decoration: none; font-size: 1rem; font-weight: bold; cursor: pointer; transition: background-color 0.3s, color 0.3s; }
.submit-button { background-color: #007bff; color: white; border: none; }
.submit-button:hover { background-color: #0056b3; }
.cancel-link { background-color: #6c757d; color: white; border: none; }
.cancel-link:hover { background-color: #5a6268; }
.error-message { color: #d9534f; background-color: #f2dede; border: 1px solid #ebccd1; padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 1rem; }
</style>
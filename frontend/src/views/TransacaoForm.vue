<template>
  <div class="page-container">
    <div class="view-header">
      <h2>{{ isEditing ? 'Editar Transação' : 'Nova Transação' }}</h2>
    </div>

    <div class="form-card card">
      <form @submit.prevent="submitForm">
        <div class="form-group" v-if="!isEditing">
          <label for="tipo">Tipo de Transação</label>
          <select id="tipo" v-model="transacao.tipo" required :disabled="isEditing">
            <option value="RECEITA">Receita</option>
            <option value="DESPESA">Despesa</option>
          </select>
        </div>
        
        <div class="form-row">
          <div class="form-group flex-3">
            <label for="descricao">Descrição</label>
            <input type="text" id="descricao" v-model="transacao.descricao" required>
          </div>
          <div class="form-group flex-1">
            <label for="valor">Valor (R$)</label>
            <MoneyInput v-model="transacao.valor" required />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="data_transacao">Data de Emissão</label>
            <input type="date" id="data_transacao" v-model="transacao.data_transacao" required>
          </div>
          <div class="form-group">
            <label for="data_vencimento">Data de Vencimento</label>
            <input type="date" id="data_vencimento" v-model="transacao.data_vencimento" required>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group flex-2">
            <label for="status">Status</label>
            <select id="status" v-model="transacao.status" @change="handleStatusChange">
              <option value="PENDENTE">Pendente</option>
              <option value="PAGO">Pago</option>
              <option value="ATRASADO">Atrasado</option>
            </select>
          </div>
          
          <div class="form-group flex-2">
            <label for="data_pagamento">Data de Pagamento</label>
            <input 
                type="date" 
                id="data_pagamento" 
                v-model="transacao.data_pagamento" 
                :disabled="transacao.status !== 'PAGO'"
            >
            <p class="help-text">Preenchido automaticamente ao marcar como Pago.</p>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="categoria">Categoria</label>
            <select id="categoria" v-model="transacao.categoria">
              <option :value="null">Selecione a Categoria</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nome }} ({{ cat.tipo }})</option>
            </select>
          </div>
          <div class="form-group">
            <label for="conta">Conta</label>
            <select id="conta" v-model="transacao.conta">
              <option :value="null">Selecione a Conta</option>
              <option v-for="conta in contas" :key="conta.id" :value="conta.id">{{ conta.nome }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="forma_pagamento">Forma de Pagamento</label>
            <select id="forma_pagamento" v-model="transacao.forma_pagamento">
              <option :value="null">Selecione a Forma</option>
              <option v-for="forma in formasPagamento" :key="forma.id" :value="forma.id">{{ forma.nome }}</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group flex-2">
            <label for="cliente">Cliente (Pagador/Recebedor)</label>
            <select id="cliente" v-model="transacao.cliente">
              <option :value="null">Selecione o Cliente (Opcional)</option>
              <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">{{ cliente.nome_exibicao }}</option>
            </select>
          </div>
          <div class="form-group flex-2">
            <label for="imovel">Imóvel</label>
            <select id="imovel" v-model="transacao.imovel">
              <option :value="null">Selecione o Imóvel (Opcional)</option>
              <option v-for="imovel in imoveis" :key="imovel.id" :value="imovel.id">{{ imovel.titulo_anuncio }}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="observacoes">Observações</label>
          <textarea id="observacoes" v-model="transacao.observacoes"></textarea>
        </div>

        <div class="action-buttons">
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Salvando...' : (isEditing ? 'Salvar Alterações' : 'Criar Transação') }}
          </button>
          <button type="button" @click="router.back()" class="btn-secondary">Cancelar</button>
        </div>
      </form>
    </div>

    <div v-if="error" class="error-message card">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import MoneyInput from '@/components/MoneyInput.vue';
import { format } from 'date-fns';

interface Transacao {
  id?: number;
  descricao: string;
  valor: number | null;
  data_transacao: string;
  data_vencimento: string;
  data_pagamento: string | null;
  tipo: 'RECEITA' | 'DESPESA' | '';
  status: 'PENDENTE' | 'PAGO' | 'ATRASADO' | string;
  categoria: number | null;
  conta: number | null;
  forma_pagamento: number | null;
  cliente: number | null;
  imovel: number | null;
  observacoes: string;
}

// Assumindo interfaces simplificadas para dropdowns
interface DropdownItem {
  id: number;
  nome: string;
}
interface ClienteDropdown extends DropdownItem {
  nome_exibicao: string;
}
interface CategoriaDropdown extends DropdownItem {
  tipo: 'RECEITA' | 'DESPESA';
}
interface ImovelDropdown {
  id: number;
  titulo_anuncio: string;
}


const route = useRoute();
const router = useRouter();
const isEditing = ref(!!route.params.id);
const transacaoId = route.params.id as string;

// Inicializa a transação, usando query params se for 'Nova Receita/Despesa'
const initialTipo = (route.query.tipo as 'RECEITA' | 'DESPESA') || '';

const transacao = ref<Transacao>({
  descricao: '',
  valor: null,
  data_transacao: format(new Date(), 'yyyy-MM-dd'),
  data_vencimento: format(new Date(), 'yyyy-MM-dd'),
  data_pagamento: null,
  tipo: initialTipo,
  status: 'PENDENTE',
  categoria: null,
  conta: null,
  forma_pagamento: null,
  cliente: null,
  imovel: null,
  observacoes: '',
});

const categorias = ref<CategoriaDropdown[]>([]);
const contas = ref<DropdownItem[]>([]);
const formasPagamento = ref<DropdownItem[]>([]);
const clientes = ref<ClienteDropdown[]>([]);
const imoveis = ref<ImovelDropdown[]>([]);

const isSubmitting = ref(false);
const error = ref<string | null>(null);

// ===============================================
// NOVO: Lógica de Automação de Data de Pagamento
// ===============================================
const handleStatusChange = () => {
  if (transacao.value.status === 'PAGO') {
    // Preenche data_pagamento com a data atual no formato YYYY-MM-DD
    transacao.value.data_pagamento = format(new Date(), 'yyyy-MM-dd');
  } else {
    // Limpa o campo se o status for alterado
    transacao.value.data_pagamento = null;
  }
};
// ===============================================

async function fetchDependencies() {
  try {
    const [
        categoriasRes, 
        contasRes, 
        formasRes, 
        clientesRes,
        imoveisRes
    ] = await Promise.all([
      apiClient.get<CategoriaDropdown[]>('/v1/financeiro/categorias/'),
      apiClient.get<DropdownItem[]>('/v1/financeiro/contas/'),
      apiClient.get<DropdownItem[]>('/v1/financeiro/formas-pagamento/'),
      apiClient.get<ClienteDropdown[]>('/v1/clientes/clientes/'), // Assumindo endpoint de lista completa
      apiClient.get<ImovelDropdown[]>('/v1/imoveis/imoveis/'), // Assumindo endpoint de lista
    ]);

    categorias.value = categoriasRes.data.filter(c => c.tipo === transacao.value.tipo);
    contas.value = contasRes.data;
    formasPagamento.value = formasRes.data;
    clientes.value = clientesRes.data;
    imoveis.value = imoveisRes.data;

  } catch (err) {
    console.error("Erro ao carregar dependências:", err);
    error.value = "Não foi possível carregar as listas de categorias/contas/clientes.";
  }
}

async function fetchTransacao() {
  try {
    const response = await apiClient.get<Transacao>(`/v1/financeiro/transacoes/${transacaoId}/`);
    const data = response.data;
    
    // Mapeamento dos dados da API para o formulário
    transacao.value = {
        descricao: data.descricao,
        valor: data.valor,
        data_transacao: data.data_transacao,
        data_vencimento: data.data_vencimento,
        data_pagamento: data.data_pagamento,
        tipo: data.tipo,
        status: data.status,
        // Converte FKs para IDs (assumindo que a API retorna o ID se não for aninhado)
        categoria: data.categoria || null,
        conta: data.conta || null,
        forma_pagamento: data.forma_pagamento || null,
        cliente: data.cliente || null,
        imovel: data.imovel || null,
        observacoes: data.observacoes,
    };

    // Filtra categorias após carregar a transação para garantir o tipo correto
    await fetchDependencies();

  } catch (err) {
    console.error("Erro ao carregar transação:", err);
    error.value = "Não foi possível carregar os dados da transação.";
  }
}

async function submitForm() {
  isSubmitting.value = true;
  error.value = null;

  // Lógica de validação simples antes de enviar
  if (!transacao.value.descricao || transacao.value.valor === null || transacao.value.valor === undefined) {
    error.value = "Descrição e Valor são obrigatórios.";
    isSubmitting.value = false;
    return;
  }
  
  try {
    const payload = {
        ...transacao.value,
        // Limpar o data_pagamento se o status for PENDENTE ou ATRASADO
        data_pagamento: transacao.value.status === 'PAGO' ? transacao.value.data_pagamento : null,
    }

    if (isEditing.value) {
      await apiClient.put(`/v1/financeiro/transacoes/${transacaoId}/`, payload);
      alert('Transação atualizada com sucesso! O repasse foi verificado.');
    } else {
      await apiClient.post('/v1/financeiro/transacoes/', payload);
      alert('Transação criada com sucesso!');
    }
    router.push({ name: 'contas-a-receber' }); // Redireciona para a tela de recebíveis
  } catch (err) {
    console.error("Erro ao salvar transação:", err);
    error.value = "Erro ao salvar transação. Verifique se todos os campos obrigatórios estão corretos e tente novamente.";
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  if (isEditing.value) {
    fetchTransacao();
  } else {
    // Se for nova transação, carrega apenas as dependências iniciais
    fetchDependencies();
    // Garante que o tipo seja definido se veio da query param
    if (initialTipo) {
        transacao.value.tipo = initialTipo;
    }
  }
});
</script>

<style scoped>
.page-container {
  padding: 0;
}
.view-header {
  margin-bottom: 1rem;
}
.view-header h2 {
  font-size: 1.8rem;
  color: #343a40;
}

.form-card {
  padding: 20px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.form-group.flex-3 {
    flex: 3;
}
.form-group.flex-2 {
    flex: 2;
}
.form-group.flex-1 {
    flex: 1;
}

label {
  font-weight: 600;
  margin-bottom: 5px;
  color: #495057;
  font-size: 0.9rem;
}

input[type="text"], 
input[type="number"], 
input[type="date"], 
select, 
textarea {
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

select:disabled {
  background-color: #f8f9fa;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.error-message {
  margin-top: 15px;
  padding: 15px;
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.help-text {
    font-size: 0.8rem;
    color: #6c757d;
    margin-top: 5px;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  .form-group {
    margin-bottom: 15px;
  }
}
</style>
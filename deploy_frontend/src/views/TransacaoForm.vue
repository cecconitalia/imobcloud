<template>
  <div class="page-container">
    <header class="header-actions">
      <div class="header-title">
        <button @click="router.back()" class="btn-back" title="Voltar">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <div>
          <h2>{{ isEditing ? 'Editar Lançamento' : 'Novo Lançamento' }}</h2>
          <span class="subtitle">Gestão Financeira</span>
        </div>
      </div>
      
      <div class="status-badge" :class="transacao.tipo">
        {{ transacao.tipo === 'RECEITA' ? 'Entrada' : transacao.tipo === 'DESPESA' ? 'Saída' : 'Defina o Tipo' }}
      </div>
    </header>

    <form @submit.prevent="submitForm" class="form-layout">
      
      <div class="layout-grid">
        
        <div class="main-column">
          <section class="card">
            <h3 class="card-title">Detalhes da Transação</h3>
            
            <div class="form-group" v-if="!isEditing">
              <label>Tipo de Operação</label>
              <div class="type-toggle">
                <label class="toggle-option" :class="{ active: transacao.tipo === 'RECEITA' }">
                  <input type="radio" value="RECEITA" v-model="transacao.tipo" name="tipo">
                  <span>Receita (Entrada)</span>
                </label>
                <label class="toggle-option" :class="{ active: transacao.tipo === 'DESPESA' }">
                  <input type="radio" value="DESPESA" v-model="transacao.tipo" name="tipo">
                  <span>Despesa (Saída)</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>Descrição do Lançamento <span class="required">*</span></label>
              <input 
                type="text" 
                v-model="transacao.descricao" 
                required 
                placeholder="Ex: Aluguel Referência Maio/2025 - Apto 304"
                class="input-lg"
              >
            </div>

            <div class="form-group">
              <label>Valor Total (R$) <span class="required">*</span></label>
              <div class="money-wrapper">
                <MoneyInput 
                  v-model="transacao.valor" 
                  required 
                  class="input-money-lg" 
                />
              </div>
            </div>

            <div class="form-group">
              <label>Observações</label>
              <textarea 
                v-model="transacao.observacoes" 
                rows="5" 
                placeholder="Informações adicionais, histórico de negociação..."
              ></textarea>
            </div>
          </section>
        </div>

        <div class="side-column">
          
          <section class="card">
            <h3 class="card-title">Prazos e Situação</h3>
            
            <div class="grid-row">
              <div class="form-group">
                <label>Vencimento <span class="required">*</span></label>
                <input type="date" v-model="transacao.data_vencimento" required class="input-date-highlight">
              </div>
              <div class="form-group">
                <label>Emissão</label>
                <input type="date" v-model="transacao.data_transacao" required>
              </div>
            </div>

            <div class="form-group">
              <label>Status Atual</label>
              <select v-model="transacao.status" @change="handleStatusChange" :class="'status-' + transacao.status.toLowerCase()">
                <option value="PENDENTE">🕒 Pendente</option>
                <option value="PAGO">✅ Pago / Baixado</option>
                <option value="ATRASADO">⚠️ Atrasado</option>
              </select>
            </div>

            <div v-if="transacao.status === 'PAGO'" class="payment-details">
              <div class="form-group">
                <label>Data Efetiva do Pagamento</label>
                <input type="date" v-model="transacao.data_pagamento" required>
              </div>
            </div>
          </section>

          <section class="card">
            <h3 class="card-title">Classificação Financeira</h3>
            
            <div class="form-group">
              <label>Categoria (DRE)</label>
              <select v-model="transacao.categoria">
                <option :value="null">Selecione a Categoria...</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nome }}</option>
              </select>
            </div>

            <div class="grid-row">
              <div class="form-group">
                <label>Conta / Caixa</label>
                <select v-model="transacao.conta">
                  <option :value="null">Selecione...</option>
                  <option v-for="c in contas" :key="c.id" :value="c.id">{{ c.nome }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Forma Pagto</label>
                <select v-model="transacao.forma_pagamento">
                  <option :value="null">Selecione...</option>
                  <option v-for="f in formasPagamento" :key="f.id" :value="f.id">{{ f.nome }}</option>
                </select>
              </div>
            </div>
          </section>

          <section class="card">
            <h3 class="card-title">Vínculos (Opcional)</h3>
            
            <div class="form-group">
              <label>Cliente</label>
              <select v-model="transacao.cliente">
                <option :value="null">-- Nenhum --</option>
                <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome_exibicao }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Imóvel</label>
              <select v-model="transacao.imovel">
                <option :value="null">-- Nenhum --</option>
                <option v-for="i in imoveis" :key="i.id" :value="i.id">{{ i.titulo_anuncio }}</option>
              </select>
            </div>
          </section>

        </div>
      </div>

      <div class="footer-actions">
        <button type="button" @click="router.back()" class="btn-cancel">Cancelar</button>
        <button type="submit" class="btn-save" :disabled="isSubmitting">
          {{ isSubmitting ? 'Salvando...' : 'Salvar Lançamento' }}
        </button>
      </div>
    </form>
    
    <div v-if="error" class="error-toast">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import MoneyInput from '@/components/MoneyInput.vue';
import { format } from 'date-fns';

// --- Interfaces ---
interface Transacao {
  id?: number;
  descricao: string;
  valor: number | null;
  data_transacao: string;
  data_vencimento: string;
  data_pagamento: string | null;
  tipo: 'RECEITA' | 'DESPESA' | '';
  status: string;
  categoria: number | null;
  conta: number | null;
  forma_pagamento: number | null;
  cliente: number | null;
  imovel: number | null;
  observacoes: string;
}

interface DropdownItem { id: number; nome: string; }
interface ClienteDropdown extends DropdownItem { nome_exibicao: string; }
interface CategoriaDropdown extends DropdownItem { tipo: 'RECEITA' | 'DESPESA'; }
interface ImovelDropdown { id: number; titulo_anuncio: string; }

// --- Refs ---
const route = useRoute();
const router = useRouter();
const isEditing = ref(!!route.params.id);
const transacaoId = route.params.id as string;
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

// --- Lógica ---
const handleStatusChange = () => {
  if (transacao.value.status === 'PAGO') {
    if (!transacao.value.data_pagamento) {
      transacao.value.data_pagamento = format(new Date(), 'yyyy-MM-dd');
    }
  } else {
    transacao.value.data_pagamento = null;
  }
};

async function fetchDependencies() {
  try {
    const [cats, accs, pays, clis, props] = await Promise.all([
      apiClient.get<CategoriaDropdown[]>('/v1/financeiro/categorias/'),
      apiClient.get<DropdownItem[]>('/v1/financeiro/contas/'),
      apiClient.get<DropdownItem[]>('/v1/financeiro/formas-pagamento/'),
      // Correção de URL para evitar duplicação e erro 404
      apiClient.get<ClienteDropdown[]>('/v1/clientes/'),
      apiClient.get<ImovelDropdown[]>('/v1/imoveis/')
    ]);
    
    const allCategorias = cats.data;
    categorias.value = transacao.value.tipo 
      ? allCategorias.filter(c => c.tipo === transacao.value.tipo)
      : allCategorias;

    contas.value = accs.data;
    formasPagamento.value = pays.data;
    clientes.value = clis.data;
    imoveis.value = props.data;
  } catch (e) {
    console.error(e);
    error.value = "Erro ao carregar dados auxiliares. Verifique sua conexão.";
  }
}

async function fetchTransacao() {
  try {
    const res = await apiClient.get<Transacao>(`/v1/financeiro/transacoes/${transacaoId}/`);
    transacao.value = { ...res.data };
    await fetchDependencies();
  } catch (e) {
    error.value = "Erro ao buscar dados da transação.";
  }
}

async function submitForm() {
  if (!transacao.value.descricao || !transacao.value.valor) {
    error.value = "Preencha a descrição e o valor.";
    return;
  }
  
  isSubmitting.value = true;
  try {
    const payload = {
      ...transacao.value,
      data_pagamento: transacao.value.status === 'PAGO' ? transacao.value.data_pagamento : null
    };

    if (isEditing.value) {
      await apiClient.put(`/v1/financeiro/transacoes/${transacaoId}/`, payload);
    } else {
      await apiClient.post('/v1/financeiro/transacoes/', payload);
    }
    router.push({ name: 'contas-a-receber' });
  } catch (e) {
    error.value = "Erro ao salvar. Verifique os dados e tente novamente.";
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  if (isEditing.value) fetchTransacao();
  else fetchDependencies();
  
  if (initialTipo) transacao.value.tipo = initialTipo;
});
</script>

<style scoped>
/* --- Layout Base --- */
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 100px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #1f2937;
}

/* --- Grid Layout Principal --- */
.layout-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1024px) {
  .layout-grid {
    grid-template-columns: 3fr 2fr; /* Coluna esquerda maior */
    align-items: start;
  }
}

/* --- Header --- */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #4b5563;
  transition: all 0.2s;
}
.btn-back:hover { background: #e5e7eb; color: #111827; }

h2 { margin: 0; font-size: 1.5rem; font-weight: 700; color: #111827; }
.subtitle { font-size: 0.875rem; color: #6b7280; }

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
}
.status-badge.RECEITA { background: #d1fae5; color: #065f46; }
.status-badge.DESPESA { background: #fee2e2; color: #991b1b; }

/* --- Cards --- */
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.06);
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #f3f4f6;
}

.card-title {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #f3f4f6;
  padding-bottom: 8px;
}

/* --- Inputs & Groups --- */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-group:last-child { margin-bottom: 0; }

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4b5563;
}

.required { color: #ef4444; }

input, select, textarea, .input-money-lg {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-lg { font-size: 1.1rem; padding: 12px; }
.input-money-lg { font-size: 1.5rem; font-weight: 700; color: #111827; text-align: left; }
.input-date-highlight { font-weight: 600; color: #111827; }

textarea { resize: vertical; min-height: 100px; }

/* --- Toggle de Tipo --- */
.type-toggle {
  display: flex;
  background: #f3f4f6;
  padding: 4px;
  border-radius: 8px;
}
.toggle-option {
  flex: 1;
  text-align: center;
  padding: 8px;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  color: #6b7280;
  transition: all 0.2s;
}
.toggle-option input { display: none; }
.toggle-option.active { background: white; color: #111827; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }

/* --- Grid de 2 Colunas --- */
.grid-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

/* --- Status Cores --- */
.status-pago { color: #059669; font-weight: 700; background-color: #ecfdf5; }
.status-pendente { color: #d97706; font-weight: 700; background-color: #fffbeb; }
.status-atrasado { color: #dc2626; font-weight: 700; background-color: #fef2f2; }

/* --- Área de Pagamento --- */
.payment-details {
  background: #f0f9ff;
  padding: 16px;
  border-radius: 8px;
  border: 1px dashed #bae6fd;
  margin-top: 16px;
}

/* --- Footer --- */
.footer-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  z-index: 100;
  box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.05);
}

.btn-cancel {
  padding: 10px 24px;
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.btn-cancel:hover { background: #f9fafb; }

.btn-save {
  padding: 10px 32px;
  background: #111827;
  border: none;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-save:hover { background: #1f2937; }
.btn-save:disabled { background: #9ca3af; cursor: not-allowed; }

/* --- Error Toast --- */
.error-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #fef2f2;
  color: #991b1b;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #ef4444;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 200;
  font-weight: 600;
}
</style>
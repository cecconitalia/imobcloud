<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <router-link to="/">Início</router-link>
              <i class="fas fa-chevron-right separator"></i> 
              <router-link to="/financeiro">Financeiro</router-link>
              <i class="fas fa-chevron-right separator"></i>
              <span class="active">{{ isEditing ? 'Editar' : 'Novo' }}</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Lançamento' : 'Novo Lançamento' }}</h1>
        </div>
      </div>
    </header>

    <div v-if="isLoadingData" class="loading-state">
         <div class="spinner"></div>
         <p>A carregar dados...</p>
    </div>

    <form v-else @submit.prevent="submitForm" class="main-content-grid">
      
      <div class="left-column">
        <div class="card form-card">
            
            <div class="form-section" v-if="!isEditing">
                <div class="tipo-toggle-wrapper">
                    <label class="radio-label" :class="{ 'active-receita': transacao.tipo === 'RECEITA' }">
                        <input type="radio" value="RECEITA" v-model="transacao.tipo" name="tipo">
                        <i class="fas fa-arrow-up"></i> Receita
                    </label>
                    <label class="radio-label" :class="{ 'active-despesa': transacao.tipo === 'DESPESA' }">
                        <input type="radio" value="DESPESA" v-model="transacao.tipo" name="tipo">
                        <i class="fas fa-arrow-down"></i> Despesa
                    </label>
                </div>
            </div>

            <div class="form-section compact-section">
                <h3 class="section-title"><i class="far fa-file-alt"></i> Detalhes da Transação</h3>
                
                <div class="form-grid">
                    <div class="form-group full-width">
                        <label>Descrição <span class="required">*</span></label>
                        <div class="input-wrapper">
                            <i class="fas fa-pen input-icon"></i>
                            <input 
                                type="text" 
                                v-model="transacao.descricao" 
                                required 
                                class="form-input has-icon" 
                                placeholder="Ex: Aluguel Apto 304 - Maio/2025" 
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Valor Total</label>
                        <MoneyInput 
                            v-model="transacao.valor" 
                            required 
                            class="form-input" 
                            :prefix="'R$ '"
                        />
                    </div>

                    <div class="form-group">
                        <label>Categoria (DRE)</label>
                        <div class="input-wrapper">
                            <i class="fas fa-tag input-icon"></i>
                            <select v-model="transacao.categoria" class="form-select has-icon">
                                <option :value="null">Selecione...</option>
                                <option v-for="cat in categoriasFiltradas" :key="cat.id" :value="cat.id">
                                    {{ cat.nome }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group full-width">
                        <label>Observações</label>
                        <textarea 
                            v-model="transacao.observacoes" 
                            rows="4" 
                            class="form-textarea" 
                            placeholder="Informações adicionais..."
                        ></textarea>
                    </div>
                </div>
            </div>

            <div class="form-actions-footer">
                <button type="button" @click="router.back()" class="btn-secondary">Cancelar</button>
                <button type="submit" class="btn-primary" :disabled="isSubmitting">
                    <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
                    <span v-else>{{ isEditing ? 'Salvar Alterações' : 'Lançar Transação' }}</span>
                </button>
            </div>
        </div>
      </div> 
      
      <div class="right-column">
            
            <div class="card info-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="far fa-calendar-check"></i> Prazos e Status</h3>
                 </div>
                 
                 <div class="form-group">
                    <label>Situação Atual</label>
                    <select v-model="transacao.status" @change="handleStatusChange" class="form-select status-select" :class="getStatusClass(transacao.status)">
                        <option value="PENDENTE">🕒 Pendente</option>
                        <option value="PAGO">✅ Pago / Recebido</option>
                        <option value="ATRASADO">⚠️ Atrasado</option>
                    </select>
                 </div>

                 <div class="form-group">
                    <label>Data de Vencimento <span class="required">*</span></label>
                    <input type="date" v-model="transacao.data_vencimento" required class="form-input" />
                 </div>

                 <div class="form-group">
                    <label>Data de Emissão</label>
                    <input type="date" v-model="transacao.data_transacao" required class="form-input" />
                 </div>

                 <div v-if="transacao.status === 'PAGO'" class="payment-area fade-in">
                    <div class="form-group">
                        <label>Data do Pagamento <span class="required">*</span></label>
                        <input type="date" v-model="transacao.data_pagamento" required class="form-input" />
                    </div>
                 </div>
            </div>

            <div class="card info-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-wallet"></i> Movimentação</h3>
                 </div>

                 <div class="form-group">
                    <label>Conta / Caixa</label>
                    <select v-model="transacao.conta" class="form-select">
                        <option :value="null">Selecione...</option>
                        <option v-for="c in contas" :key="c.id" :value="c.id">{{ c.nome }}</option>
                    </select>
                 </div>

                 <div class="form-group">
                    <label>Forma de Pagamento</label>
                    <select v-model="transacao.forma_pagamento" class="form-select">
                        <option :value="null">Selecione...</option>
                        <option v-for="f in formasPagamento" :key="f.id" :value="f.id">{{ f.nome }}</option>
                    </select>
                 </div>
            </div>

            <div class="card info-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-link"></i> Vínculos</h3>
                 </div>

                 <div class="form-group">
                    <label>Cliente</label>
                    <select v-model="transacao.cliente" class="form-select">
                        <option :value="null">-- Sem vínculo --</option>
                        <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome_exibicao }}</option>
                    </select>
                 </div>

                 <div class="form-group">
                    <label>Imóvel</label>
                    <select v-model="transacao.imovel" class="form-select">
                        <option :value="null">-- Sem vínculo --</option>
                        <option v-for="i in imoveis" :key="i.id" :value="i.id">{{ i.titulo_anuncio }}</option>
                    </select>
                 </div>
            </div>

      </div> 

    </form>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import MoneyInput from '@/components/MoneyInput.vue';
import { format } from 'date-fns';
import { useToast } from 'vue-toast-notification';

// --- Interfaces ---
interface Transacao {
  id?: number;
  descricao: string;
  valor: number | null;
  data_transacao: string;
  data_vencimento: string;
  data_pagamento: string | null;
  tipo: 'RECEITA' | 'DESPESA';
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

const route = useRoute();
const router = useRouter();
const toast = useToast();

const isEditing = ref(!!route.params.id);
const transacaoId = route.params.id as string;
const initialTipo = (route.query.tipo as 'RECEITA' | 'DESPESA') || 'RECEITA';

const isLoadingData = ref(false);
const isSubmitting = ref(false);

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

const categoriasFiltradas = computed(() => {
    return categorias.value.filter(c => c.tipo === transacao.value.tipo);
});

const handleStatusChange = () => {
  if (transacao.value.status === 'PAGO' && !transacao.value.data_pagamento) {
      transacao.value.data_pagamento = format(new Date(), 'yyyy-MM-dd');
  } else if (transacao.value.status !== 'PAGO') {
      transacao.value.data_pagamento = null;
  }
};

const getStatusClass = (status: string) => {
    switch(status) {
        case 'PAGO': return 'text-success-bold';
        case 'ATRASADO': return 'text-danger-bold';
        default: return 'text-warning-bold';
    }
};

async function fetchDependencies() {
  try {
    const [cats, accs, pays, clis, props] = await Promise.all([
      apiClient.get('/v1/financeiro/categorias/'),
      apiClient.get('/v1/financeiro/contas/'),
      apiClient.get('/v1/financeiro/formas-pagamento/'),
      apiClient.get('/v1/clientes/lista-simples/'), // Endpoint otimizado se existir, senão usar o padrão
      apiClient.get('/v1/imoveis/lista-simples/')
    ]);
    
    // Tratamento genérico para lista ou results
    const getData = (res: any) => Array.isArray(res.data) ? res.data : (res.data.results || []);

    categorias.value = getData(cats);
    contas.value = getData(accs);
    formasPagamento.value = getData(pays);
    
    // Mapeamento para garantir campos corretos
    const clisData = getData(clis);
    clientes.value = clisData.map((c: any) => ({
        id: c.id, 
        nome: c.nome, 
        nome_exibicao: c.nome_display || c.nome || c.razao_social || 'Cliente'
    }));

    const propsData = getData(props);
    imoveis.value = propsData.map((i: any) => ({
        id: i.id,
        titulo_anuncio: i.titulo_anuncio || i.titulo || `Imóvel #${i.id}`
    }));

  } catch (e) {
    console.error(e);
    toast.error("Erro ao carregar listas auxiliares.");
  }
}

async function fetchTransacao() {
  isLoadingData.value = true;
  try {
    const res = await apiClient.get<Transacao>(`/v1/financeiro/transacoes/${transacaoId}/`);
    transacao.value = { ...res.data };
    await fetchDependencies();
  } catch (e) {
    toast.error("Erro ao buscar dados da transação.");
    router.push('/financeiro');
  } finally {
    isLoadingData.value = false;
  }
}

async function submitForm() {
  if (!transacao.value.descricao || !transacao.value.valor || !transacao.value.data_vencimento) {
    toast.warning("Preencha os campos obrigatórios (Descrição, Valor, Vencimento).");
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
      toast.success("Lançamento atualizado!");
    } else {
      await apiClient.post('/v1/financeiro/transacoes/', payload);
      toast.success("Lançamento criado com sucesso!");
    }
    router.back();
  } catch (e: any) {
    console.error(e);
    toast.error("Erro ao salvar. Verifique os dados.");
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  if (isEditing.value) fetchTransacao();
  else fetchDependencies();
});
</script>

<style scoped>
/* =========================================================
   1. GERAL & HEADER (PADRÃO)
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
.form-card { min-height: 400px; display: flex; flex-direction: column; }
.info-card { padding: 1.2rem; margin-bottom: 1rem; border-left: 3px solid #e5e7eb; }

.form-section { margin-bottom: 2rem; }
.section-title {
    font-size: 1rem; color: #1f2937; margin-bottom: 1.2rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9; font-weight: 600; display: flex; align-items: center; gap: 0.6rem;
}
.compact-section { margin-bottom: 0; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 500; font-size: 0.85rem; color: #4b5563; }
.required { color: #ef4444; }

/* Inputs */
.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; font-size: 0.85rem; pointer-events: none; }
.form-input, .form-select, .form-textarea {
    width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.9rem; transition: all 0.2s; background-color: #fff; box-sizing: border-box; color: #1f2937;
    font-family: inherit;
}
.form-input.has-icon, .form-select.has-icon { padding-left: 2.2rem; }
.form-input:focus, .form-select:focus, .form-textarea:focus { 
    border-color: #3b82f6; outline: none; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
.form-textarea { resize: vertical; min-height: 100px; }

/* =========================================================
   3. COMPONENTES ESPECÍFICOS (TOGGLE TIPO)
   ========================================================= */
.tipo-toggle-wrapper { display: flex; gap: 1rem; padding: 0.5rem; background: #f9fafb; border-radius: 8px; border: 1px solid #f3f4f6; width: fit-content; }
.radio-label {
    padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; color: #6b7280; font-size: 0.9rem; font-weight: 500; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem;
}
.radio-label:hover { background: #e5e7eb; }
.radio-label i { font-size: 0.8rem; }
.radio-label input { display: none; }

.radio-label.active-receita { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.radio-label.active-despesa { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

/* Status Styles in Select */
.status-select { font-weight: 600; }
.text-success-bold { color: #059669; border-color: #86efac; background-color: #f0fdf4; }
.text-warning-bold { color: #d97706; border-color: #fcd34d; background-color: #fffbeb; }
.text-danger-bold { color: #dc2626; border-color: #fca5a5; background-color: #fef2f2; }

.payment-area { margin-top: 1rem; padding-top: 1rem; border-top: 1px dashed #e2e8f0; }
.fade-in { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

/* Footer Actions */
.form-actions-footer {
    display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: auto; padding-top: 2rem; border-top: 1px solid #f1f5f9;
}
.btn-primary, .btn-secondary {
    padding: 0.5rem 1.2rem; border-radius: 6px; border: none; font-weight: 500; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary { background-color: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.1); }
.btn-primary:hover { background-color: #1d4ed8; transform: translateY(-1px); }
.btn-secondary { background-color: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.btn-secondary:hover { background-color: #f1f5f9; border-color: #cbd5e1; color: #334155; }

/* Widgets */
.widget-header { margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f1f5f9; }
.widget-title { font-size: 0.9rem; font-weight: 600; margin: 0; color: #374151; }

/* Loading */
.loading-state { text-align: center; padding: 4rem; color: #64748b; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
}
</style>
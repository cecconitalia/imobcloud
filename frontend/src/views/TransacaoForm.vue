<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Financeiro</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <router-link to="/financeiro/transacoes">Transações</router-link>
              <i class="fas fa-chevron-right separator"></i>
              <span class="active">{{ isEditing ? 'Editar' : 'Nova' }} Transação</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Lançamento' : 'Novo Lançamento' }}</h1>
        </div>
      </div>
    </header>

    <main class="content-wrapper">
        <div v-if="isLoading" class="loading-container">
            <div class="spinner"></div>
            <p>Carregando formulário...</p>
        </div>

        <form v-else @submit.prevent="handleSubmit" class="standard-form">
            
            <div class="form-section highlight-section">
                <div class="form-grid-top">
                    <div class="form-group type-selector">
                        <label>Tipo de Movimentação</label>
                        <div class="toggle-type">
                            <label class="type-option receita" :class="{ active: form.tipo === 'RECEITA' }">
                                <input type="radio" v-model="form.tipo" value="RECEITA">
                                <span class="icon"><i class="fas fa-arrow-up"></i></span>
                                <span class="text">Receita</span>
                            </label>
                            <label class="type-option despesa" :class="{ active: form.tipo === 'DESPESA' }">
                                <input type="radio" v-model="form.tipo" value="DESPESA">
                                <span class="icon"><i class="fas fa-arrow-down"></i></span>
                                <span class="text">Despesa</span>
                            </label>
                        </div>
                    </div>

                    <div class="form-group value-input">
                        <label>Valor (R$) *</label>
                        <MoneyInput v-model.number="form.valor" class="form-control money-field" :class="form.tipo === 'DESPESA' ? 'text-red' : 'text-green'" />
                    </div>

                    <div class="form-group date-input">
                        <label>Vencimento *</label>
                        <input type="date" v-model="form.data_vencimento" class="form-control" required>
                    </div>
                </div>

                <div class="form-group full-width mt-4">
                    <label>Descrição *</label>
                    <input type="text" v-model="form.descricao" class="form-control" placeholder="Ex: Aluguel Ref. Janeiro/2025" required>
                </div>
            </div>

            <div class="form-section">
                <h3 class="section-title"><i class="fas fa-link"></i> Vínculos</h3>
                <div class="form-grid-2col">
                    
                    <div class="form-group relative" ref="clienteDropdownRef">
                        <label>Cliente / Parte (Opcional)</label>
                        <div class="input-with-icon">
                            <i class="fas fa-user"></i>
                            <input 
                                type="text" 
                                v-model="clienteSearch" 
                                class="form-control" 
                                placeholder="Pesquisar por nome ou CPF/CNPJ..."
                                @focus="showClienteList = true"
                                @input="onClienteInput"
                            >
                            <i v-if="form.cliente || clienteSearch" class="fas fa-times clear-icon" @click="clearCliente" title="Limpar"></i>
                        </div>
                        
                        <ul v-if="showClienteList && filteredClientes.length > 0" class="dropdown-list">
                            <li v-for="c in filteredClientes" :key="c.id" @click="selectCliente(c)">
                                <div class="dd-main-text">{{ c.nome }}</div>
                                <div class="dd-sub-text" v-if="c.documento">{{ c.documento }}</div>
                            </li>
                        </ul>
                        <ul v-if="showClienteList && filteredClientes.length === 0 && clienteSearch" class="dropdown-list">
                            <li class="no-results">Nenhum cliente encontrado.</li>
                        </ul>
                    </div>

                    <div class="form-group relative" ref="imovelDropdownRef">
                        <label>Imóvel Vinculado (Opcional)</label>
                        <div class="input-with-icon">
                            <i class="fas fa-home"></i>
                            <input 
                                type="text" 
                                v-model="imovelSearch" 
                                class="form-control" 
                                placeholder="Pesquisar por código, título ou endereço..."
                                @focus="showImovelList = true"
                                @input="onImovelInput"
                            >
                            <i v-if="form.imovel || imovelSearch" class="fas fa-times clear-icon" @click="clearImovel" title="Limpar"></i>
                        </div>

                        <ul v-if="showImovelList && filteredImoveis.length > 0" class="dropdown-list">
                            <li v-for="i in filteredImoveis" :key="i.id" @click="selectImovel(i)">
                                <div class="dd-main-text"><span class="code">#{{ i.codigo_referencia }}</span> {{ i.titulo_anuncio }}</div>
                                <div class="dd-sub-text">{{ i.logradouro }}</div>
                            </li>
                        </ul>
                        <ul v-if="showImovelList && filteredImoveis.length === 0 && imovelSearch" class="dropdown-list">
                            <li class="no-results">Nenhum imóvel encontrado.</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3 class="section-title"><i class="fas fa-tags"></i> Classificação</h3>
                <div class="form-grid-3col">
                    <div class="form-group">
                        <label>Categoria *</label>
                        <div class="select-wrapper">
                            <select v-model="form.categoria" class="form-control" required>
                                <option :value="null" disabled>Selecione a Categoria</option>
                                <option v-for="cat in categoriasFiltradas" :key="cat.id" :value="cat.id">
                                    {{ cat.nome }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Conta (Destino/Origem) *</label>
                        <div class="select-wrapper">
                            <select v-model="form.conta" class="form-control" required>
                                <option :value="null" disabled>Selecione a Conta</option>
                                <option v-for="acc in contas" :key="acc.id" :value="acc.id">
                                    {{ acc.nome }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Forma de Pagamento</label>
                        <div class="select-wrapper">
                            <select v-model="form.forma_pagamento" class="form-control">
                                <option :value="null">Não definido</option>
                                <option v-for="fp in formasPagamento" :key="fp.id" :value="fp.id">
                                    {{ fp.nome }}
                                </option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-section last-section">
                <div class="form-grid-2col align-end">
                    <div class="form-group">
                        <label>Situação Atual</label>
                        <select v-model="form.status" @change="handleStatusChange" class="form-control status-select" :class="getStatusClass(form.status)">
                            <option value="PENDENTE">🕒 Pendente</option>
                            <option value="PAGO">✅ {{ form.tipo === 'RECEITA' ? 'Recebido' : 'Pago' }}</option>
                            <option value="ATRASADO">⚠️ Atrasado</option>
                            <option value="CANCELADO">🚫 Cancelado</option>
                        </select>
                    </div>

                    <div class="form-group" v-if="form.status === 'PAGO'">
                        <label>Data da Baixa (Pagamento) *</label>
                        <input type="date" v-model="form.data_pagamento" class="form-control" required>
                    </div>
                </div>

                <div class="form-group mt-4">
                    <label>Observações / Anotações</label>
                    <textarea v-model="form.observacoes" class="form-control" rows="2" placeholder="Detalhes adicionais sobre esta transação..."></textarea>
                </div>
            </div>

            <div class="form-footer">
                <button type="button" @click="router.push('/financeiro/transacoes')" class="btn-secondary">
                    Cancelar
                </button>
                <button type="submit" class="btn-primary" :disabled="isSubmitting">
                    <i class="fas" :class="isSubmitting ? 'fa-spinner fa-spin' : 'fa-save'"></i> 
                    {{ isSubmitting ? 'Salvando...' : 'Salvar Lançamento' }}
                </button>
            </div>

        </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient from '@/services/api';
import MoneyInput from '@/components/MoneyInput.vue';
import { format } from 'date-fns';
import { useToast } from 'vue-toast-notification';

// --- Interfaces ---
interface Imovel { id: number; codigo_referencia: string; titulo_anuncio?: string; logradouro?: string; }
interface Cliente { id: number; nome: string; documento?: string; }
interface Categoria { id: number; nome: string; tipo: 'RECEITA' | 'DESPESA'; }
interface Conta { id: number; nome: string; }
interface FormaPagamento { id: number; nome: string; }

// --- Estado ---
const router = useRouter();
const route = useRoute();
const toast = useToast();

const isEditing = computed(() => !!route.params.id);
const isLoading = ref(true);
const isSubmitting = ref(false);

const imoveis = ref<Imovel[]>([]);
const clientes = ref<Cliente[]>([]);
const categorias = ref<Categoria[]>([]);
const contas = ref<Conta[]>([]);
const formasPagamento = ref<FormaPagamento[]>([]);

// --- Estado do Autocomplete ---
const clienteSearch = ref('');
const showClienteList = ref(false);
const clienteDropdownRef = ref<HTMLElement | null>(null);

const imovelSearch = ref('');
const showImovelList = ref(false);
const imovelDropdownRef = ref<HTMLElement | null>(null);

// --- Formulário ---
const form = ref({
    tipo: 'RECEITA' as 'RECEITA' | 'DESPESA',
    descricao: '',
    valor: 0,
    data_vencimento: format(new Date(), 'yyyy-MM-dd'),
    data_transacao: format(new Date(), 'yyyy-MM-dd'), // Garante valor padrão
    data_pagamento: null as string | null,
    status: 'PENDENTE',
    categoria: null as number | null,
    conta: null as number | null,
    forma_pagamento: null as number | null,
    cliente: null as number | null,
    imovel: null as number | null,
    observacoes: ''
});

// --- Computed: Filtros ---
const categoriasFiltradas = computed(() => {
    return categorias.value.filter(c => c.tipo === form.value.tipo);
});

const filteredClientes = computed(() => {
    if (!clienteSearch.value) return clientes.value.slice(0, 10);
    const term = clienteSearch.value.toLowerCase();
    return clientes.value.filter(c => 
        c.nome.toLowerCase().includes(term) || (c.documento && c.documento.includes(term))
    ).slice(0, 10);
});

const filteredImoveis = computed(() => {
    if (!imovelSearch.value) return imoveis.value.slice(0, 10);
    const term = imovelSearch.value.toLowerCase();
    return imoveis.value.filter(i => 
        (i.titulo_anuncio || '').toLowerCase().includes(term) ||
        (i.logradouro || '').toLowerCase().includes(term) ||
        (i.codigo_referencia || '').toLowerCase().includes(term)
    ).slice(0, 10);
});

// --- Helper Visual ---
const getStatusClass = (status: string) => {
    switch(status) {
        case 'PAGO': return 'status-paid';
        case 'ATRASADO': return 'status-late';
        case 'CANCELADO': return 'status-cancelled';
        default: return 'status-pending';
    }
}

// --- Actions Autocomplete ---
const onClienteInput = () => {
    showClienteList.value = true;
    if (form.value.cliente) form.value.cliente = null; 
};

const selectCliente = (c: Cliente) => {
    form.value.cliente = c.id;
    clienteSearch.value = c.nome;
    showClienteList.value = false;
};

const clearCliente = () => {
    form.value.cliente = null;
    clienteSearch.value = '';
};

const onImovelInput = () => {
    showImovelList.value = true;
    if (form.value.imovel) form.value.imovel = null;
};

const selectImovel = (i: Imovel) => {
    form.value.imovel = i.id;
    imovelSearch.value = `#${i.codigo_referencia} - ${i.titulo_anuncio || i.logradouro}`;
    showImovelList.value = false;
};

const clearImovel = () => {
    form.value.imovel = null;
    imovelSearch.value = '';
};

const handleClickOutside = (event: MouseEvent) => {
    if (clienteDropdownRef.value && !clienteDropdownRef.value.contains(event.target as Node)) {
        showClienteList.value = false;
    }
    if (imovelDropdownRef.value && !imovelDropdownRef.value.contains(event.target as Node)) {
        showImovelList.value = false;
    }
};

// Handler para mudança de status (Preenchimento Automático)
const handleStatusChange = () => {
    if (form.value.status === 'PAGO' && !form.value.data_pagamento) {
        form.value.data_pagamento = format(new Date(), 'yyyy-MM-dd');
    }
};

// --- API ---
async function fetchDependencies() {
    try {
        const [resCat, resConta, resFP, resCli, resImob] = await Promise.all([
            apiClient.get('/v1/financeiro/categorias/'),
            apiClient.get('/v1/financeiro/contas/'),
            apiClient.get('/v1/financeiro/formas-pagamento/'),
            apiClient.get('/v1/clientes/lista-simples/'), 
            apiClient.get('/v1/imoveis/lista-simples/')
        ]);

        categorias.value = resCat.data.results || resCat.data;
        contas.value = resConta.data.results || resConta.data;
        formasPagamento.value = resFP.data.results || resFP.data;
        
        clientes.value = resCli.data.map((c: any) => ({
            id: c.id,
            nome: c.nome_display || c.nome || 'Sem Nome',
            documento: c.documento || c.cpf_cnpj
        }));
        
        imoveis.value = resImob.data;

        if (!isEditing.value) {
            if (contas.value.length > 0) form.value.conta = contas.value[0].id;
            if (route.query.tipo && (route.query.tipo === 'RECEITA' || route.query.tipo === 'DESPESA')) {
                form.value.tipo = route.query.tipo;
            }
        }

    } catch (err) {
        console.error("Erro ao carregar dependências", err);
        toast.error("Erro ao carregar listas de seleção.");
    }
}

async function fetchTransacao() {
    try {
        const { data } = await apiClient.get(`/v1/financeiro/transacoes/${route.params.id}/`);
        
        form.value = {
            tipo: data.tipo,
            descricao: data.descricao,
            valor: Number(data.valor),
            data_vencimento: data.data_vencimento,
            data_transacao: data.data_transacao || format(new Date(), 'yyyy-MM-dd'),
            data_pagamento: data.data_pagamento,
            status: data.status,
            categoria: data.categoria,
            conta: data.conta,
            forma_pagamento: data.forma_pagamento,
            cliente: data.cliente,
            imovel: data.imovel,
            observacoes: data.observacoes
        };

        if (data.cliente) {
            const cli = clientes.value.find(c => c.id === data.cliente);
            if (cli) clienteSearch.value = cli.nome;
        }
        if (data.imovel) {
            const imo = imoveis.value.find(i => i.id === data.imovel);
            if (imo) imovelSearch.value = `#${imo.codigo_referencia} - ${imo.titulo_anuncio || imo.logradouro}`;
        }

    } catch (err) {
        console.error("Erro ao carregar transação", err);
        toast.error("Erro ao carregar dados da transação.");
        router.push('/financeiro/transacoes');
    }
}

async function handleSubmit() {
    if (!form.value.categoria || !form.value.conta) {
        toast.warning("Categoria e Conta são obrigatórios.");
        return;
    }
    
    // Auto-preenchimento final de segurança
    if (form.value.status === 'PAGO' && !form.value.data_pagamento) {
        form.value.data_pagamento = format(new Date(), 'yyyy-MM-dd');
    }

    if (form.value.status === 'PAGO' && !form.value.data_pagamento) {
        toast.warning("Para transações PAGAS, a Data da Baixa é obrigatória.");
        return;
    }

    isSubmitting.value = true;

    const payload = { ...form.value };

    // Garante data_transacao
    if (!payload.data_transacao) payload.data_transacao = format(new Date(), 'yyyy-MM-dd');

    if (payload.status !== 'PAGO') payload.data_pagamento = null;
    
    if (!payload.cliente) payload.cliente = null;
    if (!payload.imovel) payload.imovel = null;
    if (!payload.forma_pagamento) payload.forma_pagamento = null;
    if (!payload.observacoes) payload.observacoes = "";

    try {
        if (isEditing.value) {
            await apiClient.put(`/v1/financeiro/transacoes/${route.params.id}/`, payload);
            toast.success("Transação atualizada com sucesso!");
        } else {
            await apiClient.post('/v1/financeiro/transacoes/', payload);
            toast.success("Transação criada com sucesso!");
        }
        // CORREÇÃO DO ERRO DE ROTA: Usando o caminho explícito
        router.push('/financeiro/transacoes');
    } catch (err: any) {
        console.error("Erro API:", err);
        if (err.response && err.response.data) {
            const errors = err.response.data;
            const firstKey = Object.keys(errors)[0];
            const msg = Array.isArray(errors[firstKey]) ? errors[firstKey][0] : errors[firstKey];
            toast.error(`Erro em ${firstKey}: ${msg}`);
        } else {
            toast.error("Erro ao salvar. Verifique os dados.");
        }
    } finally {
        isSubmitting.value = false;
    }
}

onMounted(async () => {
    isLoading.value = true;
    await fetchDependencies();
    if (isEditing.value) {
        await fetchTransacao();
    }
    isLoading.value = false;
    document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
/* ESTRUTURA GERAL */
.page-container {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Inter', sans-serif;
  padding: 1.5rem 2.5rem;
}

.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.6rem; font-weight: 300; color: #1e293b; margin: 5px 0 0 0; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #64748b; font-weight: 500; }
.breadcrumb a { text-decoration: none; color: #64748b; transition: color 0.2s; }
.breadcrumb a:hover { color: #2563eb; }
.breadcrumb .separator { font-size: 0.6rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 600; }

.content-wrapper { max-width: 900px; margin: 0 auto; }

/* FORMULÁRIO ESTILO CARD */
.standard-form {
    background: transparent;
    display: flex; flex-direction: column; gap: 1.5rem;
}

.form-section {
    background: white; border-radius: 12px; border: 1px solid #e2e8f0;
    padding: 1.8rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.highlight-section { border-left: 4px solid #3b82f6; } 

.section-title {
    font-size: 0.95rem; font-weight: 600; color: #334155; margin: 0 0 1.2rem 0;
    text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;
    display: flex; align-items: center; gap: 8px;
}
.section-title i { color: #94a3b8; }

/* GRIDS E LAYOUT INTERNO */
.form-grid-top {
    display: grid; grid-template-columns: 2fr 1.5fr 1.5fr; gap: 1.5rem; align-items: start;
}
.form-grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.form-grid-3col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem; }

.form-group { display: flex; flex-direction: column; gap: 0.4rem; position: relative; }
.form-group label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em; }

/* INPUTS E CONTROLES */
.form-control {
    width: 100%; padding: 0.65rem 0.8rem; border: 1px solid #cbd5e1;
    border-radius: 6px; font-size: 0.9rem; color: #1e293b;
    transition: all 0.2s; box-sizing: border-box; background-color: #fff;
    height: 40px;
}
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); outline: none; }
textarea.form-control { height: auto; min-height: 80px; resize: vertical; }

.select-wrapper { position: relative; }
.select-wrapper::after {
    content: '\f078'; font-family: 'Font Awesome 5 Free'; font-weight: 900;
    position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
    color: #94a3b8; font-size: 0.7rem; pointer-events: none;
}
select.form-control { appearance: none; cursor: pointer; }

/* TOGGLE TIPO (RECEITA/DESPESA) */
.toggle-type { display: flex; background: #f1f5f9; padding: 4px; border-radius: 8px; gap: 4px; height: 40px; }
.type-option {
    flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
    cursor: pointer; border-radius: 6px; font-size: 0.85rem; font-weight: 600; color: #64748b;
    transition: all 0.2s; position: relative; overflow: hidden;
}
.type-option input { display: none; }
.type-option:hover { background: #e2e8f0; color: #475569; }

.type-option.receita.active { background: #dcfce7; color: #15803d; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.type-option.despesa.active { background: #fee2e2; color: #b91c1c; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

/* MONEY INPUT CORES */
.money-field { font-weight: 700; }
.text-green { color: #15803d; }
.text-red { color: #b91c1c; }

/* AUTOCOMPLETE */
.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; }
.input-with-icon .clear-icon { left: auto; right: 12px; cursor: pointer; pointer-events: auto; }
.input-with-icon .clear-icon:hover { color: #ef4444; }
.input-with-icon input { padding-left: 2.2rem; padding-right: 2.2rem; }

.dropdown-list {
    position: absolute; top: 100%; left: 0; right: 0; z-index: 50;
    background: white; border: 1px solid #cbd5e1; border-radius: 6px;
    margin-top: 4px; max-height: 220px; overflow-y: auto;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); list-style: none; padding: 0;
}
.dropdown-list li {
    padding: 0.7rem 1rem; cursor: pointer; border-bottom: 1px solid #f1f5f9;
    transition: background 0.1s;
}
.dropdown-list li:last-child { border-bottom: none; }
.dropdown-list li:hover { background-color: #f8fafc; }
.dd-main-text { font-size: 0.9rem; color: #1e293b; font-weight: 500; }
.dd-sub-text { font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }
.no-results { padding: 1rem; color: #94a3b8; text-align: center; font-style: italic; font-size: 0.85rem; }
.code { font-weight: 700; color: #3b82f6; }

/* STATUS STYLES */
.status-select { font-weight: 600; }
.status-pending { border-left: 4px solid #cbd5e1; }
.status-paid { border-left: 4px solid #10b981; color: #065f46; }
.status-late { border-left: 4px solid #f59e0b; color: #92400e; }
.status-cancelled { border-left: 4px solid #ef4444; color: #991b1b; }

/* RODAPÉ */
.form-footer {
    display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem;
    padding-top: 1rem; border-top: 1px solid #e2e8f0;
}
.btn-primary {
    background-color: #2563eb; color: white; border: none; padding: 0.7rem 1.8rem;
    border-radius: 6px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px;
    transition: all 0.2s; font-size: 0.9rem;
}
.btn-primary:hover { background-color: #1d4ed8; transform: translateY(-1px); box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

.btn-secondary {
    background-color: white; color: #64748b; border: 1px solid #cbd5e1; padding: 0.7rem 1.5rem;
    border-radius: 6px; font-weight: 500; cursor: pointer; transition: all 0.2s; font-size: 0.9rem;
}
.btn-secondary:hover { background-color: #f1f5f9; color: #334155; border-color: #94a3b8; }

.loading-container { text-align: center; padding: 6rem; color: #64748b; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* RESPONSIVIDADE */
@media (max-width: 768px) {
    .page-container { padding: 1rem; }
    .form-grid-top, .form-grid-2col, .form-grid-3col { grid-template-columns: 1fr; gap: 1rem; }
    .form-footer { flex-direction: column-reverse; }
    .btn-primary, .btn-secondary { width: 100%; justify-content: center; }
}
</style>
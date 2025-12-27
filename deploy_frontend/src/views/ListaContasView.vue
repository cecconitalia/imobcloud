<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Financeiro</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Contas e Caixas</span>
           </nav>
           <h1>Gerenciar Contas</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchContas" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            <button class="btn-primary-thin" @click="abrirModalNova">
              <i class="fas fa-plus"></i> Nova Conta
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(stats.saldo_total) }}</span>
          <span class="kpi-label">Saldo Consolidado</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-vault"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.qtd_bancos }}</span>
          <span class="kpi-label">Contas Bancárias</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-university"></i></div>
      </div>

      <div class="kpi-card orange">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.qtd_caixas }}</span>
          <span class="kpi-label">Caixas Internos</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-wallet"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value text-compact">{{ stats.conta_padrao || 'Nenhuma' }}</span>
          <span class="kpi-label">Conta Principal</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-star"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell search-cell">
          <label>Buscar Conta</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Nome da conta, banco ou agência..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-cell">
          <label>Tipo</label>
          <select v-model="filterTipo" class="form-control">
            <option value="">Todos os Tipos</option>
            <option value="CORRENTE">Conta Corrente</option>
            <option value="POUPANCA">Poupança</option>
            <option value="CAIXA">Caixa Interno</option>
            <option value="INVESTIMENTO">Investimento</option>
          </select>
        </div>

        <div class="filter-cell clear-cell">
            <label>&nbsp;</label>
            <button @click="resetFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="content-wrapper">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando contas bancárias...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-circle text-red-500"></i>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="filteredContas.length === 0" class="empty-state">
        <i class="fas fa-university empty-icon"></i>
        <p>Nenhuma conta encontrada.</p>
      </div>

      <div v-else class="items-grid">
        <div 
          v-for="conta in filteredContas" 
          :key="conta.id" 
          class="item-card"
        >
          <div class="item-visual">
            <div :class="['bank-avatar', conta.tipo]">
               <i :class="getAccountIcon(conta.tipo)"></i>
            </div>
            <div class="type-tag">{{ formatTipo(conta.tipo) }}</div>
          </div>

          <div class="item-details">
            <div class="item-header">
              <h3 class="item-title">
                {{ conta.nome }}
                <i v-if="conta.is_padrao" class="fas fa-star text-yellow-500 star-mini" title="Conta Principal"></i>
              </h3>
              <span class="item-subtitle">{{ conta.banco_nome || 'Gestão Interna' }}</span>
            </div>

            <div class="item-info-grid">
              <div class="info-group">
                <span class="info-label">Agência</span>
                <span class="info-value">{{ conta.agencia || '—' }}</span>
              </div>
              <div class="info-group">
                <span class="info-label">Nº Conta</span>
                <span class="info-value">{{ conta.numero_conta || '—' }}</span>
              </div>
            </div>

            <div class="item-price-area">
              <span class="price-label">Saldo Atual</span>
              <span :class="['price-value', conta.saldo >= 0 ? 'text-success' : 'text-danger']">
                {{ formatarValor(conta.saldo) }}
              </span>
            </div>
          </div>

          <div class="item-actions">
            <button @click="editarConta(conta)" class="btn-action-circle primary" title="Editar">
              <i class="fas fa-pen"></i>
            </button>
            <button @click="excluirConta(conta.id)" class="btn-action-circle danger" title="Excluir">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import { useToast } from 'vue-toast-notification';

interface Conta {
  id: number;
  nome: string;
  banco_nome?: string;
  tipo: string;
  agencia?: string;
  numero_conta?: string;
  saldo: number;
  is_padrao: boolean;
}

const contas = ref<Conta[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterTipo = ref('');
const toast = useToast();

const fetchContas = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/financeiro/contas/');
    contas.value = response.data.results || (Array.isArray(response.data) ? response.data : []);
  } catch (err: any) {
    error.value = "Não foi possível carregar os dados financeiros.";
  } finally {
    isLoading.value = false;
  }
};

const stats = computed(() => {
    if (!contas.value.length) return { saldo_total: 0, qtd_bancos: 0, qtd_caixas: 0, conta_padrao: '' };
    const saldoTotal = contas.value.reduce((acc, c) => acc + Number(c.saldo || 0), 0);
    const contaPadrao = contas.value.find(c => c.is_padrao)?.nome || '';
    return {
        saldo_total: saldoTotal,
        qtd_bancos: contas.value.filter(c => c.tipo !== 'CAIXA').length,
        qtd_caixas: contas.value.filter(c => c.tipo === 'CAIXA').length,
        conta_padrao: contaPadrao
    };
});

const filteredContas = computed(() => {
  return (contas.value || []).filter(c => {
    const nomeSearch = (c.nome || '').toLowerCase().includes(searchTerm.value.toLowerCase());
    const bancoSearch = (c.banco_nome || '').toLowerCase().includes(searchTerm.value.toLowerCase());
    const matchTipo = filterTipo.value === '' || c.tipo === filterTipo.value;
    return (nomeSearch || bancoSearch) && matchTipo;
  });
});

const formatarValor = (v: number) => (v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const formatTipo = (t: string) => {
    const map: any = { CORRENTE: 'C. Corrente', POUPANCA: 'Poupança', CAIXA: 'Caixa', INVESTIMENTO: 'Investimento' };
    return map[t] || t;
};
const getAccountIcon = (t: string) => {
    if (t === 'CAIXA') return 'fas fa-wallet';
    if (t === 'INVESTIMENTO') return 'fas fa-chart-line';
    return 'fas fa-university';
};
const resetFilters = () => { searchTerm.value = ''; filterTipo.value = ''; };
const abrirModalNova = () => {};
const editarConta = (c: any) => {};
const excluirConta = (id: number) => {};

onMounted(fetchContas);
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (Baseada em /imoveis) */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER */
.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

.btn-primary-thin { background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem; border-radius: 6px; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; }
.btn-icon-thin { background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

/* KPI GRID (Estilo Imóveis) */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; margin-bottom: 2rem; }
.kpi-card { background: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); position: relative; overflow: hidden; }
.kpi-value { font-size: 1.4rem; font-weight: 400; color: #111; }
.text-compact { font-size: 0.95rem; font-weight: 600; color: #111; }
.kpi-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-top: 4px; letter-spacing: 0.02em;}
.kpi-icon { font-size: 1.8rem; opacity: 0.1; }

.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.purple .kpi-value { color: #9333ea; }
.kpi-card.orange .kpi-value { color: #d97706; }
.kpi-card.green .kpi-value { color: #10b981; }

/* TOOLBAR (Estilo Imóveis) */
.toolbar-grid {
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 1.25rem;
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 1.25rem;
  align-items: end;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.filter-cell label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 0.5rem; display: block; }
.input-with-icon { position: relative; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.input-with-icon .form-control { padding-left: 2.5rem; }
.form-control { padding: 0.6rem 0.8rem; font-size: 0.85rem; border: 1px solid #e2e8f0; border-radius: 8px; height: 42px; width: 100%; transition: all 0.2s; }
.form-control:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); outline: none; }
.btn-clear { width: 42px; height: 42px; border: 1px solid #e2e8f0; background: #f8fafc; border-radius: 8px; color: #64748b; cursor: pointer; }

/* GRID DE ITEMS (Cópia exata de /imoveis) */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.item-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  display: flex;
  padding: 1.25rem;
  gap: 1.25rem;
  transition: all 0.2s;
  position: relative;
}
.item-card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: #cbd5e1; }

/* Visual lateral (Como a foto do imóvel) */
.item-visual {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.bank-avatar {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: #64748b;
}
.bank-avatar.CORRENTE { background: #eff6ff; color: #2563eb; }
.bank-avatar.CAIXA { background: #fff7ed; color: #d97706; }
.bank-avatar.INVESTIMENTO { background: #faf5ff; color: #9333ea; }

.type-tag {
  font-size: 0.6rem;
  font-weight: 800;
  text-transform: uppercase;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
  color: #475569;
}

/* Detalhes centrais */
.item-details { flex-grow: 1; min-width: 0; }
.item-header { margin-bottom: 0.75rem; }
.item-title { font-size: 1.05rem; font-weight: 700; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 8px; }
.star-mini { font-size: 0.8rem; }
.item-subtitle { font-size: 0.8rem; color: #94a3b8; font-weight: 500; }

.item-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem 0;
  border-top: 1px solid #f8fafc;
  border-bottom: 1px solid #f8fafc;
}
.info-group { display: flex; flex-direction: column; }
.info-label { font-size: 0.6rem; text-transform: uppercase; color: #94a3b8; font-weight: 700; }
.info-value { font-size: 0.85rem; color: #334155; font-weight: 600; font-family: 'Inter', monospace; }

.item-price-area { display: flex; flex-direction: column; }
.price-label { font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.price-value { font-size: 1.2rem; font-weight: 800; }

/* Ações laterais */
.item-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.btn-action-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
}
.btn-action-circle.primary { background: #eff6ff; color: #2563eb; }
.btn-action-circle.primary:hover { background: #2563eb; color: white; }
.btn-action-circle.danger { background: #fff1f2; color: #e11d48; }
.btn-action-circle.danger:hover { background: #e11d48; color: white; }

/* Estados */
.loading-state, .error-state, .empty-state { text-align: center; padding: 5rem; color: #94a3b8; }
.spinner { border: 3px solid #f1f5f9; border-top: 3px solid #2563eb; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.text-success { color: #10b981; }
.text-danger { color: #ef4444; }

@media (max-width: 1024px) {
  .items-grid { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .toolbar-grid { grid-template-columns: 1fr; }
}
</style>
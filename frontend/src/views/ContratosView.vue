<template>
  <div class="page-container">
    <div class="filters-bar card">
      <div class="search-wrapper">
        <i class="fas fa-search"></i>
        <input
          type="text"
          v-model="searchTerm"
          placeholder="Pesquisar por imóvel, inquilino, proprietário..."
        />
      </div>
      <div class="filter-groups">
        <select v-model="filterStatus">
          <option value="">Todos os Status</option>
          <option value="ATIVO">Ativo</option>
          <option value="PENDENTE">Pendente</option>
          <option value="CONCLUIDO">Concluído</option>
          <option value="RESCINDIDO">Rescindido</option>
          <option value="INATIVO">Inativo</option>
        </select>
        <select v-model="filterTipo">
          <option value="">Todos os Tipos</option>
          <option value="VENDA">Venda</option>
          <option value="ALUGUEL">Aluguel</option>
        </select>
      </div>
    </div>

    <div v-if="isLoading" class="loading-message card">
        <div class="spinner"></div>
        A carregar contratos...
    </div>
    <div v-if="error" class="error-message card">{{ error }}</div>

    <div v-if="filteredContratos.length > 0 && !isLoading" class="contratos-grid">
      <div v-for="contrato in filteredContratos" :key="contrato.id" class="contrato-card">
        <div class="card-header">
           <span :class="['status-badge', getStatusClass(contrato.status)]">{{ formatStatus(contrato.status) }}</span>
           <span class="tipo-badge">{{ contrato.tipo === 'VENDA' ? 'Venda' : 'Aluguel' }}</span>
        </div>
        <div class="card-body">
            <p><strong>Imóvel:</strong> {{ contrato.imovel_detalhes?.titulo_anuncio || contrato.imovel_detalhes?.codigo_referencia || 'N/A' }}</p>
            <p v-if="contrato.tipo === 'ALUGUEL'"><strong>Inquilino:</strong> {{ contrato.inquilino_detalhes?.nome_completo || contrato.inquilino_detalhes?.razao_social || 'N/A' }}</p>
            <p v-if="contrato.tipo === 'VENDA'"><strong>Comprador:</strong> {{ contrato.comprador_detalhes?.nome_completo || contrato.comprador_detalhes?.razao_social || 'N/A' }}</p>
            <p><strong>Proprietário:</strong> {{ contrato.proprietario_detalhes?.nome_completo || contrato.proprietario_detalhes?.razao_social || 'N/A' }}</p>
            <p><strong>Data Início:</strong> {{ formatarData(contrato.data_inicio) }}</p>
            <p><strong>Data Fim:</strong> {{ formatarData(contrato.data_fim) || 'Indeterminado' }}</p>
            <p><strong>Valor:</strong> {{ formatarValor(contrato.valor_total || contrato.valor_mensal) }} {{ contrato.tipo === 'ALUGUEL' ? '/mês' : '' }}</p>
        </div>
        <div class="card-actions">
          <button @click="verContrato(contrato.id)" class="btn-action btn-view"><i class="fas fa-eye"></i> Ver</button>
          <button @click="editarContrato(contrato.id)" class="btn-action btn-edit"><i class="fas fa-edit"></i> Editar</button>
           <button @click="abrirModalFinanceiro(contrato)" class="btn-action btn-financeiro"><i class="fas fa-dollar-sign"></i> Financeiro</button>
          <button @click="excluirContrato(contrato.id)" class="btn-action btn-delete"><i class="fas fa-trash-alt"></i> Excluir</button>
        </div>
      </div>
    </div>
    <div v-else-if="!isLoading && !error" class="empty-state card">
      Nenhum contrato encontrado com os filtros selecionados.
    </div>

     <ModalFinanceiroContrato
        v-if="showModalFinanceiro && contratoSelecionado"
        :contrato="contratoSelecionado"
        @close="fecharModalFinanceiro"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import ModalFinanceiroContrato from '@/components/ContratoFinanceiro.vue'; // Importa o modal

// Interfaces
interface ClienteDetalhes { id: number; nome_completo?: string; razao_social?: string; }
interface ImovelDetalhes { id: number; codigo_referencia?: string; titulo_anuncio?: string; }
interface Contrato {
  id: number;
  tipo: 'VENDA' | 'ALUGUEL';
  imovel: number;
  imovel_detalhes?: ImovelDetalhes;
  proprietario: number;
  proprietario_detalhes?: ClienteDetalhes;
  inquilino?: number | null; // Apenas para aluguel
  inquilino_detalhes?: ClienteDetalhes | null;
  comprador?: number | null; // Apenas para venda
  comprador_detalhes?: ClienteDetalhes | null;
  data_inicio: string;
  data_fim?: string | null;
  valor_total?: number | null; // Venda
  valor_mensal?: number | null; // Aluguel
  status: 'ATIVO' | 'PENDENTE' | 'CONCLUIDO' | 'RESCINDIDO' | 'INATIVO'; // Ajuste conforme backend
}


const router = useRouter();
const contratos = ref<Contrato[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterStatus = ref('');
const filterTipo = ref('');

// Estado do Modal Financeiro
const showModalFinanceiro = ref(false);
const contratoSelecionado = ref<Contrato | null>(null);

const filteredContratos = computed(() => {
  return contratos.value.filter(contrato => {
    const searchLower = searchTerm.value.toLowerCase();
    const matchSearch = !searchLower ||
      (contrato.imovel_detalhes?.titulo_anuncio?.toLowerCase() || '').includes(searchLower) ||
      (contrato.imovel_detalhes?.codigo_referencia?.toLowerCase() || '').includes(searchLower) ||
      (contrato.inquilino_detalhes?.nome_completo?.toLowerCase() || '').includes(searchLower) ||
      (contrato.inquilino_detalhes?.razao_social?.toLowerCase() || '').includes(searchLower) ||
      (contrato.comprador_detalhes?.nome_completo?.toLowerCase() || '').includes(searchLower) ||
      (contrato.comprador_detalhes?.razao_social?.toLowerCase() || '').includes(searchLower) ||
      (contrato.proprietario_detalhes?.nome_completo?.toLowerCase() || '').includes(searchLower) ||
      (contrato.proprietario_detalhes?.razao_social?.toLowerCase() || '').includes(searchLower);

    const matchStatus = !filterStatus.value || contrato.status === filterStatus.value;
    const matchTipo = !filterTipo.value || contrato.tipo === filterTipo.value;

    return matchSearch && matchStatus && matchTipo;
  });
});


async function fetchContratos() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get<Contrato[]>('/v1/contratos/');
    contratos.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar contratos:", err);
    error.value = "Não foi possível carregar os contratos.";
  } finally {
    isLoading.value = false;
  }
}

function formatarData(data: string | null | undefined): string {
  if (!data) return '';
  try {
    return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
  } catch {
    return 'Inválida';
  }
}

function formatarValor(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return 'R$ -';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatStatus(status: string): string {
    const map: { [key: string]: string } = {
        'ATIVO': 'Ativo', 'PENDENTE': 'Pendente', 'CONCLUIDO': 'Concluído',
        'RESCINDIDO': 'Rescindido', 'INATIVO': 'Inativo',
    };
    return map[status] || status;
}

function getStatusClass(status: string): string {
    switch(status) {
        case 'ATIVO': return 'status-ativo';
        case 'PENDENTE': return 'status-pendente';
        case 'CONCLUIDO': return 'status-concluido';
        case 'RESCINDIDO': return 'status-rescindido';
        case 'INATIVO': return 'status-inativo';
        default: return '';
    }
}


// --- Funções de Ação ---
function verContrato(id: number) {
    // Ajuste a rota se o nome for diferente no seu router/index.ts
    router.push({ name: 'contrato-detalhes', params: { id } });
}

function editarContrato(id: number) {
  // Ajuste a rota se o nome for diferente no seu router/index.ts
  router.push({ name: 'contrato-editar', params: { id } });
}

async function excluirContrato(id: number) {
  if (window.confirm("Tem certeza que deseja excluir este contrato? Esta ação não pode ser desfeita.")) {
    try {
      await apiClient.delete(`/v1/contratos/${id}/`);
      alert('Contrato excluído com sucesso!');
      fetchContratos(); // Recarrega a lista
    } catch (err) {
      console.error("Erro ao excluir contrato:", err);
      alert('Não foi possível excluir o contrato.');
    }
  }
}

// Funções do Modal Financeiro
function abrirModalFinanceiro(contrato: Contrato) {
    contratoSelecionado.value = contrato;
    showModalFinanceiro.value = true;
    document.body.style.overflow = 'hidden'; // Trava scroll do fundo
}

function fecharModalFinanceiro() {
    showModalFinanceiro.value = false;
    contratoSelecionado.value = null;
    document.body.style.overflow = ''; // Libera scroll do fundo
}


onMounted(fetchContratos);
</script>

<style scoped>
.page-container {
  /* padding: 2rem; */ /* Removido */
  padding: 0; /* Adicionado */
}

/* Regras .view-header e .btn-primary removidas */

.card { /* Estilo base para cards */
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
}
.card:last-child {
    margin-bottom: 0;
}


/* Filtros Melhorados */
.filters-bar {
  display: flex;
  flex-wrap: wrap; /* Permite quebrar linha */
  /* justify-content: space-between; */ /* Removido */
  align-items: center; /* Alinha verticalmente */
  gap: 1rem 1.5rem; /* Espaço vertical e horizontal */
}

.search-wrapper {
  position: relative;
  flex: 1 1 300px; /* Cresce, encolhe, base 300px */
  min-width: 250px;
}
.search-wrapper i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #adb5bd;
}
.search-wrapper input {
  width: 100%;
  padding: 10px 10px 10px 35px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box; /* Garante padding correto */
}

.filter-groups {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap; /* Permite que selects quebrem linha */
  flex-grow: 1; /* Tenta ocupar espaço */
}
.filter-groups select {
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: #fff;
  flex: 1 1 150px; /* Cresce, encolhe, base 150px */
  min-width: 150px;
}

.loading-message, .error-message, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
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

.contratos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.contrato-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.07);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.contrato-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}


.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1.2rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.status-badge {
    padding: 4px 10px; border-radius: 12px; font-size: 0.75rem;
    font-weight: bold; color: white; text-transform: uppercase;
}
.status-ativo { background-color: #198754; }
.status-pendente { background-color: #ffc107; color: #333; }
.status-concluido { background-color: #0d6efd; }
.status-rescindido { background-color: #dc3545; }
.status-inativo { background-color: #6c757d; }


.tipo-badge {
    font-size: 0.8rem; font-weight: 500; color: #495057;
    background-color: #e9ecef; padding: 3px 8px; border-radius: 4px;
}

.card-body {
  padding: 1.2rem;
  flex-grow: 1;
}
.card-body p { margin: 0 0 0.6rem 0; font-size: 0.9rem; color: #495057; }
.card-body p strong { color: #212529; margin-right: 5px; }

.card-actions {
  display: flex; justify-content: flex-end; gap: 0.5rem;
  padding: 0.8rem 1.2rem; border-top: 1px solid #e9ecef;
  background-color: #f8f9fa;
}

.btn-action {
    background: none; border: 1px solid transparent; padding: 6px 10px;
    border-radius: 5px; cursor: pointer; font-size: 0.8rem; font-weight: 500;
    transition: background-color 0.2s, color 0.2s, border-color 0.2s;
    display: inline-flex; align-items: center; gap: 0.4rem;
}
.btn-action i { font-size: 0.9em; }

.btn-view { border-color: #6c757d; color: #6c757d; }
.btn-view:hover { background-color: #6c757d; color: white; }
.btn-edit { border-color: #0d6efd; color: #0d6efd; }
.btn-edit:hover { background-color: #0d6efd; color: white; }
.btn-financeiro { border-color: #198754; color: #198754; }
.btn-financeiro:hover { background-color: #198754; color: white; }
.btn-delete { border-color: #dc3545; color: #dc3545; }
.btn-delete:hover { background-color: #dc3545; color: white; }


/* Estilos para a Modal Financeiro */
:global(.modal-overlay) {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); display: flex;
  justify-content: center; align-items: center; z-index: 1050;
}
:global(.modal-container) { /* Ajuste o seletor se o modal usar outra classe */
  background: #fff; padding: 2rem; border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 90%; max-width: 700px; /* Largura do modal financeiro */
  max-height: 90vh; overflow-y: auto; position: relative;
}
:global(.modal-close-button) { /* Ajuste o seletor */
    position: absolute; top: 1rem; right: 1rem; background: none; border: none;
    font-size: 1.5rem; cursor: pointer; color: #6c757d; line-height: 1;
}


</style>
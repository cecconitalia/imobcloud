<template>
  <div class="page-container">
    
    <div v-show="!isReportMode" class="list-view-content">
      
      <div class="content-card filters-card">
        <div class="filters-grid">
          <div class="filter-group search-group">
            <label>Buscar</label>
            <div class="search-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
              <input type="text" v-model="filtros.search" placeholder="Descrição ou Cliente..." class="filter-input search-input">
            </div>
          </div>

          <div class="filter-group">
            <label>Conta</label>
            <select v-model="filtros.conta" class="filter-input">
              <option value="">Todas</option>
              <option v-for="c in contas" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Categoria</label>
            <select v-model="filtros.categoria" class="filter-input">
              <option value="">Todas</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nome }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Tipo</label>
            <select v-model="filtros.tipo" class="filter-input">
              <option value="">Todos</option>
              <option value="RECEITA">Receitas</option>
              <option value="DESPESA">Despesas</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Status</label>
            <select v-model="filtros.status" class="filter-input">
              <option value="">Todos</option>
              <option value="PENDENTE">Pendente</option>
              <option value="PAGO">Pago</option>
              <option value="ATRASADO">Atrasado</option>
            </select>
          </div>

          <div class="filter-group">
            <label>De</label>
            <input type="date" v-model="filtros.data_inicio" class="filter-input">
          </div>

          <div class="filter-group">
            <label>Até</label>
            <input type="date" v-model="filtros.data_fim" class="filter-input">
          </div>
        </div>
        
        <div class="filters-actions">
          <button @click="novaTransacao" class="btn-add">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            Nova Transação
          </button>

          <div class="right-actions">
            <button @click="toggleReportMode" class="btn-report" title="Gerar Relatório para Impressão">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Gerar Relatório
            </button>
            <button @click="limparFiltros" class="btn-text">Limpar</button>
            <button @click="aplicarFiltros" class="btn-primary">Filtrar</button>
          </div>
        </div>
      </div>

      <div class="content-card">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>A carregar transações...</p>
        </div>

        <div v-else-if="error" class="error-state"><p>{{ error }}</p></div>

        <div v-else-if="transacoes.length === 0" class="empty-state">
          <div class="empty-icon">📄</div>
          <h3>Nenhuma transação encontrada</h3>
        </div>

        <div v-else class="table-responsive">
          <table class="modern-table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Categoria</th>
                <th>Histórico</th>
                <th>Cliente</th>
                <th>Conta</th>
                <th>Valor</th>
                <th class="actions-col">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in transacoes" :key="t.id" :class="getRowClass(t)">
                
                <td class="date-cell">
                  <div>{{ formatarData(t.data_transacao) }}</div>
                </td>
                
                <td>{{ t.categoria_nome || '-' }}</td>
                
                <td>
                  <div class="desc-cell">
                    <span class="desc-text">{{ t.descricao }}</span>
                    <span class="cliente-subtext" v-if="t.data_vencimento || t.data_pagamento">
                        <span v-if="t.data_vencimento">Vencto: {{ formatarData(t.data_vencimento) }}</span>
                        <span v-if="t.data_pagamento"> / Pg: {{ formatarData(t.data_pagamento) }}</span>
                    </span>
                  </div>
                </td>
                
                <td>
                    <span v-if="t.cliente_nome && t.cliente_nome !== 'Cliente não informado'">
                        {{ t.cliente_nome }}
                    </span>
                    <span v-else>-</span>
                </td>
                
                <td>{{ t.conta_nome || '-' }}</td>
                
                <td class="value-cell" :class="t.tipo === 'RECEITA' ? 'text-green' : 'text-red'">
                  {{ t.tipo === 'RECEITA' ? '+' : '-' }} {{ formatarValor(t.valor) }}
                </td>
                
                <td class="actions-cell actions-col">
                  <div class="action-buttons">
                    <button @click="editarTransacao(t.id)" class="btn-icon edit" title="Editar">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                      </svg>
                    </button>
                    <button @click="confirmarExclusao(t.id)" class="btn-icon delete" title="Excluir">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="icon-svg">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="footer-row">
                <td colspan="5" class="footer-label">Totais (Filtro Aplicado):</td> 
                <td colspan="2">
                  <div class="footer-sums">
                    <span class="sum-item text-green" title="Total Receitas">+ {{ formatarValor(totaisGerais.receitas) }}</span>
                    <span class="sum-item text-red" title="Total Despesas">- {{ formatarValor(totaisGerais.despesas) }}</span>
                    <span class="sum-item sum-total" :class="totaisGerais.saldo >= 0 ? 'text-blue' : 'text-red'" title="Saldo Líquido">
                        = {{ formatarValor(totaisGerais.saldo) }}
                    </span>
                  </div>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div class="pagination" v-if="totalPages > 1">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="btn-page">
            &laquo; Anterior
          </button>
          <span class="page-info">Página {{ currentPage }} de {{ totalPages }}</span>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="btn-page">
            Próxima &raquo;
          </button>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="isReportMode" class="report-preview-container">
        
        <div class="report-controls no-print">
          <div class="report-info">
            <h3>Visualização de Impressão</h3>
            <p>Verifique os dados antes de imprimir.</p>
          </div>
          <div class="report-buttons">
            <button @click="toggleReportMode" class="btn-secondary">Voltar / Editar</button>
            <button @click="imprimirExtrato" class="btn-primary btn-print-action">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
              Imprimir Agora
            </button>
          </div>
        </div>

        <div class="report-sheet">
          
          <header class="report-header">
            <div class="company-info">
              <h1>{{ nomeImobiliaria || 'Sua Imobiliária' }}</h1>
              <h2>Extrato de Transações</h2>
            </div>
            <div class="report-meta">
              <div class="meta-row">
                  <strong class="meta-label">Data de Emissão:</strong>
                  <span>{{ dataHoje }}</span>
              </div>
              <div class="meta-row">
                  <strong class="meta-label">Filtros Aplicados:</strong>
                  <span class="meta-value">{{ resumoFiltrosTexto }}</span>
              </div>
            </div>
          </header>

          <hr class="report-divider">

          <table class="report-table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Descrição / Cliente</th>
                <th>Categoria</th>
                <th>Conta</th>
                <th class="text-right">Valor</th>
                <th class="text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in transacoes" :key="'rep-'+t.id">
                <td>{{ formatarData(t.data_vencimento) }}</td>
                <td>
                  <div class="rep-desc">{{ t.descricao }}</div>
                  <div class="rep-cli" v-if="t.cliente_nome">{{ t.cliente_nome }}</div>
                </td>
                <td>{{ t.categoria_nome }}</td>
                <td>{{ t.conta_nome }}</td>
                <td class="text-right" :class="t.tipo === 'RECEITA' ? 'text-green' : 'text-red'">
                  {{ t.tipo === 'RECEITA' ? '+' : '-' }} {{ formatarValor(t.valor) }}
                </td>
                <td class="text-center">{{ t.status }}</td>
              </tr>
            </tbody>
          </table>

          <div class="report-footer">
            <div class="report-summary">
              <div class="summary-row">
                <span>Total Receitas:</span>
                <span class="text-green">{{ formatarValor(totaisGerais.receitas) }}</span>
              </div>
              <div class="summary-row">
                <span>Total Despesas:</span>
                <span class="text-red">{{ formatarValor(totaisGerais.despesas) }}</span>
              </div>
              <div class="summary-row total-highlight">
                <span>Saldo do Período:</span>
                <span :class="totaisGerais.saldo >= 0 ? 'text-blue' : 'text-red'">{{ formatarValor(totaisGerais.saldo) }}</span>
              </div>
            </div>
            <div class="report-note">
              * Relatório gerado automaticamente pelo sistema.
            </div>
          </div>

        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { format, differenceInDays } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Categoria { id: number; nome: string; }
interface Conta { id: number; nome: string; }
interface Transacao {
    id: number; descricao: string; valor: number;
    data_transacao?: string | null; data_pagamento?: string | null; data_vencimento: string;
    tipo: 'RECEITA' | 'DESPESA'; status: 'PENDENTE' | 'PAGO' | 'ATRASADO' | 'CANCELADO';
    categoria_nome?: string; conta_nome?: string; cliente_nome?: string;
}
interface Totais { receitas: number; despesas: number; saldo: number; nome_imobiliaria?: string; } 

const router = useRouter();
const transacoes = ref<Transacao[]>([]);
const categorias = ref<Categoria[]>([]);
const contas = ref<Conta[]>([]);
const totaisGerais = ref<Totais>({ receitas: 0, despesas: 0, saldo: 0 });
const nomeImobiliaria = ref(''); 

const isLoading = ref(true);
const error = ref<string | null>(null);
const isReportMode = ref(false); 

const currentPage = ref(1);
const totalPages = ref(1);
const pageSize = 20;

const filtros = reactive({
    search: '', tipo: '', status: '', data_inicio: '', data_fim: '', categoria: '', conta: '',
});

const dataHoje = computed(() => format(new Date(), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR }));

const resumoFiltrosTexto = computed(() => {
    let partes = [];
    if (filtros.data_inicio || filtros.data_fim) {
        const ini = filtros.data_inicio ? format(new Date(filtros.data_inicio + 'T00:00:00'), 'dd/MM/yyyy') : 'Início';
        const fim = filtros.data_fim ? format(new Date(filtros.data_fim + 'T00:00:00'), 'dd/MM/yyyy') : 'Hoje';
        partes.push(`Período: ${ini} a ${fim}`);
    }
    if (filtros.conta && contas.value.length) {
        const c = contas.value.find(x => x.id === Number(filtros.conta));
        if (c) partes.push(`Conta: ${c.nome}`);
    }
    if (filtros.categoria && categorias.value.length) {
        const c = categorias.value.find(x => x.id === Number(filtros.categoria));
        if (c) partes.push(`Categoria: ${c.nome}`);
    }
    if (filtros.status) partes.push(`Status: ${filtros.status}`);
    if (filtros.tipo) partes.push(`Tipo: ${filtros.tipo}`);
    if (filtros.search) partes.push(`Busca: "${filtros.search}"`);
    return partes.length > 0 ? partes.join('  •  ') : 'Todos os registos (Sem filtros)';
});

// --- Helpers ---
function formatarValor(valor: number): string {
    return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}
function formatarData(data: string | null | undefined): string {
    if (!data) return '-';
    try { return format(new Date(data + 'T00:00:00'), 'dd/MM/yy', { locale: ptBR }); } catch { return data; }
}
function getRowClass(t: Transacao): string {
    if (t.status === 'PENDENTE' || t.status === 'ATRASADO') {
        const hoje = new Date();
        const vencimento = new Date(t.data_vencimento + 'T00:00:00');
        const diff = differenceInDays(vencimento, hoje);
        if (diff < 0) return 'row-overdue'; 
        if (diff <= 3) return 'row-warning'; 
    }
    return '';
}

// --- Actions ---
function toggleReportMode() {
    if (!isReportMode.value) {
        // Ao entrar no modo relatório, busca TUDO e atualiza os totais/nome
        fetchAllForReport();
    } else {
        fetchTransacoes(currentPage.value); 
    }
    isReportMode.value = !isReportMode.value;
}
function imprimirExtrato() {
    window.print();
}

async function fetchAllForReport() {
    try {
         isLoading.value = true;
         // Atualiza nome e totais antes de gerar o relatório
         await fetchResumo(); 
         
         const params = new URLSearchParams();
         if (filtros.search) params.append('search', filtros.search);
         if (filtros.tipo) params.append('tipo', filtros.tipo);
         if (filtros.status) params.append('status', filtros.status);
         if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
         if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
         if (filtros.categoria) params.append('categoria', filtros.categoria);
         if (filtros.conta) params.append('conta', filtros.conta);
         
         params.append('page_size', '1000'); 

        const response = await apiClient.get<{ count: number; results: Transacao[] }>(`/v1/financeiro/transacoes/?${params.toString()}`);
        transacoes.value = response.data.results;
    } catch (err) {
        console.error("Erro relatório:", err);
    } finally {
        isLoading.value = false;
    }
}

function novaTransacao() { router.push({ name: 'transacao-nova' }); }
function editarTransacao(id: number) { router.push({ name: 'transacao-editar', params: { id } }); }
async function confirmarExclusao(id: number) {
    if (window.confirm("Excluir esta transação?")) {
        try {
            await apiClient.delete(`/v1/financeiro/transacoes/${id}/`);
            aplicarFiltros();
        } catch (err) { alert('Erro ao excluir.'); }
    }
}

// --- API ---
async function fetchFilterOptions() {
    try {
        const [catRes, contRes] = await Promise.all([
            apiClient.get<Categoria[]>('/v1/financeiro/categorias/'),
            apiClient.get<Conta[]>('/v1/financeiro/contas/')
        ]);
        categorias.value = catRes.data;
        contas.value = contRes.data;
    } catch (err) { console.error("Erro filtros:", err); }
}

async function fetchResumo() {
    try {
        const params = new URLSearchParams();
        if (filtros.search) params.append('search', filtros.search);
        if (filtros.tipo) params.append('tipo', filtros.tipo);
        if (filtros.status) params.append('status', filtros.status);
        if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
        if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
        if (filtros.categoria) params.append('categoria', filtros.categoria);
        if (filtros.conta) params.append('conta', filtros.conta);
        const response = await apiClient.get<Totais>(`/v1/financeiro/transacoes/resumo-filtros/?${params.toString()}`);
        totaisGerais.value = response.data;
        
        if (response.data.nome_imobiliaria) {
            nomeImobiliaria.value = response.data.nome_imobiliaria;
        }
    } catch (err) { console.error("Erro totais:", err); }
}

async function fetchTransacoes(page = 1) {
    isLoading.value = true;
    error.value = null;
    try {
        const params = new URLSearchParams({ page: page.toString(), page_size: pageSize.toString() });
        if (filtros.search) params.append('search', filtros.search);
        if (filtros.tipo) params.append('tipo', filtros.tipo);
        if (filtros.status) params.append('status', filtros.status);
        if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
        if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
        if (filtros.categoria) params.append('categoria', filtros.categoria);
        if (filtros.conta) params.append('conta', filtros.conta);

        const response = await apiClient.get<{ count: number; results: Transacao[] }>(`/v1/financeiro/transacoes/?${params.toString()}`);
        transacoes.value = response.data.results;
        totalPages.value = Math.ceil(response.data.count / pageSize);
        currentPage.value = page;
    } catch (err) { error.value = 'Não foi possível carregar.'; } finally { isLoading.value = false; }
}

function aplicarFiltros() { fetchTransacoes(1); fetchResumo(); }
function limparFiltros() {
    filtros.search = ''; filtros.tipo = ''; filtros.status = ''; filtros.data_inicio = ''; 
    filtros.data_fim = ''; filtros.categoria = ''; filtros.conta = '';
    aplicarFiltros();
}
function changePage(p: number) { if (p >= 1 && p <= totalPages.value) fetchTransacoes(p); }

onMounted(() => { fetchFilterOptions(); aplicarFiltros(); });
</script>

<style scoped>
.page-container {
    max-width: 1200px; margin: 0 auto; padding-bottom: 40px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #334155;
}

/* --- Estilos Modo LISTAGEM --- */
.content-card { background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; margin-bottom: 24px; }
.filters-card { padding: 20px; }
.filters-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 20px; }
.filter-group { display: flex; flex-direction: column; gap: 6px; }
.filter-input { box-sizing: border-box; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; outline: none; width: 100%; }
.search-wrapper { position: relative; }
.search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-input { padding-left: 34px; }
.filters-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 24px; padding-top: 20px; border-top: 1px solid #f1f5f9; }
.right-actions { display: flex; gap: 12px; }

.btn-add { display: flex; align-items: center; gap: 8px; background-color: #0f172a; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.9rem; }
.btn-report { display: flex; align-items: center; gap: 8px; background-color: #f8fafc; border: 1px solid #cbd5e1; color: #475569; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.9rem; }
.btn-report:hover { background-color: #e2e8f0; color: #1e293b; }
.btn-primary { background: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; }
.btn-text { background: none; border: none; color: #64748b; cursor: pointer; font-weight: 500; }

.modern-table { width: 100%; border-collapse: collapse; text-align: left; }
/* Font size reduzido para TH */
.modern-table th { background-color: #f8fafc; padding: 10px 16px; font-size: 0.8rem; font-weight: 600; color: #64748b; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; }
/* Font size reduzido para TD */
.modern-table td { padding: 8px 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; vertical-align: middle; }
.desc-cell { display: flex; flex-direction: column; }
.desc-text { font-weight: 500; color: #1e293b; }
/* Font size sub-texto reduzido */
.cliente-subtext { font-size: 0.75rem; color: #64748b; margin-top: 2px; }
.value-cell { font-weight: 600; font-family: 'Courier New', monospace; white-space: nowrap; }
.text-green { color: #16a34a; } .text-red { color: #dc2626; } .text-blue { color: #2563eb; }
.status-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
.status-badge.pago { background: #dcfce7; color: #166534; }
.status-badge.pendente { background: #fffbeb; color: #b45309; }
.status-badge.atrasado { background: #fee2e2; color: #991b1b; }
.row-overdue td { border-color: #fee2e2; background-color: #fef2f2; }
.row-warning td { background-color: #fffbeb; }
.footer-row { background-color: #f8fafc; font-weight: 600; }
.footer-sums { display: flex; gap: 16px; align-items: center; }
.sum-total { font-weight: 700; padding: 4px 8px; background: #fff; border-radius: 4px; border: 1px solid #e2e8f0; margin-left: 8px; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; padding: 20px; border-top: 1px solid #e2e8f0; }
.btn-page { padding: 8px 16px; border: 1px solid #cbd5e1; background: white; border-radius: 6px; cursor: pointer; }

/* ========================= */
/* ESTILOS BOTÕES DE AÇÃO (Ícones Modernos) */
/* ========================= */
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon .icon-svg {
  width: 18px;
  height: 18px;
}

.btn-icon.edit {
  color: #3b82f6; /* Azul moderno */
}
.btn-icon.edit:hover {
  background-color: #eff6ff;
  transform: translateY(-1px);
}

.btn-icon.delete {
  color: #ef4444; /* Vermelho moderno */
}
.btn-icon.delete:hover {
  background-color: #fef2f2;
  transform: translateY(-1px);
}


/* ========================= */
/* ESTILOS MODO RELATÓRIO    */
/* ========================= */
.report-preview-container {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: #525659; z-index: 9999;
    overflow-y: auto; padding: 40px 0;
    display: flex; flex-direction: column; align-items: center;
}

.report-controls { width: 100%; max-width: 210mm; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; color: white; }
.report-buttons { display: flex; gap: 10px; }
.btn-secondary { background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.4); padding: 8px 16px; border-radius: 4px; cursor: pointer; }
.btn-print-action { background: #2563eb; display: flex; gap: 8px; align-items: center; }

.report-sheet {
    background: white; width: 210mm; min-height: 297mm; padding: 15mm; box-shadow: 0 0 20px rgba(0,0,0,0.3);
    font-family: 'Times New Roman', serif; color: #000;
    flex-shrink: 0; 
    margin-bottom: 40px;
}
.report-header { text-align: center; margin-bottom: 20px; }
.report-header h1 { margin: 0; font-size: 24px; text-transform: uppercase; }
.report-header h2 { margin: 5px 0 15px; font-size: 18px; font-weight: normal; color: #555; }
.report-meta { 
    font-size: 12px; color: #666; border-top: 1px solid #eee; border-bottom: 1px solid #eee; padding: 10px 0; text-align: left; 
    display: flex; flex-direction: column; gap: 5px;
}
.meta-row { display: flex; gap: 5px; align-items: baseline; }
.meta-label { white-space: nowrap; }
.meta-value { font-style: italic; }

.report-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }
.report-table th { border-bottom: 2px solid #000; text-align: left; padding: 5px; font-weight: bold; }
.report-table td { border-bottom: 1px solid #ddd; padding: 6px 5px; vertical-align: top; }
.rep-desc { font-weight: bold; } .rep-cli { font-style: italic; color: #444; }
.text-right { text-align: right; } .text-center { text-center: center; }

.report-footer { margin-top: 30px; border-top: 2px solid #000; padding-top: 10px; }
.report-summary { display: flex; flex-direction: column; align-items: flex-end; font-size: 14px; gap: 5px; }
.summary-row { display: flex; justify-content: space-between; width: 250px; }
.total-highlight { font-weight: bold; font-size: 16px; border-top: 1px solid #999; padding-top: 5px; margin-top: 5px; }
.report-note { margin-top: 40px; font-size: 10px; color: #888; text-align: center; }

/* --- PRINT CSS ROBUSTO --- */
@media print {
    body { visibility: hidden; overflow: visible !important; height: auto !important; }
    .report-preview-container {
        visibility: visible !important; position: absolute !important; top: 0 !important; left: 0 !important;
        width: 100% !important; height: auto !important; background: white !important;
        padding: 0 !important; margin: 0 !important; z-index: 99999 !important; display: block !important;
    }
    .report-preview-container * { visibility: visible !important; }
    .report-controls { display: none !important; }
    .report-sheet { width: 100% !important; margin: 0 !important; padding: 0 !important; box-shadow: none !important; }
}
</style>
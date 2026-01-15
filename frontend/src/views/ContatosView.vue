<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>CRM</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Leads (Site)</span>
           </nav>
           
           <h1>Gerenciar Leads</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchContatos" title="Atualizar Lista">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: filtro.status === 'abertos' }" @click="filtro.status = 'abertos'">
        <div class="kpi-content">
          <span class="kpi-value">{{ totalContatosAbertos }}</span>
          <span class="kpi-label">Pendentes</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-inbox"></i></div>
      </div>

      <div class="kpi-card orange" :class="{ active: filtro.status === 'arquivados' }" @click="filtro.status = 'arquivados'">
        <div class="kpi-content">
          <span class="kpi-value">{{ totalArquivados }}</span>
          <span class="kpi-label">Arquivados</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-archive"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value text-small">{{ contatoMaisRecente }}</span>
          <span class="kpi-label">Último Recebido</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-calendar-check"></i></div>
      </div>

      <div class="kpi-card bg-gray" :class="{ active: filtro.status === 'todos' }" @click="filtro.status = 'todos'">
        <div class="kpi-content">
          <span class="kpi-value">{{ totalGeral }}</span>
          <span class="kpi-label">Total Geral</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-bullseye"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filtro.search" 
              placeholder="Nome, email, telefone ou mensagem..." 
              class="form-control"
              @input="debouncedFilter"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Status</label>
          <select v-model="filtro.status" class="form-control">
            <option value="abertos">Abertos (Pendentes)</option>
            <option value="arquivados">Arquivados</option>
            <option value="todos">Todos</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Período</label>
          <select v-model="filtro.periodo" @change="fetchContatos" class="form-control">
            <option value="todos">Todo Período</option>
            <option value="30d">Últimos 30 Dias</option>
            <option value="90d">Últimos 90 Dias</option>
          </select>
        </div>

        <div class="filter-group small-btn">
            <label>&nbsp;</label>
            <button @click="clearFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <main class="report-main-wrapper">
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando leads...</p>
      </div>
      
      <div v-else-if="error" class="error-message">{{ error }}</div>
      
      <div v-else-if="filteredContatos.length === 0" class="empty-state">
        <i class="fas fa-filter"></i>
        <p>Nenhum lead encontrado com os filtros selecionados.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="12%">Data / ID</th>
              <th width="20%">Lead (Cliente)</th>
              <th width="20%">Imóvel de Interesse</th>
              <th width="25%">Mensagem</th>
              <th width="10%">Status</th>
              <th width="13%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="contato in filteredContatos" :key="contato.id" class="clickable-row">
              
              <td>
                <div class="cell-date">
                    <span class="date-main">{{ formatarDataCurta(contato.data_contato) }}</span>
                    <span class="date-sub">
                        {{ formatarHora(contato.data_contato) }} • #{{ contato.id }}
                    </span>
                </div>
              </td>

              <td>
                 <div class="cell-cliente">
                    <span class="cliente-nome">{{ contato.nome }}</span>
                    <span class="cliente-sub"><i class="far fa-envelope"></i> {{ contato.email }}</span>
                    <span v-if="contato.telefone" class="cliente-sub"><i class="fas fa-phone-alt"></i> {{ contato.telefone }}</span>
                 </div>
              </td>

              <td>
                 <div class="cell-imovel">
                    <div v-if="contato.imovel_obj?.id">
                        <router-link :to="`/imoveis/editar/${contato.imovel_obj.id}`" class="link-imovel" @click.stop>
                            Ref: {{ contato.imovel_obj?.codigo_referencia || 'N/A' }}
                        </router-link>
                        <span class="imovel-tipo">{{ contato.imovel_obj?.tipo || 'Imóvel' }}</span>
                    </div>
                    <div v-else class="text-muted italic">
                        <i class="fas fa-building-slash"></i> Não identificado
                    </div>
                 </div>
              </td>

              <td>
                 <div class="cell-mensagem" :title="contato.mensagem">
                    "{{ contato.mensagem }}"
                 </div>
              </td>

              <td>
                 <span v-if="contato.arquivado" class="badge-type bg-gray">Arquivado</span>
                 <span v-else class="badge-type bg-blue-light">Novo Lead</span>
              </td>

              <td class="text-right" @click.stop>
                <div class="actions-flex">
                    <button 
                        v-if="!contato.arquivado"
                        @click="handleGerarOportunidade(contato)"
                        class="btn-action generate"
                        title="Gerar Oportunidade (Funil)"
                    >
                        <i class="fas fa-funnel-dollar"></i>
                    </button>

                    <button 
                        @click="handleResponder(contato)"
                        class="btn-action reply"
                        title="Responder Email"
                    >
                        <i class="fas fa-reply"></i>
                    </button>
                    
                    <button 
                        v-if="!contato.arquivado"
                        class="btn-action archive" 
                        @click="handleArquivar(contato)" 
                        title="Arquivar"
                    >
                        <i class="fas fa-archive"></i>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { debounce } from 'lodash';

interface ImovelResumo {
  id: number;
  codigo_referencia?: string;
  tipo?: string;
  endereco?: string;
}

interface Contato {
  id: number;
  imovel: number;
  imovel_obj?: ImovelResumo;
  nome: string;
  email: string;
  telefone?: string;
  mensagem: string;
  data_contato: string;
  arquivado: boolean;
}

const router = useRouter();
const contatos = ref<Contato[]>([]);
const contatosOriginais = ref<Contato[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

const filtro = ref({
    search: '',
    status: 'abertos',
    periodo: 'todos'
});

// --- COMPUTED ---
const totalArquivados = computed(() => contatosOriginais.value.filter(c => c.arquivado).length);
const totalGeral = computed(() => contatosOriginais.value.length);
const totalContatosAbertos = computed(() => contatosOriginais.value.filter(c => !c.arquivado).length);

const contatoMaisRecente = computed(() => {
    if (contatosOriginais.value.length === 0) return '-';
    const maisRecente = contatosOriginais.value.reduce((latest, contato) => {
        const dataContato = parseISO(contato.data_contato);
        return dataContato > latest ? dataContato : latest;
    }, parseISO('2000-01-01T00:00:00Z'));
    return format(maisRecente, 'dd/MM HH:mm', { locale: ptBR });
});

const filteredContatos = computed(() => {
    let lista = contatosOriginais.value;

    // Filtro de Status
    if (filtro.value.status === 'abertos') {
        lista = lista.filter(c => !c.arquivado);
    } else if (filtro.value.status === 'arquivados') {
        lista = lista.filter(c => c.arquivado);
    }

    // Filtro de Busca
    const search = filtro.value.search.toLowerCase().trim();
    if (search) {
        lista = lista.filter(c => 
            (c.nome.toLowerCase()).includes(search) ||
            (c.email.toLowerCase()).includes(search) ||
            (c.telefone?.toLowerCase() || '').includes(search) ||
            (c.imovel_obj?.codigo_referencia?.toLowerCase() || '').includes(search) ||
            (c.mensagem.toLowerCase()).includes(search)
        );
    }
    return lista;
});

// --- ACTIONS ---
async function fetchContatos() {
  isLoading.value = true;
  error.value = null;
  try {
    const searchParams: any = {
        search: filtro.value.search || undefined,
        arquivado: 'todos', // Busca tudo para filtrar localmente
        periodo: filtro.value.periodo !== 'todos' ? filtro.value.periodo : undefined
    };
    
    const response = await apiClient.get<Contato[]>('/v1/contatos/', { params: searchParams });
    contatosOriginais.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar contatos:", err);
    error.value = 'Não foi possível carregar os contatos.';
  } finally {
    isLoading.value = false;
  }
}

const debouncedFilter = debounce(fetchContatos, 500);

function formatarDataCurta(data: string | null): string {
  if (!data) return '-';
  try { return format(parseISO(data), 'dd/MM/yy', { locale: ptBR }); } 
  catch { return '-'; }
}

function formatarHora(data: string | null): string {
  if (!data) return '-';
  try { return format(parseISO(data), 'HH:mm', { locale: ptBR }); } 
  catch { return '-'; }
}

function handleResponder(contato: Contato) {
    const subject = `Contato sobre imóvel ${contato.imovel_obj?.codigo_referencia || contato.imovel}`;
    const body = `Olá ${contato.nome},\n\nEm resposta à sua mensagem:\n"${contato.mensagem}"\n\n`;
    window.location.href = `mailto:${contato.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

async function handleArquivar(contato: Contato) {
  if (!window.confirm(`Deseja arquivar o contato de ${contato.nome}?`)) return;
  try {
    await apiClient.post(`/v1/contatos/${contato.id}/arquivar/`);
    const index = contatosOriginais.value.findIndex(c => c.id === contato.id);
    if(index !== -1) contatosOriginais.value[index].arquivado = true;
  } catch(err) {
      alert("Erro ao arquivar contato.");
  }
}

function handleGerarOportunidade(contato: Contato) {
    router.push({
        name: 'oportunidade-nova',
        query: {
            imovel_id: contato.imovel,
            contato_nome: contato.nome,
            contato_email: contato.email,
            contato_telefone: contato.telefone,
            mensagem: contato.mensagem,
            contato_id: contato.id
        }
    });
}

function clearFilters() {
    filtro.value.search = '';
    filtro.value.status = 'abertos';
    filtro.value.periodo = 'todos';
    fetchContatos();
}

onMounted(fetchContatos);
watch(() => filtro.value.periodo, fetchContatos); 
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (PADRONIZADO) */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA */
.page-header { margin-bottom: 2rem; }
.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Fino */
.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* KPI GRID */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: pointer; transition: all 0.2s;
  position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }
.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-value.text-small { font-size: 1.1rem; font-weight: 600; margin-top: 4px; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }
.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }
.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }
.kpi-card.bg-gray .kpi-value { color: #475569; }
.kpi-card.bg-gray.active { border-color: #94a3b8; }

/* TOOLBAR */
.toolbar-row {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}
.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 160px; }
.search-group { flex: 2; min-width: 260px; }
.small-btn { flex: 0 0 auto; min-width: auto; }
.filter-group label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.form-control {
  width: 100%; padding: 0.5rem 0.8rem; font-size: 0.85rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 38px; box-sizing: border-box; transition: all 0.2s;
}
.input-with-icon .form-control { padding-left: 2.2rem; }
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }
.btn-clear {
    width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc;
    border-radius: 6px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #fee2e2; color: #ef4444; border-color: #fca5a5; }

/* TABELA */
.report-main-wrapper {
  background: white; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  display: flex; flex-direction: column; overflow: hidden;
}
.report-scroll-viewport { width: 100%; overflow-x: auto; }
.report-table { width: 100%; border-collapse: collapse; min-width: 900px; }
.report-table th {
  background: #f8fafc; padding: 0.8rem 1.2rem; text-align: left;
  font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1px solid #e2e8f0;
}
.report-table td {
  padding: 0.8rem 1.2rem; border-bottom: 1px solid #f1f5f9;
  font-size: 0.85rem; color: #334155; vertical-align: top;
}
.clickable-row:hover { background-color: #fcfcfc; }

/* Células Customizadas */
.cell-date { display: flex; flex-direction: column; }
.date-main { font-weight: 600; color: #1e293b; font-size: 0.9rem; }
.date-sub { font-size: 0.7rem; color: #94a3b8; }

.cell-cliente { display: flex; flex-direction: column; gap: 2px; }
.cliente-nome { font-weight: 600; color: #1e293b; }
.cliente-sub { font-size: 0.75rem; color: #64748b; display: flex; align-items: center; gap: 5px; }

.cell-imovel { display: flex; flex-direction: column; gap: 2px; }
.link-imovel { 
    color: #2563eb; font-weight: 600; text-decoration: none; 
    font-size: 0.85rem; display: inline-block;
}
.link-imovel:hover { text-decoration: underline; }
.imovel-tipo { font-size: 0.75rem; color: #94a3b8; }
.text-muted { color: #94a3b8; font-size: 0.75rem; }

.cell-mensagem { 
    font-style: italic; color: #475569; font-size: 0.8rem; 
    max-width: 300px; line-clamp: 2; -webkit-line-clamp: 2; 
    overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical;
}

.badge-type {
  font-size: 0.65rem; font-weight: 600; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.02em; display: inline-block;
}
.bg-blue-light { background: #eff6ff; color: #2563eb; }
.bg-gray { background: #f1f5f9; color: #64748b; }

/* Ações */
.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
  background: transparent; color: #94a3b8; border: 1px solid transparent;
}
.btn-action:hover { background-color: #f1f5f9; color: #334155; border-color: #e2e8f0; }

.btn-action.generate:hover { background-color: #dcfce7; color: #166534; border-color: #bbf7d0; }
.btn-action.reply:hover { background-color: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
.btn-action.archive:hover { background-color: #fef2f2; color: #ef4444; border-color: #fecaca; }

.loading-state, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.spinner {
  border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%;
  width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
}
</style>
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

      <div class="kpi-card purple" :class="{ active: filtro.status === 'todos' }" @click="filtro.status = 'todos'">
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
              placeholder="Buscar por nome, email ou imóvel..." 
              class="form-control"
              @input="debouncedFilter"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Status</label>
          <select v-model="filtro.status" class="form-control">
            <option value="abertos">Abertos</option>
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
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Carregando contatos...</p>
    </div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="filteredContatos.length === 0" class="empty-state">
      <i class="fas fa-inbox empty-icon"></i>
      <p>Nenhum contato encontrado com os filtros selecionados.</p>
    </div>

    <div v-else class="contatos-grid">
      <div 
        v-for="contato in filteredContatos" 
        :key="contato.id" 
        class="contato-card"
        :class="{ 'card-arquivado': contato.arquivado }"
      >
        <div class="card-top-bar">
           <div class="badges-left">
               <span class="contrato-id">#{{ contato.id }}</span>
               <span class="tipo-badge">Lead Site</span>
           </div>
           <div class="badges-right">
               <span :class="['status-pill', contato.arquivado ? 'status-arquivado' : 'status-novo']">
                  <i :class="contato.arquivado ? 'fas fa-archive' : 'fas fa-star'"></i> 
                  {{ contato.arquivado ? 'Arquivado' : 'Novo' }}
               </span>
           </div>
        </div>
        
        <div class="card-body">
          <div class="info-section">
             <h4 class="card-title" :title="contato.nome">
                {{ contato.nome }}
             </h4>
             
             <div class="info-row">
                <i class="fas fa-envelope"></i> {{ contato.email }}
             </div>
             <div class="info-row" v-if="contato.telefone">
                <i class="fas fa-phone"></i> {{ contato.telefone }}
             </div>
             
             <div class="imovel-ref mt-3" v-if="contato.imovel_obj?.id">
                <router-link :to="`/imoveis/editar/${contato.imovel_obj.id}`" class="link-imovel" title="Ver Imóvel">
                  <i class="fas fa-home"></i> Ref: {{ contato.imovel_obj?.codigo_referencia || 'N/A' }} 
                  <span class="imovel-tipo">({{ contato.imovel_obj?.tipo || 'N/A' }})</span>
                </router-link>
             </div>
             <div class="imovel-ref mt-3 text-muted" v-else>
                <i class="fas fa-building-slash"></i> Imóvel não identificado
             </div>
          </div>

          <div class="mensagem-box">
             <span class="msg-label">Mensagem:</span>
             <p class="msg-text">"{{ contato.mensagem }}"</p>
          </div>
        </div>
        
        <div class="card-footer-info">
           <i class="far fa-calendar-alt"></i> {{ formatarData(contato.data_contato) }}
        </div>

        <div class="card-actions">
          <div class="actions-left">
            <button 
                v-if="!contato.arquivado"
                @click="handleGerarOportunidade(contato)"
                class="btn-pill btn-ativar"
                title="Transformar em Oportunidade no Funil"
            >
                <i class="fas fa-funnel-dollar"></i> Gerar Lead
            </button>
            <span v-else class="text-muted-small"><i class="fas fa-check"></i> Processado</span>
          </div>

          <div class="actions-right">
              <button class="btn-mini btn-info" @click="handleResponder(contato)" title="Responder por Email">
                <i class="fas fa-reply"></i>
              </button>
              <button 
                  v-if="!contato.arquivado"
                  @click="handleArquivar(contato)" 
                  class="btn-mini btn-delete-mini" 
                  title="Arquivar"
              >
                <i class="fas fa-archive"></i>
              </button>
          </div>
        </div>
      </div>
    </div>

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

function formatarData(data: string | null): string {
  if (!data) return '-';
  try { return format(parseISO(data), 'dd/MM/yyyy HH:mm', { locale: ptBR }); } 
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
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; position: relative; overflow: hidden;
  cursor: pointer;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-value.text-small { font-size: 1.1rem; font-weight: 600; margin-top: 4px; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

/* Cores KPI */
.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }

.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }

.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }

.kpi-card.purple.active { background-color: #faf5ff; border-color: #9333ea; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR */
.toolbar-row {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  margin-bottom: 1.5rem;
}

.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 160px; }
.search-group { flex: 2; min-width: 260px; }
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

/* GRID DE CONTATOS */
.contatos-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem; padding-bottom: 2rem;
}

.contato-card {
  background-color: #fff; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column;
  transition: all 0.2s ease; position: relative; overflow: hidden;
}
.contato-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }
.card-arquivado { background-color: #fafafa; border-color: #f3f4f6; }

/* Card Top */
.card-top-bar {
    padding: 0.8rem 1rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f1f5f9; background: #fff;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.contrato-id {
    font-size: 0.7rem; font-weight: 700; color: #64748b;
    background: #f1f5f9; padding: 2px 6px; border-radius: 4px;
}
.tipo-badge {
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    padding: 2px 6px; border-radius: 4px; color: #2563eb; background-color: #eff6ff;
}
.status-pill {
    padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 4px;
}
.status-novo { background-color: #fef9c3; color: #b45309; }
.status-arquivado { background-color: #f1f5f9; color: #64748b; }

/* Card Body */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }

.info-section { padding: 1rem 1rem 0.5rem; }
.card-title {
    font-size: 1rem; font-weight: 600; color: #1e293b; margin: 0 0 0.5rem 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.info-row {
    font-size: 0.85rem; color: #64748b; margin-bottom: 4px;
    display: flex; align-items: center; gap: 8px;
}
.info-row i { color: #94a3b8; font-size: 0.8rem; width: 14px; text-align: center; }

.link-imovel {
    display: inline-block; font-size: 0.8rem; color: #2563eb; text-decoration: none; 
    font-weight: 500; background: #eff6ff; padding: 4px 8px; border-radius: 4px;
    max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.link-imovel:hover { background: #dbeafe; }
.imovel-tipo { color: #64748b; font-weight: 400; font-size: 0.75rem; margin-left: 4px; }

.mensagem-box {
    background-color: #f8fafc; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    padding: 0.8rem 1rem; flex-grow: 1;
}
.msg-label { font-size: 0.65rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; display: block; margin-bottom: 4px; }
.msg-text { 
    font-size: 0.85rem; color: #334155; margin: 0; line-height: 1.4; font-style: italic;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}

.card-footer-info {
    padding: 0.5rem 1rem; background-color: #fff; color: #64748b; font-size: 0.75rem; font-weight: 500;
    display: flex; align-items: center; gap: 6px;
}

/* Actions */
.card-actions {
    padding: 0.75rem 1rem; background-color: #fff; border-top: 1px solid #f1f5f9;
    display: flex; justify-content: space-between; align-items: center; gap: 1rem;
}
.actions-left { display: flex; gap: 0.5rem; }
.actions-right { display: flex; gap: 0.25rem; }

.btn-pill {
    border: none; border-radius: 4px; padding: 0.35rem 0.75rem; font-size: 0.75rem; font-weight: 600;
    cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s;
}
.btn-ativar { background-color: #dcfce7; color: #166534; }
.btn-ativar:hover { background-color: #bbf7d0; }

.text-muted-small { font-size: 0.75rem; color: #94a3b8; display: flex; align-items: center; gap: 4px; }

.btn-mini {
    width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent;
    color: #94a3b8; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; font-size: 0.8rem;
}
.btn-mini:hover { background-color: #f1f5f9; color: #334155; }
.btn-info:hover { background-color: #eff6ff; color: #2563eb; }
.btn-delete-mini:hover { background-color: #fef2f2; color: #ef4444; }

.mt-3 { margin-top: 0.75rem; }
.loading-state, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.empty-icon { font-size: 2.5rem; color: #e2e8f0; margin-bottom: 1rem; }
.spinner {
  border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%;
  width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
}
</style>
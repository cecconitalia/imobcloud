<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Agenda</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Visitas</span>
           </nav>
           
           <h1>Gerenciar Visitas</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchVisitas" title="Atualizar Lista">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            
            <router-link :to="{ name: 'visita-nova' }" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Novo Agendamento
            </router-link>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: filterStatus === '' }" @click="filterStatus = ''">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.total }}</span>
          <span class="kpi-label">Total Visitas</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-calendar-check"></i></div>
      </div>
      
      <div class="kpi-card orange" :class="{ active: filterStatus === 'PENDENTE' }" @click="filterStatus = 'PENDENTE'">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.pendentes }}</span>
          <span class="kpi-label">Pendentes</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-clock"></i></div>
      </div>
      
      <div class="kpi-card green" :class="{ active: filterStatus === 'REALIZADA' }" @click="filterStatus = 'REALIZADA'">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.realizadas }}</span>
          <span class="kpi-label">Realizadas</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-check-circle"></i></div>
      </div>
      
      <div class="kpi-card bg-gray">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.hoje }}</span>
          <span class="kpi-label">Hoje</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-calendar-day"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Cliente, imóvel, bairro..." 
              class="form-control"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Status</label>
          <select v-model="filterStatus" class="form-control">
            <option value="">Todos</option>
            <option value="PENDENTE">Pendente</option>
            <option value="REALIZADA">Realizada</option>
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
        <p>Carregando visitas...</p>
      </div>
      
      <div v-else-if="error" class="error-message">{{ error }}</div>
      
      <div v-else-if="filteredVisitas.length === 0" class="empty-state">
        <i class="fas fa-filter"></i>
        <p>Nenhuma visita encontrada com os filtros selecionados.</p>
      </div>

      <div v-else class="report-scroll-viewport">
        <table class="report-table">
          <thead>
            <tr>
              <th width="15%">Agendamento</th>
              <th width="30%">Imóvel</th>
              <th width="20%">Cliente</th>
              <th width="15%">Status</th>
              <th width="20%" class="text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="visita in filteredVisitas" :key="visita.id" @click="abrirDetalhes(visita)" class="clickable-row">
              <td>
                <div class="cell-date">
                    <span class="date-main">{{ formatarData(visita.data_visita) }}</span>
                    <span class="date-sub">
                        <i class="far fa-clock"></i> {{ formatarHora(visita.data_visita) }} • #{{ visita.id }}
                    </span>
                </div>
              </td>

              <td>
                <div class="cell-imovel">
                    <span class="imovel-title" :title="getTituloImovel(visita)">
                        {{ getTituloImovel(visita) }}
                    </span>
                    <span class="imovel-address">
                        <i class="fas fa-map-marker-alt"></i> {{ getEnderecoImovel(visita) }}
                    </span>
                </div>
              </td>

              <td>
                 <div class="cell-cliente">
                    <i class="far fa-user"></i>
                    <span>{{ visita.cliente_obj?.nome || 'Não informado' }}</span>
                 </div>
              </td>

              <td>
                 <div class="status-cell">
                    <span :class="['badge-type', visita.realizada ? 'bg-green' : 'bg-orange']">
                        {{ visita.realizada ? 'Realizada' : 'Pendente' }}
                    </span>
                    
                    <span v-if="visita.assinatura_cliente && visita.assinatura_corretor" class="badge-mini bg-blue-light" title="Assinado Digitalmente">
                        <i class="fas fa-check-double"></i> Assinado
                    </span>
                 </div>
              </td>

              <td class="text-right" @click.stop>
                <div class="actions-flex">
                    <button 
                        v-if="!(visita.assinatura_cliente && visita.assinatura_corretor)"
                        @click="abrirDetalhes(visita)" 
                        class="btn-action sign"
                        title="Assinar"
                    >
                        <i class="fas fa-file-signature"></i>
                    </button>

                    <button class="btn-action pdf" @click="abrirPDFVisita(visita.id)" title="Gerar PDF">
                        <i class="fas fa-file-pdf"></i>
                    </button>

                    <button class="btn-action view" @click="abrirDetalhes(visita)" title="Ver Detalhes">
                        <i class="fas fa-eye"></i>
                    </button>
                    
                    <div v-if="visita.assinatura_cliente || visita.assinatura_corretor" class="disabled-wrapper">
                        <button class="btn-action edit disabled" disabled>
                            <i class="fas fa-pen"></i>
                        </button>
                    </div>
                    <router-link v-else :to="`/visitas/editar/${visita.id}`" class="btn-action edit" title="Editar">
                        <i class="fas fa-pen"></i>
                    </router-link>
                    
                    <button class="btn-action delete" @click="handleDeletar(visita.id)" title="Cancelar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <AssinaturaModal
        v-if="showAssinaturaModal"
        :enderecoImovel="tituloModalAssinatura"
        :isSaving="isSavingSignature"
        @close="fecharModalAssinatura"
        @save="salvarAssinatura"
    />

    <VisitaDetalhesModal
        v-if="showDetalhesModal"
        :show="showDetalhesModal"
        :visita="visitaSelecionada"
        @close="fecharDetalhes"
        @iniciar-visita="iniciarAssinaturaDeDetalhes"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import { format, isSameDay, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useToast } from 'vue-toast-notification';

// Componentes
import AssinaturaModal from '@/components/AssinaturaModal.vue';
import VisitaDetalhesModal from '@/components/VisitaDetalhesModal.vue';

const visitas = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const searchTerm = ref('');
const filterStatus = ref('');
const toast = useToast();

// Estados dos Modais
const showAssinaturaModal = ref(false);
const visitaParaAssinar = ref<any>(null);
const isSavingSignature = ref(false);

const showDetalhesModal = ref(false);
const visitaSelecionada = ref<any>(null);

// Controle assinatura
const imoveisParaSalvar = ref<number[]>([]);
const tipoAssinaturaAtual = ref<'CORRETOR' | 'CLIENTE'>('CORRETOR');

// --- Helpers ---
function getTituloImovel(visita: any) {
    if (!visita?.imoveis_obj || visita.imoveis_obj.length === 0) return 'Nenhum imóvel vinculado';
    const primeiro = visita.imoveis_obj[0];
    const qtd = visita.imoveis_obj.length;
    if (qtd > 1) return `${primeiro.titulo_anuncio || 'Imóvel Principal'} (+${qtd - 1} outros)`;
    return primeiro.titulo_anuncio || 'Imóvel sem título';
}

function getEnderecoImovel(visita: any) {
    if (!visita?.imoveis_obj || visita.imoveis_obj.length === 0) return 'Endereço não disponível';
    const primeiro = visita.imoveis_obj[0];
    return `${primeiro.logradouro || ''}, ${primeiro.numero || ''}`;
}

const tituloModalAssinatura = computed(() => {
    const base = visitaParaAssinar.value ? getTituloImovel(visitaParaAssinar.value) : '';
    const quem = tipoAssinaturaAtual.value === 'CORRETOR' ? 'Corretor' : 'Cliente';
    return `Assinatura do ${quem} - ${base}`;
});

function abrirPDFVisita(visitaId: number) {
    const url = `${apiClient.defaults.baseURL}/v1/visitas/${visitaId}/pdf/`;
    window.open(url, '_blank');
}

const stats = computed(() => {
    const total = visitas.value.length;
    const realizadas = visitas.value.filter(v => v.realizada).length;
    const pendentes = total - realizadas;
    const hojeDate = new Date();
    const hoje = visitas.value.filter(v => {
        try { return isSameDay(parseISO(v.data_visita), hojeDate); } catch { return false; }
    }).length;
    return { total, realizadas, pendentes, hoje };
});

const filteredVisitas = computed(() => {
  return visitas.value.filter(visita => {
    const searchLower = searchTerm.value.toLowerCase();
    const statusMatch = !filterStatus.value || 
        (filterStatus.value === 'REALIZADA' && visita.realizada) ||
        (filterStatus.value === 'PENDENTE' && !visita.realizada);
    
    let textMatch = false;
    if (!searchLower) {
        textMatch = true;
    } else {
        const clienteMatch = (visita.cliente_obj?.nome?.toLowerCase() || '').includes(searchLower);
        const imovelMatch = visita.imoveis_obj?.some((im: any) => 
            (im.titulo_anuncio?.toLowerCase() || '').includes(searchLower) ||
            (im.logradouro?.toLowerCase() || '').includes(searchLower) ||
            (im.bairro?.toLowerCase() || '').includes(searchLower)
        );
        textMatch = clienteMatch || imovelMatch;
    }
    return statusMatch && textMatch;
  });
});

function formatarData(data: string) { 
    try { return format(parseISO(data), 'dd/MM/yyyy', { locale: ptBR }); } catch { return '-'; }
}
function formatarHora(data: string) { 
    try { return format(parseISO(data), 'HH:mm'); } catch { return '-'; }
}

async function fetchVisitas() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/visitas/');
    visitas.value = response.data;
  } catch (err) {
    console.error("Erro visitas:", err);
    error.value = 'Não foi possível carregar as visitas.';
  } finally {
    isLoading.value = false;
  }
}

async function handleDeletar(visitaId: number) {
  if (!window.confirm('Cancelar este agendamento?')) return;
  try {
    await apiClient.delete(`/v1/visitas/${visitaId}/`);
    visitas.value = visitas.value.filter(v => v.id !== visitaId);
    toast.success('Agendamento cancelado.');
  } catch (error: any) {
    toast.error("Erro ao cancelar.");
  }
}

function clearFilters() {
    searchTerm.value = '';
    filterStatus.value = '';
}

// Modais
function abrirDetalhes(visita: any) {
    visitaSelecionada.value = visita;
    showDetalhesModal.value = true;
}
function fecharDetalhes() {
    showDetalhesModal.value = false;
    visitaSelecionada.value = null;
}
function iniciarAssinaturaDeDetalhes(payload: any) {
    const { visitaId, imoveisIds, tipo } = payload;
    const visitaObj = visitas.value.find(v => v.id === visitaId);
    if (visitaObj) {
        imoveisParaSalvar.value = imoveisIds;
        tipoAssinaturaAtual.value = tipo;
        fecharDetalhes();
        abrirModalAssinatura(visitaObj, true);
    }
}
function abrirModalAssinatura(visita: any, veioDoDetalhe = false) {
    visitaParaAssinar.value = visita;
    if (!veioDoDetalhe) {
        if (visita.imoveis_obj) imoveisParaSalvar.value = visita.imoveis_obj.map((i: any) => i.id);
        tipoAssinaturaAtual.value = 'CLIENTE';
    }
    showAssinaturaModal.value = true;
}
function fecharModalAssinatura() {
    showAssinaturaModal.value = false;
    visitaParaAssinar.value = null;
    imoveisParaSalvar.value = [];
}
async function salvarAssinatura(base64Image: string) {
    if (!visitaParaAssinar.value) return;
    isSavingSignature.value = true;
    let localizacao = '';
    if (navigator.geolocation) {
        try {
            const position = await new Promise<GeolocationPosition>((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 4000 });
            });
            localizacao = `${position.coords.latitude}, ${position.coords.longitude}`;
        } catch {}
    }
    const res = await fetch(base64Image);
    const blob = await res.blob();
    const file = new File([blob], "assinatura.png", { type: "image/png" });
    const formData = new FormData();
    
    if (tipoAssinaturaAtual.value === 'CORRETOR') {
        formData.append('assinatura_corretor', file);
        formData.append('data_assinatura_corretor', new Date().toISOString());
    } else {
        formData.append('assinatura_cliente', file);
        formData.append('data_assinatura', new Date().toISOString());
        formData.append('realizada', 'true');
    }
    if(localizacao) formData.append('localizacao_assinatura', localizacao);
    imoveisParaSalvar.value.forEach(id => formData.append('imoveis', id.toString()));

    try {
        const response = await apiClient.patch(`/v1/visitas/${visitaParaAssinar.value.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        const index = visitas.value.findIndex(v => v.id === visitaParaAssinar.value.id);
        if (index !== -1) visitas.value[index] = { ...visitas.value[index], ...response.data };
        
        toast.success("Assinatura salva com sucesso!");
        fecharModalAssinatura();
        abrirDetalhes(visitas.value[index]);
    } catch (error) {
        toast.error("Erro ao salvar assinatura.");
    } finally {
        isSavingSignature.value = false;
    }
}

onMounted(fetchVisitas);
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (IDÊNTICO A CLIENTES) */
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
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer; text-decoration: none;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15);
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }

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
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }
.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }
.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }
.kpi-card.bg-gray .kpi-value { color: #475569; }

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
  font-size: 0.85rem; color: #334155; vertical-align: middle;
}
.clickable-row { cursor: pointer; transition: background 0.1s; }
.clickable-row:hover { background-color: #fcfcfc; }

/* Celulas customizadas */
.cell-date { display: flex; flex-direction: column; }
.date-main { font-weight: 600; color: #1e293b; font-size: 0.9rem; }
.date-sub { font-size: 0.7rem; color: #94a3b8; display: flex; align-items: center; gap: 4px; }

.cell-imovel { display: flex; flex-direction: column; }
.imovel-title { font-weight: 600; color: #1e293b; font-size: 0.85rem; }
.imovel-address { font-size: 0.75rem; color: #64748b; margin-top: 2px; display: inline-flex; align-items: center; gap: 5px; }

.cell-cliente { display: flex; align-items: center; gap: 8px; color: #475569; font-weight: 500; }
.cell-cliente i { color: #cbd5e1; }

.status-cell { display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.badge-type {
  font-size: 0.65rem; font-weight: 600; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.02em;
}
.bg-green { background: #dcfce7; color: #166534; }
.bg-orange { background: #ffedd5; color: #c2410c; }
.bg-blue-light { background: #eff6ff; color: #2563eb; }
.badge-mini { font-size: 0.6rem; padding: 2px 6px; border-radius: 3px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }

/* Ações */
.actions-flex { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-action {
  width: 32px; height: 32px; border: none; border-radius: 6px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
  background: transparent; color: #94a3b8; border: 1px solid transparent;
}
.btn-action:hover { background-color: #f1f5f9; color: #334155; border-color: #e2e8f0; }

.btn-action.sign { background-color: #eff6ff; color: #2563eb; }
.btn-action.sign:hover { background-color: #2563eb; color: #fff; }

.btn-action.pdf:hover { background-color: #fff1f2; color: #e11d48; }
.btn-action.view:hover { background-color: #f0f9ff; color: #0284c7; }
.btn-action.edit:hover { background-color: #eff6ff; color: #2563eb; }
.btn-action.delete:hover { background-color: #fee2e2; color: #ef4444; }

.btn-action.disabled { opacity: 0.3; cursor: not-allowed; pointer-events: none; }
.disabled-wrapper { cursor: not-allowed; }

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
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
          <span class="kpi-label">Total de Visitas</span>
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
      
      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ stats.hoje }}</span>
          <span class="kpi-label">Agendadas para Hoje</span>
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
              placeholder="Buscar por cliente, imóvel ou bairro..." 
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
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Carregando visitas...</p>
    </div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="filteredVisitas.length === 0" class="empty-state">
      <i class="far fa-calendar-times empty-icon"></i>
      <p>Nenhuma visita encontrada com os filtros selecionados.</p>
    </div>

    <div v-else class="visitas-grid">
      <div 
        v-for="visita in filteredVisitas" 
        :key="visita.id" 
        class="visita-card"
        :class="{ 'border-realizada': visita.realizada }"
      >
        <div class="card-top-bar">
           <div class="badges-left">
               <span class="visita-id">#{{ visita.id }}</span>
               <span class="date-badge">
                  <i class="far fa-calendar-alt"></i> {{ formatarData(visita.data_visita) }}
               </span>
           </div>
           <div class="badges-right">
               <span :class="['status-pill', visita.realizada ? 'status-realizada' : 'status-pendente']">
                  <i :class="visita.realizada ? 'fas fa-check-circle' : 'far fa-clock'"></i>
                  {{ visita.realizada ? 'Realizada' : 'Pendente' }}
               </span>
           </div>
        </div>
        
        <div class="card-body" @click="abrirDetalhes(visita)" style="cursor: pointer;">
          
          <div class="imovel-section">
             <h4 class="imovel-title" :title="getTituloImovel(visita)">
                {{ getTituloImovel(visita) }}
             </h4>
             <p class="imovel-address">
                <i class="fas fa-map-marker-alt text-muted"></i> 
                {{ getEnderecoImovel(visita) }}
             </p>
             <small class="text-muted" v-if="visita.imoveis_obj && visita.imoveis_obj.length > 1">
                 <i class="fas fa-layer-group"></i> Roteiro com {{ visita.imoveis_obj.length }} imóveis
             </small>
             <small class="text-muted" v-else>
                 {{ visita.imoveis_obj?.[0]?.bairro }} - {{ visita.imoveis_obj?.[0]?.cidade }}
             </small>
          </div>

          <div class="time-highlight">
              <i class="far fa-clock"></i> {{ formatarHora(visita.data_visita) }}
          </div>

          <div class="pessoas-container">
              <div class="pessoa-row">
                 <div class="pessoa-avatar avatar-cliente">
                    <i class="fas fa-user"></i>
                 </div>
                 <div class="pessoa-info">
                    <span class="pessoa-role">Cliente Interessado</span>
                    <span class="pessoa-name" :title="visita.cliente_obj?.nome">
                        {{ visita.cliente_obj?.nome || 'Nome não informado' }}
                    </span>
                 </div>
              </div>
          </div>
        </div>
        
        <div class="card-actions">
          <div class="actions-left">
            <span v-if="visita.assinatura_cliente && visita.assinatura_corretor" class="signed-badge">
                <i class="fas fa-check-double"></i> Assinado
            </span>

            <button 
                v-else
                @click="abrirDetalhes(visita)" 
                class="btn-pill btn-sign"
                title="Gerir Assinaturas"
            >
                <i class="fas fa-file-signature"></i> Assinar
            </button>
          </div>

          <div class="actions-right">
              <button @click="abrirPDFVisita(visita.id)" class="btn-mini btn-pdf" title="Ficha de Visita (PDF)">
                <i class="fas fa-file-pdf"></i>
              </button>

              <button @click="abrirDetalhes(visita)" class="btn-mini" title="Ver Detalhes Completos">
                <i class="fas fa-eye"></i>
              </button>
              
              <span v-if="visita.assinatura_cliente || visita.assinatura_corretor" title="Visita assinada não pode ser editada" style="cursor: not-allowed; opacity: 0.5; display: inline-block;">
                  <button class="btn-mini" disabled style="pointer-events: none;">
                    <i class="fas fa-pen"></i>
                  </button>
              </span>
              <router-link v-else :to="`/visitas/editar/${visita.id}`" class="btn-mini" title="Editar">
                <i class="fas fa-pen"></i>
              </router-link>
              
              <button @click="handleDeletar(visita.id)" class="btn-mini btn-delete-mini" title="Cancelar">
                <i class="fas fa-trash"></i>
              </button>
          </div>
        </div>
      </div>
    </div>

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

// Variáveis de controle para assinatura
const imoveisParaSalvar = ref<number[]>([]);
const tipoAssinaturaAtual = ref<'CORRETOR' | 'CLIENTE'>('CORRETOR');

// --- Helpers de Exibição ---

function getTituloImovel(visita: any) {
    if (!visita?.imoveis_obj || visita.imoveis_obj.length === 0) {
        return 'Nenhum imóvel vinculado';
    }
    const primeiro = visita.imoveis_obj[0];
    const qtd = visita.imoveis_obj.length;
    
    if (qtd > 1) {
        return `${primeiro.titulo_anuncio || 'Imóvel Principal'} (+${qtd - 1} outros)`;
    }
    return primeiro.titulo_anuncio || 'Imóvel sem título';
}

function getEnderecoImovel(visita: any) {
    if (!visita?.imoveis_obj || visita.imoveis_obj.length === 0) {
        return 'Endereço não disponível';
    }
    const primeiro = visita.imoveis_obj[0];
    return `${primeiro.logradouro || ''}, ${primeiro.numero || ''}`;
}

const tituloModalAssinatura = computed(() => {
    const base = visitaParaAssinar.value ? getTituloImovel(visitaParaAssinar.value) : '';
    const quem = tipoAssinaturaAtual.value === 'CORRETOR' ? 'Corretor' : 'Cliente';
    return `Assinatura do ${quem} - ${base}`;
});

// --- Ação PDF ---
function abrirPDFVisita(visitaId: number) {
    const url = `${apiClient.defaults.baseURL}/v1/visitas/${visitaId}/pdf/`;
    window.open(url, '_blank');
}

// --- Computed Stats ---
const stats = computed(() => {
    const total = visitas.value.length;
    const realizadas = visitas.value.filter(v => v.realizada).length;
    const pendentes = total - realizadas;
    
    const hojeDate = new Date();
    const hoje = visitas.value.filter(v => {
        try {
            return isSameDay(parseISO(v.data_visita), hojeDate);
        } catch { return false; }
    }).length;

    return { total, realizadas, pendentes, hoje };
});

// --- Filtros ---
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
    try { return format(parseISO(data), 'dd/MM/yyyy', { locale: ptBR }); } 
    catch { return '-'; }
}
function formatarHora(data: string) { 
    try { return format(parseISO(data), 'HH:mm'); } 
    catch { return '-'; }
}

async function fetchVisitas() {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/v1/visitas/');
    visitas.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar visitas:", err);
    error.value = 'Não foi possível carregar as visitas.';
  } finally {
    isLoading.value = false;
  }
}

async function handleDeletar(visitaId: number) {
  if (!window.confirm('Tem a certeza de que deseja cancelar este agendamento?')) return;
  try {
    await apiClient.delete(`/v1/visitas/${visitaId}/`);
    visitas.value = visitas.value.filter(v => v.id !== visitaId);
    toast.success('Agendamento cancelado.');
  } catch (error: any) {
    const msg = error.response?.data?.detail || "Erro ao cancelar agendamento. Tente novamente.";
    toast.error(msg);
  }
}

// --- Controle de Modais ---
function abrirDetalhes(visita: any) {
    visitaSelecionada.value = visita;
    showDetalhesModal.value = true;
}

function fecharDetalhes() {
    showDetalhesModal.value = false;
    visitaSelecionada.value = null;
}

// Chamado pelo Modal de Detalhes quando clica em "Assinar"
function iniciarAssinaturaDeDetalhes(payload: any) {
    const { visitaId, imoveisIds, tipo } = payload;
    const visitaObj = visitas.value.find(v => v.id === visitaId);
    
    if (visitaObj) {
        imoveisParaSalvar.value = imoveisIds; // IDs selecionados/filtrados
        tipoAssinaturaAtual.value = tipo; // 'CORRETOR' ou 'CLIENTE'
        
        fecharDetalhes();
        abrirModalAssinatura(visitaObj, true);
    }
}

function abrirModalAssinatura(visita: any, veioDoDetalhe = false) {
    visitaParaAssinar.value = visita;
    // Se abriu direto (sem passar pelo detalhe), assume todos os imóveis e cliente por padrão
    if (!veioDoDetalhe) {
        if (visita.imoveis_obj) {
            imoveisParaSalvar.value = visita.imoveis_obj.map((i: any) => i.id);
        }
        tipoAssinaturaAtual.value = 'CLIENTE'; // Padrão antigo
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
        } catch { 
            localizacao = ''; 
        }
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
    
    imoveisParaSalvar.value.forEach(id => {
        formData.append('imoveis', id.toString());
    });

    try {
        const response = await apiClient.patch(`/v1/visitas/${visitaParaAssinar.value.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        const index = visitas.value.findIndex(v => v.id === visitaParaAssinar.value.id);
        if (index !== -1) {
            visitas.value[index] = { ...visitas.value[index], ...response.data };
        }
        
        toast.success(`${tipoAssinaturaAtual.value === 'CORRETOR' ? 'Corretor' : 'Cliente'} assinou com sucesso!`);
        fecharModalAssinatura();
        abrirDetalhes(visitas.value[index]);

    } catch (error) {
        console.error(error);
        toast.error("Erro ao salvar assinatura.");
    } finally {
        isSavingSignature.value = false;
    }
}

onMounted(() => {
  fetchVisitas();
});
</script>

<style scoped>
/* CONFIGURAÇÃO GERAL (PADRONIZADO) */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER DA PÁGINA (PADRONIZADO) */
.page-header { margin-bottom: 2rem; }
.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Fino (PADRONIZADO) */
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

/* KPI GRID (PADRONIZADO) */
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
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }

.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }

.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }

.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR (PADRONIZADO) */
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

/* ================================================== */
/* GRID DE VISITAS (ESPECÍFICO DESTA PÁGINA) */
/* ================================================== */
.visitas-grid {
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 1.5rem; 
  padding-bottom: 2rem;
}

@media (max-width: 1300px) { .visitas-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 992px) { .visitas-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .visitas-grid { grid-template-columns: 1fr; } }

.visita-card {
  background-color: #fff; border-radius: 8px; border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); display: flex; flex-direction: column;
  transition: all 0.2s ease; position: relative; overflow: hidden;
}
.visita-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }
.border-realizada { border-left: 4px solid #10b981; }

/* Card Top */
.card-top-bar {
    padding: 0.8rem 1rem; display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #f1f5f9; background: #fff;
}
.badges-left, .badges-right { display: flex; align-items: center; gap: 8px; }

.visita-id {
    font-size: 0.7rem; font-weight: 700; color: #64748b;
    background: #f1f5f9; padding: 2px 6px; border-radius: 4px;
}
.date-badge {
    font-size: 0.75rem; color: #475569; font-weight: 600; display: flex; align-items: center; gap: 5px;
}
.status-pill {
    padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;
    text-transform: uppercase; display: flex; align-items: center; gap: 4px;
}
.status-pendente { background-color: #eff6ff; color: #1d4ed8; }
.status-realizada { background-color: #dcfce7; color: #15803d; }

/* Card Body */
.card-body { padding: 0; flex-grow: 1; display: flex; flex-direction: column; }

.imovel-section { padding: 1rem 1rem 0.5rem; }
.imovel-title {
    font-size: 0.9rem; font-weight: 600; color: #1e293b; margin: 0 0 0.25rem 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.imovel-address {
    font-size: 0.8rem; color: #64748b; margin: 0;
    display: flex; align-items: center; gap: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.time-highlight {
    background-color: #f8fafc; border-top: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;
    padding: 0.4rem 1rem; font-weight: 600; color: #2563eb; font-size: 0.85rem;
    display: flex; align-items: center; gap: 6px;
}

.pessoas-container { padding: 0.8rem 1rem; }
.pessoa-row { display: flex; align-items: center; gap: 0.75rem; }
.pessoa-avatar {
    width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; flex-shrink: 0;
}
.avatar-cliente { background-color: #fffbeb; color: #b45309; }
.pessoa-info { display: flex; flex-direction: column; overflow: hidden; }
.pessoa-role { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; margin-bottom: 1px; color: #b45309; }
.pessoa-name { font-size: 0.85rem; color: #334155; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Card Actions */
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
.btn-sign { background-color: #eff6ff; color: #2563eb; }
.btn-sign:hover { background-color: #2563eb; color: #fff; }

.signed-badge {
    display: inline-flex; align-items: center; gap: 5px; font-size: 0.75rem; 
    color: #10b981; font-weight: 600; background-color: #ecfdf5; padding: 3px 8px; border-radius: 4px;
}

.btn-mini {
    width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent;
    color: #94a3b8; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; font-size: 0.8rem;
}
.btn-mini:hover { background-color: #f1f5f9; color: #334155; }
.btn-delete-mini:hover { background-color: #fef2f2; color: #ef4444; }
.btn-pdf:hover { background-color: #fff1f2; color: #e11d48; }

.text-muted { color: #94a3b8; }
.loading-state, .error-message, .empty-state { text-align: center; padding: 4rem 2rem; color: #64748b; }
.empty-icon { font-size: 2.5rem; color: #e2e8f0; margin-bottom: 1rem; }
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
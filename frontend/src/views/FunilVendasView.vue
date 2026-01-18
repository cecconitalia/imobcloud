<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Vendas</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Funil</span>
           </nav>
           <h1>Funil de Vendas</h1>
        </div>
        <div class="actions-area">
            <button class="btn-icon-thin" @click="fetchData" title="Atualizar Dados">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            <router-link to="/oportunidades/nova" class="btn-primary-thin">
              <i class="fas fa-plus"></i> Nova Oportunidade
            </router-link>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card orange">
        <div class="kpi-content">
          <span class="kpi-value">{{ totalAtivas }}</span>
          <span class="kpi-label">Qtd. Ativas</span>
        </div>
        <div class="kpi-icon-bg text-orange-500 bg-orange-50"><i class="fas fa-filter"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ taxaFechamento }}%</span>
          <span class="kpi-label">Conversão</span>
        </div>
        <div class="kpi-icon-bg text-emerald-500 bg-emerald-50"><i class="fas fa-chart-line"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ probabilidadeMedia }}%</span>
          <span class="kpi-label">Probabilidade</span>
        </div>
        <div class="kpi-icon-bg text-purple-500 bg-purple-50"><i class="fas fa-percentage"></i></div>
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
            placeholder="Buscar oportunidade..." 
            class="form-control"
            @input="debouncedFetchOportunidades"
          >
        </div>
      </div>

      <div class="filter-group">
        <label>Responsável</label>
        <div class="custom-select">
          <select v-model="filtro.responsavel" @change="fetchData" class="form-control">
            <option value="">Todos os Corretores</option>
            <option v-for="resp in corretores" :key="resp.id" :value="resp.id">
              {{ resp.first_name }}
            </option>
          </select>
          <i class="fas fa-chevron-down select-icon"></i>
        </div>
      </div>

      <div class="filter-group small-btn">
        <label>&nbsp;</label>
        <button 
          class="btn-toggle" 
          @click="toggleCardsRecolhidos"
          :title="cardsRecolhidos ? 'Modo Expandido' : 'Modo Resumido'"
        >
          <i :class="cardsRecolhidos ? 'fas fa-columns' : 'fas fa-list'"></i>
          <span class="btn-label">{{ cardsRecolhidos ? 'Expandir' : 'Resumir' }}</span>
        </button>
      </div>
    </div>

    <main class="kanban-main-wrapper">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando funil...</p>
      </div>

      <div v-else-if="funilFases.length === 0" class="empty-state-funil">
          <i class="fas fa-layer-group fa-3x mb-3 text-gray-300"></i>
          <h3>Funil não configurado</h3>
          <p>Nenhuma etapa cadastrada.</p>
      </div>

      <div v-else class="kanban-scroll-viewport">
        <div class="kanban-board" :class="{ 'collapsed-mode': cardsRecolhidos }">
          
          <div v-for="(fase, index) in funilFases" :key="fase.id" class="kanban-column">
            
            <div class="column-header sticky-header" :style="{ borderTopColor: getFaseColor(index) }">
              <div class="header-top">
                <span class="column-title" :title="fase.titulo">
                  {{ cardsRecolhidos ? fase.titulo.substring(0, 3).toUpperCase() : fase.titulo }}
                </span>
                <span class="column-badge">{{ funilData[fase.id]?.length || 0 }}</span>
              </div>
              <div class="column-summary" v-if="somarValorFase(fase.id) > 0">
                 {{ formatarValorCompacto(somarValorFase(fase.id)) }}
              </div>
            </div>

            <div class="column-body">
              <draggable
                v-model="funilData[fase.id]"
                :group="{ name: 'oportunidades' }"
                @change="onFaseChange($event, fase.id)"
                item-key="id"
                class="draggable-area"
                ghost-class="sortable-ghost"
                drag-class="sortable-drag"
              >
                <template #item="{ element: op }">
                  <div class="kanban-card" @click="router.push(`/oportunidades/editar/${op.id}`)">
                    <div class="card-status-strip" :class="getProbabilidadeClass(op.probabilidade)"></div>
                    <div class="card-content">
                        <div class="card-top">
                            <span class="card-id">#{{ op.id }}</span>
                        </div>
                        <h4 class="card-title">{{ op.titulo }}</h4>
                        <div class="card-details">
                            <div class="detail-row" v-if="op.cliente">
                                <i class="far fa-user"></i>
                                <span class="truncate">{{ op.cliente_detalhe?.nome || op.cliente?.nome || 'Cliente' }}</span>
                            </div>
                        </div>
                        <div class="card-footer">
                            <span class="card-price">{{ formatarValor(op.valor_estimado) }}</span>
                            <div class="card-avatar" v-if="op.responsavel">
                                {{ getInitials(op.responsavel_nome || op.responsavel.first_name) }}
                            </div>
                        </div>
                    </div>
                  </div>
                </template>
              </draggable>
            </div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import draggable from 'vuedraggable';
import { debounce } from 'lodash'; 
import '@fortawesome/fontawesome-free/css/all.css';

const router = useRouter();
const COLORS = ['#3b82f6', '#06b6d4', '#eab308', '#f97316', '#8b5cf6', '#22c55e', '#64748b', '#ec4899'];

const funilFases = ref<any[]>([]); 
const oportunidades = ref<any[]>([]);
const funilData = ref<{ [key: number]: any[] }>({});
const isLoading = ref(true);
const corretores = ref<any[]>([]);
const cardsRecolhidos = ref(false);
const filtro = ref({ search: '', responsavel: '' });

// --- COMPUTADOS ---
const totalAtivas = computed(() => {
  return oportunidades.value.filter(op => {
      const fase = funilFases.value.find(f => f.id === op.fase);
      if (fase) {
          return fase.probabilidade_fechamento > 0 && fase.probabilidade_fechamento < 100;
      }
      return true; 
  }).length;
});

const taxaFechamento = computed(() => {
    let ganhos = 0;
    let perdidos = 0;

    oportunidades.value.forEach(op => {
        const fase = funilFases.value.find(f => f.id === op.fase);
        if (fase) {
            if (fase.probabilidade_fechamento === 100) ganhos++;
            if (fase.probabilidade_fechamento === 0) perdidos++;
        }
    });

    const totalFinalizado = ganhos + perdidos;
    if (totalFinalizado === 0) return '0.0';
    return ((ganhos / totalFinalizado) * 100).toFixed(1);
});

const probabilidadeMedia = computed(() => {
  if (oportunidades.value.length === 0) return '0.0';
  const total = oportunidades.value.reduce((sum, op) => sum + (op.probabilidade || 0), 0);
  return (total / oportunidades.value.length).toFixed(1);
});

// --- HELPER FUNCTIONS ---
function getFaseColor(index: number) { return COLORS[index % COLORS.length]; }

function getProbabilidadeClass(prob: number | null) {
    if (prob === null || prob === undefined) return 'bg-gray-300';
    if (prob >= 90) return 'bg-emerald-500';
    if (prob >= 50) return 'bg-blue-500';
    if (prob >= 20) return 'bg-orange-400';
    return 'bg-red-400';
}

function getInitials(name: string) {
    if (!name) return 'U';
    return name.charAt(0).toUpperCase();
}

function toggleCardsRecolhidos() { cardsRecolhidos.value = !cardsRecolhidos.value; }

// --- DATA FETCHING ---
async function fetchData() {
    isLoading.value = true;
    try {
        const resFases = await api.get('/v1/fases-funil/');
        funilFases.value = resFases.data.results || resFases.data; 

        const params = {
            search: filtro.value.search || undefined,
            responsavel: filtro.value.responsavel || undefined,
        };
        const resOps = await api.get('/v1/oportunidades/', { params });
        oportunidades.value = resOps.data.results || resOps.data;

        // Extrair lista de corretores únicos das oportunidades carregadas
        const map = new Map();
        oportunidades.value.forEach(op => {
            if (op.responsavel && typeof op.responsavel === 'object') {
                 if (!map.has(op.responsavel.id)) map.set(op.responsavel.id, op.responsavel);
            }
        });
        corretores.value = Array.from(map.values());

        distribuirOportunidades();
    } catch (e) {
        console.error("Erro API:", e);
    } finally {
        isLoading.value = false;
    }
}

const debouncedFetchOportunidades = debounce(fetchData, 400);

function distribuirOportunidades() {
    const groups: { [key: number]: any[] } = {};
    funilFases.value.forEach(f => groups[f.id] = []);
    
    const orphans: any[] = [];
    oportunidades.value.forEach(op => {
        // Verifica se 'fase' é um objeto ou ID
        const faseId = typeof op.fase === 'object' ? op.fase?.id : op.fase;
        
        if (faseId && groups[faseId]) {
            groups[faseId].push(op);
        } else {
            orphans.push(op);
        }
    });

    // Se houver órfãos, coloca na primeira coluna
    if (orphans.length > 0 && funilFases.value.length > 0) {
        const firstId = funilFases.value[0].id;
        groups[firstId] = [...groups[firstId], ...orphans];
    }
    funilData.value = groups;
}

const onFaseChange = async (event: any, novaFaseId: number) => {
    if (event.added) {
        const oportunidadeId = event.added.element.id;
        
        // Atualiza localmente para feedback instantâneo
        const opIndex = oportunidades.value.findIndex(o => o.id === oportunidadeId);
        if (opIndex !== -1) {
            oportunidades.value[opIndex].fase = novaFaseId;
            const novaFase = funilFases.value.find(f => f.id === novaFaseId);
            if(novaFase) oportunidades.value[opIndex].probabilidade = novaFase.probabilidade_fechamento;
        }

        try {
            await api.patch(`/v1/oportunidades/${oportunidadeId}/`, { fase: novaFaseId }); 
        } catch (error) {
            console.error('Erro ao mover:', error);
            fetchData(); // Reverte em caso de erro
        }
    }
};

const formatarValor = (val: any) => {
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (!num && num !== 0) return 'R$ 0,00';
  return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const formatarValorCompacto = (val: number) => {
  if (!val) return 'R$ 0';
  return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact' });
};

function somarValorFase(faseId: number): number {
    return (funilData.value[faseId] || []).reduce((sum, op) => sum + (parseFloat(op.valor_estimado) || 0), 0);
}

onMounted(fetchData);
</script>

<style scoped>
/* =========================================================
   1. GERAL & HEADER
   ========================================================= */
.page-container {
  height: 100vh;
  background-color: #f8fafc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  display: flex; flex-direction: column; padding: 1.5rem; box-sizing: border-box;
}

.page-header { flex: none; margin-bottom: 1.5rem; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.title-area h1 { font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0; }
.breadcrumb { font-size: 0.75rem; color: #64748b; font-weight: 500; text-transform: uppercase; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
.separator { font-size: 0.6rem; color: #cbd5e1; }
.actions-area { display: flex; gap: 0.75rem; }
.btn-primary-thin { background: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.875rem; text-decoration: none; display: flex; align-items: center; gap: 0.5rem; transition: background 0.2s; font-weight: 500; }
.btn-primary-thin:hover { background: #1d4ed8; }
.btn-icon-thin { background: white; border: 1px solid #e2e8f0; width: 36px; height: 36px; border-radius: 8px; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-icon-thin:hover { border-color: #cbd5e1; background: #f1f5f9; color: #334155; }

/* =========================================================
   2. KPI CARDS
   ========================================================= */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
    gap: 1rem; margin-bottom: 1.5rem; flex: none;
}
.kpi-card {
  background: white; border-radius: 12px; padding: 1rem; border: 1px solid #e2e8f0;
  display: flex; align-items: center; gap: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.kpi-icon-bg {
    width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; flex-shrink: 0;
}
.kpi-content { display: flex; flex-direction: column; }
.kpi-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.02em; }
.kpi-value { font-size: 1.5rem; font-weight: 700; line-height: 1.1; color: #1e293b; }

/* Cores KPI (Classes Utilitárias Simuladas) */
.text-orange-500 { color: #f97316; } .bg-orange-50 { background-color: #fff7ed; }
.text-emerald-500 { color: #10b981; } .bg-emerald-50 { background-color: #ecfdf5; }
.text-purple-500 { color: #8b5cf6; } .bg-purple-50 { background-color: #f5f3ff; }

/* =========================================================
   3. TOOLBAR
   ========================================================= */
.toolbar-row {
  background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 0.75rem;
  display: flex; gap: 1rem; align-items: center; margin-bottom: 1.5rem; flex: none;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.filter-group { display: flex; flex-direction: column; gap: 0.25rem; flex: 1; }
.filter-group label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #64748b; letter-spacing: 0.02em; }
.search-group { flex: 2; }
.small-btn { flex: 0 0 auto; }

.form-control { width: 100%; padding: 0.5rem 0.75rem 0.5rem 2.25rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.875rem; outline: none; transition: border 0.2s; color: #334155; background: #fff; box-sizing: border-box; height: 38px; }
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }

.custom-select { position: relative; width: 100%; }
.custom-select select { appearance: none; cursor: pointer; padding-right: 2rem; padding-left: 0.75rem; width: 100%; }
.select-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; font-size: 0.8rem; }

.btn-toggle { padding: 0 1rem; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 8px; color: #475569; font-weight: 500; font-size: 0.875rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; }
.btn-toggle:hover { background: #f1f5f9; border-color: #94a3b8; }

/* =========================================================
   4. KANBAN BOARD
   ========================================================= */
.kanban-main-wrapper { flex: 1; position: relative; width: 100%; overflow: hidden; }
.kanban-scroll-viewport {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  overflow: hidden; /* Remove scroll horizontal se o conteúdo couber */
  display: flex;
}

/* Se a tela for pequena, permite scroll horizontal */
@media (max-width: 1200px) {
    .kanban-scroll-viewport { overflow-x: auto; }
    .kanban-board { min-width: max-content; }
    .kanban-column { flex: none; width: 280px; min-width: 280px; }
}

.kanban-board { display: flex; gap: 0.75rem; height: 100%; width: 100%; padding-bottom: 0.5rem; }

/* Colunas (Estilo Flexível) */
.kanban-column {
  display: flex; flex-direction: column;
  background-color: #f1f5f9; border-radius: 12px; border: 1px solid #e2e8f0;
  height: 100%; 
  flex: 1; /* Ocupa espaço igual */
  min-width: 0; /* Permite encolher */
  transition: all 0.3s ease;
}

/* Lógica de "Recolher pra Cima": Esconde o corpo da coluna */
.collapsed-mode .column-body { display: none !important; }
.collapsed-mode .kanban-column { height: auto; flex: none; flex-basis: auto; width: auto; min-width: 80px; }

.sticky-header {
    background: #fff; padding: 0.75rem; border-bottom: 1px solid #e2e8f0; border-radius: 12px 12px 0 0;
    border-top: 4px solid transparent; flex-shrink: 0;
}
.header-top { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-bottom: 0.25rem; }
.column-title { font-weight: 700; font-size: 0.75rem; color: #334155; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; letter-spacing: 0.05em; }
.column-badge { background: #f1f5f9; color: #64748b; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; font-weight: 700; min-width: 20px; text-align: center; }
.column-summary { font-size: 0.75rem; font-weight: 600; color: #059669; text-align: right; margin-top: 4px; }
.column-body { flex: 1; overflow-y: auto; padding: 0.5rem; scrollbar-width: thin; }

/* Cards */
.draggable-area { min-height: 100%; display: flex; flex-direction: column; gap: 0.75rem; padding-bottom: 2rem; }
.kanban-card {
    background: white; border-radius: 8px; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid transparent; border-left: 0;
    cursor: grab; position: relative; overflow: hidden; display: flex;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kanban-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1); border-color: #cbd5e1; border-left: 0; }
.kanban-card:active { cursor: grabbing; }

.card-status-strip { width: 4px; flex-shrink: 0; }
.bg-gray-300 { background-color: #cbd5e1; }
.bg-emerald-500 { background-color: #10b981; }
.bg-blue-500 { background-color: #3b82f6; }
.bg-orange-400 { background-color: #fb923c; }
.bg-red-400 { background-color: #f87171; }

.card-content { flex: 1; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.4rem; overflow: hidden; }
.card-top { display: flex; justify-content: space-between; align-items: center; font-size: 0.65rem; color: #94a3b8; }
.card-id { font-weight: 700; opacity: 0.7; }
.card-title { font-size: 0.9rem; font-weight: 600; color: #1e293b; margin: 0; line-height: 1.3; }
.card-details { display: flex; flex-direction: column; gap: 2px; font-size: 0.75rem; color: #64748b; }
.detail-row { display: flex; align-items: center; gap: 6px; }
.detail-row i { width: 14px; text-align: center; font-size: 0.7rem; opacity: 0.7; }
.truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.card-footer { margin-top: 0.4rem; padding-top: 0.5rem; border-top: 1px dashed #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
.card-price { font-size: 0.8rem; font-weight: 700; color: #059669; }
.card-avatar { width: 22px; height: 22px; border-radius: 50%; background: #e0f2fe; color: #0369a1; font-size: 0.65rem; font-weight: 700; display: flex; align-items: center; justify-content: center; border: 1px solid #bae6fd; }

.sortable-ghost { opacity: 0.4; background: #f1f5f9; border: 2px dashed #94a3b8; box-shadow: none; }
.sortable-drag { opacity: 1; transform: rotate(2deg); box-shadow: 0 10px 20px rgba(0,0,0,0.15); z-index: 100; }

.loading-state, .empty-state-funil { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; }
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 768px) {
    .page-container { padding: 1rem; }
    .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
    .actions-area { width: 100%; justify-content: space-between; }
    .toolbar-row { flex-direction: column; align-items: stretch; height: auto; }
    .kpi-grid { grid-template-columns: 1fr 1fr; }
    .btn-toggle .btn-label { display: inline; }
}
</style>
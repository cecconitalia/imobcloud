<template>
  <div class="funil-view-root">
    
    <header class="view-header-section">
      <div class="header-row">
        <div class="title-group">
          <h1>Funil de Vendas</h1>
          <p class="subtitle">Gestão estratégica de oportunidades</p>
        </div>
        
        <div class="actions-group">
          <button class="btn-secondary btn-icon" @click="fetchOportunidades" title="Atualizar Dados">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
          </button>
          <router-link to="/oportunidades/nova" class="btn-primary">
            <i class="fas fa-plus"></i>
            <span class="btn-label">Nova Oportunidade</span>
          </router-link>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card orange">
          <span class="kpi-label">Qtd. Ativas</span>
          <span class="kpi-value">{{ totalAtivas }}</span>
        </div>

        <div class="kpi-card blue">
          <span class="kpi-label">Em Aberto (R$)</span>
          <span class="kpi-value">{{ formatarValor(valorEstimadoAberto) }}</span>
        </div>

        <div class="kpi-card green">
          <span class="kpi-label">Conversão</span>
          <span class="kpi-value">{{ taxaFechamento }}%</span>
        </div>

        <div class="kpi-card purple">
          <span class="kpi-label">Probabilidade</span>
          <span class="kpi-value">{{ probabilidadeMedia }}%</span>
        </div>
      </div>

      <div class="toolbar-row">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="filtro.search" 
            placeholder="Buscar oportunidade..." 
            @input="debouncedFetchOportunidades"
          >
        </div>

        <div class="filters-box">
          <div class="custom-select">
            <select v-model="filtro.responsavel" @change="fetchOportunidades">
              <option value="">Todos os Corretores</option>
              <option v-for="resp in corretores" :key="resp.id" :value="resp.id">
                {{ resp.first_name }}
              </option>
            </select>
            <i class="fas fa-chevron-down"></i>
          </div>

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
    </header>

    <main class="kanban-main-wrapper">
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando funil...</p>
      </div>

      <div v-else class="kanban-scroll-viewport">
        
        <div class="kanban-board" :class="{ 'collapsed-mode': cardsRecolhidos }">
          
          <div v-for="fase in funilFases" :key="fase.id" class="kanban-column">
            
            <div class="column-header" :style="{ borderTopColor: fasesDeFunilCores[fase.id] }">
              <div class="header-content">
                <span class="column-title" :title="fase.titulo">{{ fase.titulo }}</span>
                <span class="column-count">{{ funilData[fase.id]?.length || 0 }}</span>
              </div>
              <div class="column-total" v-if="cardsRecolhidos">
                {{ formatarValorCompacto(somarValorFase(fase.id)) }}
              </div>
            </div>

            <div class="column-body" v-show="!cardsRecolhidos">
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
                    <div class="card-border" :style="{ backgroundColor: fasesDeFunilCores[fase.id] }"></div>
                    <div class="card-content">
                      <h4 class="card-title">{{ op.titulo }}</h4>
                      <div class="card-meta">
                        <div class="meta-row" v-if="op.cliente">
                          <i class="far fa-user"></i> <span>{{ op.cliente.nome_completo.split(' ')[0] }}</span>
                        </div>
                        <div class="meta-row" v-if="op.imovel">
                          <i class="far fa-building"></i> <span>Ref. {{ op.imovel.id }}</span>
                        </div>
                      </div>
                      <div class="card-footer">
                        <span class="card-price">{{ formatarValor(op.valor_estimado) }}</span>
                        <div class="card-avatar" :title="op.responsavel?.first_name">
                          {{ op.responsavel?.first_name?.charAt(0).toUpperCase() || '?' }}
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </draggable>
            </div>

            <div class="column-placeholder" v-if="cardsRecolhidos"></div>

          </div>

        </div>
      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import draggable from 'vuedraggable';
import { debounce } from 'lodash'; 
import '@fortawesome/fontawesome-free/css/all.css';

const router = useRouter();

// --- ESTADO ---
const oportunidades = ref<any[]>([]);
const funilData = ref<{ [key: string]: any[] }>({});
const isLoading = ref(true);
const corretores = ref<any[]>([]);
const cardsRecolhidos = ref(false);
const valorEstimadoAberto = ref(0);

const funilFases = ref([
  { id: 'LEAD', titulo: 'Lead' }, 
  { id: 'CONTATO', titulo: 'Contato' },
  { id: 'VISITA', titulo: 'Visita' },
  { id: 'PROPOSTA', titulo: 'Proposta' },
  { id: 'NEGOCIACAO', titulo: 'Negociação' },
  { id: 'GANHO', titulo: 'Ganho' },
  { id: 'PERDIDO', titulo: 'Perdido' }
]);

const fasesDeFunilCores: { [key: string]: string } = { 
  'LEAD': '#3b82f6', 
  'CONTATO': '#06b6d4', 
  'VISITA': '#eab308', 
  'PROPOSTA': '#f97316', 
  'NEGOCIACAO': '#8b5cf6', 
  'GANHO': '#22c55e', 
  'PERDIDO': '#64748b' 
};

const filtro = ref({
  search: '',
  responsavel: ''
});

// --- COMPUTADOS ---
const totalAtivas = computed(() => {
  return oportunidades.value.filter(op => op.fase !== 'GANHO' && op.fase !== 'PERDIDO').length;
});

const taxaFechamento = computed(() => {
  const ganhos = funilData.value['GANHO']?.length || 0;
  const perdidos = funilData.value['PERDIDO']?.length || 0;
  const total = ganhos + perdidos;
  if (total === 0) return '0.0';
  return ((ganhos / total) * 100).toFixed(1);
});

const probabilidadeMedia = computed(() => {
  if (oportunidades.value.length === 0) return '0.0';
  const total = oportunidades.value.reduce((sum, op) => sum + (op.probabilidade || 0), 0);
  return (total / oportunidades.value.length).toFixed(1);
});

// --- ACTIONS ---
const onFaseChange = async (event: any, novaFaseId: string) => {
    if (event.added) {
        const oportunidadeId = event.added.element.id;
        try {
            await api.patch(`/v1/clientes/oportunidades/${oportunidadeId}/`, { fase: novaFaseId }); 
            const idx = oportunidades.value.findIndex(op => op.id === oportunidadeId);
            if(idx !== -1) oportunidades.value[idx].fase = novaFaseId; 
            fetchValorEstimadoAberto(); 
        } catch (error) {
            console.error('Erro ao mover:', error);
            fetchOportunidades(); 
        }
    }
};

async function fetchValorEstimadoAberto() {
    try {
        const res = await api.get('/v1/relatorios/', { params: { tipo: 'valor_estimado_aberto' } }); 
        valorEstimadoAberto.value = res.data.valor_total_aberto || 0;
    } catch (err) { console.error(err); }
}

async function fetchOportunidades() {
  isLoading.value = true;
  try {
    const params = {
        search: filtro.value.search || undefined,
        responsavel: filtro.value.responsavel || undefined,
    };
    const response = await api.get('/v1/clientes/oportunidades/', { params }); 
    oportunidades.value = response.data;

    const map = new Map();
    oportunidades.value.forEach(op => {
        if (op.responsavel && !map.has(op.responsavel.id)) map.set(op.responsavel.id, op.responsavel);
    });
    corretores.value = Array.from(map.values());
    fetchValorEstimadoAberto();
  } catch (err) { console.error(err); } finally { isLoading.value = false; }
}

const debouncedFetchOportunidades = debounce(fetchOportunidades, 300);

function toggleCardsRecolhidos() { cardsRecolhidos.value = !cardsRecolhidos.value; }

function somarValorFase(faseId: string): number {
    return (funilData.value[faseId] || []).reduce((sum, op) => sum + (parseFloat(op.valor_estimado) || 0), 0);
}

watch(oportunidades, (novaLista) => {
  const groups: { [key: string]: any[] } = {};
  funilFases.value.forEach(f => groups[f.id] = []);
  novaLista.forEach(op => {
    if (groups[op.fase]) groups[op.fase].push(op);
  });
  funilData.value = groups;
}, { deep: true, immediate: true });

const formatarValor = (val: any) => {
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (!num && num !== 0) return 'R$ 0,00';
  return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
};

const formatarValorCompacto = (val: number) => {
  if (!val) return 'R$ 0';
  return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact' });
};

onMounted(fetchOportunidades);
</script>

<style scoped>
/* =========================================================
   1. LAYOUT RAÍZ - ISOLAMENTO DE SCROLL (ABSOLUTE METHOD)
   ========================================================= */
.funil-view-root {
  /* Altura da tela menos header/padding do layout principal */
  height: calc(100vh - 120px); 
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden; 
  gap: 1rem;
}

/* =========================================================
   2. HEADER & TOOLBAR (FIXO)
   ========================================================= */
.view-header-section {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header-row { display: flex; justify-content: space-between; align-items: flex-end; }
.title-group h1 { font-size: 1.5rem; font-weight: 700; color: #1e293b; margin: 0; }
.subtitle { font-size: 0.875rem; color: #64748b; margin: 0.25rem 0 0 0; }

.actions-group { display: flex; gap: 0.5rem; }
.btn-primary {
  background: #2563eb; color: white; border: none; padding: 0.6rem 1.2rem;
  border-radius: 8px; font-weight: 600; font-size: 0.9rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; text-decoration: none;
  transition: background 0.2s; white-space: nowrap;
}
.btn-primary:hover { background: #1d4ed8; }
.btn-secondary {
  background: white; border: 1px solid #e2e8f0; color: #64748b;
  width: 40px; height: 40px; border-radius: 8px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.btn-secondary:hover { background: #f8fafc; color: #2563eb; border-color: #cbd5e1; }

/* KPIs Grid - 4 COLUNAS */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }

.kpi-card {
  background: white; border-radius: 10px; padding: 0.8rem 1rem;
  border: 1px solid #e2e8f0; display: flex; flex-direction: column;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #64748b; margin-bottom: 2px; }
.kpi-value { font-size: 1.25rem; font-weight: 700; color: #0f172a; letter-spacing: -0.02em; }

/* Cores dos KPIs */
.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.green .kpi-value { color: #16a34a; }
.kpi-card.purple .kpi-value { color: #9333ea; }
.kpi-card.orange .kpi-value { color: #f97316; }

/* Toolbar */
.toolbar-row {
  background: white; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 0.6rem; display: flex; gap: 1rem; align-items: center;
}
.search-box { position: relative; flex: 1; min-width: 200px; }
.search-box i { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.search-box input {
  width: 100%; padding: 0.5rem 1rem 0.5rem 2.5rem; border: 1px solid #cbd5e1;
  border-radius: 6px; font-size: 0.9rem; outline: none; box-sizing: border-box;
}
.search-box input:focus { border-color: #2563eb; }

.filters-box { display: flex; gap: 0.5rem; align-items: center; }
.custom-select { position: relative; }
.custom-select select {
  appearance: none; background: white; border: 1px solid #cbd5e1;
  padding: 0.5rem 2rem 0.5rem 1rem; border-radius: 6px; font-size: 0.85rem;
  color: #334155; cursor: pointer; min-width: 160px;
}
.custom-select i { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; font-size: 0.8rem; }

.btn-toggle {
  display: flex; align-items: center; gap: 0.5rem; background: #f1f5f9;
  border: 1px solid #cbd5e1; color: #475569; padding: 0.5rem 1rem;
  border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 0.85rem; white-space: nowrap;
}
.btn-toggle:hover { background: #e2e8f0; color: #1e293b; }

/* =========================================================
   3. KANBAN MAIN WRAPPER (CORREÇÃO DE OVERFLOW)
   ========================================================= */
.kanban-main-wrapper {
  flex: 1;
  position: relative; 
  width: 100%;
  min-height: 0;
  overflow: hidden; 
  background-color: transparent;
}

/* =========================================================
   4. SCROLL VIEWPORT (ABSOLUTE POSITIONING)
   ========================================================= */
.kanban-scroll-viewport {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-x: auto; 
  overflow-y: hidden; 
  display: flex;
  align-items: stretch;
  padding-bottom: 8px;
  
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.kanban-scroll-viewport::-webkit-scrollbar { height: 10px; background-color: #f1f5f9; }
.kanban-scroll-viewport::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 6px; border: 2px solid #f1f5f9; }
.kanban-scroll-viewport::-webkit-scrollbar-thumb:hover { background-color: #94a3b8; }

/* =========================================================
   5. BOARD & COLUNAS
   ========================================================= */
.kanban-board {
  display: flex;
  gap: 16px;
  height: 100%;
  width: max-content; 
  min-width: 100%;    
  padding-right: 16px;
}

.kanban-board.collapsed-mode {
  width: 100%;
  padding-right: 0;
}

.kanban-column {
  display: flex;
  flex-direction: column;
  background-color: #f1f5f9;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  height: 100%;
  flex-shrink: 0;
  width: 290px;
}

.kanban-board.collapsed-mode .kanban-column {
  flex: 1; 
  min-width: 0;
  width: auto;
}

/* Header */
.column-header {
  padding: 0.8rem;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  border-radius: 12px 12px 0 0;
  border-top: 4px solid transparent;
  display: flex; justify-content: space-between; align-items: center;
  flex-shrink: 0;
  height: 54px;
  box-sizing: border-box;
}
.column-title { 
  font-weight: 700; font-size: 0.8rem; color: #334155; text-transform: uppercase; 
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
}
.column-count { 
  background: #f1f5f9; color: #64748b; font-size: 0.75rem; 
  padding: 2px 8px; border-radius: 99px; font-weight: 600; 
}
.column-total { font-size: 0.75rem; font-weight: 600; color: #059669; white-space: nowrap; }

/* Body com Scroll Vertical */
.column-body {
  flex: 1; 
  overflow-y: auto; 
  overflow-x: hidden;
  padding: 0.8rem;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}
.column-body::-webkit-scrollbar { width: 6px; }
.column-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.column-body::-webkit-scrollbar-track { background: transparent; }

/* Cards */
.draggable-area { min-height: 100%; display: flex; flex-direction: column; gap: 0.8rem; }
.sortable-ghost { opacity: 0.4; background: #e2e8f0; border: 2px dashed #94a3b8; }
.sortable-drag { transform: rotate(2deg); cursor: grabbing; }

.kanban-card {
  background: white; border: 1px solid #e2e8f0; border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: grab; 
  position: relative; overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kanban-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.06); border-color: #cbd5e1; }

.card-border { position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }
.card-content { padding: 0.8rem 0.8rem 0.8rem 1.2rem; }

.card-title {
  font-size: 0.9rem; font-weight: 600; color: #1e293b; margin: 0 0 0.5rem 0;
  line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}

.card-meta { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 0.8rem; }
.meta-row { display: flex; align-items: center; gap: 0.5rem; color: #64748b; font-size: 0.75rem; }
.meta-row i { font-size: 0.8rem; width: 14px; text-align: center; color: #94a3b8; }
.meta-row span { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.card-footer {
  border-top: 1px solid #f1f5f9; padding-top: 0.6rem; display: flex; justify-content: space-between; align-items: center;
}
.card-price { 
  font-size: 0.8rem; font-weight: 700; color: #059669; 
  background: #dcfce7; padding: 3px 8px; border-radius: 4px; 
}
.card-avatar {
  width: 24px; height: 24px; border-radius: 50%; background: #e2e8f0;
  color: #64748b; font-size: 0.7rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid white; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.loading-state { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; }
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* Mobile Adaptations */
@media (max-width: 1200px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 1024px) {
  .header-row { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-group { width: 100%; justify-content: space-between; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .search-box { min-width: 100%; }
  .kpi-grid { display: none; } /* Opcional: ocultar KPIs em telas muito pequenas para dar espaço ao funil */
  
  .kanban-board.collapsed-mode { width: max-content; }
  .kanban-board.collapsed-mode .kanban-column { width: 280px; flex: none; }
  .btn-label { display: none; }
}
</style>
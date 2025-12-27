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
            <button class="btn-icon-thin" @click="toggleCardsRecolhidos" :title="cardsRecolhidos ? 'Modo Expandido' : 'Modo Resumido'">
              <i :class="cardsRecolhidos ? 'fas fa-columns' : 'fas fa-list'"></i>
            </button>

            <button class="btn-icon-thin" @click="fetchOportunidades" title="Atualizar Dados">
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
          <span class="kpi-label">Oportunidades Ativas</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-filter"></i></div>
      </div>

      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(valorEstimadoAberto) }}</span>
          <span class="kpi-label">Valor em Aberto</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-money-bill-wave"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ taxaFechamento }}%</span>
          <span class="kpi-label">Taxa de Conversão</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ probabilidadeMedia }}%</span>
          <span class="kpi-label">Probabilidade Média</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-bullseye"></i></div>
      </div>
    </div>

    <div class="toolbar-grid">
        <div class="filter-cell search-cell">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filtro.search" 
              placeholder="Buscar por título, cliente..." 
              class="form-control"
              @input="debouncedFetchOportunidades"
            >
          </div>
        </div>

        <div class="filter-cell">
          <label>Responsável</label>
          <select v-model="filtro.responsavel" @change="fetchOportunidades" class="form-control">
            <option value="">Todos os Corretores</option>
            <option v-for="resp in corretores" :key="resp.id" :value="resp.id">
              {{ resp.first_name }}
            </option>
          </select>
        </div>

        <div class="filter-cell clear-cell">
            <label>&nbsp;</label>
            <button @click="limparFiltros" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

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

            <div class="column-summary" v-if="!cardsRecolhidos">
               <span class="summary-label">Total Fase</span>
               <span class="summary-value">{{ formatarValorCompacto(somarValorFase(fase.id)) }}</span>
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

function limparFiltros() {
    filtro.value.search = '';
    filtro.value.responsavel = '';
    fetchOportunidades();
}

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
/* CONFIGURAÇÃO GERAL (PADRONIZADO) */
.page-container {
  height: calc(100vh - 60px); /* Ajuste para não gerar scroll duplo na página inteira */
  display: flex;
  flex-direction: column;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  box-sizing: border-box;
}

/* HEADER DA PÁGINA (PADRONIZADO) */
.page-header { margin-bottom: 2rem; flex-shrink: 0; }
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
    gap: 1.25rem; margin-bottom: 2rem; flex-shrink: 0;
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: all 0.2s; position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue .kpi-value, .kpi-card.blue .kpi-icon { color: #2563eb; }
.kpi-card.green .kpi-value, .kpi-card.green .kpi-icon { color: #059669; }
.kpi-card.orange .kpi-value, .kpi-card.orange .kpi-icon { color: #d97706; }
.kpi-card.purple .kpi-value, .kpi-card.purple .kpi-icon { color: #9333ea; }

/* TOOLBAR (GRID LAYOUT) */
.toolbar-grid {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb;
  padding: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  display: grid; grid-template-columns: 2fr 1fr auto; /* Layout de grade */
  gap: 1rem; align-items: end; margin-bottom: 1.5rem; flex-shrink: 0;
}

.filter-cell { display: flex; flex-direction: column; gap: 0.3rem; }
.search-cell { grid-column: span 1; } 
.clear-cell { justify-self: start; }

.filter-cell label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }

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

/* =========================================================
   KANBAN ESPECÍFICO (ADAPTADO AO CONTAINER)
   ========================================================= */
.kanban-main-wrapper {
  flex: 1; position: relative; width: 100%; min-height: 0; 
  overflow: hidden; background-color: transparent; border-radius: 8px;
}

.kanban-scroll-viewport {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  overflow-x: auto; overflow-y: hidden; 
  display: flex; align-items: stretch; padding-bottom: 8px;
  /* Estilo da barra de rolagem */
  scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent;
}

.kanban-scroll-viewport::-webkit-scrollbar { height: 8px; background-color: #f1f5f9; }
.kanban-scroll-viewport::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 4px; border: 2px solid #f1f5f9; }
.kanban-scroll-viewport::-webkit-scrollbar-thumb:hover { background-color: #94a3b8; }

.kanban-board {
  display: flex; gap: 16px; height: 100%; width: max-content; min-width: 100%; padding-right: 16px;
}
.kanban-board.collapsed-mode { width: 100%; padding-right: 0; }

.kanban-column {
  display: flex; flex-direction: column;
  background-color: #f1f5f9; border-radius: 12px; border: 1px solid #e2e8f0;
  height: 100%; flex-shrink: 0; width: 290px;
}
.kanban-board.collapsed-mode .kanban-column { flex: 1; min-width: 0; width: auto; }

/* Header da Coluna */
.column-header {
  padding: 0.8rem; background: #fff; border-bottom: 1px solid #e2e8f0;
  border-radius: 12px 12px 0 0; border-top: 4px solid transparent;
  display: flex; justify-content: space-between; align-items: center;
  flex-shrink: 0; height: 54px; box-sizing: border-box;
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

/* Corpo da Coluna */
.column-body {
  flex: 1; overflow-y: auto; overflow-x: hidden; padding: 0.8rem;
  scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent;
}
.column-body::-webkit-scrollbar { width: 6px; }
.column-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.column-body::-webkit-scrollbar-track { background: transparent; }

.column-summary {
    padding: 0.5rem 0.8rem; background-color: #f8fafc; border-top: 1px solid #e2e8f0;
    border-radius: 0 0 12px 12px; display: flex; justify-content: space-between; align-items: center;
    font-size: 0.75rem; color: #64748b;
}
.summary-value { font-weight: 700; color: #334155; }

/* Cards */
.draggable-area { min-height: 100%; display: flex; flex-direction: column; gap: 0.8rem; }
.sortable-ghost { opacity: 0.4; background: #e2e8f0; border: 2px dashed #94a3b8; }
.sortable-drag { transform: rotate(2deg); cursor: grabbing; }

.kanban-card {
  background: white; border: 1px solid #e2e8f0; border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: grab; 
  position: relative; overflow: hidden; transition: transform 0.2s, box-shadow 0.2s;
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

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-grid { grid-template-columns: 1fr; }
  .kanban-board.collapsed-mode { width: max-content; }
  .kanban-board.collapsed-mode .kanban-column { width: 280px; flex: none; }
}
</style>
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
          <span class="kpi-label">Qtd. Ativas</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-filter"></i></div>
      </div>

      <div class="kpi-card blue">
        <div class="kpi-content">
          <span class="kpi-value">{{ formatarValor(valorEstimadoAberto) }}</span>
          <span class="kpi-label">Em Aberto (R$)</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-dollar-sign"></i></div>
      </div>

      <div class="kpi-card green">
        <div class="kpi-content">
          <span class="kpi-value">{{ taxaFechamento }}%</span>
          <span class="kpi-label">Conversão</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
      </div>

      <div class="kpi-card purple">
        <div class="kpi-content">
          <span class="kpi-value">{{ probabilidadeMedia }}%</span>
          <span class="kpi-label">Probabilidade</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-percentage"></i></div>
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
          <select v-model="filtro.responsavel" @change="fetchOportunidades" class="form-control">
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
                  <div class="kanban-card standard-list-card" @click="router.push(`/oportunidades/editar/${op.id}`)" :style="{ borderTopColor: fasesDeFunilCores[fase.id] }">
                    <div class="card-header-simple">
                         <h4 class="card-title">{{ op.titulo }}</h4>
                    </div>
                   
                    <div class="card-body-simple">
                      <div class="info-group" v-if="op.cliente">
                        <span class="info-label">Cliente:</span>
                        <span class="info-value">{{ op.cliente.nome_completo }}</span>
                      </div>
                      <div class="info-group" v-if="op.imovel">
                         <span class="info-label">Imóvel:</span>
                        <span class="info-value">Ref. {{ op.imovel.id }}</span>
                      </div>
                    </div>

                    <div class="card-footer-simple">
                      <span class="card-price-simple">{{ formatarValor(op.valor_estimado) }}</span>
                      <div class="responsible-info" v-if="op.responsavel">
                        <span class="resp-name">{{ op.responsavel.first_name }}</span>
                        <div class="card-avatar small" :title="op.responsavel.first_name">
                          {{ op.responsavel.first_name?.charAt(0).toUpperCase() || '?' }}
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
   1. GERAL (PADRÃO CLIENTES VIEW)
   ========================================================= */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  display: flex;
  flex-direction: column;
}

/* =========================================================
   2. HEADER & BREADCRUMB
   ========================================================= */
.page-header {
  margin-bottom: 2rem;
}

.title-area { display: flex; flex-direction: column; gap: 6px; }
.title-area h1 {
  font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em;
}

.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;
}
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.header-main {
  display: flex; justify-content: space-between; align-items: flex-end;
}

.actions-area { display: flex; gap: 0.75rem; }

/* Botões Estilo Fino */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
  text-decoration: none;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15);
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* =========================================================
   3. KPIS (ESTILO CLIENTES)
   ========================================================= */
.kpi-grid { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 1.25rem; margin-bottom: 2rem; 
}

.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: default; 
  position: relative; overflow: hidden; transition: all 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { 
    font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; 
}

/* Cores KPI */
.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.green .kpi-value { color: #059669; }
.kpi-card.purple .kpi-value { color: #9333ea; }
.kpi-card.orange .kpi-value { color: #d97706; }

/* =========================================================
   4. TOOLBAR (ESTILO CLIENTES)
   ========================================================= */
.toolbar-row {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 1rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
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

.custom-select { position: relative; }
.select-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.8rem; pointer-events: none; }
.custom-select select { appearance: none; padding-right: 2rem; }

.btn-toggle {
  height: 38px; padding: 0 1rem; border: 1px solid #cbd5e1; background: #f8fafc;
  border-radius: 6px; color: #64748b; cursor: pointer; font-size: 0.85rem; font-weight: 500;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; white-space: nowrap;
}
.btn-toggle:hover { background: #e2e8f0; color: #1e293b; border-color: #94a3b8; }

/* =========================================================
   5. KANBAN WRAPPER & SCROLL (AJUSTADO PARA CABER NA TELA)
   ========================================================= */
.kanban-main-wrapper {
  flex: 1;
  position: relative; 
  width: 100%;
  min-height: 500px;
  overflow: hidden; 
  background-color: transparent;
}

.kanban-scroll-viewport {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  overflow-x: hidden; /* Remove scroll horizontal no desktop */
  overflow-y: hidden; 
  display: flex;
  align-items: stretch;
  padding-bottom: 8px;
}

/* =========================================================
   6. BOARD & COLUNAS (FLEXÍVEIS)
   ========================================================= */
.kanban-board {
  display: flex;
  gap: 10px; /* Reduzido levemente o gap para caber melhor */
  height: 100%;
  width: 100%; /* Ocupa 100% da largura, sem overflow */
  padding-right: 0;
}

.kanban-column {
  display: flex;
  flex-direction: column;
  background-color: #f1f5f9;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  height: 100%;
  flex: 1; /* Faz as colunas dividirem o espaço igualmente */
  min-width: 0; /* Permite que encolham abaixo do conteúdo se necessário */
  width: auto; /* Remove largura fixa */
}

/* Header Coluna */
.column-header {
  padding: 0.8rem 0.5rem; /* Padding lateral reduzido */
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  border-radius: 12px 12px 0 0;
  border-top: 4px solid transparent;
  display: flex; justify-content: space-between; align-items: center;
  flex-shrink: 0;
  height: 54px;
  box-sizing: border-box;
}
.header-content {
  display: flex; align-items: center; gap: 6px; overflow: hidden;
}
.column-title { 
  font-weight: 700; font-size: 0.75rem; color: #334155; text-transform: uppercase; 
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
}
.column-count { 
  background: #f1f5f9; color: #64748b; font-size: 0.7rem; 
  padding: 1px 6px; border-radius: 99px; font-weight: 600; 
}
.column-total { font-size: 0.7rem; font-weight: 600; color: #059669; white-space: nowrap; }

/* Body com Scroll Vertical */
.column-body {
  flex: 1; 
  overflow-y: auto; 
  overflow-x: hidden;
  padding: 0.5rem; /* Padding interno reduzido para economizar espaço */
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}
.column-body::-webkit-scrollbar { width: 4px; }
.column-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
.column-body::-webkit-scrollbar-track { background: transparent; }

/* Cards */
.draggable-area { min-height: 100%; display: flex; flex-direction: column; gap: 0.6rem; }
.sortable-ghost { opacity: 0.4; background: #e2e8f0; border: 2px dashed #94a3b8; }
.sortable-drag { transform: rotate(2deg); cursor: grabbing; }

/* --- ESTILOS DOS CARDS PADRÃO LISTA --- */
.kanban-card.standard-list-card {
  background: white; 
  border: 1px solid #e2e8f0; 
  border-top-width: 3px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
  cursor: grab; 
  padding: 0.6rem; /* Padding reduzido no card */
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.kanban-card.standard-list-card:hover { 
  transform: translateY(-1px); 
  box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
  border-color: #cbd5e1; 
}

.card-header-simple { margin-bottom: 0.1rem; }

.card-title {
  font-size: 0.85rem; font-weight: 600; color: #1e293b; margin: 0;
  line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.card-body-simple {
  display: flex; flex-direction: column; gap: 0.15rem; font-size: 0.75rem; color: #64748b;
}

.info-group {
  display: flex; align-items: center; gap: 0.3rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.info-label { font-weight: 500; color: #94a3b8; }
.info-value { color: #334155; font-weight: 500; }

.card-footer-simple {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 0.2rem; padding-top: 0.4rem; border-top: 1px solid #f1f5f9;
}

.card-price-simple { font-size: 0.8rem; font-weight: 700; color: #0f172a; }

.responsible-info { display: flex; align-items: center; gap: 0.4rem; }
.resp-name { font-size: 0.7rem; color: #64748b; max-width: 50px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.card-avatar.small {
  width: 20px; height: 20px; border-radius: 50%; background: #f1f5f9;
  color: #64748b; font-size: 0.65rem; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid #e2e8f0;
}

.loading-state { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; }
.spinner { width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* =========================================================
   RESPONSIVIDADE: MOBILE RETORNA AO SCROLL HORIZONTAL
   ========================================================= */
@media (max-width: 1200px) {
  .kanban-scroll-viewport { overflow-x: auto; } /* Reativa scroll em telas médias/pequenas */
  .kanban-board { width: max-content; gap: 16px; padding-right: 16px; }
  .kanban-column { flex: none; width: 280px; min-width: 280px; }
  
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .search-box { min-width: 100%; }
  .kpi-grid { display: none; }
}
</style>
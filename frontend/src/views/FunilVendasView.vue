<template>
  <div class="page-container">
    
    <div v-if="!isLoading" class="dashboard-grid">
      <div class="stat-card stat-total-oportunidades">
        <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
        <div class="stat-info">
            <h3>Total de Oportunidades</h3>
            <p>{{ totalOportunidades }}</p>
        </div>
      </div>
      <div class="stat-card stat-valor-aberto">
        <div class="stat-icon"><i class="fas fa-hand-holding-usd"></i></div>
        <div class="stat-info">
            <h3>Valor Estimado em Aberto</h3>
            <p>{{ formatarValor(valorEstimadoAberto) }}</p>
        </div>
      </div>
      <div class="stat-card stat-taxa-fechamento">
        <div class="stat-icon"><i class="fas fa-percent"></i></div>
        <div class="stat-info">
            <h3>Taxa de Fechamento</h3>
            <p>{{ taxaFechamento }}%</p>
        </div>
      </div>
      <div class="stat-card stat-probabilidade-media">
        <div class="stat-icon"><i class="fas fa-sync-alt"></i></div>
        <div class="stat-info">
            <h3>Probabilidade Média</h3>
            <p>{{ probabilidadeMedia }}%</p>
        </div>
      </div>
    </div>

    <div class="search-and-filter-bar">
      <input 
        type="text" 
        v-model="filtro.search" 
        placeholder="Buscar por título, cliente..." 
        class="search-input"
        @input="debouncedFetchOportunidades" 
      />
      
      <div class="filter-group">
        <label for="responsavel-filter">Corretor:</label>
        <select id="responsavel-filter" v-model="filtro.responsavel" @change="fetchOportunidades">
          <option value="">Todos</option>
          <option v-for="resp in corretores" :key="resp.id" :value="resp.id">
            {{ resp.first_name }}
          </option>
        </select>
      </div>

      <button @click="limparFiltros" class="btn-mini" title="Limpar Filtros" style="margin-left: auto;">
        <i class="fas fa-eraser"></i>
      </button>

      <button 
        @click="toggleCardsRecolhidos" 
        class="btn-mini" 
        :title="cardsRecolhidos ? 'Expandir Fases' : 'Recolher Fases (Resumo)'"
      >
        <i :class="cardsRecolhidos ? 'fas fa-border-all' : 'fas fa-minus-square'"></i> 
      </button>

      <router-link to="/oportunidades/nova" class="btn-add">
        <i class="fas fa-plus"></i> <span class="mobile-hide">Nova Oportunidade</span>
      </router-link>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      A carregar funil de vendas...
    </div>

    <div v-else class="funil-board-container" :class="{ 'layout-resumo': cardsRecolhidos }">
      <div v-for="fase in funilFases" :key="fase.id" class="funil-coluna">
        
        <div class="coluna-header">
          <div class="header-left">
             <h3 class="coluna-titulo">{{ fase.titulo }}</h3>
             <span v-if="cardsRecolhidos" class="fase-total-valor">
                {{ formatarValorCompacto(somarValorFase(fase.id)) }}
             </span>
          </div>
          <span class="badge" :style="{ backgroundColor: fasesDeFunilCores[fase.id] || '#6c757d' }">
            {{ funilData[fase.id]?.length || 0 }}
          </span>
        </div>
        
        <div v-show="!cardsRecolhidos" class="coluna-body">
          <draggable
            v-model="funilData[fase.id]"
            :group="{ name: 'oportunidades' }"
            @change="onFaseChange($event, fase.id)"
            item-key="id"
            class="oportunidade-list"
          >
            <template #item="{ element: oportunidade }">
              <transition-group name="oportunidade-list-fade" tag="div">
                <router-link :to="`/oportunidades/editar/${oportunidade.id}`" class="oportunidade-card-link">
                  
                  <div class="oportunidade-card">
                    <h4 class="card-titulo" :title="oportunidade.titulo">{{ oportunidade.titulo }}</h4>
                    
                    <div class="card-details">
                        <p class="card-text card-cliente" :title="oportunidade.cliente?.nome_completo">
                            <i class="fas fa-user-circle"></i> {{ oportunidade.cliente?.nome_completo || '—' }}
                        </p>
                        <p class="card-text card-imovel" :title="oportunidade.imovel?.endereco">
                            <i class="fas fa-map-marker-alt"></i> {{ oportunidade.imovel?.endereco || '—' }}
                        </p>
                    </div>

                    <div class="card-footer">
                      <span class="card-valor">{{ formatarValor(oportunidade.valor_estimado) }}</span>
                      <div class="card-responsavel">
                        <span class="responsavel-avatar" :title="oportunidade.responsavel?.first_name">
                            {{ oportunidade.responsavel?.first_name?.charAt(0).toUpperCase() || '?' }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                </router-link>
              </transition-group>
            </template>
          </draggable>
        </div>
        
        <div v-if="cardsRecolhidos" class="coluna-body-placeholder"></div>

      </div>
    </div>

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

// --- DADOS E ESTADO ---
const oportunidades = ref<any[]>([]);
const funilData = ref<{ [key: string]: any[] }>({});
const isLoading = ref(true);
const error = ref<string | null>(null);
const corretores = ref<any[]>([]);
const cardsRecolhidos = ref(false);

const valorEstimadoAberto = ref(0);

// Definição FIXA das fases
const funilFases = ref([
  { id: 'LEAD', titulo: 'Lead' }, 
  { id: 'CONTATO', titulo: 'Contato' },
  { id: 'VISITA', titulo: 'Visita' },
  { id: 'PROPOSTA', titulo: 'Proposta' },
  { id: 'NEGOCIACAO', titulo: 'Negoc.' },
  { id: 'GANHO', titulo: 'Ganho' },
  { id: 'PERDIDO', titulo: 'Perdido' }
]);

const fasesDeFunilCores: { [key: string]: string } = { 
  'LEAD': '#4DA3FF',
  'CONTATO': '#00C8A0',
  'VISITA': '#FFD93D',
  'PROPOSTA': '#FFB347',
  'NEGOCIACAO': '#FF8C42',
  'GANHO': '#4CAF50',
  'PERDIDO': '#B0B0B0'
};

const filtro = ref({
  search: '',
  responsavel: ''
});

// --- COMPUTADOS ---

const oportunidadesFiltradas = computed(() => oportunidades.value);

const totalOportunidades = computed(() => oportunidades.value.length);

const taxaFechamento = computed(() => {
  const negociosGanhos = funilData.value['GANHO']?.length || 0;
  const negociosPerdidos = funilData.value['PERDIDO']?.length || 0;
  const totalFechados = negociosGanhos + negociosPerdidos;
  if (totalFechados === 0) return '0.00';
  return ((negociosGanhos / totalFechados) * 100).toFixed(2);
});

const probabilidadeMedia = computed(() => {
  if (oportunidades.value.length === 0) return '0.00';
  const totalProbabilidade = oportunidades.value.reduce((sum, op) => sum + (op.probabilidade || 0), 0);
  return (totalProbabilidade / oportunidades.value.length).toFixed(2);
});

// --- MÉTODOS DE DADOS ---

const onFaseChange = async (event: any, novaFaseId: string) => {
    if (event.added) {
        const oportunidadeId = event.added.element.id;
        try {
            await api.patch(`/v1/clientes/oportunidades/${oportunidadeId}/`, { fase: novaFaseId }); 
            
            const index = oportunidades.value.findIndex(op => op.id === oportunidadeId);
            if(index !== -1) {
                oportunidades.value[index].fase = novaFaseId; 
            }
            fetchValorEstimadoAberto(); // Atualiza o valor estimado após a mudança de fase
        } catch (error) {
            console.error('Erro ao mover a oportunidade:', error);
            fetchOportunidades(); 
        }
    }
};

async function fetchValorEstimadoAberto() {
    try {
        const response = await api.get('/v1/relatorios/', { 
            params: { tipo: 'valor_estimado_aberto' }
        }); 
        valorEstimadoAberto.value = response.data.valor_total_aberto || 0;
    } catch (err) {
        console.error("Erro ao buscar valor estimado aberto:", err);
    }
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

    const responsaveisMap = new Map();
    oportunidades.value.forEach(op => {
        if (op.responsavel && !responsaveisMap.has(op.responsavel.id)) {
            responsaveisMap.set(op.responsavel.id, op.responsavel);
        }
    });
    corretores.value = Array.from(responsaveisMap.values());

    fetchValorEstimadoAberto();

  } catch (err) {
    console.error("Erro ao buscar oportunidades:", err);
    error.value = "Não foi possível carregar o funil.";
  } finally {
    isLoading.value = false;
  }
}

const debouncedFetchOportunidades = debounce(fetchOportunidades, 300);

// --- MÉTODOS DE UI E FORMATAÇÃO ---

function toggleCardsRecolhidos() {
    cardsRecolhidos.value = !cardsRecolhidos.value;
}

function somarValorFase(faseId: string): number {
    const items = funilData.value[faseId] || [];
    return items.reduce((sum, op) => sum + (parseFloat(op.valor_estimado) || 0), 0);
}

watch(oportunidadesFiltradas, (novaLista) => {
  const agrupado: { [key: string]: any[] } = {};
  
  funilFases.value.forEach(fase => {
    agrupado[fase.id] = []; 
  });

  novaLista.forEach(oportunidade => {
    const faseId = oportunidade.fase; 
    if (agrupado[faseId]) {
        agrupado[faseId].push(oportunidade);
    }
  });
  
  funilData.value = agrupado;
}, { immediate: true });

function formatarValor(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined) return 'R$ -';
    const num = typeof valor === 'string' ? parseFloat(valor) : valor;
    if (isNaN(num)) return 'R$ -'; 
    return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2 });
}

function formatarValorCompacto(valor: number): string {
    if (!valor) return '';
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact' });
}

function limparFiltros() {
  filtro.value.search = '';
  filtro.value.responsavel = '';
  fetchOportunidades();
}

onMounted(() => {
  fetchOportunidades();
});
</script>

<style scoped>
/* ================================================== */
/* 1. Layout Geral (Ajuste para Dashboard Layout) */
/* ================================================== */
.page-container { 
    /* Padding: Top Right Bottom Left 
       - 2rem na direita para garantir que o scroll não corte o último card.
       - 0 na esquerda para remover o espaço em branco solicitado.
    */
    padding: 0 2rem 0 0; 
    display: flex; 
    flex-direction: column; 
    /* Cálculo exato para ocupar a tela sem scroll duplo */
    height: calc(100vh - 140px); 
    width: 100%; 
    max-width: 100%; /* Permite ocupar toda a largura */
    margin: 0;       /* Remove a centralização (margin auto) */
    overflow: hidden; 
    box-sizing: border-box;
}

/* ================================================== */
/* 2. Dashboard Stats */
/* ================================================== */
.dashboard-grid {
  display: grid; 
  grid-template-columns: repeat(4, 1fr); 
  gap: 1.25rem; margin-bottom: 1.5rem; padding: 0 0.5rem;
  flex-shrink: 0; 
}
.stat-card {
  background-color: #ffffff; 
  border: none; border-radius: 12px; padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04); display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover { 
  transform: translateY(-3px); 
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}
.stat-icon {
    width: 50px; height: 50px; border-radius: 12px; 
    display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
    background-color: #e0e0e0; 
    color: #424242;
}

.stat-info h3 { 
  font-size: 0.8rem; color: #616161; 
  font-weight: 600; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;
}
.stat-info p { 
  font-size: 1.55rem; font-weight: 700; color: #212121; 
  margin: 0; line-height: 1.2;
}

/* --- Cores Sóbrias --- */
.stat-total-oportunidades .stat-icon { background-color: #E0F7FA; color: #00BCD4; } 
.stat-total-oportunidades .stat-info p { color: #00838F; } 

.stat-valor-aberto .stat-icon { background-color: #FFF8E1; color: #FFB300; } 
.stat-valor-aberto .stat-info p { color: #FF6F00; } 

.stat-taxa-fechamento .stat-icon { background-color: #E8F5E9; color: #4CAF50; }
.stat-taxa-fechamento .stat-info p { color: #388E3C; } 

.stat-probabilidade-media .stat-icon { background-color: #F3E5F5; color: #9C27B0; }
.stat-probabilidade-media .stat-info p { color: #6A1B9A; } 


@media (max-width: 1200px) {
  .dashboard-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
  /* Remove padding lateral em telas muito pequenas para aproveitar espaço */
  .page-container { padding: 0 1rem; }
}

/* ================================================== */
/* 3. Filtros */
/* ================================================== */
.search-and-filter-bar {
  display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;
  align-items: center; background-color: transparent; padding: 0 0.5rem; box-shadow: none;
  flex-shrink: 0;
}
.search-input {
  padding: 10px; border: 1px solid #ccc; border-radius: 5px; width: 100%; max-width: 350px; box-sizing: border-box; font-family: system-ui, sans-serif;
}
.filter-group { display: flex; align-items: center; gap: 0.5rem; }
.filter-group label { font-weight: 500; color: #555; white-space: nowrap; }
.filter-group select {
  padding: 8px 12px; border: 1px solid #ccc; border-radius: 5px; font-size: 0.95rem;
  background-color: #f8f9fa; min-width: 120px; font-family: system-ui, sans-serif;
}
.btn-add {
  background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 5px;
  cursor: pointer; font-weight: bold; transition: background-color 0.3s ease; font-size: 0.95rem;
  display: flex; align-items: center; gap: 0.5rem; margin-left: 1rem; width: auto; text-decoration: none;
  font-family: system-ui, sans-serif;
}
.btn-add:hover { background-color: #0056b3; }

.btn-mini {
    width: 32px; height: 32px; border-radius: 6px; border: 1px solid transparent; background: transparent;
    color: #9ca3af; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s;
}
.btn-mini:hover { background-color: #f3f4f6; color: #374151; }
.mobile-hide { display: inline; }

/* ================================================== */
/* 4. Kanban Board (CORREÇÃO DE SCROLL) */
/* ================================================== */
.loading-message { text-align: center; padding: 2rem; color: #6c757d; font-size: 0.9rem; }
.spinner {
  border: 3px solid #e9ecef; border-top: 3px solid #0d6efd; border-radius: 50%;
  width: 30px; height: 30px; animation: spin 0.8s linear infinite; margin: 0 auto 0.5rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.funil-board-container {
  display: flex; 
  gap: 0.5rem; 
  /* Padding extra na direita para garantir espaço no final do scroll */
  padding: 0 0.5rem 0.5rem 0.5rem;
  width: 100%;
  flex-grow: 1;
  overflow-x: auto; 
  overflow-y: hidden;
  align-items: stretch; 
}

/* Espaçador no final do flex container para garantir margem direita ao rolar */
.funil-board-container::after {
    content: "";
    display: block;
    min-width: 0.5rem; /* Garante um espaço extra no fim do scroll */
    height: 1px;
}

/* Custom Scrollbar */
.funil-board-container::-webkit-scrollbar {
    height: 8px;
}
.funil-board-container::-webkit-scrollbar-thumb {
    background-color: #ccc;
    border-radius: 4px;
}
.funil-board-container::-webkit-scrollbar-track {
    background-color: #f1f1f1;
}

.funil-coluna {
  background-color: #e9ecef; border-radius: 6px;
  flex: 0 0 auto; 
  min-width: 260px; 
  width: 260px; 
  display: flex; flex-direction: column; 
  height: 100%;
  border: 1px solid #dee2e6;
  transition: width 0.3s ease, min-width 0.3s ease;
}

.funil-board-container.layout-resumo .funil-coluna {
    height: auto; 
    min-height: 50px;
    min-width: 100px;
    width: 100px;
    flex: 1; 
}

.coluna-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.4rem 0.5rem; border-bottom: 1px solid #ced4da;
  background-color: #f8f9fa; border-top-left-radius: 6px; border-top-right-radius: 6px;
  min-height: 36px;
}
.coluna-titulo {
  font-size: 0.8rem; font-weight: 700; color: #495057; margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.fase-total-valor {
    font-size: 0.7rem; color: #198754; font-weight: 600; margin-left: 0.5rem;
}
.header-left {
    display: flex; align-items: center; overflow: hidden;
}
.badge {
  color: white; border-radius: 8px; padding: 1px 6px;
  font-size: 0.65rem; font-weight: bold; min-width: 18px; text-align: center; margin-left: 4px; flex-shrink: 0;
}

.coluna-body { 
    padding: 0.3rem; 
    overflow-y: auto; 
    flex-grow: 1;
    scrollbar-width: thin;
    scrollbar-color: #ced4da transparent;
}
.coluna-body::-webkit-scrollbar { width: 6px; }
.coluna-body::-webkit-scrollbar-thumb { background-color: #ced4da; border-radius: 3px; }

.oportunidade-list { min-height: 50px; height: 100%; }

/* ================================================== */
/* 5. Cards de Oportunidade */
/* ================================================== */
.oportunidade-card-link { text-decoration: none; color: inherit; display: block; margin-bottom: 0.3rem; }
.oportunidade-card {
  background-color: white; border-radius: 4px; padding: 0.4rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08); cursor: grab;
  transition: all 0.1s ease; border-left: 3px solid transparent;
  overflow: hidden; display: flex; flex-direction: column;
}
.oportunidade-card:hover {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.12); transform: translateY(-1px); border-left-color: #007bff;
}

.card-titulo { 
    font-size: 0.8rem; font-weight: 600; color: #343a40; margin: 0 0 0.2rem 0; line-height: 1.2; 
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.card-details { margin-bottom: 0.3rem; }
.card-text {
  font-size: 0.65rem; color: #6c757d; margin: 0 0 1px 0; line-height: 1.1;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 3px;
}
.card-text i { font-size: 0.6rem; width: 10px; text-align: center; }

.card-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 0.2rem; border-top: 1px solid #f1f3f5; padding-top: 0.2rem;
}
.card-valor { font-size: 0.7rem; font-weight: 700; color: #198754; }
.responsavel-avatar {
  width: 18px; height: 18px; border-radius: 50%; background-color: #6c757d; color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 0.55rem; text-transform: uppercase;
}

@media (max-width: 768px) {
  .search-and-filter-bar { flex-direction: column; align-items: stretch; }
  .search-input { max-width: 100%; }
  .filter-group { flex-direction: column; align-items: stretch; }
  .btn-add { margin-left: 0; justify-content: center; }
  
  .page-container { height: calc(100vh - 100px); }
}
</style>
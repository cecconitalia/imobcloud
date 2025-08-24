<template>
  <div class="funil-view-container">
    <header class="funil-header">
      <h1 class="page-title">Funil de Vendas</h1>
      <router-link to="/oportunidades/nova" class="btn-novo-funil">
        <i class="fas fa-plus"></i> Nova Oportunidade
      </router-link>
    </header>

    <div class="filter-controls">
      <div class="filter-group">
        <label for="search-input">Pesquisar:</label>
        <input 
          id="search-input" 
          v-model="filtro.search" 
          type="text" 
          placeholder="Título, cliente ou endereço"
          class="filter-input"
        />
      </div>
      <div class="filter-group">
        <label for="responsavel-filter">Corretor:</label>
        <select 
          id="responsavel-filter" 
          v-model="filtro.responsavel"
          class="filter-input"
        >
          <option value="">Todos</option>
          <option v-for="resp in corretores" :key="resp.id" :value="resp.id">
            {{ resp.first_name }}
          </option>
        </select>
      </div>
      <button @click="limparFiltros" class="btn-limpar-filtros">Limpar Filtros</button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>A carregar funil de vendas...</p>
    </div>

    <div v-else class="funil-board-container">
      <div v-for="fase in funilFases" :key="fase.id" class="funil-coluna">
        <div class="coluna-header">
          <h3 class="coluna-titulo">{{ fase.titulo }}</h3>
          <span class="badge" :style="{ backgroundColor: fasesDeFunilCores[fase.id] }">{{ funilData[fase.id]?.length || 0 }}</span>
        </div>
        <div class="coluna-body">
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
                  <div class="oportunidade-card" :key="oportunidade.id" :class="{ 'recolhido': cardsRecolhidos }">
                    <h4 class="card-titulo">{{ oportunidade.titulo }}</h4>
                    <p class="card-cliente" v-if="!cardsRecolhidos">{{ oportunidade.cliente?.nome_completo }}</p>
                    <p class="card-imovel" v-if="!cardsRecolhidos">{{ oportunidade.imovel?.endereco || 'Sem Imóvel' }}</p>
                    <div class="card-footer" v-if="!cardsRecolhidos">
                      <span class="card-valor">{{ formatarValor(oportunidade.valor_estimado) }}</span>
                      <div class="card-responsavel">
                        <span class="responsavel-avatar" :title="oportunidade.responsavel?.first_name">{{ oportunidade.responsavel?.first_name?.charAt(0).toUpperCase() || '?' }}</span>
                      </div>
                    </div>
                  </div>
                </router-link>
              </transition-group>
            </template>
          </draggable>
        </div>
      </div>
    </div>
    
    <button @click="toggleCardsRecolhidos" class="btn-recolher-cards">
        {{ cardsRecolhidos ? 'Expandir Cards' : 'Recolher Cards' }}
    </button>
    
    <div v-if="!isLoading" class="funil-stats">
      <h3 class="stats-title">Estatísticas do Funil</h3>
      <div class="stats-grid">
        <div class="stats-item">
          <i class="fas fa-chart-line"></i>
          <p>Total de Oportunidades: {{ totalOportunidades }}</p>
        </div>
        <div class="stats-item">
          <i class="fas fa-dollar-sign"></i>
          <p>Valor Total Estimado: {{ formatarValor(totalValorFunil) }}</p>
        </div>
        <div class="stats-item">
          <i class="fas fa-percent"></i>
          <p>Taxa de Fechamento: {{ taxaFechamento }}%</p>
        </div>
        <div class="stats-item">
          <i class="fas fa-sync-alt"></i>
          <p>Probabilidade Média: {{ probabilidadeMedia }}%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import draggable from 'vuedraggable';
import '@fortawesome/fontawesome-free/css/all.css';

const router = useRouter();

const oportunidades = ref<any[]>([]);
const funilData = ref<{ [key: string]: any[] }>({});
const isLoading = ref(true);
const error = ref<string | null>(null);
const corretores = ref<any[]>([]);
const funilFases = ref<any[]>([]);

const cardsRecolhidos = ref(false);

const filtro = ref({
  search: '',
  responsavel: ''
});

const fasesDeFunilCores = computed(() => {
  const cores = {};
  funilFases.value.forEach(fase => {
    const titulo = fase.titulo.toUpperCase();
    if (titulo.includes('LEAD')) cores[fase.id] = '#4DA3FF';
    else if (titulo.includes('CONTATO')) cores[fase.id] = '#00C8A0';
    else if (titulo.includes('VISIT')) cores[fase.id] = '#FFD93D';
    else if (titulo.includes('PROPOSTA')) cores[fase.id] = '#FFB347';
    else if (titulo.includes('NEGOCIA')) cores[fase.id] = '#FF8C42';
    else if (titulo.includes('GANHO')) cores[fase.id] = '#4CAF50';
    else if (titulo.includes('PERDIDO')) cores[fase.id] = '#B0B0B0';
    else cores[fase.id] = '#6c757d';
  });
  return cores;
});

const oportunidadesFiltradas = computed(() => {
  let lista = oportunidades.value;

  if (filtro.value.search) {
    const termo = filtro.value.search.toLowerCase();
    lista = lista.filter(op => {
      const titulo = op.titulo?.toLowerCase().includes(termo);
      const clienteNome = op.cliente?.nome_completo?.toLowerCase().includes(termo);
      const imovelEndereco = op.imovel?.endereco?.toLowerCase().includes(termo);
      return titulo || clienteNome || imovelEndereco;
    });
  }

  if (filtro.value.responsavel) {
    lista = lista.filter(op => op.responsavel?.id === parseInt(filtro.value.responsavel));
  }

  return lista;
});

const totalOportunidades = computed(() => oportunidades.value.length);
const totalValorFunil = computed(() => {
  return oportunidades.value.reduce((sum, op) => {
    const valor = op.valor_estimado ? parseFloat(op.valor_estimado) : 0;
    return sum + valor;
  }, 0);
});
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

const onFaseChange = async (event: any, novaFaseId: string) => {
    if (event.added) {
        const oportunidadeId = event.added.element.id;
        const fase = funilFases.value.find(f => f.id === novaFaseId);
        if (!fase) return;

        try {
            await api.patch(`/v1/oportunidades/${oportunidadeId}/`, { fase: fase.id });
            console.log(`Oportunidade ${oportunidadeId} movida para ${fase.titulo}`);
            fetchOportunidades();
        } catch (error) {
            console.error('Erro ao mover a oportunidade:', error);
            fetchOportunidades();
        }
    }
};

function toggleCardsRecolhidos() {
    cardsRecolhidos.value = !cardsRecolhidos.value;
}

watch(oportunidadesFiltradas, (novaLista) => {
  const agrupado: { [key: string]: any[] } = {};
  funilFases.value.forEach(fase => {
    agrupado[fase.id] = [];
  });
  novaLista.forEach(oportunidade => {
    const faseEncontrada = funilFases.value.find(f => f.id === oportunidade.fase);
    if (faseEncontrada) {
        agrupado[faseEncontrada.id].push(oportunidade);
    }
  });
  funilData.value = agrupado;
}, { immediate: true });

async function fetchFunilEtapas() {
    try {
        funilFases.value = [
            { id: 'LEAD', titulo: 'Novo Lead' },
            { id: 'CONTATO', titulo: 'Primeiro Contato' },
            { id: 'VISITA', titulo: 'Visitação' },
            { id: 'PROPOSTA', titulo: 'Proposta' },
            { id: 'NEGOCIACAO', titulo: 'Fechamento' },
            { id: 'GANHO', titulo: 'Negócio Ganho' },
            { id: 'PERDIDO', titulo: 'Negócio Perdido' }
        ];
    } catch (err) {
        console.error("Erro ao buscar as etapas do funil:", err);
    }
}

async function fetchOportunidades() {
  isLoading.value = true;
  try {
    await fetchFunilEtapas();
    const response = await api.get('/v1/oportunidades/');
    oportunidades.value = response.data;
    const responsaveisUnicos = Array.from(new Set(oportunidades.value.map(op => op.responsavel?.id)))
      .filter(id => id !== undefined)
      .map(id => oportunidades.value.find(op => op.responsavel?.id === id).responsavel);
    corretores.value = responsaveisUnicos;
  } catch (err) {
    console.error("Erro ao buscar oportunidades:", err);
    error.value = "Não foi possível carregar o funil de vendas.";
  } finally {
    isLoading.value = false;
  }
}

function formatarValor(valor: number | null) {
  if (!valor) return 'R$ -';
  return parseFloat(valor.toString()).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function limparFiltros() {
  filtro.value.search = '';
  filtro.value.responsavel = '';
}

onMounted(() => {
  fetchOportunidades();
});
</script>

<style scoped>
/* Estilos gerais */
.funil-view-container {
  padding: 2rem;
  background-color: #f4f7f6;
  min-height: 100vh;
}

/* Header */
.funil-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 1rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 600;
  color: #343a40;
  margin: 0;
}

.btn-novo-funil {
  background-color: #28a745;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: bold;
  font-size: 1rem;
  transition: background-color 0.2s, transform 0.2s;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-novo-funil:hover {
  background-color: #218838;
  transform: translateY(-2px);
}

/* Controles de filtro */
.filter-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
  background-color: #fff;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.filter-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #495057;
  font-size: 0.9rem;
}

.filter-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.filter-input:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.btn-limpar-filtros {
  background-color: #6c757d;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  align-self: flex-end;
}

.btn-limpar-filtros:hover {
  background-color: #5a6268;
}

.loading-state {
  text-align: center;
  padding: 5rem;
  color: #6c757d;
}

.spinner {
  border: 4px solid rgba(0, 123, 255, 0.1);
  border-left-color: #007bff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Kanban Board Funil */
.funil-board-container {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  background-color: #f4f7f6;
  white-space: nowrap;
  flex-wrap: nowrap;
}

.funil-coluna {
  background-color: #e9ecef;
  border-radius: 8px;
  min-width: 157px;
  flex: 1; 
  padding: 0.66rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.coluna-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.66rem;
  border-bottom: 1px solid #ced4da;
  margin-bottom: 0.66rem;
}

.coluna-titulo {
  font-size: 0.968rem;
  font-weight: 600;
  color: #343a40;
  margin: 0;
  white-space: normal;
  text-overflow: ellipsis;
  overflow: hidden;
}

.badge {
  background-color: #6c757d;
  color: white;
  border-radius: 12px;
  padding: 0.176rem 0.528rem;
  font-size: 0.704rem;
  font-weight: bold;
}

.oportunidade-list {
  min-height: 100px;
  flex-grow: 1;
}

.oportunidade-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

/* Estilos do card de oportunidade */
.oportunidade-card {
  background-color: white;
  border-radius: 8px;
  padding: 0.561rem;
  margin-bottom: 0.44rem;
  box-shadow: 0 1.7px 3.4px rgba(0, 0, 0, 0.08);
  cursor: grab;
  transition: all 0.3s ease;
  border-left: 4.25px solid transparent;
  white-space: normal;
  
  /* TRANSITION para a altura */
  height: auto;
  transition: all 0.3s ease-out;
}

/* Estado recolhido */
.oportunidade-card.recolhido {
    height: 40px; /* Altura fixa para o estado recolhido */
    padding-bottom: 0;
}

/* Oculta o conteúdo interno quando o card está recolhido */
.oportunidade-card.recolhido .card-cliente,
.oportunidade-card.recolhido .card-imovel,
.oportunidade-card.recolhido .card-footer {
    display: none;
}

.oportunidade-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
  border-left-color: var(--primary-color);
}

.card-titulo {
  font-size: 0.836rem;
  font-weight: 600;
  color: #343a40;
  margin: 0 0 0.176rem 0;
  line-height: 1.2;
}

.card-cliente, .card-imovel {
  font-size: 0.748rem;
  color: #6c757d;
  margin: 0;
  line-height: 1.2;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.66rem;
  border-top: 1px solid #e9ecef;
  padding-top: 0.44rem;
}

.card-valor {
  font-size: 0.88rem;
  font-weight: bold;
  color: #28a745;
}

.card-responsavel {
  display: flex;
  align-items: center;
}

.responsavel-avatar {
  width: 21.12px;
  height: 21.12px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.6rem;
}

/* --- Estatísticas --- */
.funil-stats {
  margin-top: 2.244rem;
  background-color: #fff;
  padding: 1.496rem;
  border-radius: 8.976px;
  box-shadow: 0 3.4px 10.2px rgba(0, 0, 0, 0.05);
}

.stats-title {
  font-size: 1.122rem;
  font-weight: 600;
  color: #343a40;
  margin-top: 0;
  margin-bottom: 1.122rem;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.561rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(164.56px, 1fr));
  gap: 1.496rem;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 0.748rem;
}

.stats-item i {
  font-size: 1.867rem;
  color: #007bff;
}

.stats-item p {
  font-size: 0.748rem;
  font-weight: 500;
  color: #495057;
  margin: 0;
}

/* --- Transições --- */
.oportunidade-list-fade-move {
  transition: transform 0.5s;
}

.oportunidade-list-fade-enter-active,
.oportunidade-list-fade-leave-active {
  transition: all 0.5s ease;
}

.oportunidade-list-fade-enter-from,
.oportunidade-list-fade-leave-to {
  opacity: 0;
  transform: translateY(17px);
}

.oportunidade-list-fade-leave-active {
  position: absolute;
}

.btn-recolher-cards {
    margin-top: 1rem;
    padding: 10px 20px;
    border: none;
    background-color: #34495e;
    color: white;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.btn-recolher-cards:hover {
    background-color: #2c3e50;
}

@media (max-width: 768px) {
  .funil-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .page-title {
    font-size: 1.76rem;
  }
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-limpar-filtros {
    width: 100%;
  }
  .funil-board-container {
    flex-wrap: nowrap;
  }
}
</style>
<template>
  <div class="funil-view-container">
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

const fasesDeFunilCores: { [key: string]: string } = { // Definido como objeto diretamente
  'LEAD': '#4DA3FF',
  'CONTATO': '#00C8A0',
  'VISITA': '#FFD93D',
  'PROPOSTA': '#FFB347',
  'NEGOCIACAO': '#FF8C42',
  'GANHO': '#4CAF50',
  'PERDIDO': '#B0B0B0'
};


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
            // Ajuste a URL para o endpoint correto de oportunidades
            await api.patch(`/v1/clientes/oportunidades/${oportunidadeId}/`, { fase_funil: fase.id });
            console.log(`Oportunidade ${oportunidadeId} movida para ${fase.titulo}`);
            // Opcional: Atualizar apenas a oportunidade movida localmente em vez de refazer o fetch
            const index = oportunidades.value.findIndex(op => op.id === oportunidadeId);
            if(index !== -1) {
                oportunidades.value[index].fase = fase.id; // Ou fase_funil dependendo do nome do campo
            }
        } catch (error) {
            console.error('Erro ao mover a oportunidade:', error);
            // Reverter a mudança visual ou refazer o fetch para garantir consistência
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
    agrupado[fase.id] = []; // Inicializa com ID da fase
  });
  novaLista.forEach(oportunidade => {
    // A chave para agrupar deve ser o ID da fase da oportunidade
    const faseIdDaOportunidade = oportunidade.fase; // Ou oportunidade.fase_funil, dependendo do nome do campo
    if (agrupado[faseIdDaOportunidade]) {
        agrupado[faseIdDaOportunidade].push(oportunidade);
    } else {
        // Se a fase da oportunidade não existir no funilFases (caso raro), agrupa separadamente ou loga um aviso
        console.warn(`Fase ${faseIdDaOportunidade} da oportunidade ${oportunidade.id} não encontrada nas fases definidas.`);
        // Poderia criar um grupo 'Outros' se necessário:
        // if (!agrupado['Outros']) agrupado['Outros'] = [];
        // agrupado['Outros'].push(oportunidade);
    }
  });
  funilData.value = agrupado;
}, { immediate: true });


async function fetchFunilEtapas() {
    try {
        // Busca as fases da API
        const response = await api.get('/v1/clientes/fases-funil/');
        // Ordena as fases pela ordem definida no backend
        funilFases.value = response.data.sort((a: any, b: any) => a.ordem - b.ordem);

        // Inicializa funilData com todas as fases vazias após buscar as fases
        const agrupadoInicial: { [key: string]: any[] } = {};
        funilFases.value.forEach(fase => {
            agrupadoInicial[fase.id] = [];
        });
        funilData.value = agrupadoInicial;

    } catch (err) {
        console.error("Erro ao buscar as etapas do funil:", err);
        // Define fases padrão como fallback em caso de erro
        funilFases.value = [
             { id: 'LEAD', titulo: 'Novo Lead', ordem: 1 }, // Adiciona ordem para consistência
             { id: 'CONTATO', titulo: 'Primeiro Contato', ordem: 2 },
             { id: 'VISITA', titulo: 'Visitação', ordem: 3 },
             { id: 'PROPOSTA', titulo: 'Proposta', ordem: 4 },
             { id: 'NEGOCIACAO', titulo: 'Fechamento', ordem: 5 },
             { id: 'GANHO', titulo: 'Negócio Ganho', ordem: 6 },
             { id: 'PERDIDO', titulo: 'Negócio Perdido', ordem: 7 }
        ].sort((a,b) => a.ordem - b.ordem);
         // Inicializa funilData com fases padrão
         const agrupadoInicial: { [key: string]: any[] } = {};
         funilFases.value.forEach(fase => {
             agrupadoInicial[fase.id] = [];
         });
         funilData.value = agrupadoInicial;
    }
}


async function fetchOportunidades() {
  isLoading.value = true;
  try {
    // Primeiro busca as etapas/fases do funil
    await fetchFunilEtapas();
    // Depois busca as oportunidades
    const response = await api.get('/v1/clientes/oportunidades/'); // Endpoint ajustado
    oportunidades.value = response.data;

    // Processa a lista de corretores unicos (responsáveis)
    const responsaveisMap = new Map();
    oportunidades.value.forEach(op => {
        if (op.responsavel && !responsaveisMap.has(op.responsavel.id)) {
            responsaveisMap.set(op.responsavel.id, op.responsavel);
        }
    });
    corretores.value = Array.from(responsaveisMap.values());

    // O watch(oportunidadesFiltradas) já vai reagrupar os dados

  } catch (err) {
    console.error("Erro ao buscar oportunidades:", err);
    error.value = "Não foi possível carregar o funil de vendas.";
  } finally {
    isLoading.value = false;
  }
}

function formatarValor(valor: number | string | null | undefined): string {
    if (valor === null || valor === undefined) return 'R$ -';
    const num = typeof valor === 'string' ? parseFloat(valor) : valor;
    if (isNaN(num)) return 'R$ -'; // Retorna se não for um número válido
    return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
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
  /* padding: 2rem; */ /* Removido */
  padding: 0; /* Adicionado */
  background-color: #f4f7f6;
  min-height: 100vh;
}

/* Header Removido */
/* .funil-header { ... } */
/* .page-title { ... } */
/* .btn-novo-funil { ... } */


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
  align-self: flex-end; /* Mantém alinhado em baixo */
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
  gap: 0.5rem; /* Espaço reduzido entre colunas */
  overflow-x: auto; /* Scroll horizontal */
  padding-bottom: 0.5rem; /* Espaço para scrollbar */
  background-color: #f4f7f6; /* Fundo geral */
  white-space: nowrap; /* Impede que colunas quebrem linha */
  flex-wrap: nowrap;
}

.funil-coluna {
  background-color: #e9ecef; /* Fundo da coluna */
  border-radius: 8px;
  min-width: 250px; /* Largura mínima da coluna */
  max-width: 300px; /* Largura máxima da coluna */
  flex: 1 0 250px; /* Base 250px, não cresce, não encolhe */
  /* padding: 0.75rem; */ /* Padding removido para controle interno */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 250px); /* Altura ajustável, considere filtros/stats */
}

.coluna-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem; /* Padding do header */
  border-bottom: 1px solid #ced4da;
  /* margin-bottom: 0.75rem; */ /* Removido para colar no corpo */
  background-color: #f8f9fa; /* Fundo do header */
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.coluna-titulo {
  font-size: 1rem; /* Tamanho do título */
  font-weight: 600;
  color: #343a40;
  margin: 0;
  white-space: normal;
  text-overflow: ellipsis;
  overflow: hidden;
}

.badge {
  /* background-color: #6c757d; */ /* Cor será definida dinamicamente */
  color: white;
  border-radius: 12px;
  padding: 0.2rem 0.6rem;
  font-size: 0.8rem;
  font-weight: bold;
}

.coluna-body {
    padding: 0.75rem; /* Adicionado padding ao corpo */
    overflow-y: auto; /* Scroll vertical para a lista */
    flex-grow: 1; /* Ocupa espaço restante */
}


.oportunidade-list {
  min-height: 100px; /* Altura mínima */
  /* flex-grow: 1; */ /* Removido, o pai .coluna-body controla o crescimento */
}

.oportunidade-card-link {
  text-decoration: none;
  color: inherit;
  display: block; /* Garante que o link ocupe o espaço */
  margin-bottom: 0.5rem; /* Espaço entre os cards */
}

/* Estilos do card de oportunidade */
.oportunidade-card {
  background-color: white;
  border-radius: 8px;
  padding: 0.75rem; /* Padding interno */
  /* margin-bottom: 0.5rem; */ /* Movido para o link pai */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); /* Sombra mais suave */
  cursor: grab;
  transition: all 0.3s ease;
  border-left: 5px solid transparent; /* Borda inicial transparente */
  white-space: normal; /* Permite quebra de texto */

  /* TRANSITION para a altura */
  overflow: hidden; /* Importante para a animação de altura */
  transition: all 0.3s ease-out, height 0.3s ease-out; /* Adiciona height à transição */
}

/* Estado recolhido */
.oportunidade-card.recolhido {
    height: 45px; /* Altura fixa para o estado recolhido (ligeiramente maior) */
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    display: flex; /* Alinha o título verticalmente */
    align-items: center;
}
.oportunidade-card.recolhido .card-titulo {
    margin: 0;
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
  border-left-color: #007bff; /* Usa a cor primária no hover */
}
.oportunidade-card:active {
    cursor: grabbing;
}


.card-titulo {
  font-size: 0.9rem; /* Tamanho do título */
  font-weight: 600;
  color: #343a40;
  margin: 0 0 0.2rem 0; /* Margem inferior menor */
  line-height: 1.3; /* Espaçamento entre linhas */
}

.card-cliente, .card-imovel {
  font-size: 0.8rem; /* Tamanho do texto secundário */
  color: #6c757d;
  margin: 0 0 0.1rem 0; /* Margem inferior menor */
  line-height: 1.3;
  /* Evita quebra de texto indesejada */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem; /* Margem superior */
  border-top: 1px solid #e9ecef; /* Linha divisória */
  padding-top: 0.5rem; /* Espaço acima do rodapé */
}

.card-valor {
  font-size: 0.9rem; /* Tamanho do valor */
  font-weight: bold;
  color: #28a745; /* Verde */
}

.card-responsavel {
  display: flex;
  align-items: center;
}

.responsavel-avatar {
  width: 24px; /* Tamanho do avatar */
  height: 24px;
  border-radius: 50%;
  background-color: #007bff; /* Cor do avatar */
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.7rem; /* Tamanho da letra no avatar */
  text-transform: uppercase; /* Letra maiúscula */
}

/* --- Estatísticas --- */
.funil-stats {
  margin-top: 2rem;
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 12px; /* Aumentado */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* Sombra mais suave */
}

.stats-title {
  font-size: 1.25rem; /* Tamanho do título */
  font-weight: 600;
  color: #343a40;
  margin-top: 0;
  margin-bottom: 1.25rem; /* Margem inferior */
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 0.6rem; /* Espaço abaixo da linha */
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); /* Mínimo maior */
  gap: 1.5rem; /* Espaço entre itens */
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 0.8rem; /* Espaço entre ícone e texto */
}

.stats-item i {
  font-size: 2rem; /* Tamanho do ícone */
  color: #007bff; /* Cor do ícone */
  width: 30px; /* Garante alinhamento */
  text-align: center;
}

.stats-item p {
  font-size: 0.9rem; /* Tamanho do texto */
  font-weight: 500;
  color: #495057;
  margin: 0;
}

/* --- Transições --- */
.oportunidade-list-fade-move {
  transition: transform 0.5s ease; /* Adicionado easing */
}

.oportunidade-list-fade-enter-active,
.oportunidade-list-fade-leave-active {
  transition: all 0.4s ease; /* Duração menor */
}

.oportunidade-list-fade-enter-from,
.oportunidade-list-fade-leave-to {
  opacity: 0;
  transform: translateY(20px); /* Aumentado o deslocamento */
}

.oportunidade-list-fade-leave-active {
  position: absolute; /* Necessário para a animação de saída */
  width: calc(100% - 1.5rem); /* Ajusta a largura durante a saída */
}

.btn-recolher-cards {
    margin-top: 1rem;
    margin-left: auto; /* Alinha à direita */
    display: block; /* Garante que margin-left funcione */
    padding: 10px 20px;
    border: none;
    background-color: #34495e; /* Azul escuro */
    color: white;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
    font-size: 0.9rem;
}

.btn-recolher-cards:hover {
    background-color: #2c3e50; /* Azul mais escuro */
}

/* Scrollbars */
.funil-board-container::-webkit-scrollbar {
    height: 8px;
}
.funil-board-container::-webkit-scrollbar-track {
    background: #e9ecef;
    border-radius: 4px;
}
.funil-board-container::-webkit-scrollbar-thumb {
    background: #adb5bd;
    border-radius: 4px;
}
.funil-board-container::-webkit-scrollbar-thumb:hover {
    background: #6c757d;
}

.coluna-body::-webkit-scrollbar {
    width: 6px;
}
.coluna-body::-webkit-scrollbar-thumb {
    background: #ced4da;
    border-radius: 3px;
}
.coluna-body::-webkit-scrollbar-thumb:hover {
    background: #adb5bd;
}


@media (max-width: 768px) {
  /* Header já removido, não precisa de ajuste */
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-limpar-filtros {
    width: 100%;
    margin-top: 0.5rem; /* Adiciona espaço acima */
  }
  .funil-board-container {
     /* Garante que o scroll funcione bem no mobile */
     -webkit-overflow-scrolling: touch;
  }
   .funil-coluna {
        min-width: 220px; /* Colunas um pouco menores no mobile */
        flex-basis: 220px;
   }
   .btn-recolher-cards {
       margin-right: 1rem; /* Afasta da borda direita no mobile */
   }
}
</style>
<template>
  <div class="funil-container">
    <header class="view-header">
      <h1>Funil de Vendas</h1>
      <router-link to="/oportunidades/nova" class="btn-primary">
        + Nova Oportunidade
      </router-link>
    </header>

    <div class="filter-bar">
      <div class="filter-group">
        <label for="search-input">Pesquisar:</label>
        <input 
          id="search-input" 
          v-model="filtro.search" 
          type="text" 
          placeholder="Título, cliente ou endereço"
          class="form-control"
        />
      </div>
      
      <div class="filter-group">
        <label for="responsavel-filter">Corretor:</label>
        <select 
          id="responsavel-filter" 
          v-model="filtro.responsavel"
          class="form-control"
        >
          <option value="">Todos</option>
          <option v-for="resp in corretores" :key="resp.id" :value="resp.id">
            {{ resp.first_name }}
          </option>
        </select>
      </div>

      <button @click="limparFiltros" class="btn-secondary">Limpar Filtros</button>
    </div>

    <div v-if="isLoading" class="loading-message">
      A carregar oportunidades...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="!isLoading" class="funil-split-layout">
      <div class="funil-board-vertical-wrapper">
        <div class="funil-board-vertical">
          <div 
            v-for="(fase, index) in fasesAtivas" 
            :key="fase.id" 
            class="funil-fase-item" 
            :style="{ width: calcularLargura(index), backgroundColor: fasesDeFunilCores[fase.id] }"
          >
            <div class="fase-header">
              <h3 class="fase-titulo">
                {{ fase.titulo }} ({{ funilData[fase.id]?.length || 0 }})
              </h3>
            </div>
            
            <div v-if="isFiltroAtivo" class="oportunidades-lista">
              <div 
                v-for="oportunidade in funilData[fase.id]" 
                :key="oportunidade.id" 
                class="oportunidade-card"
                :style="{ borderLeftColor: fasesDeFunilCores[fase.id] }"
              >
                <router-link :to="`/oportunidades/editar/${oportunidade.id}`" class="oportunidade-card-link">
                  <h4 class="card-titulo">{{ oportunidade.titulo }}</h4>
                  <div class="card-footer">
                    <span class="card-valor">{{ formatarValor(oportunidade.valor_estimado) }}</span>
                    <div class="card-responsavel">
                      <span class="responsavel-avatar">{{ oportunidade.responsavel?.username.charAt(0).toUpperCase() || '?' }}</span>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <div 
          class="funil-fases-finais-container"
          :style="{ width: funilWidths[fasesAtivas.length - 1] }"
        >
          <div 
            v-for="fase in fasesFinaisVisiveis" 
            :key="fase.id" 
            class="funil-fase-item-final"
            :style="{ backgroundColor: fasesDeFunilCores[fase.id] }"
          >
            <div class="fase-header">
              <h3 class="fase-titulo">
                {{ fase.titulo }} ({{ funilData[fase.id]?.length || 0 }})
              </h3>
            </div>
            <div v-if="isFiltroAtivo" class="oportunidades-lista">
              <div v-for="oportunidade in funilData[fase.id]" :key="oportunidade.id" class="oportunidade-card-final">
                <router-link :to="`/oportunidades/editar/${oportunidade.id}`" class="oportunidade-card-link">
                  <h4 class="card-titulo">{{ oportunidade.titulo }}</h4>
                  <div class="card-footer">
                    <span class="card-valor">{{ formatarValor(oportunidade.valor_estimado) }}</span>
                    <div class="card-responsavel">
                      <span class="responsavel-avatar">{{ oportunidade.responsavel?.username.charAt(0).toUpperCase() || '?' }}</span>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="funil-stats">
        <div class="stats-card">
          <h4>Estatísticas do Funil</h4>
          <div class="stat-item">
            <span class="stat-label">Total de Oportunidades:</span>
            <span class="stat-value">{{ totalOportunidades }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Valor Total Estimado:</span>
            <span class="stat-value">{{ formatarValor(totalValorFunil) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Taxa de Conversão:</span>
            <span class="stat-value">{{ taxaConversao }}%</span>
          </div>
          <div class="stats-separator"></div>
          <div class="stat-list">
            <div v-for="(fase, index) in fasesDoFunil" :key="fase.id" class="stat-item">
              <span class="stat-label" :style="{ color: fasesDeFunilCores[fase.id] }">{{ fase.titulo }}:</span>
              <span class="stat-value">{{ funilData[fase.id]?.length || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';

const oportunidades = ref<any[]>([]);
const funilData = ref<{ [key: string]: any[] }>({});
const isLoading = ref(true);
const error = ref<string | null>(null);
const corretores = ref<any[]>([]);

const filtro = ref({
  search: '',
  responsavel: ''
});

const fasesDoFunil = ref([
  { id: 'LEAD', titulo: 'Novo Lead' },
  { id: 'CONTATO', titulo: 'Primeiro Contato' },
  { id: 'VISITA', titulo: 'Visita Agendada' },
  { id: 'PROPOSTA', titulo: 'Proposta Enviada' },
  { id: 'NEGOCIACAO', titulo: 'Em Negociação' },
  { id: 'GANHO', titulo: 'Negócio Ganho' },
  { id: 'PERDIDO', titulo: 'Negócio Perdido' },
]);

const fasesAtivas = computed(() => fasesDoFunil.value.filter(f => f.id !== 'GANHO' && f.id !== 'PERDIDO'));
const fasesFinais = computed(() => fasesDoFunil.value.filter(f => f.id === 'GANHO' || f.id === 'PERDIDO'));
const fasesFinaisVisiveis = computed(() => {
  if (isFiltroAtivo.value) {
    return fasesFinais.value;
  }
  return fasesFinais.value.filter(f => f.id === 'GANHO');
});

// Nova paleta de cores fornecida pelo utilizador
const fasesDeFunilCores: { [key: string]: string } = {
  'LEAD': '#4DA3FF',
  'CONTATO': '#00C8A0',
  'VISITA': '#FFD93D',
  'PROPOSTA': '#FFB347',
  'NEGOCIACAO': '#FF8C42',
  'GANHO': '#4CAF50',
  'PERDIDO': '#B0B0B0',
};

const isFiltroAtivo = computed(() => {
  return !!filtro.value.search || !!filtro.value.responsavel;
});

const funilWidths = computed(() => {
  const numFases = fasesAtivas.value.length;
  const initialWidth = 95;
  const minWidth = 40;
  const step = (initialWidth - minWidth) / (numFases - 1);
  const widths: string[] = [];
  for (let i = 0; i < numFases; i++) {
    widths.push(`${initialWidth - (i * step)}%`);
  }
  return widths;
});

function calcularLargura(index: number): string {
  return funilWidths.value[index];
}

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
const taxaConversao = computed(() => {
  const totalLeads = funilData.value['LEAD']?.length || 0;
  const negociosGanhos = funilData.value['GANHO']?.length || 0;
  if (totalLeads === 0) return 0;
  return ((negociosGanhos / totalLeads) * 100).toFixed(2);
});

watch(oportunidadesFiltradas, (novaLista) => {
  const agrupado: { [key: string]: any[] } = {};
  fasesDoFunil.value.forEach(fase => {
    agrupado[fase.id] = [];
  });
  novaLista.forEach(oportunidade => {
    agrupado[oportunidade.fase].push(oportunidade);
  });
  funilData.value = agrupado;
}, { immediate: true });

async function fetchOportunidades() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/clientes/oportunidades/');
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

function calcularValorTotal(oportunidadesDaFase: any[] | undefined) {
  if (!oportunidadesDaFase) return '';
  const total = oportunidadesDaFase.reduce((sum, op) => {
    const valor = op.valor_estimado ? parseFloat(op.valor_estimado) : 0;
    return sum + valor;
  }, 0);
  
  if (total === 0) return '';
  return formatarValor(total);
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
/* Estilos Gerais */
.funil-container {
  padding: 0.5rem;
  background-color: #f8f9fa;
  min-height: calc(100vh - 60px);
}

/* Header da Página */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  font-size: 0.7rem;
  transition: background-color 0.2s;
}
.btn-primary:hover {
  background-color: #0056b3;
}

/* Barra de Filtros */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: flex-end;
  background-color: #fff;
  padding: 0.5rem;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.filter-group {
  display: flex;
  flex-direction: column;
}
.filter-group label {
  font-weight: 600;
  margin-bottom: 0.1rem;
  font-size: 0.7rem;
  color: #495057;
}
.form-control {
  padding: 4px 6px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.75rem;
  transition: border-color 0.2s;
}
.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.75rem;
  height: 26px;
  transition: background-color 0.2s;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

/* Layout de Duas Colunas */
.funil-split-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
@media (max-width: 992px) {
  .funil-split-layout {
    grid-template-columns: 1fr;
  }
}
.funil-board-vertical-wrapper {
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}

/* Layout do Funil Vertical */
.funil-board-vertical {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.5rem;
}
.funil-fase-item {
  border-radius: 4px;
  padding: 0.4rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
  color: #212529;
  transition: width 0.3s ease;
  position: relative;
  clip-path: none;
}
.fase-header {
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 0.2rem;
  margin-bottom: 0.4rem;
}
.fase-titulo {
  font-size: 0.75rem;
  font-weight: bold;
  margin: 0;
}
.oportunidades-lista {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  max-height: 150px;
  overflow-y: auto;
}

/* Cartão de Oportunidade */
.oportunidade-card-link {
  text-decoration: none;
  color: inherit;
}
.oportunidade-card {
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  padding: 0.3rem;
  box-shadow: 0 1px 1px rgba(0,0,0,0.05);
  cursor: pointer;
  border-left: none;
  transition: transform 0.2s, box-shadow 0.2s;
  clip-path: none;
}
.oportunidade-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.card-titulo {
  font-size: 0.75rem;
  font-weight: bold;
  margin: 0 0 0.1rem 0;
  color: #343a40;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.3rem;
}
.card-valor {
  font-weight: bold;
  color: #28a745;
  font-size: 0.75rem;
}
.responsavel-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.6rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* Nova Seção de Fases Finais */
.funil-fases-finais-container {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding-top: 0.5rem;
  border-top: 2px dashed #ddd;
  margin: 0 auto;
}
.funil-fase-item-final {
  width: 48%;
  border-radius: 4px;
  padding: 0.4rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
  color: #212529;
  position: relative;
  clip-path: none;
}
.funil-fase-item-final .oportunidade-card {
  border-left: none;
  clip-path: none;
}
@media (max-width: 576px) {
  .funil-fases-finais-container {
    flex-direction: column;
    align-items: center;
  }
  .funil-fase-item-final {
    width: 95%;
  }
}

/* Estilos da seção de estatísticas */
.funil-stats {
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  height: fit-content;
}
.stats-card h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1rem;
  font-weight: bold;
  color: #343a40;
}
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
}
.stat-label {
  font-weight: 600;
  color: #6c757d;
}
.stat-value {
  font-weight: bold;
  color: #495057;
}
.stats-separator {
  border-bottom: 1px solid #e9ecef;
  margin: 1rem 0;
}
.stat-list {
  display: flex;
  flex-direction: column;
}
</style>
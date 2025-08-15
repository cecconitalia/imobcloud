<template>
  <div class="funil-container">
    <header class="view-header">
      <h1>Funil de Vendas</h1>
      <router-link to="/oportunidades/nova" class="btn-primary">
        + Nova Oportunidade
      </router-link>
    </header>

    <div class="filter-card">
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

    <div v-if="!isLoading" class="funil-split-layout-new">
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
                    <span class="card-probabilidade">{{ oportunidade.probabilidade }}%</span>
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
                    <span class="card-probabilidade">{{ oportunidade.probabilidade }}%</span>
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
      
      <div class="oportunidades-tabela-container">
        <div v-if="oportunidadesFiltradas.length > 0" class="table-responsive">
          <table class="oportunidades-table">
            <thead>
              <tr>
                <th @click="ordenar('titulo')">
                  Oportunidade 
                  <i v-if="sortKey === 'titulo'" :class="sortOrderClass"></i>
                </th>
                <th @click="ordenar('responsavel__first_name')">
                  Responsável
                  <i v-if="sortKey === 'responsavel__first_name'" :class="sortOrderClass"></i>
                </th>
                <th @click="ordenar('valor_estimado')">
                  Valor Estimado 
                  <i v-if="sortKey === 'valor_estimado'" :class="sortOrderClass"></i>
                </th>
                <th @click="ordenar('data_atualizacao')">
                  Última Atividade
                  <i v-if="sortKey === 'data_atualizacao'" :class="sortOrderClass"></i>
                </th>
                <th @click="ordenar('fase')">
                  Fase
                  <i v-if="sortKey === 'fase'" :class="sortOrderClass"></i>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="oportunidade in oportunidadesOrdenadas" :key="oportunidade.id" @click="goToOpportunity(oportunidade.id)">
                <td>
                  <span class="oportunidade-titulo-cell">{{ oportunidade.titulo }}</span>
                  <span class="oportunidade-cliente-cell">{{ oportunidade.cliente?.nome_completo }}</span>
                </td>
                <td>
                  <div class="responsavel-cell">
                    <span class="responsavel-avatar-small">{{ oportunidade.responsavel?.username.charAt(0).toUpperCase() || '?' }}</span>
                    <span class="responsavel-nome">{{ oportunidade.responsavel?.first_name || 'Não atribuído' }}</span>
                  </div>
                </td>
                <td>{{ formatarValor(oportunidade.valor_estimado) }}</td>
                <td>{{ formatarData(oportunidade.data_atualizacao) }}</td>
                <td><span class="fase-badge" :style="{ backgroundColor: fasesDeFunilCores[oportunidade.fase] }">{{ fasesDoFunil.find(f => f.id === oportunidade.fase)?.titulo }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="no-results-message">
          Nenhuma oportunidade encontrada com os filtros selecionados.
        </div>
      </div>
    </div>
    
    <div class="funil-stats-full-width">
      <div class="stats-card-professional">
        <div class="header-wrapper">
          <h4 class="section-title-professional">Estatísticas do Funil</h4>
        </div>
        <div class="stats-grid-professional">
          <div class="stat-card-professional-item">
            <i class="fas fa-chart-pie stat-icon"></i>
            <div class="stat-info">
              <span class="stat-label">Total de Oportunidades</span>
              <span class="stat-value">{{ totalOportunidades }}</span>
            </div>
          </div>
          <div class="stat-card-professional-item">
            <i class="fas fa-dollar-sign stat-icon"></i>
            <div class="stat-info">
              <span class="stat-label">Valor Total Estimado</span>
              <span class="stat-value">{{ formatarValor(totalValorFunil) }}</span>
            </div>
          </div>
          <div class="stat-card-professional-item">
            <i class="fas fa-sync-alt stat-icon"></i>
            <div class="stat-info">
              <span class="stat-label">Taxa de Fechamento</span>
              <span class="stat-value">{{ taxaFechamento }}%</span>
            </div>
          </div>
          <div class="stat-card-professional-item">
            <i class="fas fa-percent stat-icon"></i>
            <div class="stat-info">
              <span class="stat-label">Probabilidade Média</span>
              <span class="stat-value">{{ probabilidadeMedia }}%</span>
            </div>
          </div>
        </div>
        <div class="stats-separator-professional"></div>
        <div class="stat-list-professional">
          <div v-for="fase in fasesDoFunil" :key="fase.id" class="stat-item-professional">
            <span class="stat-label-with-dot" :style="{ '--dot-color': fasesDeFunilCores[fase.id] }">
              {{ fase.titulo }}
            </span>
            <span class="stat-value">{{ funilData[fase.id]?.length || 0 }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

const router = useRouter();

const oportunidades = ref<any[]>([]);
const funilData = ref<{ [key: string]: any[] }>({});
const isLoading = ref(true);
const error = ref<string | null>(null);
const corretores = ref<any[]>([]);

const filtro = ref({
  search: '',
  responsavel: ''
});

const sortKey = ref('data_atualizacao');
const sortOrder = ref(1); // 1 para ascendente, -1 para descendente

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

const oportunidadesOrdenadas = computed(() => {
  if (!sortKey.value) {
    return oportunidadesFiltradas.value;
  }

  return [...oportunidadesFiltradas.value].sort((a, b) => {
    let aValue = getNestedValue(a, sortKey.value);
    let bValue = getNestedValue(b, sortKey.value);

    // Converte para número se o valor for um string de número
    if (typeof aValue === 'string' && !isNaN(parseFloat(aValue as string))) {
      aValue = parseFloat(aValue);
    }
    if (typeof bValue === 'string' && !isNaN(parseFloat(bValue as string))) {
      bValue = parseFloat(bValue);
    }

    if (aValue < bValue) return -1 * sortOrder.value;
    if (aValue > bValue) return 1 * sortOrder.value;
    return 0;
  });
});

function getNestedValue(obj: any, key: string) {
  return key.split('__').reduce((o, i) => (o ? o[i] : null), obj);
}

const sortOrderClass = computed(() => {
  return sortOrder.value === 1 ? 'fas fa-sort-up' : 'fas fa-sort-down';
});

function ordenar(key: string) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value * -1;
  } else {
    sortKey.value = key;
    sortOrder.value = 1;
  }
}

const totalOportunidades = computed(() => oportunidades.value.length);
const totalValorFunil = computed(() => {
  return oportunidades.value.reduce((sum, op) => {
    const valor = op.valor_estimado ? parseFloat(op.valor_estimado) : 0;
    return sum + valor;
  }, 0);
});
// AQUI ESTÁ A ALTERAÇÃO: A lógica da taxa de conversão foi alterada para taxa de fechamento.
const taxaFechamento = computed(() => {
  const negociosGanhos = funilData.value['GANHO']?.length || 0;
  const negociosPerdidos = funilData.value['PERDIDO']?.length || 0;
  const totalFechados = negociosGanhos + negociosPerdidos;
  if (totalFechados === 0) return '0.00';
  return ((negociosGanhos / totalFechados) * 100).toFixed(2);
});

// NOVO: Cálculo da probabilidade média
const probabilidadeMedia = computed(() => {
  if (oportunidades.value.length === 0) return '0.00';
  const totalProbabilidade = oportunidades.value.reduce((sum, op) => sum + (op.probabilidade || 0), 0);
  return (totalProbabilidade / oportunidades.value.length).toFixed(2);
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

function formatarData(dataString: string) {
  if (!dataString) return '-';
  const data = new Date(dataString);
  return data.toLocaleDateString('pt-BR');
}

function limparFiltros() {
  filtro.value.search = '';
  filtro.value.responsavel = '';
}

function goToOpportunity(id: number) {
  router.push(`/oportunidades/editar/${id}`);
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

/* === NOVO ESTILO DA BARRA DE FILTROS === */
.filter-card {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
}
.filter-group {
  display: flex;
  flex-direction: column;
}
.filter-group label {
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 0.8rem;
  color: #495057;
}
.form-control {
  padding: 8px 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.9rem;
  height: 38px;
  transition: background-color 0.2s;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
/* === FIM DO NOVO ESTILO DA BARRA DE FILTROS === */

/* Layout de Duas Colunas - NOVO LAYOUT */
.funil-split-layout-new {
  display: grid;
  grid-template-columns: 1fr 2fr; /* Funil ocupa 1 parte, a tabela 2 partes */
  gap: 1.5rem;
}
@media (max-width: 992px) {
  .funil-split-layout-new {
    grid-template-columns: 1fr;
  }
}

/* Layout do Funil Vertical */
.funil-board-vertical-wrapper {
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}
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
/* NOVO: Estilo para a probabilidade no card */
.card-probabilidade {
    font-size: 0.75rem;
    font-weight: bold;
    color: #007bff;
    margin-left: auto;
    padding-right: 0.5rem;
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

/* Estilos da seção de tabela de oportunidades */
.oportunidades-tabela-container {
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.section-title {
  font-size: 1.5rem;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #343a40;
}
.table-responsive {
  overflow-x: auto;
}
.oportunidades-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
.oportunidades-table th,
.oportunidades-table td {
  padding: 8px 10px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}
.oportunidades-table th {
  background-color: #f1f3f5;
  font-weight: bold;
  color: #495057;
  cursor: pointer;
  position: relative;
  white-space: nowrap;
}
.oportunidades-table th:hover {
  background-color: #e9ecef;
}
.oportunidades-table th i {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #adb5bd;
}
.oportunidades-table tbody tr {
  transition: background-color 0.2s;
  cursor: pointer;
}
.oportunidades-table tbody tr:hover {
  background-color: #f8f9fa;
}
.oportunidade-titulo-cell {
  font-weight: bold;
  display: block;
}
.oportunidade-cliente-cell {
  font-size: 0.8rem;
  color: #6c757d;
  display: block;
}
.responsavel-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.responsavel-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
}
.responsavel-nome {
  white-space: nowrap;
}
.fase-badge {
  padding: 4px 8px;
  border-radius: 12px;
  color: white;
  font-weight: bold;
  font-size: 0.7rem;
  white-space: nowrap;
}
.no-results-message {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
}

/* Estilos para o novo card de estatísticas */
.funil-stats-full-width {
  margin-top: 1.5rem;
}
.stats-card-professional {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-left: 5px solid #007bff;
}
.section-title-professional {
  font-size: 1.25rem;
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #343a40;
  font-weight: bold;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.75rem;
}
.stats-grid-professional {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}
.stat-card-professional-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
}
.stat-icon {
  font-size: 2rem;
  color: #007bff;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-label {
  font-size: 0.85rem;
  color: #6c757d;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #343a40;
}
.stats-separator-professional {
  border-bottom: 1px solid #e9ecef;
  margin: 1.5rem 0;
}
.stat-list-professional {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  list-style: none;
  padding: 0;
  margin: 0;
}
.stat-item-professional {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-basis: 48%; /* Para duas colunas em telas grandes */
  font-size: 0.9rem;
}
.stat-label-with-dot {
  position: relative;
  padding-left: 1.25rem;
  color: #495057;
}
.stat-label-with-dot::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: var(--dot-color);
}
</style>
<template>
  <div class="report-container">
    <h1>Relatório de Autorizações</h1>
    <p class="description">Monitore a validade dos contratos e a exclusividade dos imóveis.</p>

    <div class="stats-grid">
      <div class="stat-card total clickable" @click="applyFilterFromCard('total')">
        <div class="stat-icon"><i class="fas fa-file-contract"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total }}</span>
          <span class="stat-label">Total de Contratos</span>
        </div>
      </div>

      <div class="stat-card expired clickable" @click="applyFilterFromCard('expired')">
        <div class="stat-icon"><i class="fas fa-exclamation-circle"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.expired }}</span>
          <span class="stat-label">Contratos Expirados</span>
        </div>
      </div>

      <div class="stat-card risk clickable" @click="applyFilterFromCard('risk30')">
        <div class="stat-icon"><i class="fas fa-clock"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.risk30 }}</span>
          <span class="stat-label">Risco Imediato (0-30 dias)</span>
        </div>
      </div>

      <div class="stat-card warning clickable" @click="applyFilterFromCard('warning90')">
        <div class="stat-icon"><i class="fas fa-calendar-alt"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.risk90 }}</span>
          <span class="stat-label">Atenção (31-90 dias)</span>
        </div>
      </div>
    </div>
    <div class="filters">
      <div class="filter-group">
        <label for="validade">Contratos a Vencer</label>
        <select id="validade" v-model="validadeDias" @change="fetchReportData()">
          <option value="">Todos os Ativos</option>
          <option value="30">Vencimento em 30 dias</option>
          <option value="90">Vencimento em 90 dias</option>
          <option value="180">Vencimento em 180 dias</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="exclusividade">Tipo de Contrato</label>
        <select id="exclusividade" v-model="exclusividade" @change="fetchReportData()">
          <option value="">Todos</option>
          <option value="true">Apenas Exclusivos</option>
          <option value="false">Apenas Não Exclusivos</option>
        </select>
      </div>
       <div class="filter-group">
        <label for="expirados">Status</label>
        <select id="expirados" v-model="statusFiltro" @change="fetchReportData()">
          <option value="ativos">Apenas Ativos/Risco</option>
          <option value="expirados">Apenas Expirados</option>
        </select>
      </div>
      
      <div class="filter-group-action">
        <button @click="downloadPDF" :disabled="isLoading || !reportData.length" class="btn-pdf" title="Gerar PDF para Impressão">
          <i :class="isLoading ? 'fas fa-spinner fa-spin' : 'fas fa-file-pdf'"></i>
          Gerar PDF
        </button>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-message">
      <i class="fas fa-spinner fa-spin"></i> A carregar dados do relatório...
    </div>

    <div v-else-if="!reportData.length" class="no-data-message">
      Nenhum imóvel encontrado com os critérios de filtro.
    </div>

    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Ref.</th>
            <th>Imóvel</th>
            <th>Proprietário</th>
            <th>Exclusividade</th>
            <th>Vencimento</th>
            <th>Dias Restantes</th>
            <th>Risco</th>
            <th>Comissão (%)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in reportData" :key="item.id" :class="getRowClass(item.dias_restantes)">
            <td>{{ item.codigo_referencia }}</td>
            <td>
              <router-link :to="{ name: 'imovel-editar', params: { id: item.id } }">
                {{ item.titulo_anuncio }}
              </router-link>
            </td>
            <td>{{ item.proprietario }}</td>
            <td>{{ item.exclusividade }}</td>
            <td>{{ formatDate(item.data_fim_autorizacao) }}</td>
            <td :class="{'negative-days': item.dias_restantes < 0}">
                {{ item.dias_restantes }}
            </td>
            <td><span :class="getStatusClass(item.status_risco)">{{ item.status_risco }}</span></td>
            <td>{{ formatPercent(item.comissao) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css'; 

const isLoading = ref(false);
const reportData = ref<any[]>([]); 
const rawReportData = ref<any[]>([]); // Dados brutos para o dashboard

// Tipagem do Card Filter
type CardFilterType = 'total' | 'expired' | 'risk30' | 'warning90' | undefined;

// Estatísticas para os cards
const stats = ref({
  total: 0,
  expired: 0,
  risk30: 0,
  risk90: 0
});

// Filtros
const validadeDias = ref('');
const exclusividade = ref('');
const statusFiltro = ref('ativos');

interface AutorizacaoItem {
  id: number;
  codigo_referencia: string;
  titulo_anuncio: string;
  proprietario: string;
  data_fim_autorizacao: string;
  dias_restantes: number;
  status_risco: 'Expirado' | 'Risco (30 dias)' | 'Atenção (90 dias)' | 'Ativo';
  exclusividade: 'Sim' | 'Não';
  comissao: number;
}

const getApiParams = () => {
    const params: { [key: string]: string | undefined } = {
      exclusividade: exclusividade.value || undefined,
    };
    
    if (statusFiltro.value === 'expirados') {
        params.validade_dias = '0';
    } 
    else if (validadeDias.value !== '') {
        params.validade_dias = validadeDias.value;
    }
    
    return params;
}

const calculateStats = (data: AutorizacaoItem[]) => {
  stats.value = {
    total: data.length,
    // Filtramos apenas onde a data de fim da autorização existe para calcular risco
    expired: data.filter(i => i.dias_restantes !== null && i.dias_restantes < 0).length,
    risk30: data.filter(i => i.dias_restantes !== null && i.dias_restantes >= 0 && i.dias_restantes <= 30).length,
    risk90: data.filter(i => i.dias_restantes !== null && i.dias_restantes > 30 && i.dias_restantes <= 90).length
  };
};

const fetchDashboardData = async () => {
  try {
    // Chamada sem parâmetros para o backend retornar todos os status e datas
    const response = await apiClient.get('/v1/imoveis/relatorio/autorizacoes/');
    const allData = response.data as AutorizacaoItem[];
    rawReportData.value = allData;
    calculateStats(allData);
  } catch (error) {
    console.error('Erro ao buscar dados completos para o dashboard:', error);
  }
};


/**
 * Busca os dados de autorização, aplicando os filtros selecionados, para a Tabela.
 * @param cardFilter Se presente, aplica um filtro adicional específico para cards.
 */
const fetchReportData = async (cardFilter?: CardFilterType) => {
  isLoading.value = true;
  try {
    // 1. Pega os parâmetros do SELECT
    const params = getApiParams();
    
    // 2. Chama a API com os filtros da tabela
    const response = await apiClient.get('/v1/imoveis/relatorio/autorizacoes/', { params });
    
    let filteredData = response.data as AutorizacaoItem[];
    
    // 3. Pós-filtro padrão do cliente (mantém apenas ativos OU apenas expirados)
    if (statusFiltro.value === 'expirados') {
       filteredData = filteredData.filter(item => item.dias_restantes !== null && item.dias_restantes < 0);
    } else { // statusFiltro === 'ativos'
       filteredData = filteredData.filter(item => item.dias_restantes === null || item.dias_restantes >= 0);
    }

    // 4. FILTRO ESPECÍFICO DE CARD (para ranges complexos como 31-90 dias)
    if (cardFilter === 'warning90') {
        filteredData = filteredData.filter(item => item.dias_restantes !== null && item.dias_restantes > 30 && item.dias_restantes <= 90);
    }
    
    reportData.value = filteredData;


  } catch (error) {
    console.error('Erro ao buscar o relatório de autorizações:', error);
    alert('Não foi possível carregar o relatório.');
  } finally {
    isLoading.value = false;
  }
};


/**
 * Manipulador de clique para os cards do dashboard.
 * Seta os selects para o estado desejado e chama o fetch.
 */
const applyFilterFromCard = (type: CardFilterType) => {
  // Reseta filtros não relacionados à validade para o estado 'Todos'
  exclusividade.value = '';
  
  if (type === 'total') {
    statusFiltro.value = 'ativos';
    validadeDias.value = '';
  } else if (type === 'expired') {
    statusFiltro.value = 'expirados';
    validadeDias.value = ''; 
  } else if (type === 'risk30') {
    statusFiltro.value = 'ativos'; 
    validadeDias.value = '30';
  } else if (type === 'warning90') {
    statusFiltro.value = 'ativos'; 
    validadeDias.value = '90'; 
  }
  
  // Chama a função de busca, passando o tipo de filtro do card
  fetchReportData(type);
};

// --- MÉTODO PARA DOWNLOAD DO PDF (AGORA ABRE EM NOVA ABA) ---
const downloadPDF = async () => {
  isLoading.value = true;
  try {
    const params = getApiParams();
    
    const response = await apiClient.get('/v1/imoveis/relatorio/autorizacoes/pdf/', { 
      params,
      responseType: 'blob' // Informa ao Axios para esperar um arquivo binário
    });

    // 1. Cria um objeto URL para o Blob (o PDF)
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    
    // 2. ABRE O PDF EM UMA NOVA ABA PARA VISUALIZAÇÃO
    window.open(url, '_blank');

    // 3. Limpa a URL do objeto após um pequeno atraso. 
    // Isso é uma boa prática para liberar memória.
    setTimeout(() => window.URL.revokeObjectURL(url), 100);

  } catch (error) {
    console.error('Erro ao gerar PDF do relatório:', error);
    alert('Não foi possível gerar o PDF. Verifique o console para detalhes.');
  } finally {
    isLoading.value = false;
  }
};


const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  const data = new Date(dateString);
  const dataUTC = new Date(data.valueOf() + data.getTimezoneOffset() * 60000);
  return dataUTC.toLocaleDateString('pt-BR');
};

const formatPercent = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A';
    return value.toFixed(2).replace('.', ',') + ' %';
};

const getRowClass = (dias: number) => {
  if (dias < 0) return 'expired';
  if (dias <= 30) return 'risk';
  if (dias <= 90) return 'warning';
  return '';
};

const getStatusClass = (status: string) => {
  switch (status) {
    case 'Expirado': return 'status-expired';
    case 'Risco (30 dias)': return 'status-risk';
    case 'Atenção (90 dias)': return 'status-warning';
    default: return 'status-active';
  }
};

onMounted(async () => {
    // Carrega o dashboard e a tabela inicialmente
    await fetchDashboardData();
    await fetchReportData();
});
</script>

<style scoped>
.report-container {
  padding: 20px;
}

h1 {
    font-size: 1.8rem;
    color: #007bff;
    margin-bottom: 5px;
}

.description {
  color: #6c757d;
  margin-bottom: 20px;
}

/* --- ESTILOS DOS CARDS (DASHBOARD) --- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: white;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s;
  border-left: 5px solid #ccc;
}

.stat-card.clickable {
    cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 10px rgba(0,0,0,0.15);
}

.stat-icon {
  font-size: 2rem;
  margin-right: 20px;
  opacity: 0.8;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
}

/* Cores Específicas dos Cards */
.stat-card.total {
  border-left-color: #007bff; /* Azul */
}
.stat-card.total .stat-icon { color: #007bff; }

.stat-card.expired {
  border-left-color: #dc3545; /* Vermelho */
}
.stat-card.expired .stat-icon { color: #dc3545; }
.stat-card.expired .stat-value { color: #dc3545; }

.stat-card.risk {
  border-left-color: #ffc107; /* Amarelo */
}
.stat-card.risk .stat-icon { color: #ffc107; }

.stat-card.warning {
  border-left-color: #0d6efd; /* Azul Claro/Padrão */
}
.stat-card.warning .stat-icon { color: #0d6efd; }

/* ------------------------------------- */

.filters {
  display: flex;
  flex-wrap: wrap; 
  gap: 20px;
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f8f9fa;
  align-items: flex-end; 
}

.filter-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
  color: #495057;
  font-size: 0.9rem;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 150px;
}

.filter-group-action {
  margin-left: auto;
}

.btn-pdf {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s ease;
}
.btn-pdf:hover {
  background-color: #c82333;
}
.btn-pdf:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.btn-pdf i {
  font-size: 0.9rem;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

th, td {
  padding: 12px 15px;
  border: 1px solid #dee2e6;
  text-align: left;
}

thead th {
  background-color: #007bff;
  color: white;
  font-weight: 600;
}

tbody tr:nth-child(even) {
  background-color: #f8f9fa;
}

tbody tr:hover {
  background-color: #e9ecef;
}

.expired {
  background-color: #f8d7da !important;
  color: #721c24;
}
.risk {
  background-color: #fff3cd !important;
  color: #856404;
}
.warning {
  background-color: #cfe2ff !important;
  color: #0d6efd;
}
.negative-days {
    font-weight: bold;
    color: #dc3545;
}

.status-expired {
  font-weight: bold;
  color: white;
  background-color: #dc3545;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  font-size: 0.85rem;
}
.status-risk {
  font-weight: bold;
  color: #856404;
  background-color: #ffc107;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  font-size: 0.85rem;
}
.status-warning {
  color: #0d6efd;
  background-color: #e0f2ff;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  font-size: 0.85rem;
}
.status-active {
  color: #28a745;
  font-weight: 500;
  font-size: 0.85rem;
}

.no-data-message {
  text-align: center;
  padding: 40px;
  font-size: 1.1rem;
  color: #6c757d;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.loading-message {
  text-align: center;
  padding: 20px;
  font-size: 1.1rem;
  color: #007bff;
}
.loading-message i {
    margin-right: 10px;
}

td a {
    color: #0056b3;
    text-decoration: none;
    font-weight: 500;
}
td a:hover {
    text-decoration: underline;
}
</style>
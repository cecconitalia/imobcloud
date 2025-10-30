<template>
  <div class="report-container">
    <h1>Relatório de Autorizações</h1>
    <p class="description">Monitore a validade dos contratos e a exclusividade dos imóveis.</p>

    <div class="filters">
      <div class="filter-group">
        <label for="validade">Contratos a Vencer</label>
        <select id="validade" v-model="validadeDias" @change="fetchReportData">
          <option value="">Todos os Ativos</option>
          <option value="30">Vencimento em 30 dias</option>
          <option value="90">Vencimento em 90 dias</option>
          <option value="180">Vencimento em 180 dias</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="exclusividade">Tipo de Contrato</label>
        <select id="exclusividade" v-model="exclusividade" @change="fetchReportData">
          <option value="">Todos</option>
          <option value="true">Apenas Exclusivos</option>
          <option value="false">Apenas Não Exclusivos</option>
        </select>
      </div>
       <div class="filter-group">
        <label for="expirados">Status</label>
        <select id="expirados" v-model="statusFiltro" @change="fetchReportData">
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
// Assumindo que você tem os ícones FontAwesome (como indicado nos arquivos anteriores)
import '@fortawesome/fontawesome-free/css/all.css'; 

const isLoading = ref(false);
const reportData = ref<any[]>([]);

// Filtros
const validadeDias = ref('');
const exclusividade = ref('');
const statusFiltro = ref('ativos');

// Tipos para auxiliar o TypeScript (Opcional, mas útil)
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

// --- FUNÇÃO PARA PEGAR OS PARÂMETROS DE FILTRO (REUTILIZÁVEL) ---
const getApiParams = () => {
    let diasFiltro = validadeDias.value;
    
    const params: { [key: string]: string | undefined } = {
      exclusividade: exclusividade.value || undefined,
    };
    
    if (statusFiltro.value === 'expirados') {
        params.validade_dias = '0'; // '0' é o código para buscar expirados na API
    } else if (validadeDias.value !== '') {
        params.validade_dias = validadeDias.value;
    }
    // Se statusFiltro for 'ativos' e validadeDias for '', nenhum 'validade_dias' é enviado,
    // e a API (conforme _get_autorizacao_queryset) retornará todos os ativos.
    
    return params;
}


const fetchReportData = async () => {
  isLoading.value = true;
  try {
    const params = getApiParams();
    
    const response = await apiClient.get('/v1/imoveis/relatorio/autorizacoes/', { params });
    
    let filteredData = response.data as AutorizacaoItem[];
    
    // Pós-filtro no cliente para garantir que a API (que usa validade_dias=0 para expirados)
    // se alinhe com o seletor de status.
    if (statusFiltro.value === 'expirados') {
       filteredData = filteredData.filter(item => item.dias_restantes < 0);
    } else { // statusFiltro === 'ativos'
       filteredData = filteredData.filter(item => item.dias_restantes >= 0);
    }
    
    reportData.value = filteredData;


  } catch (error) {
    console.error('Erro ao buscar o relatório de autorizações:', error);
    alert('Não foi possível carregar o relatório.');
  } finally {
    isLoading.value = false;
  }
};

// --- MÉTODO PARA DOWNLOAD DO PDF ---
const downloadPDF = async () => {
  isLoading.value = true;
  try {
    // 1. Pega os mesmos parâmetros de filtro atuais
    const params = getApiParams();
    
    // 2. Chama o novo endpoint de PDF
    const response = await apiClient.get('/v1/imoveis/relatorio/autorizacoes/pdf/', { 
      params,
      responseType: 'blob' // Muito importante: informa ao Axios para esperar um arquivo
    });

    // 3. Cria um link temporário e simula o clique para baixar
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `relatorio_autorizacoes_${new Date().toISOString().split('T')[0]}.pdf`);
    document.body.appendChild(link);
    link.click();
    
    // 4. Limpa
    link.remove();
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error('Erro ao gerar PDF do relatório:', error);
    alert('Não foi possível gerar o PDF. Verifique o console para detalhes.');
  } finally {
    isLoading.value = false;
  }
};


const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  // Use 'pt-BR' para garantir o formato correto de data
  const data = new Date(dateString);
  // Adiciona o fuso horário (se não houver) para evitar que a data mude
  const dataUTC = new Date(data.valueOf() + data.getTimezoneOffset() * 60000);
  return dataUTC.toLocaleDateString('pt-BR');
};

const formatPercent = (value: number | null) => {
    if (value === null || value === undefined) return 'N/A';
    // Formatação BRL para percentual (ex: 8.00 -> 8,00 %)
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

onMounted(fetchReportData);
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

.filters {
  display: flex;
  flex-wrap: wrap; /* Permite quebrar linha em telas menores */
  gap: 20px;
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f8f9fa;
  align-items: flex-end; /* Alinha os itens na parte inferior */
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

/* Estilo para o botão de PDF */
.filter-group-action {
  margin-left: auto; /* Joga o botão para a direita */
}

.btn-pdf {
  background-color: #dc3545; /* Cor vermelha para PDF */
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

/* Classes de Risco na Tabela */
.expired {
  background-color: #f8d7da !important; /* Vermelho claro */
  color: #721c24;
}
.risk {
  background-color: #fff3cd !important; /* Amarelo claro */
  color: #856404;
}
.warning {
  background-color: #cfe2ff !important; /* Azul claro */
  color: #0d6efd;
}
.negative-days {
    font-weight: bold;
    color: #dc3545;
}

/* Estilos para os spans de status */
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

/* Corrigindo o link do router para não ficar roxo (visitado) */
td a {
    color: #0056b3;
    text-decoration: none;
    font-weight: 500;
}
td a:hover {
    text-decoration: underline;
}
</style>
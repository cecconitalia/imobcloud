<template>
  <div class="autorizacoes-container">
    <div v-if="isLoading" class="loading-message">A carregar dados...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="data" class="content-area">
      
      <div class="summary-cards">
        <div class="card" @click="setFilter('expirando_em_30_dias')" :class="{ active: activeFilter === 'expirando_em_30_dias' }">
          <p class="card-value">{{ data.sumario.expirando_em_30_dias }}</p>
          <p class="card-label">Expirando em 30 Dias</p>
        </div>
        <div class="card" @click="setFilter('expiradas_recentemente')" :class="{ active: activeFilter === 'expiradas_recentemente' }">
          <p class="card-value">{{ data.sumario.expiradas_recentemente }}</p>
          <p class="card-label">Expiradas (Últimos 30d)</p>
        </div>
        <div class="card" @click="setFilter('ativas')" :class="{ active: activeFilter === 'ativas' }">
          <p class="card-value">{{ data.sumario.ativas }}</p>
          <p class="card-label">Autorizações Ativas</p>
        </div>
        <div class="card" @click="setFilter('sem_data')" :class="{ active: activeFilter === 'sem_data' }">
          <p class="card-value">{{ data.sumario.sem_data }}</p>
          <p class="card-label">Registos Incompletos</p>
        </div>
      </div>

      <div class="imoveis-table-container">
        <div class="table-header-actions">
            <h2 class="table-title">Imóveis com Autorização</h2>
            <button @click="goToCreateAutorizacao" class="btn-add">
                <i class="fas fa-plus"></i> Adicionar Autorização
            </button>
        </div>
        <table>
          <thead>
            <tr>
              <th>Ref.</th>
              <th>Imóvel</th>
              <th>Proprietário</th>
              <th>Fim da Autorização</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="imovel in filteredImoveis" :key="imovel.id">
              <td>{{ imovel.codigo_referencia }}</td>
              <td>{{ imovel.titulo_anuncio }}</td>
              <td>{{ imovel.proprietario__nome_completo || 'N/A' }}</td>
              <td>{{ formatarData(imovel.data_fim_autorizacao) }}</td>
              <td>
                <span :class="['status-badge', getStatusClass(imovel.status_autorizacao)]">
                  {{ imovel.status_autorizacao }}
                </span>
              </td>
              <td class="actions-cell">
                <router-link :to="`/imoveis/editar/${imovel.id}?tab=autorizacao`" class="btn-sm btn-edit">
                  Ver/Editar
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
         <p v-if="!isLoading && filteredImoveis.length === 0" class="no-results">
            Nenhum imóvel encontrado para o filtro selecionado.
         </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useRouter } from 'vue-router'; 

const router = useRouter(); 

// Interfaces adaptadas para a estrutura esperada (baseada no código anterior)
interface ImovelAutorizacao {
    id: number;
    codigo_referencia: string;
    titulo_anuncio: string;
    proprietario__nome_completo: string | null; 
    data_fim_autorizacao: string | null;
    status_autorizacao: 'Ativo' | 'Expirando' | 'Expirado' | 'Incompleto'; 
}

interface SumarioAutorizacoes {
    expirando_em_30_dias: number;
    expiradas_recentemente: number;
    ativas: number;
    sem_data: number; 
}

interface AutorizacoesData {
    sumario: SumarioAutorizacoes;
    imoveis: ImovelAutorizacao[];
}


const data = ref<AutorizacoesData | null>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const activeFilter = ref<string | null>(null);


const filteredImoveis = computed(() => {
  if (!data.value || !data.value.imoveis) return [];
  if (!activeFilter.value) return data.value.imoveis; 

  switch (activeFilter.value) {
    case 'expirando_em_30_dias':
      return data.value.imoveis.filter((i: ImovelAutorizacao) => i.status_autorizacao === 'Expirando');
    case 'expiradas_recentemente':
      {
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0); 
        const limitePassado = new Date();
        limitePassado.setDate(hoje.getDate() - 30);
        limitePassado.setHours(0, 0, 0, 0);

        return data.value.imoveis.filter((i: ImovelAutorizacao) => {
            if (i.status_autorizacao !== 'Expirado' || !i.data_fim_autorizacao) return false;
            try {
                const dataFim = new Date(i.data_fim_autorizacao + 'T00:00:00'); 
                return dataFim >= limitePassado && dataFim < hoje;
            } catch {
                return false; 
            }
        });
      }
    case 'ativas':
      return data.value.imoveis.filter((i: ImovelAutorizacao) => i.status_autorizacao === 'Ativo');
    case 'sem_data':
      return data.value.imoveis.filter((i: ImovelAutorizacao) => i.status_autorizacao === 'Incompleto');
    default:
      return data.value.imoveis;
  }
});

// FUNÇÃO DE NAVEGAÇÃO ADICIONADA
function goToCreateAutorizacao() {
    router.push({ name: 'autorizacao-nova' });
}


function setFilter(filter: string) {
    if (activeFilter.value === filter) {
        activeFilter.value = null; 
    } else {
        activeFilter.value = filter;
    }
}

async function fetchData() {
  isLoading.value = true;
  error.value = null; 
  try {
    // URL CORRIGIDA para /v1/autorizacao-status/
    const response = await apiClient.get<AutorizacoesData>('/v1/autorizacao-status/');
    data.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar dados de autorizações:", err);
    // Exibe a mensagem de erro da API ou uma genérica
    if (err.response && err.response.status === 404) {
        error.value = "Erro 404: O endpoint '/v1/autorizacao-status/' não foi encontrado no servidor.";
    } else {
        error.value = err.response?.data?.detail || 'Não foi possível carregar os dados das autorizações.';
    }
  } finally {
    isLoading.value = false;
  }
}

// Renomeado para 'formatarData' como no código original
function formatarData(data: string | null): string {
  if (!data) return 'N/A';
  try {
      // Usando date-fns para consistência, tratando a data como local
      return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
  } catch {
      return 'Inválida';
  }
}


// Lógica de classe baseada nos status do código original
function getStatusClass(status: string) {
  switch (status) {
    case 'Ativo': return 'status-ativo';
    case 'Expirando': return 'status-expirando';
    case 'Expirado': return 'status-expirado';
    case 'Incompleto': return 'status-incompleto';
    default: return '';
  }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.autorizacoes-container {
  padding: 0; 
}

.loading-message, .error-message, .no-results {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #6c757d;
}
.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 12px rgba(0,0,0,0.1);
}
.card.active {
    border-color: #007bff;
    box-shadow: 0 6px 10px rgba(0, 123, 255, 0.2);
}
.card-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  color: #007bff;
}
.card-label {
  margin: 0.5rem 0 0 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.imoveis-table-container {
    background-color: #fff;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    overflow-x: auto;
}

/* NOVO ESTILO: Garante que o título e o botão fiquem na mesma linha, alinhados. */
.table-header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    /* Adicionamos padding/margin interno para não afetar o padding do container pai */
    padding: 0 0.5rem; 
}

.table-title {
    font-size: 1.3rem;
    margin: 0;
    color: #333;
}

.btn-add {
  background-color: #007bff; 
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s ease;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  /* Removido margin-left: auto para usar o justify-content: space-between */
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}

.btn-add:hover {
  background-color: #0056b3;
}
/* FIM CORREÇÕES DE ESTILO */

table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border-bottom: 1px solid #ddd;
  padding: 12px 15px; 
  text-align: left;
  white-space: nowrap;
}
th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #495057;
}
tr:hover {
  background-color: #f1f1f1;
}

/* Estilos de status como no código original */
.status-badge {
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8em;
  font-weight: bold;
  color: white;
  text-align: center;
  display: inline-block; 
}
.status-ativo { background-color: #28a745; } 
.status-expirando { background-color: #ffc107; color: #333; } 
.status-expirado { background-color: #dc3545; } 
.status-incompleto { background-color: #6c757d; } 

.actions-cell {
    text-align: center; 
}
.btn-sm { 
  padding: 5px 10px;
  font-size: 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  font-weight: 500;
  text-decoration: none; 
  display: inline-block; 
}
.btn-edit { 
  background-color: #17a2b8; 
  color: white;
}
.btn-edit:hover {
  background-color: #138496; 
}

.no-results {
   text-align: center;
   padding: 2rem;
   color: #6c757d;
}
</style>
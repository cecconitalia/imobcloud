<template>
  <div class="autorizacoes-container">
    <header class="view-header">
      <h1>Gestão de Autorizações de Captação</h1>
    </header>

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
                <router-link :to="`/imoveis/editar/${imovel.id}`" class="btn-secondary">
                  Ver/Editar
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
         <p v-if="filteredImoveis.length === 0" class="no-results">
            Nenhum imóvel encontrado para o filtro selecionado.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';

const data = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);
const activeFilter = ref<string | null>(null);

const filteredImoveis = computed(() => {
  if (!data.value || !data.value.imoveis) return [];
  if (!activeFilter.value) return data.value.imoveis;

  switch (activeFilter.value) {
    case 'expirando_em_30_dias':
      return data.value.imoveis.filter((i: any) => i.status_autorizacao === 'Expirando');
    case 'expiradas_recentemente': {
        const hoje = new Date();
        const limitePassado = new Date();
        limitePassado.setDate(hoje.getDate() - 30);
        return data.value.imoveis.filter((i: any) => {
            if (i.status_autorizacao !== 'Expirado') return false;
            const dataFim = new Date(i.data_fim_autorizacao);
            return dataFim >= limitePassado && dataFim < hoje;
        });
    }
    case 'ativas':
      return data.value.imoveis.filter((i: any) => i.status_autorizacao === 'Ativo');
    case 'sem_data':
      return data.value.imoveis.filter((i: any) => i.status_autorizacao === 'Incompleto');
    default:
      return data.value.imoveis;
  }
});

function setFilter(filter: string) {
    if (activeFilter.value === filter) {
        activeFilter.value = null; // Clicar novamente para limpar o filtro
    } else {
        activeFilter.value = filter;
    }
}

async function fetchData() {
  isLoading.value = true;
  try {
    // CORREÇÃO: A URL foi alterada para o caminho correto, removendo o prefixo 'imoveis/'
    const response = await apiClient.get('/v1/autorizacao-status/');
    data.value = response.data;
  } catch (err: any) {
    console.error("Erro ao buscar dados de autorizações:", err);
    error.value = err.response?.data?.detail || 'Não foi possível carregar os dados.';
  } finally {
    isLoading.value = false;
  }
}

function formatarData(data: string | null) {
  if (!data) return 'N/A';
  const dataObj = new Date(data);
  return dataObj.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
}

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
.autorizacoes-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.loading-message, .error-message { text-align: center; padding: 2rem; }
.error-message { color: red; }

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
}
.card-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0;
  color: #007bff;
}
.card-label {
  margin: 0;
  color: #6c757d;
}

.imoveis-table-container {
    background-color: #fff;
    padding: 1.5rem;
    border-radius: 8px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border-bottom: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}
th {
  background-color: #f8f9fa;
}
.status-badge {
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8em;
  font-weight: bold;
  color: white;
}
.status-ativo { background-color: #28a745; }
.status-expirando { background-color: #ffc107; color: #333; }
.status-expirado { background-color: #dc3545; }
.status-incompleto { background-color: #6c757d; }
.actions-cell { text-align: center; }
.btn-secondary {
  background-color: #6c757d;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  text-decoration: none;
}
.no-results {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
}
</style>
<template>
  <div class="page-container">
    <div v-if="stats" class="summary-grid">
      <div class="summary-card pending-revenue">
        <h4>Total a Receber (Pendente)</h4>
        <p>{{ formatarValor(stats.total_a_receber) }}</p>
      </div>
       </div>

    <div v-if="isLoading" class="loading-state card">A carregar...</div>
    <div v-if="error" class="error-message card">{{ error }}</div>

    <div class="table-card" v-if="!isLoading && !error">
      <div v-if="transacoes.length">
        <table class="styled-table">
          <thead>
            <tr>
              <th>Vencimento</th>
              <th>Cliente</th>
              <th>Descrição</th>
              <th class="text-right">Valor</th>
              <th class="text-center">Status</th>
              </tr>
          </thead>
          <tbody>
            <tr v-for="transacao in transacoes" :key="transacao.id">
              <td>{{ formatarData(transacao.data_vencimento) }}</td>
              <td>{{ transacao.cliente?.nome_completo || 'N/A' }}</td>
              <td>{{ transacao.descricao }}</td>
              <td class="text-right text-success">{{ formatarValor(transacao.valor) }}</td>
              <td class="text-center">
                <span :class="['status-badge', getStatusClass(transacao.status)]">
                  {{ transacao.status }} </span>
              </td>
              </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="no-data-message">
        Nenhuma conta a receber encontrada.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import { format } from 'date-fns'; // Importar format
import { ptBR } from 'date-fns/locale'; // Importar locale

// Interfaces baseadas no código que funcionava
interface ClienteResumo {
    nome_completo?: string;
    // Adicionar outros campos se a API retornar
}
interface TransacaoReceber {
    id: number;
    data_vencimento: string;
    cliente?: ClienteResumo | null;
    descricao: string;
    valor: number;
    status: 'PENDENTE' | 'ATRASADO' | 'PAGO' | string; // Incluir outros status se houver
}
interface StatsReceberOriginal {
    total_a_receber: number;
    // Adicionar outros campos se a API retornar
}


const transacoes = ref<TransacaoReceber[]>([]); // Tipagem aplicada
const stats = ref<StatsReceberOriginal | null>(null); // Tipagem aplicada
const isLoading = ref(true);
const error = ref<string | null>(null);

// Função formatarValor ajustada para aceitar undefined
const formatarValor = (valor: number | null | undefined): string => {
    if (valor === null || valor === undefined) return 'R$ 0,00';
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

// Função formatarData usando date-fns para consistência
const formatarData = (data: string | null): string => {
    if (!data) return 'N/A';
    try {
        // Assume que a data vem como YYYY-MM-DD
        return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
    } catch {
        return 'Inválida';
    }
};


// Função getStatusClass baseada no código que funcionava
const getStatusClass = (status: string): string => {
  switch (status) {
    case 'PENDENTE': return 'status-pending'; // Amarelo
    case 'ATRASADO': return 'status-overdue'; // Vermelho
    case 'PAGO': return 'status-paid';       // Verde
    default: return '';                      // Cinza/Default
  }
};

async function fetchData() {
  isLoading.value = true;
  error.value = null;
  try {
    // Usando os endpoints originais que funcionavam
    const [transacoesResponse, statsResponse] = await Promise.all([
      apiClient.get<TransacaoReceber[]>('/v1/financeiro/transacoes/a-receber/'), // Tipagem
      apiClient.get<StatsReceberOriginal>('/v1/financeiro/transacoes/contas-pendentes-stats/') // Tipagem
    ]);
    transacoes.value = transacoesResponse.data;
    stats.value = statsResponse.data;
  } catch (err) {
    console.error("Erro ao buscar dados de contas a receber:", err);
    // Usando a mensagem de erro que você viu
    error.value = "Não foi possível carregar os dados iniciais da página.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.page-container {
    /* padding: 2rem; */ /* Removido */
    padding: 0; /* Adicionado */
    /* max-width: 1200px; */ /* Removido - Deixa o layout principal controlar */
    /* margin: auto; */ /* Removido */
}

/* Regras .view-header e .btn-primary removidas */

.summary-grid {
    display: grid;
    /* Alterado para permitir mais colunas se necessário, mas começando com 1 */
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}
.summary-card {
    padding: 1.5rem; border-radius: 8px; background-color: #fff;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid;
}
.summary-card h4 { margin: 0 0 0.5rem 0; font-size: 1rem; color: #6c757d; font-weight: 500;} /* Ajustado peso */
.summary-card p { margin: 0; font-size: 2.2rem; font-weight: bold; }
.pending-revenue { border-color: #ffc107; } /* Amarelo */
/* Adicionar cores para outros cards se a API /stats retornar mais dados */
/* .received-month { border-color: #198754; } */
/* .overdue-revenue { border-color: #dc3545; } */


.table-card {
    background: white; padding: 1.5rem; border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow-x: auto; /* Permite scroll horizontal */
}
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th {
    padding: 1rem; text-align: left; border-bottom: 2px solid #dee2e6;
    color: #495057; background-color: #f8f9fa; font-weight: 600; /* Mais negrito */
}
.styled-table td {
    padding: 1rem; border-bottom: 1px solid #e9ecef; vertical-align: middle; /* Alinha verticalmente */
}
/* Permite quebra de linha na descrição e cliente */
.styled-table td:nth-child(2), .styled-table td:nth-child(3) {
     white-space: normal;
     min-width: 150px; /* Largura mínima */
}


.text-right { text-align: right; }
.text-center { text-align: center; }
.text-success { color: #198754; font-weight: bold; } /* Verde para Receita */

.status-badge {
    padding: 0.3rem 0.6rem; border-radius: 12px; font-size: 0.8rem;
    font-weight: bold; color: white; display: inline-block; /* Garante padding */
}
.status-pending { background-color: #ffc107; color: #333; } /* Amarelo */
.status-overdue { background-color: #dc3545; } /* Vermelho */
.status-paid { background-color: #198754; }    /* Verde */
/* Adicionar outros status se necessário */

.loading-state, .error-message, .no-data-message {
    text-align: center; padding: 2rem; color: #6c757d;
}
.error-message {
    color: #dc3545; /* Vermelho */
    background-color: #f8d7da; /* Fundo vermelho claro */
    border: 1px solid #f5c6cb; /* Borda vermelha clara */
    border-radius: 8px;
    margin-bottom: 1.5rem; /* Espaço abaixo */
    padding: 1rem; /* Padding interno */
}
.no-data-message {
    background-color: #fff; border-radius: 8px; margin-top: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05); padding: 2rem;
}

</style>
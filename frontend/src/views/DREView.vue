<template>
  <div class="page-container">
    <div class="filters-card card">
      <div class="form-group">
        <label for="start-date">Data de Início:</label>
        <input type="date" id="start-date" v-model="startDate" class="filter-input">
      </div>
      <div class="form-group">
        <label for="end-date">Data de Fim:</label>
        <input type="date" id="end-date" v-model="endDate" class="filter-input">
      </div>
      <button @click="fetchDRE" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'A carregar...' : 'Gerar Relatório' }}
      </button>
       <button @click="imprimirDRE" class="btn-secondary" :disabled="!dreData || isLoading">
            <i class="fas fa-print"></i> Imprimir / PDF
        </button>
    </div>

    <div v-if="isLoading && !error" class="loading-state card">
        A gerar relatório DRE...
    </div>
    <div v-if="error" class="error-message card">{{ error }}</div>

    <div v-if="dreData && !isLoading && !error" class="results-container card" id="dre-print-area">
        <div class="report-header">
             <h2>Demonstrativo de Resultados do Exercício (DRE)</h2>
            <p>Período: {{ formatarData(startDate) }} a {{ formatarData(endDate) }}</p>
        </div>

      <div class="summary-grid">
        <div class="summary-card revenue">
          <h4>(+) Total Receitas</h4>
          <p>{{ formatarValor(dreData.total_receitas) }}</p>
        </div>
        <div class="summary-card expenses">
          <h4>(-) Total Despesas</h4>
          <p>{{ formatarValor(dreData.total_despesas) }}</p>
        </div>
        <div class="summary-card balance" :class="getResultadoClass(dreData.resultado_liquido)">
          <h4>(=) Resultado Líquido</h4>
          <p>{{ formatarValor(dreData.resultado_liquido) }}</p>
        </div>
      </div>

       <table class="dre-table">
          <thead>
              <tr>
                  <th>Descrição</th>
                  <th class="text-right">Valor (R$)</th>
              </tr>
          </thead>
          <tbody>
              <tr class="section-header">
                  <td colspan="2"><strong>(+) Receitas Operacionais</strong></td>
              </tr>
              <tr v-for="receita in dreData.detalhes_receitas" :key="`rec-${receita.categoria_id}`">
                  <td class="item-categoria">{{ receita.categoria_nome }}</td>
                  <td class="text-right text-success">{{ formatarValor(receita.total) }}</td>
              </tr>
              <tr class="subtotal">
                  <td><strong>Total Receitas</strong></td>
                  <td class="text-right text-success"><strong>{{ formatarValor(dreData.total_receitas) }}</strong></td>
              </tr>

              <tr class="section-header">
                  <td colspan="2"><strong>(-) Despesas Operacionais</strong></td>
              </tr>
               <tr v-for="despesa in dreData.detalhes_despesas" :key="`desp-${despesa.categoria_id}`">
                  <td class="item-categoria">{{ despesa.categoria_nome }}</td>
                  <td class="text-right text-danger">{{ formatarValor(despesa.total) }}</td>
              </tr>
              <tr class="subtotal">
                  <td><strong>Total Despesas</strong></td>
                  <td class="text-right text-danger"><strong>{{ formatarValor(dreData.total_despesas) }}</strong></td>
              </tr>

               <tr><td colspan="2">&nbsp;</td></tr> <tr class="resultado-final" :class="getResultadoClass(dreData.resultado_liquido)">
                  <td><strong>(=) Resultado Líquido do Período</strong></td>
                   <td class="text-right"><strong>{{ formatarValor(dreData.resultado_liquido) }}</strong></td>
               </tr>
          </tbody>
      </table>
    </div>
     <div v-if="!dreData && !isLoading && !error" class="empty-state card">
          Selecione o período e clique em "Gerar Relatório" para visualizar o DRE.
     </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import apiClient from '@/services/api';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface CategoriaDetalhe {
    categoria_id: number;
    categoria_nome: string;
    total: number;
}

interface DreData {
    total_receitas: number;
    total_despesas: number;
    resultado_liquido: number;
    detalhes_receitas: CategoriaDetalhe[];
    detalhes_despesas: CategoriaDetalhe[];
}

const today = new Date();
const startDate = ref(format(startOfMonth(today), 'yyyy-MM-dd')); // Início do mês atual
const endDate = ref(format(endOfMonth(today), 'yyyy-MM-dd')); // Fim do mês atual

const dreData = ref<DreData | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

function formatarValor(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return 'R$ 0,00';
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(data: string | null | undefined): string {
    if (!data) return '-';
    try {
        // Assume yyyy-MM-dd e adiciona T00:00:00 para tratar como local
        return format(new Date(data + 'T00:00:00'), 'dd/MM/yyyy', { locale: ptBR });
    } catch {
        return 'Inválida';
    }
}


function getResultadoClass(valor: number): string {
    return valor >= 0 ? 'text-success' : 'text-danger';
}

async function fetchDRE() {
  isLoading.value = true;
  error.value = null;
  dreData.value = null; // Limpa dados anteriores

  if (!startDate.value || !endDate.value) {
      error.value = "Por favor, selecione as datas de início e fim.";
      isLoading.value = false;
      return;
  }

  try {
    // URL ajustada para /v1/financeiro/dre/
    const response = await apiClient.get<DreData>('/v1/financeiro/dre/', {
      params: {
        start_date: startDate.value,
        end_date: endDate.value
      }
    });
    dreData.value = response.data;
  } catch (err) {
    console.error("Erro ao gerar DRE:", err);
    error.value = "Não foi possível gerar o relatório. Verifique as datas e tente novamente.";
  } finally {
    isLoading.value = false;
  }
}

function imprimirDRE() {
    const printContent = document.getElementById('dre-print-area');
    if (printContent) {
        const printWindow = window.open('', '_blank', 'height=800,width=800');
        if (printWindow) {
             printWindow.document.write('<html><head><title>Relatório DRE</title>');
            // Adicionar estilos básicos para impressão
            printWindow.document.write(`
                <style>
                    body { font-family: sans-serif; margin: 20px; }
                    .report-header { text-align: center; margin-bottom: 20px; }
                    .report-header h2 { margin: 0; }
                    .report-header p { margin: 5px 0 0 0; color: #555; }
                    .summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid #ccc; padding-bottom: 1rem; }
                    .summary-card { padding: 1rem; border-radius: 5px; text-align: center; color: #333; }
                    .summary-card h4 { margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: normal; color: #555;}
                    .summary-card p { margin: 0; font-size: 1.5rem; font-weight: bold; }
                    .revenue p { color: #198754; }
                    .expenses p { color: #dc3545; }
                    .balance.text-success p { color: #198754; }
                    .balance.text-danger p { color: #dc3545; }
                    .dre-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
                    .dre-table th, .dre-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    .dre-table th { background-color: #f2f2f2; font-weight: bold; }
                    .text-right { text-align: right; }
                    .text-success { color: #198754; }
                    .text-danger { color: #dc3545; }
                    .section-header td { background-color: #f8f9fa; font-weight: bold; padding-top: 15px; }
                    .item-categoria { padding-left: 20px; }
                    .subtotal td { border-top: 1px solid #aaa; font-weight: bold; }
                    .resultado-final td { border-top: 2px solid #333; font-weight: bold; font-size: 1.1em; padding-top: 10px;}
                    .resultado-final.text-success td { color: #198754; }
                    .resultado-final.text-danger td { color: #dc3545; }
                     @media print {
                        .summary-grid { grid-template-columns: repeat(3, 1fr); } /* Garante 3 colunas na impressão */
                        .btn-primary, .btn-secondary { display: none; } /* Esconde botões */
                        body { margin: 0; } /* Remove margens do body na impressão */
                    }
                </style>
            `);
            printWindow.document.write('</head><body>');
            printWindow.document.write(printContent.innerHTML);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            printWindow.focus(); // Necessário para alguns navegadores
             // Espera um pouco para garantir que o conteúdo foi carregado antes de imprimir
            setTimeout(() => {
                printWindow.print();
                // printWindow.close(); // Fecha automaticamente após imprimir (opcional)
            }, 500);
        }
    } else {
        alert("Não foi possível encontrar a área de impressão.");
    }
}


// Inicialmente não busca os dados, espera o usuário clicar em gerar.
// onMounted(fetchDRE); // Removido para não carregar ao montar
</script>

<style scoped>
.page-container {
    /* padding: 2rem; */ /* Removido */
    padding: 0; /* Adicionado */
}

/* Regra .view-header removida */

.card { /* Estilo base comum */
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem; /* Espaçamento padrão abaixo */
}
.card:last-child {
    margin-bottom: 0;
}

.filters-card {
    display: flex;
    flex-wrap: wrap; /* Permite quebrar linha */
    gap: 1rem 1.5rem;
    align-items: flex-end; /* Alinha na base */
}
.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    flex-grow: 1; /* Tenta ocupar espaço */
    min-width: 150px; /* Largura mínima */
}
.form-group label {
    font-weight: 500;
    font-size: 0.85rem;
    color: #495057;
}
.filter-input { /* Aplica aos inputs de data */
    padding: 0.6rem 0.8rem;
    border: 1px solid #ced4da;
    border-radius: 5px;
    font-size: 0.9rem;
    width: 100%;
    box-sizing: border-box;
}
.btn-primary, .btn-secondary {
    padding: 0.6rem 1.2rem; /* Padding ajustado */
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    height: fit-content; /* Alinha com inputs */
    display: inline-flex; /* Para alinhar ícone se houver */
    align-items: center;
    gap: 0.5rem;
}
.btn-primary { background-color: #0d6efd; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-primary:disabled, .btn-secondary:disabled { background-color: #adb5bd; cursor: not-allowed; }

.loading-state, .error-message, .empty-state {
  text-align: center; padding: 2rem; color: #6c757d;
}
.error-message { color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; }

.results-container {
    padding: 2rem; /* Adiciona padding interno ao container de resultados */
}

.report-header {
    text-align: center;
    margin-bottom: 2rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 1rem;
}
.report-header h2 {
    margin: 0;
    color: #343a40;
}
.report-header p {
    margin: 5px 0 0 0;
    color: #6c757d;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* Responsivo */
    gap: 1.5rem;
    margin-bottom: 2rem;
}
.summary-card {
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    color: #fff; /* Texto branco para contraste */
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.summary-card h4 { margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 500; opacity: 0.9; }
.summary-card p { margin: 0; font-size: 2rem; font-weight: 600; }

.revenue { background-color: #198754; } /* Verde escuro */
.expenses { background-color: #dc3545; } /* Vermelho */
.balance { background-color: #0d6efd; } /* Azul */
/* Cor dinâmica para o resultado no card */
.balance.text-success { background-color: #198754; }
.balance.text-danger { background-color: #dc3545; }


.dre-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    font-size: 0.95rem; /* Tamanho da fonte da tabela */
}
.dre-table th, .dre-table td {
    border: 1px solid #e9ecef; /* Borda mais suave */
    padding: 0.8rem 1rem;
    text-align: left;
    vertical-align: middle;
}
.dre-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #495057;
}
.text-right { text-align: right; }
.text-success { color: #198754; }
.text-danger { color: #dc3545; }

.section-header td {
    background-color: #f1f3f5; /* Fundo levemente diferente */
    font-weight: bold;
    padding-top: 1rem; /* Mais espaço acima */
    padding-bottom: 0.5rem;
    color: #343a40;
}
.item-categoria {
    padding-left: 2rem; /* Indentação */
    color: #495057;
}
.subtotal td {
    border-top: 1px solid #adb5bd; /* Linha de subtotal */
    font-weight: bold;
    padding-top: 0.8rem;
    background-color: #f8f9fa;
}
.resultado-final td {
    border-top: 2px solid #343a40; /* Linha dupla para resultado final */
    font-weight: bold;
    font-size: 1.1em; /* Maior */
    padding-top: 1rem;
    padding-bottom: 1rem;
}
/* Cor dinâmica para o resultado final */
.resultado-final.text-success td { color: #198754; }
.resultado-final.text-danger td { color: #dc3545; }

</style>
<template>
  <div class="min-h-screen bg-gray-50/50 p-6 font-sans text-gray-700">
    
    <header class="mb-8">
      <div class="flex justify-between items-end">
        <div>
           <nav class="flex items-center gap-2 text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">
              <span>Início</span>
              <i class="fas fa-chevron-right text-[10px] text-gray-300"></i>
              <span class="text-blue-600 font-bold">Visão Geral</span>
           </nav>
           <h1 class="text-2xl font-light text-gray-800 tracking-tight">
             Dashboard
           </h1>
        </div>
        
        <div>
            <button 
              @click="fetchData" 
              class="flex items-center justify-center w-10 h-10 bg-white border border-gray-200 rounded-lg text-gray-500 hover:text-blue-600 hover:border-blue-200 hover:bg-blue-50 transition-all shadow-sm active:scale-95 disabled:opacity-50"
              :disabled="isLoading" 
              title="Atualizar"
            >
                <i class="fas fa-sync-alt" :class="{ 'animate-spin': isLoading }"></i>
            </button>
        </div>
      </div>
    </header>

    <div v-if="isLoading" class="flex flex-col gap-6 animate-pulse">
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        <div class="h-32 bg-gray-200 rounded-xl" v-for="n in 4" :key="`sk-kpi-${n}`"></div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="h-96 bg-gray-200 rounded-xl"></div>
          <div class="h-96 bg-gray-200 rounded-xl lg:col-span-2"></div>
      </div>
    </div>

    <div v-if="error" class="p-4 bg-red-50 border border-red-100 rounded-xl flex items-center justify-between text-red-700 mb-6 shadow-sm">
        <div class="flex items-center gap-3">
          <i class="fas fa-exclamation-triangle text-xl"></i>
          <span class="font-medium">{{ error }}</span>
        </div>
        <button @click="fetchData" class="px-4 py-1.5 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition-colors shadow-sm">
          Tentar Novamente
        </button>
    </div>

    <div v-if="!isLoading && !error" class="animate-fade-in animate-duration-300">
      
      <section class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
        
        <BaseStatCard 
          title="Imóveis Ativos" 
          :value="geralStats?.total_imoveis || 0"
          color="primary"
          @click="$router.push('/imoveis')"
        >
          <template #icon><i class="fas fa-home text-xl"></i></template>
        </BaseStatCard>

        <BaseStatCard 
          title="Clientes Base" 
          :value="geralStats?.total_clientes || 0"
          color="purple"
          @click="$router.push('/clientes')"
        >
          <template #icon><i class="fas fa-users text-xl"></i></template>
        </BaseStatCard>

        <BaseStatCard 
          title="Contratos Ativos" 
          :value="geralStats?.total_contratos_ativos || 0"
          color="warning"
          @click="$router.push('/contratos')"
        >
          <template #icon><i class="fas fa-file-signature text-xl"></i></template>
        </BaseStatCard>

        <BaseStatCard 
          title="A Receber (30d)" 
          :value="formatCurrency(geralStats?.total_a_receber_30d)"
          color="success"
        >
          <template #icon><i class="fas fa-chart-line text-xl"></i></template>
        </BaseStatCard>
        
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 h-full flex flex-col">
            <div class="flex justify-between items-center mb-6 border-b border-gray-50 pb-4">
                <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                    <i class="fas fa-wallet text-sm"></i>
                  </div>
                  Finanças do Mês
                </h3>
                <router-link to="/financeiro" class="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline">
                  Detalhes
                </router-link>
            </div>

            <div class="flex flex-col gap-4 flex-1">
                <div class="flex items-center gap-4 p-3 rounded-lg bg-emerald-50/50 border border-emerald-100/50">
                    <div class="w-10 h-10 rounded-full bg-white border border-emerald-100 flex items-center justify-center text-emerald-600 shadow-sm">
                      <i class="fas fa-arrow-up text-sm"></i>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-xs font-semibold text-gray-500 uppercase">Receitas Recebidas</span>
                        <span class="text-lg font-bold text-emerald-700">{{ formatCurrency(finStats?.a_receber?.pago_mes_atual) }}</span>
                    </div>
                </div>

                <div class="flex items-center gap-4 p-3 rounded-lg bg-red-50/50 border border-red-100/50">
                    <div class="w-10 h-10 rounded-full bg-white border border-red-100 flex items-center justify-center text-red-600 shadow-sm">
                      <i class="fas fa-arrow-down text-sm"></i>
                    </div>
                    <div class="flex flex-col">
                        <span class="text-xs font-semibold text-gray-500 uppercase">Despesas Pagas</span>
                        <span class="text-lg font-bold text-red-700">{{ formatCurrency(finStats?.a_pagar?.pago_mes_atual) }}</span>
                    </div>
                </div>

                <div class="mt-auto pt-4 border-t border-dashed border-gray-200 flex justify-between items-end">
                    <span class="text-sm font-bold text-gray-600">Saldo em Caixa</span>
                    <span class="text-2xl font-extrabold" :class="saldoMesAtual >= 0 ? 'text-blue-600' : 'text-red-600'">
                        {{ formatCurrency(saldoMesAtual) }}
                    </span>
                </div>
            </div>
        </div>

        <div class="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm p-6 h-full flex flex-col">
            <div class="flex justify-between items-center mb-6 border-b border-gray-50 pb-4">
                <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
                  <div class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                     <i class="fas fa-key text-sm"></i>
                  </div>
                  Monitoramento de Aluguéis
                </h3>
                <router-link to="/contratos" class="text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:underline">
                  Ver Contratos
                </router-link>
            </div>

            <div class="flex flex-wrap gap-3 mb-6">
                <div class="px-3 py-1.5 rounded-lg bg-amber-50 text-amber-700 border border-amber-100 text-xs font-medium flex items-center gap-2" v-if="aluguelStats?.alugueis_a_vencer">
                    <i class="fas fa-clock"></i> <strong>{{ aluguelStats.alugueis_a_vencer }}</strong> a vencer (7d)
                </div>
                <div class="px-3 py-1.5 rounded-lg bg-red-50 text-red-700 border border-red-100 text-xs font-medium flex items-center gap-2" v-if="aluguelStats?.alugueis_atrasados">
                    <i class="fas fa-exclamation-circle"></i> <strong>{{ aluguelStats.alugueis_atrasados }}</strong> em atraso
                </div>
                <div v-if="!aluguelStats?.alugueis_a_vencer && !aluguelStats?.alugueis_atrasados" class="px-3 py-1.5 rounded-lg bg-green-50 text-green-700 border border-green-100 text-xs font-medium flex items-center gap-2">
                    <i class="fas fa-check-circle"></i> Tudo em dia!
                </div>
            </div>

            <div class="overflow-x-auto w-full">
                <table class="w-full text-sm text-left border-collapse" v-if="aluguelStats?.proximos_alugueis?.length">
                    <thead>
                        <tr class="text-xs text-gray-400 uppercase tracking-wider border-b border-gray-100">
                            <th class="py-3 font-semibold pl-2">Imóvel</th>
                            <th class="py-3 font-semibold">Inquilino</th>
                            <th class="py-3 font-semibold text-center">Vencimento</th>
                            <th class="py-3 font-semibold text-right pr-2">Valor</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50">
                        <tr 
                          v-for="aluguel in aluguelStats.proximos_alugueis.slice(0, 5)" 
                          :key="aluguel.id"
                          class="hover:bg-gray-50/80 transition-colors"
                        >
                            <td class="py-3 pl-2">
                                <div class="font-medium text-gray-800 truncate max-w-[180px]" :title="aluguel.imovel_titulo">
                                  {{ aluguel.imovel_titulo }}
                                </div>
                            </td>
                            <td class="py-3">
                                <span class="text-gray-500 truncate block max-w-[120px]" :title="aluguel.inquilino_nome">
                                  {{ aluguel.inquilino_nome }}
                                </span>
                            </td>
                            <td class="py-3 text-center">
                                <span class="px-2.5 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-600">
                                  {{ formatDate(aluguel.data_vencimento) }}
                                </span>
                            </td>
                            <td class="py-3 text-right pr-2 font-bold text-gray-700">
                              {{ formatCurrency(aluguel.valor) }}
                            </td>
                        </tr>
                    </tbody>
                </table>
                
                <div v-else class="flex flex-col items-center justify-center py-12 text-gray-400 bg-gray-50/50 rounded-lg border border-dashed border-gray-200">
                    <i class="fas fa-clipboard-check text-3xl mb-2 opacity-30"></i>
                    <p class="text-sm">Nenhum vencimento próximo.</p>
                </div>
            </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api';
import BaseStatCard from '@/components/BaseStatCard.vue';
import '@fortawesome/fontawesome-free/css/all.css';

// --- Interfaces ---
interface GeralStats {
  total_imoveis: number;
  total_clientes: number;
  total_contratos_ativos: number;
  total_a_receber_30d: number;
}

interface FinStats {
    a_receber: { pendente: number; pago_mes_atual: number; };
    a_pagar: { pendente: number; pago_mes_atual: number; };
    saldo_previsto: number;
}

interface AluguelItem {
    id: number;
    imovel_titulo: string;
    inquilino_nome: string; 
    data_vencimento: string;
    valor: number;
}

interface AluguelStats {
  alugueis_a_vencer: number;
  alugueis_atrasados: number;
  proximos_alugueis: AluguelItem[];
}

// --- Estados ---
const geralStats = ref<GeralStats | null>(null);
const finStats = ref<FinStats | null>(null);
const aluguelStats = ref<AluguelStats | null>(null);

const isLoading = ref(true);
const error = ref<string | null>(null);

// --- COMPUTED ---
const saldoMesAtual = computed(() => {
  if (!finStats.value) return 0;
  const receita = Number(finStats.value.a_receber.pago_mes_atual) || 0;
  const despesa = Number(finStats.value.a_pagar.pago_mes_atual) || 0;
  return receita - despesa;
});

// --- Helpers ---
function formatCurrency(value: number | string | undefined) {
  if (value === undefined || value === null || value === '') return 'R$ 0,00';
  const num = Number(value);
  if (isNaN(num)) return 'R$ 0,00';
  return num.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatDate(dateStr: string) {
    if (!dateStr) return '-';
    try {
        const [year, month, day] = dateStr.split('-');
        return `${day}/${month}`;
    } catch { return dateStr; }
}

async function fetchData() {
  isLoading.value = true;
  error.value = null;
  
  try {
    const [resGeral, resFin, resAluguel] = await Promise.all([
        apiClient.get<GeralStats>('/v1/stats/'),
        apiClient.get<FinStats>('/v1/financeiro/transacoes/stats/'),
        apiClient.get<AluguelStats>('/v1/alugueis/dashboard-stats/')
    ]);

    geralStats.value = resGeral.data;
    finStats.value = resFin.data;
    aluguelStats.value = resAluguel.data;

  } catch (err: any) {
    console.error("Erro ao carregar dashboard:", err);
    error.value = 'Não foi possível carregar os dados. Verifique sua conexão.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => { fetchData(); });
</script>
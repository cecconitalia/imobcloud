<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import BaseStatCard from '../components/BaseStatCard.vue';

const authStore = useAuthStore();
const isLoading = ref(false);
const stats = ref<any>(null);

// --- PERMISSÕES COMPUTADAS ---
const isAdmin = computed(() => authStore.user?.is_superuser || authStore.user?.is_admin);

const canViewFinance = computed(() => {
    if (isAdmin.value) return true;
    const permissions = authStore.user?.custom_permissions || [];
    return permissions.includes('view_financeiro_dash') || permissions.includes('financeiro_view');
});

const canViewImoveis = computed(() => {
    if (isAdmin.value) return true;
    const permissions = authStore.user?.custom_permissions || [];
    return permissions.length === 0 || permissions.includes('view_imovel');
});

// --- UI HELPERS ---
const firstName = computed(() => authStore.user?.first_name || authStore.user?.username || 'Usuário');

const userRoleLabel = computed(() => {
    if (isAdmin.value) return 'Painel Administrativo';
    return 'Painel do Corretor';
});

const currentDate = computed(() => {
    return format(new Date(), "EEEE, d 'de' MMMM", { locale: ptBR })
        .replace(/^\w/, (c) => c.toUpperCase());
});

// --- API ---
const refreshData = async () => {
    isLoading.value = true;
    try {
        const response = await api.get('/v1/core/stats/'); 
        stats.value = response.data;
    } catch (error) {
        console.error("Erro ao carregar dashboard:", error);
    } finally {
        isLoading.value = false;
    }
};

// --- FORMATTERS ---
const formatCurrency = (val: any) => {
    const num = Number(val);
    if (isNaN(num)) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(num);
};

const formatTime = (dateStr: string) => {
    if(!dateStr) return '';
    try {
        return format(parseISO(dateStr), 'HH:mm');
    } catch (e) { return '--:--'; }
};

const getDay = (dateStr: string) => {
    if(!dateStr) return '';
    try {
        return format(parseISO(dateStr), 'dd');
    } catch (e) { return '00'; }
};

const getMonth = (dateStr: string) => {
    if(!dateStr) return '';
    try {
        return format(parseISO(dateStr), 'MMM', { locale: ptBR }).toUpperCase();
    } catch (e) { return 'MES'; }
};

const calculatePercent = (val: number, total: number) => {
    if (!total || total === 0) return 0;
    return Math.min(100, (val / total) * 100);
};

onMounted(() => {
    refreshData();
});
</script>

<template>
  <div class="p-6 md:p-8 min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    
    <header class="mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4 animate-fade-in-down">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
          Olá, {{ firstName }}! <span class="animate-wave inline-block origin-bottom-right text-3xl">👋</span>
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 font-medium flex items-center gap-2">
          <div class="i-mdi-calendar text-blue-500"></div>
          {{ currentDate }} &bull; {{ userRoleLabel }}
        </p>
      </div>
      
      <div class="flex gap-3 w-full md:w-auto">
        <router-link :to="{ name: 'clientes' }" class="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-semibold shadow-sm transition-all hover:-translate-y-0.5 text-sm no-underline">
           <div class="i-mdi-account-group text-lg"></div>
           <span class="hidden md:inline">Clientes</span>
        </router-link>
        
        <router-link :to="{ name: 'funil-vendas' }" class="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold shadow-sm transition-all hover:-translate-y-0.5 text-sm no-underline">
           <div class="i-mdi-filter text-lg"></div>
           <span class="hidden md:inline">Funil</span>
        </router-link>

        <button @click="refreshData" class="w-10 h-10 md:w-auto md:px-4 md:h-auto flex items-center justify-center gap-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm">
            <div class="i-mdi-refresh text-xl" :class="{ 'animate-spin': isLoading }"></div>
        </button>
      </div>
    </header>

    <div v-if="isLoading && !stats" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
        <div class="h-32 bg-gray-200 dark:bg-gray-800 rounded-2xl" v-for="i in 4" :key="i"></div>
    </div>

    <div v-else class="space-y-8 animate-fade-in-up">
        
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            
            <BaseStatCard
                title="Negócios no Funil"
                :value="stats?.oportunidades_ativas || 0"
                icon="i-mdi-filter"
                color="blue"
                trend="Funil Ativo"
                trend-direction="neutral"
                @click="$router.push({ name: 'funil-vendas' })"
                class="cursor-pointer hover:ring-2 hover:ring-blue-500/50"
            />

            <BaseStatCard
                title="Tarefas Pendentes"
                :value="stats?.tarefas_pendentes || 0"
                icon="i-mdi-calendar-check"
                color="amber"
                trend="Prioridade Alta"
                trend-direction="down"
                @click="$router.push({ name: 'tarefas-board' })"
                class="cursor-pointer hover:ring-2 hover:ring-amber-500/50"
            />

            <BaseStatCard v-if="canViewFinance"
                title="Receita (Mês)"
                :value="stats?.receita_mes || 0"
                :is-money="true"
                icon="i-mdi-currency-usd"
                color="emerald"
                trend="Entradas Confirmadas"
                trend-direction="up"
                @click="$router.push({ name: 'financeiro-dashboard' })"
                class="cursor-pointer hover:ring-2 hover:ring-emerald-500/50"
            />

            <BaseStatCard v-if="canViewImoveis"
                title="Imóveis Ativos"
                :value="stats?.imoveis_ativos || 0"
                icon="i-mdi-home-city"
                color="purple"
                trend="Disponíveis no Site"
                trend-direction="neutral"
                @click="$router.push({ name: 'imoveis' })"
                class="cursor-pointer hover:ring-2 hover:ring-purple-500/50"
            />
        </section>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div class="lg:col-span-2 space-y-8">
                
                <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
                    <div class="p-5 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50">
                        <h3 class="font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                            <div class="i-mdi-check-circle text-amber-500"></div> 
                            Minhas Tarefas de Hoje
                        </h3>
                        <router-link :to="{ name: 'tarefas-board' }" class="text-xs font-bold text-blue-600 hover:underline uppercase tracking-wide no-underline">Ver Todas</router-link>
                    </div>
                    
                    <div class="p-0">
                        <div v-if="!stats?.tarefas_hoje?.length" class="flex flex-col items-center justify-center py-10 text-gray-400">
                            <div class="i-mdi-emoticon-happy-outline text-5xl mb-3 opacity-50"></div>
                            <p class="text-sm font-medium">Tudo em dia! Nenhuma tarefa para hoje.</p>
                        </div>
                        
                        <ul v-else class="divide-y divide-gray-100 dark:divide-gray-700 m-0 p-0 list-none">
                            <li v-for="task in stats.tarefas_hoje" :key="task.id" class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors flex items-start gap-3 group cursor-pointer" @click="$router.push({ name: 'tarefas-board' })">
                                <div class="mt-1 w-5 h-5 rounded-full border-2 border-gray-300 dark:border-gray-600 group-hover:border-blue-500 transition-colors flex-shrink-0"></div>
                                <div class="flex-1 min-w-0">
                                    <span class="block text-sm font-semibold text-gray-800 dark:text-gray-200 group-hover:text-blue-600 transition-colors truncate">{{ task.titulo }}</span>
                                    <div class="flex items-center gap-2 mt-1 text-xs text-gray-500">
                                        <span class="bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded text-gray-600 dark:text-gray-300 whitespace-nowrap">{{ formatTime(task.data_vencimento) }}</span>
                                        <span v-if="task.cliente_nome" class="truncate">&bull; {{ task.cliente_nome }}</span>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

                <div v-if="canViewFinance" class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden">
                    <div class="p-5 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50">
                        <h3 class="font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                            <div class="i-mdi-chart-line text-emerald-500"></div> 
                            Fluxo Financeiro (Previsão)
                        </h3>
                        <router-link :to="{ name: 'financeiro-dashboard' }" class="text-xs font-bold text-blue-600 hover:underline uppercase tracking-wide no-underline">Detalhes</router-link>
                    </div>
                    <div class="p-6 grid grid-cols-1 sm:grid-cols-3 gap-6 divide-y sm:divide-y-0 sm:divide-x divide-gray-100 dark:divide-gray-700">
                        <div class="text-center sm:text-left">
                            <p class="text-xs font-bold text-gray-500 uppercase mb-1">Entradas</p>
                            <p class="text-lg font-bold text-emerald-600">{{ formatCurrency(stats?.financeiro_previsto_entrada || 0) }}</p>
                        </div>
                        <div class="text-center sm:text-left pt-4 sm:pt-0 sm:pl-6">
                            <p class="text-xs font-bold text-gray-500 uppercase mb-1">Saídas</p>
                            <p class="text-lg font-bold text-rose-600">{{ formatCurrency(stats?.financeiro_previsto_saida || 0) }}</p>
                        </div>
                        <div class="text-center sm:text-left pt-4 sm:pt-0 sm:pl-6">
                            <p class="text-xs font-bold text-gray-500 uppercase mb-1">Saldo Projetado</p>
                            <p class="text-xl font-bold text-gray-800 dark:text-white">
                                {{ formatCurrency((stats?.financeiro_previsto_entrada || 0) - (stats?.financeiro_previsto_saida || 0)) }}
                            </p>
                        </div>
                    </div>
                </div>

            </div>

            <div class="space-y-8">
                
                <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm p-6">
                    <div class="flex justify-between items-center mb-6">
                        <h3 class="font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                            <div class="i-mdi-filter-variant text-blue-500"></div> Funil
                        </h3>
                        <router-link :to="{ name: 'funil-vendas' }" class="text-xs font-bold text-blue-600 hover:underline no-underline">ABRIR</router-link>
                    </div>

                    <div v-if="!stats?.funil_resumo?.length" class="text-center py-8 text-gray-400 text-sm">
                        Nenhuma oportunidade ativa.
                        <router-link :to="{ name: 'oportunidade-nova' }" class="block mt-2 text-blue-600 font-bold hover:underline no-underline">Criar Nova</router-link>
                    </div>

                    <div v-else class="space-y-4">
                        <div v-for="(fase, index) in stats.funil_resumo" :key="index">
                            <div class="flex justify-between text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                                <span>{{ fase.titulo }}</span>
                                <span class="font-bold text-gray-800 dark:text-white">{{ fase.total }}</span>
                            </div>
                            <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
                                <div class="bg-blue-500 h-2.5 rounded-full transition-all duration-1000 ease-out" 
                                     :style="{ width: calculatePercent(fase.total, stats.total_oportunidades) + '%' }"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm p-6">
                    <div class="flex justify-between items-center mb-6">
                        <h3 class="font-bold text-gray-800 dark:text-gray-100 flex items-center gap-2">
                            <div class="i-mdi-map-marker-path text-purple-500"></div> Visitas
                        </h3>
                        <router-link :to="{ name: 'visitas' }" class="text-xs font-bold text-blue-600 hover:underline no-underline">AGENDA</router-link>
                    </div>

                    <div v-if="!stats?.proximas_visitas?.length" class="text-center py-8 text-gray-400 text-sm">
                        Nenhuma visita agendada.
                    </div>

                    <div v-else class="space-y-4">
                        <div v-for="visita in stats.proximas_visitas" :key="visita.id" class="flex items-center gap-4 group cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 p-2 rounded-xl transition-colors -mx-2" @click="$router.push({ name: 'visitas' })">
                            <div class="w-12 h-12 bg-purple-50 dark:bg-purple-900/20 rounded-xl flex flex-col items-center justify-center text-purple-600 dark:text-purple-400 border border-purple-100 dark:border-purple-800 flex-shrink-0">
                                <span class="text-xs font-bold uppercase leading-none">{{ getMonth(visita.data) }}</span>
                                <span class="text-lg font-bold leading-none mt-0.5">{{ getDay(visita.data) }}</span>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="text-sm font-bold text-gray-800 dark:text-white truncate group-hover:text-purple-600 transition-colors">
                                    {{ visita.imovel_titulo || 'Imóvel #' + visita.imovel_id }}
                                </p>
                                <p class="text-xs text-gray-500 truncate flex items-center gap-1">
                                    <div class="i-mdi-account text-gray-400"></div> {{ visita.cliente_nome }}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.animate-wave {
  animation: wave 2.5s infinite;
  display: inline-block;
}

.animate-fade-in-down {
  animation: fadeInDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes wave {
  0% { transform: rotate(0deg); }
  10% { transform: rotate(14deg); }
  20% { transform: rotate(-8deg); }
  30% { transform: rotate(14deg); }
  40% { transform: rotate(-4deg); }
  50% { transform: rotate(10deg); }
  60% { transform: rotate(0deg); }
  100% { transform: rotate(0deg); }
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
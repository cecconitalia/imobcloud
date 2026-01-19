<template>
  <div class="page-container">
    
    <header class="dash-header">
      <div class="welcome-area">
        <h1>Olá, {{ firstName }}! <span class="wave">👋</span></h1>
        <p class="subtitle">{{ currentDate }} &bull; {{ userRoleLabel }}</p>
      </div>
      
      <div class="header-actions">
        <router-link :to="{ name: 'clientes' }" class="btn-quick action-green" title="Gerenciar Clientes">
            <i class="fas fa-users"></i> <span class="hide-mobile">Clientes</span>
        </router-link>
        
        <router-link :to="{ name: 'funil-vendas' }" class="btn-quick action-blue" title="Ver Funil de Vendas">
            <i class="fas fa-filter"></i> <span class="hide-mobile">Funil</span>
        </router-link>

        <button @click="refreshData" class="btn-icon-refresh" title="Atualizar Dashboard">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
        </button>
      </div>
    </header>

    <div v-if="isLoading && !stats" class="loading-skeleton">
        <div class="skeleton-card" v-for="i in 4" :key="i"></div>
    </div>

    <div v-else class="dashboard-content">
        
        <section class="kpi-grid">
            
            <div class="kpi-card" @click="$router.push({ name: 'funil-vendas' })" style="cursor: pointer;">
                <div class="kpi-icon bg-blue-soft"><i class="fas fa-filter text-blue"></i></div>
                <div class="kpi-data">
                    <span class="kpi-value">{{ stats?.oportunidades_ativas || 0 }}</span>
                    <span class="kpi-label">Negócios no Funil</span>
                </div>
            </div>

            <div class="kpi-card" @click="$router.push({ name: 'tarefas-board' })" style="cursor: pointer;">
                <div class="kpi-icon bg-orange-soft"><i class="fas fa-tasks text-orange"></i></div>
                <div class="kpi-data">
                    <span class="kpi-value">{{ stats?.tarefas_pendentes || 0 }}</span>
                    <span class="kpi-label">Tarefas Pendentes</span>
                </div>
            </div>

            <div v-if="canViewFinance" class="kpi-card" @click="$router.push({ name: 'financeiro-dashboard' })" style="cursor: pointer;">
                <div class="kpi-icon bg-green-soft"><i class="fas fa-dollar-sign text-green"></i></div>
                <div class="kpi-data">
                    <span class="kpi-value">{{ formatCurrency(stats?.receita_mes || 0) }}</span>
                    <span class="kpi-label">Receita (Mês Atual)</span>
                </div>
            </div>

            <div v-if="canViewImoveis" class="kpi-card" @click="$router.push({ name: 'imoveis' })" style="cursor: pointer;">
                <div class="kpi-icon bg-purple-soft"><i class="fas fa-home text-purple"></i></div>
                <div class="kpi-data">
                    <span class="kpi-value">{{ stats?.imoveis_ativos || 0 }}</span>
                    <span class="kpi-label">Imóveis Ativos</span>
                </div>
            </div>
        </section>

        <div class="main-grid">
            
            <div class="grid-column">
                
                <div class="widget-card">
                    <div class="widget-header">
                        <h3><i class="fas fa-check-circle text-orange"></i> Minhas Tarefas de Hoje</h3>
                        <router-link :to="{ name: 'tarefas-board' }" class="link-small">Ver todas</router-link>
                    </div>
                    <div class="widget-body">
                        <div v-if="!stats?.tarefas_hoje?.length" class="empty-widget">
                            <i class="far fa-smile"></i>
                            <p>Tudo em dia! Nenhuma tarefa para hoje.</p>
                        </div>
                        <ul v-else class="task-list">
                            <li v-for="task in stats.tarefas_hoje" :key="task.id" class="task-item">
                                <div class="task-check"></div>
                                <div class="task-info">
                                    <span class="task-title">{{ task.titulo }}</span>
                                    <span class="task-meta">{{ formatTime(task.data_vencimento) }} &bull; {{ task.cliente_nome }}</span>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

                <div v-if="canViewFinance" class="widget-card mt-4">
                    <div class="widget-header">
                        <h3><i class="fas fa-chart-line text-green"></i> Desempenho Financeiro</h3>
                        <router-link :to="{ name: 'financeiro-dashboard' }" class="link-small">Detalhes</router-link>
                    </div>
                    <div class="widget-body finance-summary">
                        <div class="fin-row">
                            <span>Entradas Previstas</span>
                            <span class="fin-val text-green">{{ formatCurrency(stats?.financeiro_previsto_entrada || 0) }}</span>
                        </div>
                        <div class="fin-row">
                            <span>Saídas Previstas</span>
                            <span class="fin-val text-red">{{ formatCurrency(stats?.financeiro_previsto_saida || 0) }}</span>
                        </div>
                        <div class="fin-divider"></div>
                        <div class="fin-row total">
                            <span>Saldo Projetado</span>
                            <span class="fin-val">{{ formatCurrency((stats?.financeiro_previsto_entrada || 0) - (stats?.financeiro_previsto_saida || 0)) }}</span>
                        </div>
                    </div>
                </div>

            </div>

            <div class="grid-column">
                
                <div class="widget-card">
                    <div class="widget-header">
                        <h3><i class="fas fa-filter text-blue"></i> Funil de Vendas</h3>
                        <router-link :to="{ name: 'funil-vendas' }" class="link-small">Abrir Quadro</router-link>
                    </div>
                    <div class="widget-body">
                        <div class="funnel-chart">
                            <div v-for="(fase, index) in stats?.funil_resumo || []" :key="index" class="funnel-row">
                                <div class="funnel-label">{{ fase.titulo }}</div>
                                <div class="funnel-bar-container">
                                    <div class="funnel-bar" :style="{ width: calculatePercent(fase.total, stats.total_oportunidades) + '%' }"></div>
                                    <span class="funnel-count">{{ fase.total }}</span>
                                </div>
                            </div>
                            <div v-if="!stats?.funil_resumo?.length" class="empty-widget">
                                <p>Nenhuma oportunidade ativa.</p>
                                <router-link :to="{ name: 'oportunidade-nova' }" class="btn-link-sm">Criar Oportunidade</router-link>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="widget-card mt-4">
                    <div class="widget-header">
                        <h3><i class="fas fa-map-marker-alt text-purple"></i> Próximas Visitas</h3>
                        <router-link :to="{ name: 'visitas' }" class="link-small">Agenda</router-link>
                    </div>
                    <div class="widget-body">
                        <div v-if="!stats?.proximas_visitas?.length" class="empty-widget">
                            <p>Nenhuma visita agendada.</p>
                        </div>
                        <div v-else class="visit-list">
                            <div v-for="visita in stats.proximas_visitas" :key="visita.id" class="visit-item">
                                <div class="visit-date">
                                    <span class="day">{{ getDay(visita.data) }}</span>
                                    <span class="month">{{ getMonth(visita.data) }}</span>
                                </div>
                                <div class="visit-details">
                                    <strong>{{ visita.imovel_titulo || 'Imóvel #' + visita.imovel_id }}</strong>
                                    <span>{{ visita.cliente_nome }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { format, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

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
    return format(parseISO(dateStr), 'HH:mm');
};

const getDay = (dateStr: string) => {
    if(!dateStr) return '';
    return format(parseISO(dateStr), 'dd');
};

const getMonth = (dateStr: string) => {
    if(!dateStr) return '';
    return format(parseISO(dateStr), 'MMM', { locale: ptBR }).toUpperCase();
};

const calculatePercent = (val: number, total: number) => {
    if (!total || total === 0) return 0;
    return Math.min(100, (val / total) * 100);
};

onMounted(() => {
    refreshData();
});
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f4f7f6;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER */
.dash-header {
    display: flex; justify-content: space-between; align-items: flex-end;
    margin-bottom: 2rem;
}
.welcome-area h1 { font-size: 1.8rem; color: #1e293b; font-weight: 700; margin: 0; display: flex; align-items: center; gap: 10px; }
.wave { font-size: 1.5rem; animation: wave 2s infinite; display: inline-block; transform-origin: 70% 70%; }
.subtitle { color: #64748b; font-size: 0.9rem; margin-top: 5px; font-weight: 500; text-transform: capitalize; }

.header-actions { display: flex; gap: 10px; }

.btn-quick {
    padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; font-size: 0.85rem;
    text-decoration: none; display: flex; align-items: center; gap: 8px; transition: transform 0.2s;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: white;
}
.btn-quick:hover { transform: translateY(-2px); }
.action-green { background: linear-gradient(135deg, #10b981, #059669); }
.action-blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }

.btn-icon-refresh {
    width: 40px; height: 40px; border-radius: 8px; border: 1px solid #e2e8f0;
    background: white; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
}
.btn-icon-refresh:hover { background: #f8fafc; color: #2563eb; border-color: #cbd5e1; }

/* KPI GRID */
.kpi-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem; margin-bottom: 2rem;
}

.kpi-card {
    background: white; border-radius: 12px; padding: 1.5rem;
    display: flex; align-items: center; gap: 1.2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #f1f5f9;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08); }

.kpi-icon {
    width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem;
}
.kpi-data { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: #1e293b; line-height: 1.1; }
.kpi-label { font-size: 0.75rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-top: 4px; }

/* Colors Utility */
.bg-blue-soft { background: #eff6ff; } .text-blue { color: #3b82f6; }
.bg-green-soft { background: #f0fdf4; } .text-green { color: #10b981; }
.bg-orange-soft { background: #fff7ed; } .text-orange { color: #f59e0b; }
.bg-purple-soft { background: #f5f3ff; } .text-purple { color: #8b5cf6; }
.text-red { color: #ef4444; }

/* MAIN GRID */
.main-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; }

.widget-card {
    background: white; border-radius: 12px; border: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02); overflow: hidden; display: flex; flex-direction: column;
}
.mt-4 { margin-top: 1.5rem; }

.widget-header {
    padding: 1.2rem 1.5rem; border-bottom: 1px solid #f1f5f9;
    display: flex; justify-content: space-between; align-items: center;
}
.widget-header h3 { font-size: 1rem; color: #334155; margin: 0; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.link-small { font-size: 0.8rem; color: #3b82f6; text-decoration: none; font-weight: 500; }
.link-small:hover { text-decoration: underline; }

.widget-body { padding: 1.5rem; }

/* TAREFAS LIST */
.task-list { list-style: none; padding: 0; margin: 0; }
.task-item { display: flex; align-items: flex-start; gap: 12px; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px dashed #f1f5f9; }
.task-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.task-check { width: 18px; height: 18px; border: 2px solid #cbd5e1; border-radius: 50%; margin-top: 3px; cursor: pointer; }
.task-info { display: flex; flex-direction: column; }
.task-title { font-size: 0.9rem; color: #334155; font-weight: 500; }
.task-meta { font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }

/* FINANCE SUMMARY */
.finance-summary { display: flex; flex-direction: column; gap: 10px; }
.fin-row { display: flex; justify-content: space-between; font-size: 0.9rem; color: #475569; }
.fin-val { font-weight: 600; font-family: monospace; font-size: 1rem; }
.fin-divider { height: 1px; background: #e2e8f0; margin: 5px 0; }
.fin-row.total { color: #1e293b; font-weight: 700; font-size: 1.1rem; }

/* FUNNEL CHART */
.funnel-row { margin-bottom: 12px; }
.funnel-label { font-size: 0.8rem; color: #64748b; margin-bottom: 4px; font-weight: 500; }
.funnel-bar-container { display: flex; align-items: center; gap: 10px; }
.funnel-bar {
    height: 10px; background: linear-gradient(90deg, #3b82f6, #93c5fd); border-radius: 10px;
    min-width: 5px; transition: width 1s ease-out;
}
.funnel-count { font-size: 0.8rem; font-weight: 700; color: #334155; }
.btn-link-sm { font-size: 0.8rem; color: #2563eb; font-weight: 600; text-decoration: none; margin-top: 0.5rem; display: inline-block; }

/* VISITS LIST */
.visit-list { display: flex; flex-direction: column; gap: 12px; }
.visit-item { display: flex; align-items: center; gap: 12px; }
.visit-date {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 10px;
    display: flex; flex-direction: column; align-items: center; min-width: 50px;
}
.visit-date .day { font-size: 1.1rem; font-weight: 700; color: #1e293b; line-height: 1; }
.visit-date .month { font-size: 0.65rem; font-weight: 600; color: #64748b; margin-top: 2px; }
.visit-details { display: flex; flex-direction: column; }
.visit-details strong { font-size: 0.9rem; color: #334155; }
.visit-details span { font-size: 0.8rem; color: #64748b; }

.empty-widget { text-align: center; color: #94a3b8; padding: 1rem 0; }
.empty-widget i { font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.5; }

/* SKELETON LOADING */
.loading-skeleton { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; margin-top: 2rem; }
.skeleton-card { height: 120px; background: #e2e8f0; border-radius: 12px; animation: pulse 1.5s infinite; }

@keyframes wave { 0% { transform: rotate(0deg); } 10% { transform: rotate(14deg); } 20% { transform: rotate(-8deg); } 30% { transform: rotate(14deg); } 40% { transform: rotate(-4deg); } 50% { transform: rotate(10deg); } 60% { transform: rotate(0deg); } 100% { transform: rotate(0deg); } }
@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 0.8; } 100% { opacity: 0.6; } }

@media (max-width: 1024px) {
    .page-container { padding: 1rem; }
    .main-grid { grid-template-columns: 1fr; }
    .hide-mobile { display: none; }
}
</style>
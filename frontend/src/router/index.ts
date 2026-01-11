// frontend/src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth' 

// Importações dos layouts
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import PublicLayout from '@/layouts/PublicLayout.vue'

// ==========================================================
// ===== IMPORTAÇÕES DAS VIEWS (ALFABÉTICO) =================
// ==========================================================
import AlugueisDashboardView from '@/views/AlugueisDashboardView.vue'
import AutorizacoesReportView from '@/views/AutorizacoesReportView.vue'
import AutorizacoesView from '@/views/AutorizacoesView.vue'
import CalendarioPublicacoesView from '@/views/CalendarioPublicacoesView.vue'
import CalendarioTarefas from '@/views/CalendarioTarefas.vue'
import CategoriaFormView from '@/views/CategoriaFormView.vue'
import ClienteFormView from '@/views/ClienteFormView.vue'
import ClientesView from '@/views/ClientesView.vue'
import ConfiguracaoBancoView from '@/views/ConfiguracaoBancoView.vue'
import ConfiguracaoIAView from '@/views/ConfiguracaoIA.vue'
import ContaFormView from '@/views/ContaFormView.vue'
import ContratoEditorView from '@/views/ContratoEditorView.vue'
import ContratoFormView from '@/views/ContratoFormView.vue'
import ContratoReadView from '@/views/ContratoReadView.vue' 
import ContratosView from '@/views/ContratosView.vue'
import ContatosView from '@/views/ContatosView.vue'
import CorretoresView from '@/views/CorretoresView.vue'
import CorretorRegistrationView from '@/views/CorretorRegistrationView.vue'
import DashboardView from '@/views/DashboardView.vue'
import DREView from '@/views/DREView.vue'
import FinanceiroDashboardView from '@/views/FinanceiroDashboard.vue'
import FormaPagamentoFormView from '@/views/FormaPagamentoFormView.vue'
import FunilVendasView from '@/views/FunilVendasView.vue'
import ImoveisView from '@/views/ImoveisView.vue'
import ImovelFormView from '@/views/ImovelFormView.vue'
import ImovelImagensView from '@/views/ImovelImagensView.vue'
import IntegracoesView from '@/views/IntegracoesView.vue'
import ListaCategoriasView from '@/views/ListaCategoriasView.vue'
import ListaContasView from '@/views/ListaContasView.vue'
import ListaFormasPagamentoView from '@/views/ListaFormasPagamentoView.vue'
import ListaTransacoesView from '@/views/ListaTransacoes.vue'
import LockScreenView from '@/views/LockScreenView.vue'
import LoginView from '@/views/LoginView.vue'
import OportunidadeFormView from '@/views/OportunidadeFormView.vue'
import PublicacoesView from '@/views/PublicacoesView.vue'
import RegisterView from '@/views/RegisterView.vue'
import RelatoriosView from '@/views/RelatoriosView.vue'
import TransacaoFormView from '@/views/TransacaoForm.vue'
import VisitaFormView from '@/views/VisitaFormView.vue'
import VisitasView from '@/views/VisitasView.vue'
// === IMPORTAÇÕES DE VISTORIA ===
import VistoriasView from '@/views/VistoriasView.vue';
import VistoriaFormView from '@/views/VistoriaFormView.vue';
import VistoriaAmbientesView from '@/views/VistoriaAmbientesView.vue';

// Views Financeiras (Sub-pastas)
import ContasPagarView from '@/views/financeiro/ContasPagarView.vue'
import ContasReceberView from '@/views/financeiro/ContasReceberView.vue'
import RemessaRetornoView from '@/views/financeiro/RemessaRetornoView.vue'

// Views Públicas
import PublicHomeView from '@/views/PublicHomeView.vue'
import PublicImovelDetailView from '@/views/PublicImovelDetailView.vue'
// ==========================================================

// Adicionar um tipo para a meta das rotas
declare module 'vue-router' {
    interface RouteMeta {
        requiresAuth?: boolean;
        isAdmin?: boolean;
        title?: string;
    }
}

const router = createRouter({
    history: createWebHistory('/'),
    routes: [
        // --- 1. ROTA RAIZ (HOME PÚBLICA / SAAS) ---
        {
            path: '/',
            name: 'public-home',
            component: PublicHomeView,
            meta: { 
                title: 'Início - ImobHome',
                requiresAuth: false
            },
            beforeEnter: (to, from, next) => {
                // Se estiver num subdomínio (ex: teste.imobhome.com.br), redireciona para /site
                // para carregar o layout da agência corretamente.
                const hostname = window.location.hostname;
                const isSubdomain = hostname.split('.').length > 1 && !hostname.startsWith('www') && !hostname.startsWith('localhost');
                
                // Exceção especial para teste.localhost
                const isLocalhostTest = hostname === 'teste.localhost';

                if (isSubdomain || isLocalhostTest) {
                    next('/site');
                } else {
                    next();
                }
            }
        },

        // --- 2. SITE DE IMÓVEIS (SUBDOMÍNIO) ---
        {
            path: '/site',
            component: PublicLayout,
            children: [
                {
                    path: '',
                    name: 'site-home',
                    component: PublicHomeView,
                    meta: { title: 'Imóveis' }
                },
                {
                    path: 'imovel/:id',
                    name: 'public-imovel-detail',
                    component: PublicImovelDetailView,
                    meta: { title: 'Detalhes do Imóvel' }
                }
            ]
        },

        // --- 3. AUTENTICAÇÃO E UTILITÁRIOS ---
        {
            path: '/login',
            name: 'login',
            component: LoginView,
            meta: { title: 'Login', requiresAuth: false }
        },
        {
            path: '/cadastro',
            name: 'register',
            component: RegisterView,
            meta: { title: 'Crie sua conta', requiresAuth: false }
        },
        {
            path: '/bloqueado',
            name: 'lock-screen',
            component: LockScreenView,
            meta: { title: 'Acesso Suspenso', requiresAuth: false }
        },

        // --- 4. PAINEL DE GESTÃO (SEM PREFIXO /PAINEL) ---
        {
            path: '/', 
            component: DashboardLayout,
            meta: { requiresAuth: true },
            children: [
                {
                    path: '', 
                    redirect: '/dashboard'
                },
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: DashboardView,
                    meta: { title: 'Dashboard' }
                },
                {
                    path: 'alugueis/dashboard',
                    name: 'alugueis-dashboard',
                    component: AlugueisDashboardView,
                    meta: { title: 'Dashboard de Aluguéis' }
                },
                {
                    path: 'funil-vendas',
                    name: 'funil-vendas',
                    component: FunilVendasView,
                    meta: { title: 'Funil de Vendas' }
                },
                {
                    path: 'oportunidades/nova',
                    name: 'oportunidade-nova',
                    component: OportunidadeFormView,
                    meta: { title: 'Nova Oportunidade' }
                },
                {
                    path: 'oportunidades/editar/:id',
                    name: 'oportunidade-editar',
                    component: OportunidadeFormView,
                    meta: { title: 'Editar Oportunidade' }
                },
                {
                    path: 'imoveis',
                    name: 'imoveis',
                    component: ImoveisView,
                    meta: { title: 'Gerenciar Imóveis' }
                },
                {
                    path: 'imoveis/novo',
                    name: 'imovel-novo',
                    component: ImovelFormView,
                    meta: { title: 'Adicionar Novo Imóvel' }
                },
                {
                    path: 'imoveis/editar/:id',
                    name: 'imovel-editar',
                    component: ImovelFormView,
                    meta: { title: 'Editar Imóvel' }
                },
                {
                    path: 'imoveis/:id/imagens',
                    name: 'imovel-imagens',
                    component: ImovelImagensView,
                    props: (route) => ({ imovelId: route.params.id }),
                    meta: { title: 'Gerenciar Imagens do Imóvel', isAdmin: true }
                },
                {
                    path: 'clientes',
                    name: 'clientes',
                    component: ClientesView,
                    meta: { title: 'Gerenciar Clientes' }
                },
                {
                    path: 'clientes/novo',
                    name: 'cliente-novo',
                    component: ClienteFormView,
                    meta: { title: 'Adicionar Novo Cliente' }
                },
                {
                    path: 'clientes/editar/:id',
                    name: 'cliente-editar',
                    component: ClienteFormView,
                    meta: { title: 'Editar Cliente' }
                },
                {
                    path: 'contratos',
                    name: 'contratos',
                    component: ContratosView,
                    meta: { title: 'Gerenciar Contratos' }
                },
                {
                    path: 'contratos/novo',
                    name: 'contrato-novo',
                    component: ContratoFormView,
                    meta: { title: 'Adicionar Novo Contrato' }
                },
                {
                    path: 'contratos/editar/:id',
                    name: 'contrato-editar',
                    component: ContratoFormView,
                    meta: { title: 'Editar Contrato' }
                },
                {
                    path: 'contratos/:id/detalhes', 
                    name: 'ContratoRead', 
                    component: ContratoReadView,
                    meta: { title: 'Detalhes do Contrato' }
                },
                {
                    path: 'contratos/editar-documento/:id',
                    name: 'contrato-editar-documento',
                    component: ContratoEditorView,
                    meta: { title: 'Editar Documento do Contrato' }
                },
                // === VISTORIAS ===
                { 
                    path: 'vistorias', 
                    name: 'vistorias', 
                    component: VistoriasView, 
                    meta: { title: 'Gerenciar Vistorias' } 
                },
                {
                    path: 'vistorias/nova',
                    name: 'vistoria-nova',
                    component: VistoriaFormView,
                    meta: { title: 'Nova Vistoria' }
                },
                {
                    path: 'vistorias/editar/:id',
                    name: 'vistoria-editar',
                    component: VistoriaFormView,
                    meta: { title: 'Editar Vistoria' }
                },
                {
                    path: 'vistorias/checklist/:id',
                    name: 'vistoria-checklist',
                    component: VistoriaAmbientesView,
                    meta: { title: 'Executar Vistoria' }
                },
                // =================
                {
                    path: 'visitas',
                    name: 'visitas',
                    component: VisitasView,
                    meta: { title: 'Gerenciar Visitas' }
                },
                {
                    path: 'visitas/nova',
                    name: 'visita-nova',
                    component: VisitaFormView,
                    meta: { title: 'Agendar Nova Visita' }
                },
                {
                    path: 'visitas/editar/:id',
                    name: 'visita-editar',
                    component: VisitaFormView,
                    meta: { title: 'Editar Visita' }
                },
                {
                    path: 'contatos',
                    name: 'contatos',
                    component: ContatosView,
                    meta: { title: 'Gerenciar Contatos', isAdmin: true }
                },
                {
                    path: 'corretores',
                    name: 'corretores',
                    component: CorretoresView,
                    meta: { title: 'Gerenciar Utilizadores', isAdmin: true }
                },
                {
                    path: 'corretores/novo',
                    name: 'corretor-novo',
                    component: CorretorRegistrationView,
                    meta: { title: 'Registar Novo Utilizador', isAdmin: true }
                },
                {
                    path: 'corretores/editar/:id',
                    name: 'corretor-editar',
                    component: CorretorRegistrationView,
                    meta: { title: 'Editar Utilizador', isAdmin: true }
                },
                {
                    path: 'calendario',
                    name: 'calendario',
                    component: CalendarioTarefas,
                    meta: { title: 'Meu Calendário' }
                },
                {
                    path: 'publicacoes',
                    name: 'publicacoes',
                    component: PublicacoesView,
                    meta: { title: 'Central de Publicações' }
                },
                {
                    path: 'calendario-publicacoes',
                    name: 'calendario-publicacoes',
                    component: CalendarioPublicacoesView,
                    meta: { title: 'Calendário de Publicações' }
                },
                {
                    path: 'relatorios',
                    name: 'relatorios',
                    component: RelatoriosView,
                    meta: { title: 'Relatórios', isAdmin: true }
                },
                {
                    path: 'relatorios/autorizacoes',
                    name: 'relatorio-autorizacoes',
                    component: AutorizacoesReportView,
                    meta: { title: 'Relatório de Autorizações', isAdmin: true }
                },
                {
                    path: 'autorizacoes',
                    name: 'autorizacoes',
                    component: AutorizacoesView,
                    meta: { title: 'Gestão de Autorizações', isAdmin: true }
                },
                {
                    path: 'configuracoes-ia',
                    name: 'configuracoes-ia',
                    component: ConfiguracaoIAView,
                    meta: { title: 'Configurações da IA', isAdmin: true }
                },
                {
                    path: 'integracoes',
                    name: 'integracoes',
                    component: IntegracoesView,
                    meta: { title: 'Integrações', isAdmin: true }
                },
                {
                    path: 'integracoes/bancos/nova',
                    name: 'configuracao-banco-nova',
                    component: ConfiguracaoBancoView,
                    meta: { title: 'Nova Configuração de Banco', isAdmin: true }
                },
                {
                    path: 'integracoes/bancos/editar/:id',
                    name: 'configuracao-banco-editar',
                    component: ConfiguracaoBancoView,
                    meta: { title: 'Editar Configuração de Banco', isAdmin: true }
                },
                // === FINANCEIRO ===
                {
                    path: 'financeiro',
                    name: 'financeiro',
                    redirect: { name: 'financeiro-dashboard' }, 
                },
                {
                    path: 'financeiro/dashboard',
                    name: 'financeiro-dashboard',
                    component: FinanceiroDashboardView,
                    meta: { title: 'Dashboard Financeiro', isAdmin: true }
                },
                {
                    path: 'financeiro/transacoes',
                    name: 'lista-transacoes',
                    component: ListaTransacoesView,
                    meta: { title: 'Transações Financeiras', isAdmin: true }
                },
                {
                    path: 'financeiro/transacoes/nova',
                    name: 'transacao-nova',
                    component: TransacaoFormView,
                    meta: { title: 'Nova Transação', isAdmin: true }
                },
                {
                    path: 'financeiro/transacoes/editar/:id',
                    name: 'transacao-editar',
                    component: TransacaoFormView,
                    meta: { title: 'Editar Transação', isAdmin: true }
                },
                {
                    path: 'financeiro/dre',
                    name: 'dre',
                    component: DREView,
                    meta: { title: 'Relatório DRE', isAdmin: true }
                },
                {
                    path: 'financeiro/contas',
                    name: 'lista-contas',
                    component: ListaContasView,
                    meta: { title: 'Gerenciar Contas Bancárias', isAdmin: true }
                },
                {
                    path: 'financeiro/contas/nova',
                    name: 'conta-nova',
                    component: ContaFormView,
                    meta: { title: 'Nova Conta Bancária', isAdmin: true }
                },
                {
                    path: 'financeiro/contas/editar/:id',
                    name: 'conta-editar',
                    component: ContaFormView,
                    meta: { title: 'Editar Conta Bancária', isAdmin: true }
                },
                {
                    path: 'financeiro/categorias',
                    name: 'lista-categorias',
                    component: ListaCategoriasView,
                    meta: { title: 'Gerenciar Categorias Financeiras', isAdmin: true }
                },
                {
                    path: 'financeiro/categorias/nova',
                    name: 'nova-categoria',
                    component: CategoriaFormView,
                    meta: { title: 'Adicionar Categoria', isAdmin: true }
                },
                {
                    path: 'financeiro/categorias/editar/:id',
                    name: 'editar-categoria',
                    component: CategoriaFormView,
                    meta: { title: 'Editar Categoria', isAdmin: true }
                },
                {
                    path: 'financeiro/formas-pagamento',
                    name: 'lista-formas-pagamento',
                    component: ListaFormasPagamentoView,
                    meta: { title: 'Gerenciar Formas de Pagamento', isAdmin: true }
                },
                {
                    path: 'financeiro/formas-pagamento/nova',
                    name: 'nova-forma-pagamento',
                    component: FormaPagamentoFormView,
                    meta: { title: 'Adicionar Forma de Pagamento', isAdmin: true }
                },
                {
                    path: 'financeiro/formas-pagamento/editar/:id',
                    name: 'editar-forma-pagamento',
                    component: FormaPagamentoFormView,
                    meta: { title: 'Editar Forma de Pagamento', isAdmin: true }
                },
                {
                    path: 'financeiro/contas-a-pagar',
                    name: 'contas-a-pagar',
                    component: ContasPagarView,
                    meta: { title: 'Contas a Pagar', isAdmin: true }
                },
                {
                    path: 'financeiro/contas-a-receber',
                    name: 'contas-a-receber',
                    component: ContasReceberView,
                    meta: { title: 'Contas a Receber', isAdmin: true }
                },
                {
                    path: 'financeiro/remessa-retorno',
                    name: 'remessa-retorno',
                    component: RemessaRetornoView,
                    meta: { title: 'Remessa e Retorno', isAdmin: true }
                },
            ]
        },

        // Rota de fallback
        {
            path: '/:pathMatch(.*)*',
            redirect: '/'
        }
    ]
})

router.beforeEach((to, from, next) => {
    // Diagnóstico
    console.log(`[Router] Navegando para: ${String(to.name)}, Path: ${to.path}`);

    let authStore: any;
    try {
        authStore = useAuthStore();
    } catch (e) {
        // Ignora
    }

    document.title = `${to.meta.title || 'ImobHome'}`;

    // Verifica se a rota ou a rota pai requer auth
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth === true);
    
    // Recupera dados
    let isAuthenticated = false;
    let currentCargo: string | null = null;

    // 1. Tenta pegar do Store
    if (authStore && authStore.token) {
        isAuthenticated = true;
        currentCargo = authStore.userCargo;
    } else {
        // 2. Tenta pegar do LocalStorage
        const token = localStorage.getItem('authToken');
        isAuthenticated = !!token;
        currentCargo = localStorage.getItem('userCargo');
    }

    if (isAuthenticated && authStore && !authStore.token) {
        authStore.initialize(); 
    }

    // --- LÓGICA DE PROTEÇÃO DE ROTAS ---
    if (requiresAuth && !isAuthenticated) {
        next({ name: 'login' });
    } else if (to.name === 'login' && isAuthenticated) {
        next({ name: 'dashboard' });
    } else if (isAuthenticated && to.meta.isAdmin) {
        if (currentCargo === 'ADMIN' || currentCargo === 'SUPERADMIN') {
            next();
        } else {
            console.warn(`Acesso negado. Rota exige ADMIN/SUPERADMIN.`);
            next({ name: 'dashboard' });
        }
    } else {
        next();
    }
});

export default router;
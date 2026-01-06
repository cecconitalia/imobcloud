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
import LockScreenView from '@/views/LockScreenView.vue' // <--- IMPORTAÇÃO NOVA
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
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        // --- 1. ROTA RAIZ (AGORA É A LANDING PAGE) ---
        {
            path: '/',
            name: 'public-home',
            component: PublicHomeView,
            meta: { 
                title: 'Início - ImobHome',
                requiresAuth: false // Explícito: não requer login
            }
        },

        // --- 2. SITE DE IMÓVEIS (SUBDOMÍNIO) ---
        {
            path: '/site',
            component: PublicLayout,
            children: [
                {
                    path: '', // /site redireciona para a home pública também se necessário, ou lista de imóveis
                    name: 'site-home',
                    component: PublicHomeView, // Reutilizando a home ou criar uma específica
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

        // --- 3. LOGIN ---
        {
            path: '/login',
            name: 'login',
            component: LoginView,
            meta: {
                title: 'Login',
                requiresAuth: false
            }
        },

        // --- 3.1 CADASTRO (NOVA ROTA) ---
        {
            path: '/cadastro',
            name: 'register',
            component: RegisterView,
            meta: {
                title: 'Crie sua conta',
                requiresAuth: false
            }
        },

        // --- 3.2 TELA DE BLOQUEIO FINANCEIRO (NOVA ROTA) ---
        {
            path: '/bloqueado',
            name: 'lock-screen',
            component: LockScreenView,
            meta: {
                title: 'Acesso Suspenso',
                requiresAuth: false // Permite ver a tela mesmo sem passar no guard padrão
            }
        },

        // --- 4. PAINEL DE GESTÃO (MOVIDO DE '/' PARA '/painel') ---
        {
            path: '/', // MUDANÇA IMPORTANTE: Prefixo para área logada
            component: DashboardLayout,
            meta: { requiresAuth: true }, // Proteção continua aqui
            children: [
                {
                    path: '',
                    redirect: '/dashboard' // Redirecionamento interno
                },
                {
                    path: 'dashboard',
                    name: 'dashboard',
                    component: DashboardView,
                    meta: {
                        title: 'Dashboard'
                    }
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
                    meta: {
                        title: 'Funil de Vendas',
                        requiresAuth: true
                    }
                },
                {
                    path: 'oportunidades/nova',
                    name: 'oportunidade-nova',
                    component: OportunidadeFormView,
                    meta: {
                        title: 'Nova Oportunidade',
                        requiresAuth: true
                    }
                },
                {
                    path: 'oportunidades/editar/:id',
                    name: 'oportunidade-editar',
                    component: OportunidadeFormView,
                    meta: {
                        title: 'Editar Oportunidade',
                        requiresAuth: true
                    }
                },
                {
                    path: 'imoveis',
                    name: 'imoveis',
                    component: ImoveisView,
                    meta: {
                        title: 'Gerenciar Imóveis'
                    }
                },
                {
                    path: 'imoveis/novo',
                    name: 'imovel-novo',
                    component: ImovelFormView,
                    meta: {
                        title: 'Adicionar Novo Imóvel',
                        requiresAuth: true
                    }
                },
                {
                    path: 'imoveis/editar/:id',
                    name: 'imovel-editar',
                    component: ImovelFormView,
                    meta: {
                        title: 'Editar Imóvel',
                        requiresAuth: true
                    }
                },
                {
                    path: 'imoveis/:id/imagens',
                    name: 'imovel-imagens',
                    component: ImovelImagensView,
                    props: (route) => ({ imovelId: route.params.id }),
                    meta: {
                        title: 'Gerenciar Imagens do Imóvel',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'clientes',
                    name: 'clientes',
                    component: ClientesView,
                    meta: {
                        title: 'Gerenciar Clientes'
                    }
                },
                {
                    path: 'clientes/novo',
                    name: 'cliente-novo',
                    component: ClienteFormView,
                    meta: {
                        title: 'Adicionar Novo Cliente',
                        requiresAuth: true
                    }
                },
                {
                    path: 'clientes/editar/:id',
                    name: 'cliente-editar',
                    component: ClienteFormView,
                    meta: {
                        title: 'Editar Cliente',
                        requiresAuth: true
                    }
                },
                {
                    path: 'contratos',
                    name: 'contratos',
                    component: ContratosView,
                    meta: {
                        title: 'Gerenciar Contratos'
                    }
                },
                {
                    path: 'contratos/novo',
                    name: 'contrato-novo',
                    component: ContratoFormView,
                    meta: {
                        title: 'Adicionar Novo Contrato',
                        requiresAuth: true
                    }
                },
                {
                    path: 'contratos/editar/:id',
                    name: 'contrato-editar',
                    component: ContratoFormView,
                    meta: {
                        title: 'Editar Contrato',
                        requiresAuth: true
                    }
                },
                {
                    path: 'contratos/:id/detalhes', 
                    name: 'ContratoRead', 
                    component: ContratoReadView,
                    meta: { title: 'Detalhes do Contrato', requiresAuth: true }
                },
                {
                    path: 'contratos/editar-documento/:id',
                    name: 'contrato-editar-documento',
                    component: ContratoEditorView,
                    meta: {
                        title: 'Editar Documento do Contrato',
                        requiresAuth: true
                    }
                },
                // === ROTAS DE VISTORIA ===
                { 
                    path: 'vistorias', 
                    name: 'vistorias', 
                    component: VistoriasView, 
                    meta: { 
                        title: 'Gerenciar Vistorias', 
                        requiresAuth: true 
                    } 
                },
                {
                    path: 'vistorias/nova',
                    name: 'vistoria-nova',
                    component: VistoriaFormView,
                    meta: { 
                        title: 'Nova Vistoria', 
                        requiresAuth: true 
                    }
                },
                {
                    path: 'vistorias/editar/:id',
                    name: 'vistoria-editar',
                    component: VistoriaFormView,
                    meta: { 
                        title: 'Editar Vistoria', 
                        requiresAuth: true 
                    }
                },
                {
                    path: 'vistorias/checklist/:id',
                    name: 'vistoria-checklist',
                    component: VistoriaAmbientesView,
                    meta: { title: 'Executar Vistoria', requiresAuth: true }
                },
                // ==========================
                {
                    path: 'visitas',
                    name: 'visitas',
                    component: VisitasView,
                    meta: {
                        title: 'Gerenciar Visitas'
                    }
                },
                {
                    path: 'visitas/nova',
                    name: 'visita-nova',
                    component: VisitaFormView,
                    meta: {
                        title: 'Agendar Nova Visita',
                        requiresAuth: true
                    }
                },
                {
                    path: 'visitas/editar/:id',
                    name: 'visita-editar',
                    component: VisitaFormView,
                    meta: {
                        title: 'Editar Visita',
                        requiresAuth: true
                    }
                },
                {
                    path: 'contatos',
                    name: 'contatos',
                    component: ContatosView,
                    meta: {
                        title: 'Gerenciar Contatos',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'corretores',
                    name: 'corretores',
                    component: CorretoresView,
                    meta: {
                        title: 'Gerenciar Utilizadores',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'corretores/novo',
                    name: 'corretor-novo',
                    component: CorretorRegistrationView,
                    meta: {
                        title: 'Registar Novo Utilizador',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'corretores/editar/:id',
                    name: 'corretor-editar',
                    component: CorretorRegistrationView,
                    meta: {
                        title: 'Editar Utilizador',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'calendario',
                    name: 'calendario',
                    component: CalendarioTarefas,
                    meta: {
                        title: 'Meu Calendário',
                        requiresAuth: true
                    }
                },
                {
                    path: 'publicacoes',
                    name: 'publicacoes',
                    component: PublicacoesView,
                    meta: {
                        title: 'Central de Publicações',
                        requiresAuth: true
                    }
                },
                {
                    path: 'calendario-publicacoes',
                    name: 'calendario-publicacoes',
                    component: CalendarioPublicacoesView,
                    meta: {
                        title: 'Calendário de Publicações',
                        requiresAuth: true
                    }
                },
                {
                    path: 'relatorios',
                    name: 'relatorios',
                    component: RelatoriosView,
                    meta: {
                        title: 'Relatórios',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'relatorios/autorizacoes',
                    name: 'relatorio-autorizacoes',
                    component: AutorizacoesReportView,
                    meta: { 
                        title: 'Relatório de Autorizações',
                        requiresAuth: true,
                        isAdmin: true 
                    }
                },
                {
                    path: 'autorizacoes',
                    name: 'autorizacoes',
                    component: AutorizacoesView,
                    meta: {
                        title: 'Gestão de Autorizações',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'configuracoes-ia',
                    name: 'configuracoes-ia',
                    component: ConfiguracaoIAView,
                    meta: {
                        title: 'Configurações da IA',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'integracoes',
                    name: 'integracoes',
                    component: IntegracoesView,
                    meta: {
                        title: 'Integrações',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'integracoes/bancos/nova',
                    name: 'configuracao-banco-nova',
                    component: ConfiguracaoBancoView,
                    meta: {
                        title: 'Nova Configuração de Banco',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'integracoes/bancos/editar/:id',
                    name: 'configuracao-banco-editar',
                    component: ConfiguracaoBancoView,
                    meta: {
                        title: 'Editar Configuração de Banco',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro',
                    name: 'financeiro',
                    redirect: '/dashboard', // Ajustado para incluir /painel
                },
                {
                    path: 'financeiro/dashboard',
                    name: 'financeiro-dashboard',
                    component: FinanceiroDashboardView,
                    meta: {
                        title: 'Dashboard Financeiro',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/transacoes',
                    name: 'lista-transacoes',
                    component: ListaTransacoesView,
                    meta: {
                        title: 'Transações Financeiras',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/transacoes/nova',
                    name: 'transacao-nova',
                    component: TransacaoFormView,
                    meta: {
                        title: 'Nova Transação',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/transacoes/editar/:id',
                    name: 'transacao-editar',
                    component: TransacaoFormView,
                    meta: {
                        title: 'Editar Transação',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/dre',
                    name: 'dre',
                    component: DREView,
                    meta: {
                        title: 'Relatório DRE',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/contas',
                    name: 'lista-contas',
                    component: ListaContasView,
                    meta: {
                        title: 'Gerenciar Contas Bancárias',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/contas/nova',
                    name: 'conta-nova',
                    component: ContaFormView,
                    meta: {
                        title: 'Nova Conta Bancária',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/contas/editar/:id',
                    name: 'conta-editar',
                    component: ContaFormView,
                    meta: {
                        title: 'Editar Conta Bancária',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/categorias',
                    name: 'lista-categorias',
                    component: ListaCategoriasView,
                    meta: {
                        title: 'Gerenciar Categorias Financeiras',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/categorias/nova',
                    name: 'nova-categoria',
                    component: CategoriaFormView,
                    meta: {
                        title: 'Adicionar Categoria',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/categorias/editar/:id',
                    name: 'editar-categoria',
                    component: CategoriaFormView,
                    meta: {
                        title: 'Editar Categoria',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/formas-pagamento',
                    name: 'lista-formas-pagamento',
                    component: ListaFormasPagamentoView,
                    meta: {
                        title: 'Gerenciar Formas de Pagamento',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/formas-pagamento/nova',
                    name: 'nova-forma-pagamento',
                    component: FormaPagamentoFormView,
                    meta: {
                        title: 'Adicionar Forma de Pagamento',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/formas-pagamento/editar/:id',
                    name: 'editar-forma-pagamento',
                    component: FormaPagamentoFormView,
                    meta: {
                        title: 'Editar Forma de Pagamento',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/contas-a-pagar',
                    name: 'contas-a-pagar',
                    component: ContasPagarView,
                    meta: {
                        title: 'Contas a Pagar',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/contas-a-receber',
                    name: 'contas-a-receber',
                    component: ContasReceberView,
                    meta: {
                        title: 'Contas a Receber',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
                {
                    path: 'financeiro/remessa-retorno',
                    name: 'remessa-retorno',
                    component: RemessaRetornoView,
                    meta: {
                        title: 'Remessa e Retorno',
                        requiresAuth: true,
                        isAdmin: true
                    }
                },
            ]
        },

        // Rota de fallback
        {
            path: '/:pathMatch(.*)*',
            redirect: '/' // Redireciona para a Home (PublicHomeView) se não encontrar
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

    // Verifica explicitamente se a rota requer auth (true)
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth === true);
    
    // Recupera dados
    let isAuthenticated = false;
    let currentCargo: string | null = null;
    let isSuperUser = false;

    // 1. Tenta pegar do Store
    if (authStore && authStore.token) {
        isAuthenticated = true;
        currentCargo = authStore.userCargo;
        isSuperUser = authStore.user?.is_superuser === true; 
    } else {
        // 2. Tenta pegar do LocalStorage
        const token = localStorage.getItem('authToken');
        isAuthenticated = !!token;
        currentCargo = localStorage.getItem('userCargo');
        
        try {
            const storedUser = JSON.parse(localStorage.getItem('userData') || '{}');
            isSuperUser = storedUser?.is_superuser === true;
        } catch (e) {
            isSuperUser = false;
        }
    }

    if (isAuthenticated && authStore && !authStore.token) {
        authStore.initialize(); 
    }

    // --- LÓGICA DE PROTEÇÃO DE ROTAS ---
    if (requiresAuth && !isAuthenticated) {
        // Se tenta acessar rota protegida (ex: /painel/...) sem login -> vai para Login
        next({ name: 'login' });
    } else if (to.name === 'login' && isAuthenticated) {
        // Se já está logado e tenta ir para Login -> vai para Dashboard
        next({ name: 'dashboard' });
    } else if (isAuthenticated && to.meta.isAdmin) {
        // Proteção de rotas Admin
        if (currentCargo === 'ADMIN' || currentCargo === 'SUPERADMIN') {
            next();
        } else {
            console.warn(`Acesso negado. Rota exige ADMIN/SUPERADMIN.`);
            next({ name: 'dashboard' });
        }
    } else {
        // Rotas públicas (como /, /login, /site, /bloqueado) passam direto
        next();
    }
});

export default router
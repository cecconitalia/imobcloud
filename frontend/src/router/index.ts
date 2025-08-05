import { createRouter, createWebHistory } from 'vue-router'

// Importações dos layouts
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import PublicLayout from '@/layouts/PublicLayout.vue'

// Importações das views do Painel
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ImoveisView from '@/views/ImoveisView.vue'
import ImovelFormView from '@/views/ImovelFormView.vue'
import ImovelImagensView from '@/views/ImovelImagensView.vue'
import ClientesView from '@/views/ClientesView.vue'
import ClienteFormView from '@/views/ClienteFormView.vue'
import ContratosView from '@/views/ContratosView.vue'
import ContratoFormView from '@/views/ContratoFormView.vue'
import VisitasView from '@/views/VisitasView.vue'
import VisitaFormView from '@/views/VisitaFormView.vue'
import ContatosView from '@/views/ContatosView.vue'
import CorretorRegistrationView from '@/views/CorretorRegistrationView.vue'
import FunilVendasView from '@/views/FunilVendasView.vue'
import OportunidadeFormView from '@/views/OportunidadeFormView.vue'

// Importações das views do Site Público
import PublicHomeView from '@/views/PublicHomeView.vue'
import PublicImovelDetailView from '@/views/PublicImovelDetailView.vue'

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
    // --- ROTAS DO SITE PÚBLICO ---
    {
      path: '/site',
      component: PublicLayout,
      children: [
        {
          path: '',
          name: 'public-home',
          component: PublicHomeView,
          meta: { title: 'Início' }
        },
        {
          path: 'imovel/:id',
          name: 'public-imovel-detail',
          component: PublicImovelDetailView,
          meta: { title: 'Detalhes do Imóvel' }
        }
      ]
    },

    // --- ROTAS DO PAINEL DE GESTÃO ---
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {
        title: 'Login'
      }
    },
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
          meta: {
            title: 'Dashboard'
          }
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
          path: 'imoveis',
          name: 'imoveis',
          component: ImoveisView,
          meta: {
            title: 'Gerir Imóveis'
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
          meta: {
            title: 'Gerir Imagens do Imóvel',
            requiresAuth: true,
            isAdmin: true
          }
        },
        {
          path: 'clientes',
          name: 'clientes',
          component: ClientesView,
          meta: {
            title: 'Gerir Clientes'
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
            title: 'Gerir Contratos'
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
          path: 'visitas',
          name: 'visitas',
          component: VisitasView,
          meta: {
            title: 'Gerir Visitas'
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
            title: 'Gerir Contatos',
            requiresAuth: true,
            isAdmin: true
          }
        },
        {
          path: 'corretor/novo',
          name: 'corretor-novo',
          component: CorretorRegistrationView,
          meta: {
            title: 'Registar Novo Corretor',
            requiresAuth: true,
            isAdmin: true
          }
        },
      ]
    },
    
    // Rota de fallback
    {
        path: '/:pathMatch(.*)*',
        redirect: '/login'
    }
  ]
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'ImobCloud'}`

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = !!localStorage.getItem('authToken')
  const userCargo = localStorage.getItem('userCargo')

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated) {
    next({ name: 'dashboard' })
  } else if (isAuthenticated) {
    if (to.meta.isAdmin && userCargo !== 'ADMIN') {
      alert("Você não tem permissão para aceder a esta página.")
      next({ name: 'dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
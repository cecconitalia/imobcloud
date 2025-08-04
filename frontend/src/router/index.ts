import { createRouter, createWebHistory } from 'vue-router'

// Importações dos layouts
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import PublicLayout from '@/layouts/PublicLayout.vue' // ADICIONADO

// Importações das views do Painel (sem alterações)
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ImoveisView from '@/views/ImoveisView.vue'
import ImovelFormView from '@/views/ImovelFormView.vue'
import ImovelImagensView from '@/views/ImovelImagensView.vue'
import ClientesView from '@/views/ClientesView.vue'
import ClienteFormView from '@/views/ClienteFormView.vue'
import ContratosView from '@/views/ContratosView.vue'
import ContratoFormView from '@/views/ContratoFormView.vue'

// Importações das views do Site Público (ADICIONADO)
import PublicHomeView from '@/views/PublicHomeView.vue'
import PublicImovelDetailView from '@/views/PublicImovelDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // --- ROTAS DO SITE PÚBLICO (NOVA SEÇÃO ADICIONADA) ---
    // Acessível via http://subdominio.localhost:5173/site
    {
      path: '/site',
      component: PublicLayout,
      children: [
        {
          path: '', // Página inicial do site
          name: 'public-home',
          component: PublicHomeView,
          meta: { title: 'Início' }
        },
        {
          path: 'imovel/:id', // Página de detalhes do imóvel
          name: 'public-imovel-detail',
          component: PublicImovelDetailView,
          meta: { title: 'Detalhes do Imóvel' }
        }
      ]
    },

    // --- ROTAS DO PAINEL DE GESTÃO (SEÇÃO ORIGINAL, SEM ALTERAÇÕES) ---
    // O seu painel continua a funcionar na rota principal '/'
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
            title: 'Adicionar Novo Imóvel'
          }
        },
        {
          path: 'imoveis/editar/:id',
          name: 'imovel-editar',
          component: ImovelFormView,
          meta: {
            title: 'Editar Imóvel'
          }
        },
        {
          path: 'imoveis/:id/imagens',
          name: 'imovel-imagens',
          component: ImovelImagensView,
          meta: {
            title: 'Gerir Imagens do Imóvel'
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
            title: 'Adicionar Novo Cliente'
          }
        },
        {
          path: 'clientes/editar/:id',
          name: 'cliente-editar',
          component: ClienteFormView,
          meta: {
            title: 'Editar Cliente'
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
            title: 'Adicionar Novo Contrato'
          }
        },
        {
          path: 'contratos/editar/:id',
          name: 'contrato-editar',
          component: ContratoFormView,
          meta: {
            title: 'Editar Contrato'
          }
        }
      ]
    },
    
    // Rota de fallback (SEM ALTERAÇÕES)
    // Se um URL não for encontrado, redireciona para a página principal (o painel).
    {
        path: '/:pathMatch(.*)*',
        redirect: '/'
    }
  ]
})

// Guarda de Navegação (SEM ALTERAÇÕES)
router.beforeEach((to, from, next) => {
  document.title = `${String(to.meta.title) || 'ImobCloud'}`

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = !!localStorage.getItem('authToken')

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
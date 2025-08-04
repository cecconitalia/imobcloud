import { createRouter, createWebHistory } from 'vue-router'

// Importações dos componentes de view
import LoginView from '@/views/LoginView.vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import ImoveisView from '@/views/ImoveisView.vue'
import ImovelFormView from '@/views/ImovelFormView.vue'
import ImovelImagensView from '@/views/ImovelImagensView.vue' // IMPORTAÇÃO ADICIONADA
import ClientesView from '@/views/ClientesView.vue'
import ClienteFormView from '@/views/ClienteFormView.vue'
import ContratosView from '@/views/ContratosView.vue'
import ContratoFormView from '@/views/ContratoFormView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
          redirect: '/imoveis'
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
        // --- ROTA DE IMAGENS ADICIONADA ---
        {
          path: 'imoveis/:id/imagens', // Rota para a gestão de imagens
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
    {
        path: '/:pathMatch(.*)*',
        redirect: '/'
    }
  ]
})

// Guarda de Navegação (sem alterações)
router.beforeEach((to, from, next) => {
  document.title = `${String(to.meta.title) || 'ImobCloud'}`

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = !!localStorage.getItem('authToken')

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated) {
    next({ name: 'imoveis' })
  } else {
    next()
  }
})

export default router
import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 1. Importação do Reset CSS (para limpar estilos nativos do navegador)
import '@unocss/reset/tailwind.css'

// 2. Importação Principal do UnoCSS (Obrigatório para funcionar)
import 'virtual:uno.css'

// 3. Importação do CSS customizado global
import './style.css'

// Importação do FontAwesome
import '@fortawesome/fontawesome-free/css/all.css'

import App from './App.vue'
import router from './router'
import money from 'v-money3'

// Importação da Store de Autenticação
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

// Instalação dos Plugins (A ordem importa: Pinia deve vir antes do uso da store)
app.use(pinia)
app.use(router)
app.use(money)

// Inicializa Auth Store
// Isso verifica se existe token salvo no localStorage ao recarregar a página
const authStore = useAuthStore()

// Verificação de segurança caso o método initialize não exista na store por algum motivo
if (authStore && typeof authStore.initialize === 'function') {
    authStore.initialize()
}

// Nota: A chamada antiga 'setupInterceptors(router, authStore)' foi REMOVIDA.
// A lógica de interceptação de erros 401/403 agora reside internamente no 
// arquivo 'src/services/api.ts' para evitar erros de build e dependência circular.

app.mount('#app')
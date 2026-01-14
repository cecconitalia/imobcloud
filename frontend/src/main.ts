// 1. Importação do Reset CSS (para limpar estilos nativos do navegador)
import '@unocss/reset/tailwind.css'

// 2. Importação Principal do UnoCSS (Obrigatório para funcionar)
import 'virtual:uno.css'

// 3. Importação do CSS customizado global
import './style.css'

// Se você usa FontAwesome instalado via npm, importe aqui. 
// Caso contrário, certifique-se que ele está no index.html
import '@fortawesome/fontawesome-free/css/all.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import money from 'v-money3'

// Importações dos serviços e stores
import { setupInterceptors } from './services/api'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(money)

// Inicializa Auth Store
const authStore = useAuthStore()
if (authStore.initialize) {
    authStore.initialize()
}

// Configura interceptors
setupInterceptors(router, authStore)

app.mount('#app')
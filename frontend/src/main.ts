import './style.css' 
// ^^^ CORRIGIDO: O arquivo padrão do Vite é 'style.css' e fica na raiz de src.
// Se você tiver um 'assets/main.css' específico, verifique se a pasta e o arquivo existem.

// import './assets/fontawesome.css' 
// ^^^ ATENÇÃO: Comentei esta linha preventivamente. 
// Se você NÃO tiver o arquivo 'fontawesome.css' dentro de 'src/assets/', o build vai quebrar aqui também.
// Se você usa FontAwesome via pacote npm (ex: @fortawesome/...), essa importação manual não é necessária.
// Caso você tenha o arquivo, pode descomentar.

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

// 1. Instala o Pinia PRIMEIRO (Crucial para as stores funcionarem)
app.use(pinia)

// 2. Instala o Router
app.use(router)

// 3. Plugins adicionais (v-money3 para campos de moeda)
app.use(money)

// 4. Inicializa o Auth Store
// Recupera a instância da store agora que o Pinia está ativo
const authStore = useAuthStore()

// Tenta restaurar a sessão se o método existir
if (authStore.initialize) {
    authStore.initialize()
}

// 5. Configura os interceptadores do Axios
// Injeta o 'router' para redirecionamentos e 'authStore' para logout/limpeza
setupInterceptors(router, authStore)

app.mount('#app')
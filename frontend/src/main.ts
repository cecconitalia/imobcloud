import { createApp } from 'vue'
import { createPinia } from 'pinia' // Importante: Pinia deve vir antes do uso da Store
import App from './App.vue'
import router from './router'
import money from 'v-money3'
import { setupInterceptors } from './services/api';
import { useAuthStore } from '@/stores/auth'; // Importamos a store para inicializar o token

import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

// 1. Instala o Pinia PRIMEIRO (para que as stores funcionem)
app.use(pinia)

// 2. Instala o Router
app.use(router)

// 3. Plugins adicionais
app.use(money)

// 4. Inicializa o Auth Store
// Isso recupera o token do localStorage e configura o header 'Authorization' do Axios
// para que as requisições não falhem após um refresh (F5).
const authStore = useAuthStore();
if (authStore.initialize) {
    authStore.initialize();
}

// 5. Configura os interceptadores do Axios (para redirecionar ao login no erro 401)
setupInterceptors(router);

app.mount('#app')
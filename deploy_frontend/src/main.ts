import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import money from 'v-money3'
import { setupInterceptors } from './services/api';
import { useAuthStore } from '@/stores/auth';

import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

// 1. Instala o Pinia PRIMEIRO
app.use(pinia)

// 2. Instala o Router
app.use(router)

// 3. Plugins adicionais
app.use(money)

// 4. Inicializa o Auth Store
const authStore = useAuthStore();
if (authStore.initialize) {
    authStore.initialize();
}

// 5. Configura os interceptadores COM a store
// CORREÇÃO: Passando 'authStore' para que o logout limpe a memória do Pinia
setupInterceptors(router, authStore);

app.mount('#app')
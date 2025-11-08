import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import money from 'v-money3'
import { setupInterceptors } from './services/api'; // <--- Importa a função de setup

import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

// Ativa o interceptor de erro 401, passando o roteador.
setupInterceptors(router); 

app.use(pinia)
app.use(router)
app.use(money)

app.mount('#app')
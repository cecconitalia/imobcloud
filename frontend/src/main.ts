import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia' // Importa o Pinia
import money from 'v-money3' // Importa a máscara

import './assets/main.css'

const app = createApp(App)
const pinia = createPinia() // Cria a instância do Pinia

app.use(pinia) // Usa o Pinia
app.use(router)
app.use(money) // Usa a máscara

app.mount('#app')
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ command }) => {
  return {
    plugins: [
      vue(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    // A MÁGICA ESTÁ AQUI:
    // Se for comando 'build' (produção/Django), usa base '/static/'.
    // Se for 'serve' (npm run dev), usa base '/' (raiz).
    base: command === 'build' ? '/static/' : '/',
  }
})
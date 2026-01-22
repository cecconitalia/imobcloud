import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  return {
    plugins: [
      vue(),
      // A configuração agora é carregada automaticamente de uno.config.ts
      // Mantendo o vite.config.ts limpo e focado na infraestrutura de build
      UnoCSS(), 
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 8001,
      host: true, // Necessário para Docker/Rede local
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
        '/media': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    },
    // Lógica crítica para integração com Django Static Files
    base: command === 'build' ? '/static/' : '/',
    build: {
      // Evita warnings de chunks muito grandes
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          // Separa bibliotecas de terceiros do código da aplicação para melhor cache
          manualChunks: {
            'vendor-vue': ['vue', 'vue-router', 'pinia'],
            'vendor-ui': ['@vueuse/core'], // Adicione outras libs pesadas aqui se necessário
          }
        }
      }
    }
  }
})
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import { presetUno, presetIcons, presetWebFonts } from 'unocss'

// https://vitejs.dev/config/
export default defineConfig(({ command }) => {
  return {
    plugins: [
      vue(),
      // Configuração completa do UnoCSS injetada diretamente aqui
      UnoCSS({
        presets: [
          presetUno(), // Habilita classes compatíveis com Tailwind/Bootstrap (flex, p-4, bg-blue-500)
          presetIcons({
            scale: 1.2,
            cdn: 'https://esm.sh/'
          }),
          presetWebFonts({
            provider: 'google',
            fonts: {
              sans: 'Inter:400,600,700',
            },
          }),
        ],
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 8001,
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
    base: command === 'build' ? '/static/' : '/',
  }
})
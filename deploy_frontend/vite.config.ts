import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

// ==========================================================
// ==================== IMPORTAR O NOVO PLUGIN ================
// ==========================================================
import { viteStaticCopy } from 'vite-plugin-static-copy'
// ==========================================================

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    
    // ==========================================================
    // ==================== CONFIGURAR O PLUGIN ===================
    // ==========================================================
    // Isto copia os ficheiros do TinyMCE para a sua pasta 'dist'
    // para que o editor funcione localmente sem publicidade.
    viteStaticCopy({
      targets: [
        {
          src: 'node_modules/tinymce/skins',
          dest: 'tinymce'
        },
        {
          src: 'node_modules/tinymce/themes',
          dest: 'tinymce'
        },
        {
          src: 'node_modules/tinymce/models',
          dest: 'tinymce'
        },
        {
          src: 'node_modules/tinymce/icons',
          dest: 'tinymce'
        },
        {
          src: 'node_modules/tinymce/plugins',
          dest: 'tinymce'
        }
      ]
    })
    // ==========================================================
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
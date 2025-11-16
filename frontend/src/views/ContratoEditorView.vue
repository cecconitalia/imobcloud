<template>
  <div class="page-container editor-container">
    <div class="view-header">
      <h1>Editor de Documento de Contrato</h1>
      <button @click="router.back()" class="btn btn-secondary">
        <i class="fas fa-arrow-left"></i> Voltar
      </button>
    </div>

    <div v-if="isLoading" class="loading-message card">
      <div class="spinner"></div>
      Carregando documento...
    </div>

    <div v-if="error" class="error-message card">{{ error }}</div>

    <div v-if="!isLoading && !error" class="card">
      
      <div v-if="editor" class="editor-toolbar">
        <button @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()">
          <i class="fas fa-undo"></i>
        </button>
        <button @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()">
          <i class="fas fa-redo"></i>
        </button>

        <button @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }">
          H1
        </button>
        <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }">
          H2
        </button>
        <button @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }">
          H3
        </button>

        <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }">
          <i class="fas fa-bold"></i>
        </button>
        <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }">
          <i class="fas fa-italic"></i>
        </button>
        <button @click="editor.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor.isActive('underline') }">
          <i class="fas fa-underline"></i>
        </button>
        <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }">
          <i class="fas fa-strikethrough"></i>
        </button>

        <button @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }">
          <i class="fas fa-list-ul"></i>
        </button>
        <button @click="editor.chain().focus().toggleBlockquote().run()" :class="{ 'is-active': editor.isActive('blockquote') }">
          <i class="fas fa-quote-right"></i>
        </button>
        <button @click="editor.chain().focus().setHorizontalRule().run()">
          <i class="fas fa-minus"></i>
        </button>
        
        </div>

      <editor-content :editor="editor" class="editor-content-area" />

      <div class="editor-actions">
        <button @click="handleSave" class="btn btn-success" :disabled="isSaving">
          <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-save"></i>
          Salvar Alterações no Documento
        </button>
        <p>
          <small>
            Atenção: As alterações salvas aqui são permanentes e usadas para gerar
            o PDF final.
          </small>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

// ==========================================================
// ==================== IMPORTAR O TIPTAP E EXTENSÕES ========
// ==========================================================
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit'; // Pacote base
import { Heading } from '@tiptap/extension-heading';

// Importações Corrigidas (com {})
import { Underline } from '@tiptap/extension-underline';

// REMOVIDAS AS EXTENSÕES PROBLEMÁTICAS
// import { TextAlign } from '@tiptap/extension-text-align';
// import { FontFamily } from '@tiptap/extension-font-family';
// import { TextStyle } from '@tiptap/extension-text-style';
// ==========================================================

const route = useRoute();
const router = useRouter(); 
const toast = useToast();

const contratoId = ref<string | null>(null);
const htmlContent = ref(''); 
const isLoading = ref(true);
const isSaving = ref(false);
const error = ref<string | null>(null);

// ==========================================================
// ==================== CONFIGURAÇÃO DO EDITOR TIPTAP =========
// ==========================================================
const editor = useEditor({
  content: '',
  extensions: [
    // Corrigido: Dizer ao StarterKit para NÃO incluir o 'heading' padrão
    StarterKit.configure({
      heading: false,
    }),
    
    // Carregar o 'heading' configurado
    Heading.configure({
      levels: [1, 2, 3],
      HTMLAttributes: {
        class: (attrs) => {
          if (attrs.level === 1) return 'h1-pdf'; 
          if (attrs.level === 2) return 'h2-pdf';
          if (attrs.level === 3) return 'h3-pdf';
          return '';
        },
      },
    }),
    
    // Extensões adicionais
    Underline,
    
    // REMOVIDAS AS EXTENSÕES PROBLEMÁTICAS
    // TextAlign.configure(...),
    // TextStyle, 
    // FontFamily,
  ],
  editorProps: {
    attributes: {
      class: 'prose-mirror-editor',
    },
  },
});
// ==========================================================


// ==========================================================
// ==================== FUNÇÕES (Fonte/Tamanho) REMOVIDAS ====
// ==========================================================
// const setFontFamily = ...
// const setFontSize = ...
// ==========================================================


// Função para buscar o HTML do contrato
async function fetchContratoHtml() {
  isLoading.value = true;
  error.value = null;
  contratoId.value = route.params.id as string;

  if (!contratoId.value) {
    error.value = 'ID do contrato não encontrado.';
    isLoading.value = false;
    return;
  }

  try {
    const response = await apiClient.get(
      `/v1/contratos/${contratoId.value}/get-html/`
    );
    
    if (editor.value) {
      editor.value.commands.setContent(response.data);
    }
    
  } catch (err) {
    console.error('Erro ao buscar HTML do contrato:', err);
    error.value = 'Não foi possível carregar o documento do contrato.';
    toast.error(error.value);
  } finally {
    isLoading.value = false;
  }
}

// Função para salvar o HTML editado
async function handleSave() {
  if (!editor.value || !contratoId.value) return;
  
  isSaving.value = true;

  const htmlParaSalvar = editor.value.getHTML();

  try {
    await apiClient.post(
      `/v1/contratos/${contratoId.value}/salvar-html-editado/`,
      {
        html_content: htmlParaSalvar,
      }
    );
    toast.success('Documento do contrato salvo com sucesso!');
    
    router.push({ name: 'contratos' }); // Volta para a lista de contratos

  } catch (err) {
    console.error('Erro ao salvar HTML do contrato:', err);
    toast.error('Falha ao salvar o documento.');
  } finally {
    isSaving.value = false;
  }
}

onMounted(fetchContratoHtml);

// Limpar o editor da memória
onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy();
  }
});
</script>

<style>
/* ========================================================== */
/* ================== ESTILOS GLOBAIS DO EDITOR ============== */
/* ========================================================== */
.editor-content-area .prose-mirror-editor {
  min-height: 600px;
  border: 1px solid #ccc;
  border-radius: 0 0 8px 8px; /* Cantos arredondados em baixo */
  padding: 2cm; 
  background: #fdfdfd;
  color: #000;
  
  font-family: 'Times New Roman', serif; 
  line-height: 1.6; 
  font-size: 12px; 
}
.editor-content-area .prose-mirror-editor:focus {
  outline: none;
  border: 1px solid #007bff;
}

/* Estilos do PDF (Títulos) */
.editor-content-area .prose-mirror-editor .h1-pdf {
  font-size: 16px; text-transform: uppercase;
  text-align: center; margin-bottom: 20px; font-weight: bold; 
}
.editor-content-area .prose-mirror-editor .h2-pdf {
  font-size: 14px; text-align: left; margin-top: 25px; margin-bottom: 10px; 
  font-weight: bold;
}
.editor-content-area .prose-mirror-editor .h3-pdf {
  font-size: 12px; text-align: left; font-weight: bold; 
  margin-bottom: 10px;
}

/* Estilos do PDF (Texto) */
.editor-content-area .prose-mirror-editor p {
  text-align: justify; 
  text-indent: 40px; 
  margin-bottom: 10px; 
}
.editor-content-area .prose-mirror-editor ul {
  list-style-type: disc;
  padding-left: 40px;
  text-align: justify;
}
.editor-content-area .prose-mirror-editor li {
  text-align: justify;
}
.editor-content-area .prose-mirror-editor u {
  text-decoration: underline;
}
.editor-content-area .prose-mirror-editor s {
  text-decoration: line-through;
}
.editor-content-area .prose-mirror-editor blockquote {
  border-left: 3px solid #ccc;
  margin-left: 1rem;
  padding-left: 1rem;
  font-style: italic;
  color: #555;
}
.editor-content-area .prose-mirror-editor hr {
  border-top: 1px solid #000;
  margin: 1rem 0;
}

/* ========================================================== */
/* ==================== ESTILOS DA TOOLBAR ================== */
/* ========================================================== */
.editor-toolbar {
  border: 1px solid #ccc;
  border-bottom: none; /* Une-se ao editor */
  border-radius: 8px 8px 0 0;
  background-color: #f8f9fa;
  padding: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.editor-toolbar button,
.editor-toolbar select.editor-select {
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.25rem 0.6rem;
  cursor: pointer;
  font-weight: 500;
  line-height: 1.2;
  font-size: 0.85rem; /* Alinhar tamanho */
}
.editor-toolbar button.is-active,
.editor-toolbar select.editor-select:focus {
  background-color: #007bff;
  color: white;
  border-color: #0056b3;
  outline: none;
}
.editor-toolbar button:hover:not(.is-active) {
  background-color: #e9ecef;
}
.editor-toolbar button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
/* ========================================================== */


/* Estilos da página (Scoped) */
.editor-container {
  padding: 0;
}
.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}
.loading-message,
.error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 0.5rem;
}
.view-header h1 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #333;
}

.editor-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.editor-actions p {
  color: #6c757d;
  text-align: center;
  margin: 0;
}

/* Botões */
.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
.btn-success {
  background-color: #198754;
  color: white;
  border: 1px solid #198754;
}
.btn-success:hover:not(:disabled) {
  background-color: #157347;
}
.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style>
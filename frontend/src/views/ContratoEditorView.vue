<template>
  <div class="page-container editor-container">
    <div v-if="isLoading" class="loading-message card-full-padding">
      <div class="spinner"></div>
      Carregando documento...
    </div>

    <div v-if="error" class="error-message card-full-padding">{{ error }}</div>

    <div v-if="!isLoading && !error && editor" class="card card-no-padding">
      
      <div class="editor-toolbar">
        
        <div class="toolbar-group">
          <button @click="router.back()" class="btn-toolbar-action btn-secondary-toolbar" title="Voltar">
            <i class="fas fa-arrow-left"></i> Voltar
          </button>
          <button @click="handleSave" class="btn-toolbar-action btn-success-toolbar" :disabled="isSaving || isGeneratingPdf" title="Salvar Documento">
            <i v-if="isSaving" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-save"></i>
            Salvar
          </button>
          <button @click="handleVisualizarPDF" class="btn-toolbar-action btn-info-toolbar" :disabled="isGeneratingPdf || isSaving" title="Visualizar PDF">
            <i v-if="isGeneratingPdf" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-file-pdf"></i>
            PDF
          </button>
        </div>
        
        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <button @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()" title="Desfazer">
            <i class="fas fa-undo"></i>
          </button>
          <button @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()" title="Refazer">
            <i class="fas fa-redo"></i>
          </button>
        </div>
        
        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <select 
            class="toolbar-select" 
            :value="getActiveFontFamily()"
            @change="handleFontFamilyChange"
            title="Fonte"
          >
            <option 
              v-for="font in fontFamilies" :key="font.value" 
              :value="font.value"
              :style="{ 'font-family': font.value }"
            >
              {{ font.label }}
            </option>
          </select>
          
          <select 
            class="toolbar-select" 
            :value="getActiveFontSize()"
            @change="handleFontSizeChange"
            title="Tamanho da Fonte"
          >
            <option 
              v-for="size in fontSizes" :key="size.value" 
              :value="size.value"
            >
              {{ size.label }}
            </option>
          </select>
        </div>
        
        <div class="toolbar-divider"></div>
        
        <div class="toolbar-group">
          <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" title="Negrito">
            <i class="fas fa-bold"></i>
          </button>
          <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }" title="Itálico">
            <i class="fas fa-italic"></i>
          </button>
          <button @click="editor.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor.isActive('underline') }" title="Sublinhado">
            <i class="fas fa-underline"></i>
          </button>
          <button @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }" title="Tachado">
            <i class="fas fa-strikethrough"></i>
          </button>
          
          <div class="toolbar-color-wrapper" title="Cor do Texto">
            <i class="fas fa-font"></i>
            <input 
              type="color" 
              @input="editor.chain().focus().setColor($event.target.value).run()" 
              :value="editor.getAttributes('textStyle').color || '#000000'"
              class="toolbar-color-picker"
            >
          </div>
          <div class="toolbar-color-wrapper" title="Cor do Marca-texto">
            <i class="fas fa-highlighter"></i>
            <input 
              type="color" 
              @input="editor.chain().focus().toggleHighlight({ color: $event.target.value }).run()"
              :value="editor.getAttributes('highlight')?.color || '#ffffff'"
              class="toolbar-color-picker"
            >
          </div>
          <button @click="editor.chain().focus().unsetAllMarks().run()" title="Limpar Formatação">
            <i class="fas fa-eraser"></i>
          </button>
        </div>

        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <button @click="editor.chain().focus().setTextAlign('left').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" title="Alinhar à Esquerda">
            <i class="fas fa-align-left"></i>
          </button>
          <button @click="editor.chain().focus().setTextAlign('center').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" title="Centralizar">
            <i class="fas fa-align-center"></i>
          </button>
          <button @click="editor.chain().focus().setTextAlign('right').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" title="Alinhar à Direita">
            <i class="fas fa-align-right"></i>
          </button>
          <button @click="editor.chain().focus().setTextAlign('justify').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'justify' }) }" title="Justificar">
            <i class="fas fa-align-justify"></i>
          </button>
        </div>
        
        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <button @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }" title="Lista">
            <i class="fas fa-list-ul"></i>
          </button>
          <button @click="editor.chain().focus().toggleBlockquote().run()" :class="{ 'is-active': editor.isActive('blockquote') }" title="Citação">
            <i class="fas fa-quote-right"></i>
          </button>
          <button @click="editor.chain().focus().setHorizontalRule().run()" title="Linha Horizontal">
            <i class="fas fa-minus"></i>
          </button>
        </div>

      </div>

      <editor-content :editor="editor" class="editor-content-area" />

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
import StarterKit from '@tiptap/starter-kit';
// import { Heading } from '@tiptap/extension-heading'; // Removido
import { Underline } from '@tiptap/extension-underline';
import { TextAlign } from '@tiptap/extension-text-align';
import { TextStyle } from '@tiptap/extension-text-style'; // Importação Base
import { Color } from '@tiptap/extension-color';
import { Highlight } from '@tiptap/extension-highlight';
import { FontFamily } from '@tiptap/extension-font-family';

// ==========================================================
// === Importar a extensão customizada do NOVO ARQUIVO    ===
// ==========================================================
import { FontSize } from '@/extensions/tiptapExtensions';
// ==========================================================


const route = useRoute();
const router = useRouter(); 
const toast = useToast();

const contratoId = ref<string | null>(null);
const isLoading = ref(true);
const isSaving = ref(false);
const error = ref<string | null>(null);
const isGeneratingPdf = ref(false);

const fontFamilies = ref([
  { label: 'Padrão (Times)', value: 'Times New Roman' },
  { label: 'Arial', value: 'Arial' },
  { label: 'Verdana', value: 'Verdana' },
  { label: 'Courier New', value: 'Courier New' },
  { label: 'Georgia', value: 'Georgia' },
]);

const fontSizes = ref([
  { label: 'Padrão (12px)', value: '12px' },
  { label: '10px', value: '10px' },
  { label: '11px', value: '11px' },
  { label: '14px', value: '14px' },
  { label: '16px', value: '16px' },
  { label: '18px', value: '18px' },
]);


// ==========================================================
// ==================== CONFIGURAÇÃO DO EDITOR TIPTAP =========
// ==========================================================
const editor = useEditor({
  content: '',
  extensions: [
    StarterKit.configure({
      heading: false,     // CORREÇÃO: Desabilitar títulos padrão
      textStyle: false,   // Desabilitar textStyle padrão
    }),
    
    // Títulos (Heading) removidos
    
    Underline,
    
    TextAlign.configure({
      types: ['paragraph'], // Aplicar somente a parágrafos
    }),
    
    // Configuração para permitir `fontFamily` e `fontSize`
    TextStyle,    // A extensão BASE (essencial)
    FontFamily,   // Estende 'TextStyle' com 'fontFamily'
    FontSize,     // Estende 'TextStyle' com 'fontSize' (NOSSA EXTENSÃO IMPORTADA)

    Color,        // Estende 'TextStyle' com 'color'
    Highlight.configure({
      multicolor: true,
    }),
  ],
  editorProps: {
    attributes: {
      class: 'prose-mirror-editor',
    },
  },
});
// ==========================================================

// ==========================================================
// === HANDLERS E GETTERS (Corrigidos)                    ===
// ==========================================================
function handleFontFamilyChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  editor.value?.chain().focus().setFontFamily(target.value).run();
}

function handleFontSizeChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  const size = target.value;
  if (size === '12px') { // Assumindo 12px como padrão
    editor.value?.chain().focus().unsetFontSize().run();
  } else {
    editor.value?.chain().focus().setFontSize(size).run();
  }
}

function getActiveFontFamily() {
  if (!editor.value) return 'Times New Roman';
  return editor.value.getAttributes('textStyle').fontFamily || 'Times New Roman';
}

function getActiveFontSize() {
  if (!editor.value) return '12px';
  return editor.value.getAttributes('textStyle').fontSize || '12px';
}
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

// ==========================================================
// === FUNÇÃO SALVAR (MODIFICADA)                         ===
// ==========================================================
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
    
    // ==========================================================
    // === CORREÇÃO: Linha de redirecionamento REMOVIDA
    // router.push({ name: 'contratos' }); 
    // ==========================================================

  } catch (err) {
    console.error('Erro ao salvar HTML do contrato:', err);
    toast.error('Falha ao salvar o documento.');
  } finally {
    isSaving.value = false;
  }
}

// Função para visualizar o PDF
async function handleVisualizarPDF() {
  if (isGeneratingPdf.value || !contratoId.value) return; 
  isGeneratingPdf.value = true;
  
  try {
    toast.info('Gerando PDF... Por favor, aguarde.', { duration: 2000, position: 'top-right' });
    
    const response = await apiClient.get(
      `/v1/contratos/${contratoId.value}/visualizar-pdf/`,
      {
        responseType: 'blob' 
      }
    );
    const file = new Blob([response.data], { type: 'application/pdf' });
    const fileURL = URL.createObjectURL(file);
    window.open(fileURL, '_blank');
    setTimeout(() => URL.revokeObjectURL(fileURL), 10000);

  } catch (error: any) {
    console.error('Erro ao visualizar PDF:', error.response?.data || error);
    const errorMsg = error.response?.data?.error || "Falha ao gerar o PDF.";
    toast.error(errorMsg, { duration: 5000, position: 'top-right' });
  } finally {
    isGeneratingPdf.value = false;
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
  border-top: 1px solid #ccc;
  padding: 2cm; 
  background: #fdfdfd;
  color: #000;
  
  /* Estilo Padrão */
  font-family: 'Times New Roman', serif; 
  line-height: 1.6; 
  font-size: 12px; 
}
.editor-content-area .prose-mirror-editor:focus {
  outline: none;
}


/* Estilos do PDF (Texto) */
.editor-content-area .prose-mirror-editor p {
  text-align: justify; 
  text-indent: 40px; 
  margin-bottom: 10px; 
}
/* Alinhamento do Tiptap (Aplicado a qualquer tag) */
.editor-content-area .prose-mirror-editor [style*="text-align: left"] {
  text-align: left;
}
.editor-content-area .prose-mirror-editor [style*="text-align: center"] {
  text-align: center;
  text-indent: 0px;
}
.editor-content-area .prose-mirror-editor [style*="text-align: right"] {
  text-align: right;
  text-indent: 0px;
}
.editor-content-area .prose-mirror-editor [style*="text-align: justify"] {
  text-align: justify;
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
/* Estilo Padrão do Marca-texto */
.editor-content-area .prose-mirror-editor mark {
  background-color: #fef08a;
}
/* O Tiptap aplicará <mark style="background-color: #...">, 
  que irá sobrescrever o padrão acima, como esperado.
*/


/* ========================================================== */
/* ==================== ESTILOS DA TOOLBAR ================== */
/* ========================================================== */
.editor-toolbar {
  border: 1px solid #ccc;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  background-color: #f8f9fa;
  padding: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center; /* Alinhar verticalmente */
}

.toolbar-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}
.toolbar-divider {
  width: 1px;
  height: 24px;
  background-color: #ddd;
  margin: 0 0.25rem;
}


/* Botões simples (ícones) */
.editor-toolbar button {
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.25rem 0.6rem;
  cursor: pointer;
  font-weight: 500;
  line-height: 1.2;
  font-size: 0.85rem; 
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  height: 29.5px; /* Altura padrão */
}

/* Botões de Ação (com texto, na toolbar) */
.editor-toolbar .btn-toolbar-action {
  padding: 0.25rem 0.75rem; /* Mais padding para texto */
  font-weight: 500;
  font-size: 0.8rem;
  border-width: 1px;
  border-style: solid;
  transition: background-color 0.2s;
}
.editor-toolbar .btn-toolbar-action i {
  font-size: 0.9em;
}

/* Cores dos botões de ação */
.editor-toolbar .btn-secondary-toolbar {
  background-color: #6c757d; color: white; border-color: #6c757d;
}
.editor-toolbar .btn-secondary-toolbar:hover {
  background-color: #5a6268;
}
.editor-toolbar .btn-success-toolbar {
  background-color: #198754; color: white; border-color: #198754;
}
.editor-toolbar .btn-success-toolbar:hover:not(:disabled) {
  background-color: #157347;
}
.editor-toolbar .btn-info-toolbar {
  background-color: #0d6efd; color: white; border-color: #0d6efd;
}
.editor-toolbar .btn-info-toolbar:hover:not(:disabled) {
  background-color: #0b5ed7;
}

/* Estados (ativo, hover, disabled) */
.editor-toolbar button.is-active {
  background-color: #007bff;
  color: white;
  border-color: #0056b3;
  outline: none;
}
.editor-toolbar button:hover:not(.is-active) {
  background-color: #e9ecef;
}
.editor-toolbar button:disabled,
.editor-toolbar .btn-toolbar-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #e9ecef;
  color: #6c757d;
  border-color: #ced4da;
}
/* Manter a cor de fundo para botões de ação desabilitados */
.editor-toolbar .btn-success-toolbar:disabled {
  background-color: #198754; opacity: 0.6; color: white;
}
.editor-toolbar .btn-info-toolbar:disabled {
  background-color: #0d6efd; opacity: 0.6; color: white;
}
.editor-toolbar .btn-secondary-toolbar:disabled {
  background-color: #6c757d; opacity: 0.6; color: white;
}


/* Select (Dropdown) para Fontes/Tamanhos */
.toolbar-select {
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.25rem 0.4rem;
  cursor: pointer;
  font-weight: 500;
  line-height: 1.2;
  font-size: 0.85rem; 
  height: 29.5px; /* Alinhar altura com botões */
  max-width: 120px; /* Limitar largura */
}
.toolbar-select:hover {
  background-color: #e9ecef;
}
.toolbar-select:focus {
  outline: 2px solid #007bff;
  border-color: #0056b3;
}


/* Seletores de Cor */
.toolbar-color-wrapper {
  display: inline-flex;
  align-items: center;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.25rem 0.6rem;
  gap: 0.4rem;
  height: 29.5px;
  box-sizing: border-box;
}
.toolbar-color-picker {
  width: 20px;
  height: 20px;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}
.toolbar-color-picker::-webkit-color-swatch-wrapper {
  padding: 0;
}
.toolbar-color-picker::-webkit-color-swatch {
  border: 1px solid #888;
  border-radius: 4px;
}
.toolbar-color-picker::-moz-color-swatch {
  border: 1px solid #888;
  border-radius: 4px;
}

</style>

<style scoped>
/* Estilos da página (Scoped) */
.editor-container {
  padding: 0;
}
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}
.card-no-padding {
  padding: 0;
  border-radius: 8px; /* Garantir que o card tenha o radius */
  overflow: hidden; /* Garantir que a toolbar se ajuste */
  border: 1px solid #ccc; /* Adiciona borda ao container geral */
}
.card-full-padding {
  padding: 1.5rem;
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

</style>
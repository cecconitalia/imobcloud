<template>
  <div class="w-full max-w-4xl mx-auto font-sans relative z-30">
    
    <div 
      class="absolute -inset-0.5 bg-gradient-to-r from-primary-600 via-purple-600 to-indigo-600 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000 animate-pulse-slow pointer-events-none">
    </div>
    
    <div 
      class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-xl flex items-center p-1.5 border border-slate-100 dark:border-slate-700 transition-all focus-within:ring-2 focus-within:ring-primary-500/20 focus-within:border-primary-500/50"
    >
      
      <div class="pl-4 pr-3 flex-center h-full">
        <div v-if="loading" class="i-lucide-loader-2 w-6 h-6 animate-spin text-primary-600"></div>
        <div v-else class="i-lucide-sparkles w-6 h-6 text-purple-600 dark:text-purple-400 animate-pulse"></div>
      </div>

      <input 
        ref="inputRef"
        v-model="query"
        type="text" 
        :placeholder="placeholderText" 
        @keydown.enter="handleSearch"
        @keydown="handleKeydown"
        class="w-full bg-transparent border-none outline-none text-slate-700 dark:text-slate-100 text-lg placeholder-slate-400 h-12 px-2"
        autocomplete="off"
      />

      <div class="pr-3 flex items-center gap-2">
        <div 
          v-if="!query" 
          class="hidden sm:flex items-center gap-1 px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700"
        >
          <span class="text-xs text-slate-500 font-mono">⌘K</span>
        </div>
        
        <button 
          @click="handleSearch"
          class="p-2 rounded-xl bg-primary-50 text-primary-600 hover:bg-primary-100 dark:bg-primary-900/20 dark:text-primary-400 dark:hover:bg-primary-900/40 transition-colors"
          :disabled="loading"
        >
          <div class="i-lucide-arrow-right w-5 h-5"></div>
        </button>
      </div>
    </div>

    <div v-if="showSuggestions && !loading" class="absolute top-full left-0 w-full mt-2 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-100 dark:border-slate-800 overflow-hidden animate-fade-in-up">
      <div class="p-2 grid grid-cols-1 sm:grid-cols-2 gap-2">
        <button 
          v-for="(sugestao, index) in sugestoes" 
          :key="index"
          @click="selectSuggestion(sugestao.texto)"
          class="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 text-left transition-colors group/item"
        >
          <div 
            class="w-8 h-8 rounded-full bg-primary-50 dark:bg-slate-800 text-primary-600 flex-center group-hover/item:bg-white dark:group-hover/item:bg-slate-700 shadow-sm border border-slate-100 dark:border-slate-700 transition-all"
          >
            <div :class="[sugestao.icon, 'text-sm']"></div>
          </div>
          <span class="text-sm text-slate-600 dark:text-slate-300 font-medium">{{ sugestao.texto }}</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  loading: { type: Boolean, default: false }
});

const emit = defineEmits(['search']);

const query = ref('');
const inputRef = ref<HTMLInputElement | null>(null);
const showSuggestions = ref(false);

const placeholderText = computed(() => {
  return props.loading 
    ? "A Inteligência Artificial está processando..." 
    : "Digite um comando ou pergunte à IA (ex: 'Novo contrato para João')";
});

interface Sugestao {
  texto: string;
  icon: string;
}

const sugestoes: Sugestao[] = [
  { texto: "Apartamento com 2 quartos no centro", icon: 'i-lucide-building-2' },
  { texto: "Casa com piscina e churrasqueira", icon: 'i-lucide-home' },
  { texto: "Relatório financeiro mensal", icon: 'i-lucide-bar-chart-3' },
  { texto: "Cadastrar novo cliente", icon: 'i-lucide-user-plus' },
];

function handleSearch() {
  if (query.value.trim()) {
    emit('search', query.value);
    showSuggestions.value = false;
  }
}

function selectSuggestion(texto: string) {
  query.value = texto;
  handleSearch();
}

function handleKeydown(e: KeyboardEvent) {
  // Esc para fechar sugestões ou limpar
  if (e.key === 'Escape') {
    if (showSuggestions.value) showSuggestions.value = false;
    else {
      query.value = '';
      inputRef.value?.blur();
    }
  }
  // Mostrar sugestões ao digitar
  if (query.value.length > 0) {
    showSuggestions.value = true;
  }
}

// Global Keyboard Shortcuts
const onGlobalKeydown = (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    inputRef.value?.focus();
    showSuggestions.value = true;
  }
};

onMounted(() => {
  window.addEventListener('keydown', onGlobalKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', onGlobalKeydown);
});
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
<template>
  <div class="w-full max-w-4xl mx-auto font-sans">
    
    <div class="relative group z-20">
      <div 
        class="absolute -inset-1 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000 group-focus-within:opacity-100 group-focus-within:duration-200">
      </div>
      
      <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-xl flex items-center p-2 border border-slate-100 dark:border-slate-700 transition-all">
        
        <div class="pl-4 pr-3 text-purple-600 dark:text-purple-400">
          <Sparkles v-if="!loading" class="w-6 h-6 animate-pulse" />
          <Loader2 v-else class="w-6 h-6 animate-spin text-blue-500" />
        </div>

        <input 
          ref="inputRef"
          v-model="query"
          type="text" 
          :placeholder="placeholderText" 
          class="w-full bg-transparent border-none outline-none text-slate-700 dark:text-slate-100 text-lg placeholder-slate-400 h-12"
          @keyup.enter="handleSearch"
          :disabled="loading"
        />

        <button 
          @click="handleSearch"
          :disabled="!query.trim() || loading"
          class="ml-2 p-3 rounded-xl bg-slate-100 text-slate-400 hover:bg-purple-600 hover:text-white dark:bg-slate-800 dark:text-slate-500 dark:hover:bg-purple-600 dark:hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95"
        >
          <ArrowRight class="w-5 h-5" />
        </button>
      </div>
    </div>

    <div v-if="!loading" class="mt-6 flex flex-wrap justify-center gap-2 animate-fade-in-up">
      <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider w-full text-center mb-1">Experimente perguntar:</span>
      
      <button 
        v-for="(sugestao, index) in sugestoes" 
        :key="index"
        @click="aplicarSugestao(sugestao)"
        class="px-4 py-2 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border border-slate-200 dark:border-slate-700 rounded-full text-sm text-slate-600 dark:text-slate-300 hover:border-purple-400 hover:text-purple-600 hover:shadow-md transition-all cursor-pointer flex items-center gap-2"
      >
        <component :is="sugestao.icon" class="w-3.5 h-3.5 opacity-70" />
        {{ sugestao.texto }}
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { Sparkles, ArrowRight, Loader2, Home, Building2, Wallet } from 'lucide-vue-next';

const props = defineProps({
  loading: { type: Boolean, default: false }
});

const emit = defineEmits(['search']);

const query = ref('');
const inputRef = ref<HTMLInputElement | null>(null);

const placeholderText = computed(() => {
  return props.loading 
    ? "A Inteligência Artificial está analisando seu pedido..." 
    : "Descreva o imóvel dos sonhos (ex: Casa de 3 quartos no centro até 500 mil)";
});

const sugestoes = [
  { texto: "Apartamento com 2 quartos no centro", icon: Building2 },
  { texto: "Casa com piscina e churrasqueira", icon: Home },
  { texto: "Aluguel até R$ 2.000,00", icon: Wallet },
  { texto: "Terreno para investimento", icon: Sparkles },
];

function handleSearch() {
  if (query.value.trim()) {
    emit('search', query.value);
  }
}

function aplicarSugestao(sugestao: any) {
  query.value = sugestao.texto;
  handleSearch();
}
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.5s ease-out forwards;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
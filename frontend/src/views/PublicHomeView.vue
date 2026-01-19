<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import publicApiClient from '@/services/publicApiClient';
import ImovelPublicCard from '@/components/ImovelPublicCard.vue';

const route = useRoute();

// --- Estados ---
const isScrolled = ref(false);
const imoveis = ref<any[]>([]);
const loading = ref(false);
const useAI = ref(false);
const aiMessage = ref('');

// Filtros
const filters = ref({
  search: '',
  tipo: '',
  status: '',
  quartos_min: '',
  vagas_min: '',
  valor_min: '',
  valor_max: ''
});

// --- Lógica de Detecção de Modo ---
const isAgencyMode = computed(() => {
  const hostname = window.location.hostname;
  if (route.path.startsWith('/site')) return true;
  const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === 'teste.localhost';
  const isOfficialProduction = hostname === 'imobhome.com.br' || hostname === 'www.imobhome.com.br';
  return !(isLocalhost || isOfficialProduction);
});

const searchPlaceholder = computed(() => {
  return useAI.value 
    ? "Ex: Casa moderna com 3 suítes perto do metrô..." 
    : "Cidade, bairro ou código do imóvel...";
});

// --- Métodos ---
function limparFiltros() {
  filters.value = {
    search: '', tipo: '', status: '', quartos_min: '', vagas_min: '', valor_min: '', valor_max: ''
  };
  fetchImoveis();
}

async function fetchImoveis() {
  if (!isAgencyMode.value) return;
  loading.value = true;
  aiMessage.value = '';
  
  try {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    let subdomain = (parts.length > 1 && parts[0] !== 'www') ? parts[0] : 'estilomusical';
    if (hostname.includes('localhost')) subdomain = 'estilomusical';

    if (useAI.value && filters.value.search.trim().length > 0) {
      const response = await publicApiClient.post('/public/imoveis/busca-ia/', {
        query: filters.value.search
      }, { params: { subdomain } });
      
      imoveis.value = response.data.imoveis || [];
      aiMessage.value = response.data.mensagem || '';
    } else {
      const params: any = { subdomain, publicado: true, ...filters.value };
      const response = await publicApiClient.get('/public/imoveis/', { params });
      imoveis.value = response.data.results || response.data;
    }
  } catch (error: any) {
    console.error("Erro na busca:", error);
    aiMessage.value = error.response?.data?.error ? `⚠️ ${error.response.data.error}` : "Erro ao conectar com a busca inteligente.";
    if(useAI.value) imoveis.value = [];
  } finally {
    loading.value = false;
  }
}

const handleScroll = () => { isScrolled.value = window.scrollY > 20; };
const scrollTo = (id: string) => { document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }); };

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
  if (isAgencyMode.value) fetchImoveis();
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<template>
  <div v-if="isAgencyMode" class="min-h-screen bg-slate-50 font-sans animate-fade-in">
    
    <div class="relative min-h-[550px] flex items-center justify-center pt-24 pb-32 px-4 text-center rounded-b-[40px] overflow-hidden bg-[url('https://images.unsplash.com/photo-1600585154340-be6199f7a09f?auto=format&fit=crop&q=80')] bg-cover bg-center">
      <div class="absolute inset-0 bg-gradient-to-b from-indigo-950/80 to-indigo-900/95 z-1"></div>
      
      <div class="relative z-10 max-w-4xl w-full">
        <span class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-indigo-200 text-sm font-semibold mb-6 animate-bounce-in">
          <i class="i-mdi-sparkles text-yellow-400"></i> Busca Inteligente Ativada
        </span>
        
        <h2 class="text-4xl md:text-6xl font-extrabold text-white mb-4 leading-tight">
          Onde começa o seu <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">novo capítulo?</span>
        </h2>
        <p class="text-lg md:text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
          Encontre o imóvel ideal através de nossa curadoria digital ou descreva seus desejos para nossa IA.
        </p>
        
        <div class="max-w-3xl mx-auto">
          <div 
            class="bg-white p-2 rounded-2xl md:rounded-full flex flex-col md:flex-row items-center shadow-2xl transition-all duration-300 border-4"
            :class="useAI ? 'border-purple-500/50 shadow-purple-500/20' : 'border-white/10'"
          >
            <div class="flex items-center flex-1 w-full px-4">
              <i class="text-xl mr-3" :class="[useAI ? 'i-mdi-robot-outline text-purple-600' : 'i-mdi-magnify text-slate-400']"></i>
              <input 
                type="text" 
                v-model="filters.search" 
                :placeholder="searchPlaceholder" 
                class="w-full py-4 bg-transparent border-none outline-none text-slate-800 text-lg placeholder:text-slate-400"
                @keyup.enter="fetchImoveis"
                :disabled="loading"
              >
            </div>
            
            <button 
              @click="fetchImoveis" 
              class="w-full md:w-auto px-10 py-4 rounded-xl md:rounded-full font-bold text-white transition-all active:scale-95 disabled:opacity-70 flex items-center justify-center gap-2"
              :class="useAI ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:shadow-lg hover:shadow-purple-500/40' : 'bg-slate-900 hover:bg-slate-800'"
              :disabled="loading"
            >
              <div v-if="loading" class="i-mdi-loading animate-spin text-xl"></div>
              <span>{{ loading ? (useAI ? 'Analisando...' : 'Buscando...') : 'Encontrar' }}</span>
            </button>
          </div>

          <div class="mt-6 flex items-center justify-center gap-3">
            <button 
              @click="useAI = !useAI"
              class="group flex items-center gap-2 cursor-pointer select-none"
            >
              <div 
                class="w-12 h-6 rounded-full relative transition-colors duration-300"
                :class="useAI ? 'bg-purple-600' : 'bg-white/20'"
              >
                <div 
                  class="absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform duration-300"
                  :class="useAI ? 'translate-x-6' : ''"
                ></div>
              </div>
              <span class="text-sm font-medium transition-colors" :class="useAI ? 'text-white' : 'text-slate-400'">
                Usar Busca com Inteligência Artificial
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!useAI" class="max-w-7xl mx-auto px-4 -mt-12 relative z-20">
      <div class="bg-white rounded-2xl shadow-xl border border-slate-100 p-4 md:p-6">
        <div class="flex flex-wrap items-center gap-4">
          
          <div class="flex-1 min-w-[200px] relative">
            <select v-model="filters.tipo" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-700 outline-none focus:border-indigo-500 transition-colors appearance-none">
              <option value="">Tipo de Imóvel</option>
              <option value="CASA">Casa</option>
              <option value="APARTAMENTO">Apartamento</option>
              <option value="TERRENO">Terreno</option>
              <option value="SALA_COMERCIAL">Sala Comercial</option>
            </select>
            <div class="absolute right-4 top-1/2 -translate-y-1/2 i-mdi-chevron-down pointer-events-none text-slate-400"></div>
          </div>

          <div class="flex-1 min-w-[150px] relative">
            <select v-model="filters.status" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-700 outline-none focus:border-indigo-500 transition-colors appearance-none">
              <option value="">Transação</option>
              <option value="A_VENDA">Comprar</option>
              <option value="PARA_ALUGAR">Alugar</option>
            </select>
            <div class="absolute right-4 top-1/2 -translate-y-1/2 i-mdi-chevron-down pointer-events-none text-slate-400"></div>
          </div>

          <div class="w-full md:w-auto flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-1">
            <span class="text-xs font-bold text-slate-400 ml-2">R$</span>
            <input type="number" v-model="filters.valor_min" placeholder="Mínimo" class="w-24 bg-transparent py-2 outline-none text-sm text-slate-700">
            <span class="text-slate-300">|</span>
            <input type="number" v-model="filters.valor_max" placeholder="Máximo" class="w-24 bg-transparent py-2 outline-none text-sm text-slate-700">
          </div>

          <button @click="fetchImoveis" class="bg-indigo-600 text-white w-12 h-12 rounded-xl flex items-center justify-center hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200 active:scale-90">
            <i class="i-mdi-filter-variant text-xl"></i>
          </button>
        </div>
      </div>
    </div>

    <main class="max-w-7xl mx-auto px-4 py-12">
      
      <div v-if="aiMessage" class="mb-10 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-100 rounded-2xl p-6 flex gap-4 items-start shadow-sm animate-fade-in-up">
        <div class="bg-purple-600 p-3 rounded-xl text-white shadow-lg">
          <i class="i-mdi-robot text-2xl"></i>
        </div>
        <div class="flex-1">
          <h4 class="font-bold text-purple-900 mb-1">Dica da nossa IA:</h4>
          <p class="text-slate-700 leading-relaxed">{{ aiMessage }}</p>
        </div>
        <button @click="aiMessage = ''" class="text-slate-400 hover:text-slate-600 p-1">
          <i class="i-mdi-close"></i>
        </button>
      </div>

      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="n in 6" :key="n" class="bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-100">
          <div class="w-full h-64 bg-slate-200 animate-pulse"></div>
          <div class="p-6 space-y-4">
            <div class="h-6 bg-slate-200 rounded w-3/4 animate-pulse"></div>
            <div class="h-4 bg-slate-200 rounded w-1/2 animate-pulse"></div>
            <div class="h-8 bg-slate-200 rounded w-1/3 animate-pulse pt-4"></div>
          </div>
        </div>
      </div>

      <div v-else-if="imoveis.length === 0" class="py-20 text-center">
        <div class="inline-flex items-center justify-center w-24 h-24 rounded-full bg-slate-100 text-slate-300 mb-6">
          <i class="i-mdi-home-search text-5xl"></i>
        </div>
        <h3 class="text-2xl font-bold text-slate-800 mb-2">Ops! Nenhum imóvel por aqui</h3>
        <p class="text-slate-500 mb-8">Não encontramos nada com esses critérios. Que tal tentar uma nova frase na busca com IA?</p>
        <button @click="limparFiltros" class="px-8 py-3 bg-white border border-slate-200 rounded-xl font-bold text-indigo-600 hover:bg-slate-50 transition-colors">
          Ver todos os imóveis
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <ImovelPublicCard 
          v-for="imovel in imoveis" 
          :key="imovel.id" 
          :imovel="imovel"
          class="hover:-translate-y-2 transition-transform duration-300"
        />
      </div>
    </main>

    <a href="https://wa.me/5511999999999" target="_blank" class="fixed bottom-8 right-8 w-16 h-16 bg-green-500 text-white rounded-full flex items-center justify-center text-3xl shadow-2xl shadow-green-500/40 hover:scale-110 transition-transform z-50 animate-bounce-in">
      <i class="i-mdi-whatsapp"></i>
    </a>

  </div>

  <div v-else class="min-h-screen bg-white font-sans">
    <nav 
      class="fixed top-0 w-full z-100 transition-all duration-300 h-20 flex items-center"
      :class="isScrolled ? 'bg-white/80 backdrop-blur-lg shadow-md' : 'bg-transparent'"
    >
      <div class="max-w-7xl mx-auto w-full px-6 flex justify-between items-center">
        <div class="flex items-center gap-2 cursor-pointer group" @click="scrollTo('top')">
          <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white group-hover:rotate-12 transition-transform">
            <i class="i-mdi-laptop-house text-2xl"></i>
          </div>
          <span class="text-2xl font-black text-slate-900 tracking-tight">Imob<span class="text-indigo-600">Home</span></span>
        </div>
        <div class="flex items-center gap-4 md:gap-8">
          <router-link to="/login" class="font-bold text-slate-600 hover:text-indigo-600 transition-colors">Entrar</router-link>
          <router-link to="/cadastro" class="bg-slate-900 text-white px-6 py-2.5 rounded-xl font-bold hover:bg-indigo-600 transition-all active:scale-95 shadow-lg shadow-slate-200">
            Experimentar Grátis
          </router-link>
        </div>
      </div>
    </nav>

    <section id="top" class="pt-40 pb-20 px-6">
      <div class="max-w-5xl mx-auto text-center">
        <h1 class="text-5xl md:text-7xl font-black text-slate-900 mb-8 leading-tight">
          Sua imobiliária no <br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 italic">piloto automático.</span>
        </h1>
        <p class="text-xl text-slate-500 mb-12 max-w-2xl mx-auto leading-relaxed">
          Gestão de leads com IA, publicação automática em redes sociais e site próprio incluso. Tudo em um só lugar.
        </p>
        <div class="flex flex-col md:flex-row justify-center gap-4">
          <router-link to="/cadastro" class="px-10 py-5 bg-indigo-600 text-white rounded-2xl font-black text-lg hover:bg-indigo-700 hover:shadow-2xl hover:shadow-indigo-200 transition-all active:scale-95">
            Começar Agora — É Grátis
          </router-link>
          <button class="px-10 py-5 bg-white text-slate-900 border-2 border-slate-100 rounded-2xl font-black text-lg hover:bg-slate-50 transition-all">
            Ver Demonstração
          </button>
        </div>
        
        <div class="mt-20 relative px-4 md:px-0">
          <div class="bg-slate-900 rounded-3xl p-2 shadow-3xl">
             <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80" class="rounded-2xl opacity-90" alt="ImobCloud Dashboard">
          </div>
          <div class="absolute -bottom-6 -right-6 md:right-12 bg-white p-4 rounded-2xl shadow-xl border border-slate-100 hidden md:block">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                <i class="i-mdi-trending-up"></i>
              </div>
              <div>
                <p class="text-xs text-slate-400 font-bold uppercase">Novos Leads</p>
                <p class="text-lg font-black text-slate-900">+124% este mês</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style>
/* Estilos globais necessários para as animações base */
.animate-fade-in { animation: fadeIn 0.6s ease-out; }
.animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
.animate-bounce-in { animation: bounceIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55); }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeInUp { 
  from { opacity: 0; transform: translateY(20px); } 
  to { opacity: 1; transform: translateY(0); } 
}
@keyframes bounceIn {
  0% { opacity: 0; transform: scale(0.3); }
  50% { opacity: 1; transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); }
}
</style>
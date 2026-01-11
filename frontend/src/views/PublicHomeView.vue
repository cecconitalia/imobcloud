<template>
  <div v-if="isAgencyMode" class="agency-home fade-in">
    
    <div class="agency-hero">
      <div class="hero-overlay"></div>
      <div class="container hero-container">
        <span class="hero-badge">
            <i class="fas fa-sparkles"></i> Nova Busca Inteligente
        </span>
        <h2 class="agency-title">Qual o imóvel dos seus sonhos?</h2>
        <p class="agency-subtitle">Descreva o que você procura e nossa IA encontra para você.</p>
        
        <div class="search-wrapper">
          <div class="search-box glass-effect" :class="{ 'ai-active': useAI }">
            <div class="input-icon">
                <i class="fas" :class="useAI ? 'fa-robot' : 'fa-search'"></i>
            </div>
            <input 
              type="text" 
              v-model="filters.search" 
              :placeholder="searchPlaceholder" 
              @keyup.enter="fetchImoveis"
              :disabled="loading"
            >
            <button @click="fetchImoveis" class="btn-search" :disabled="loading">
              <span v-if="loading && useAI" class="typing-dots">Pensando...</span>
              <span v-else-if="loading">Buscando...</span>
              <span v-else>Buscar</span>
            </button>
          </div>

          <div class="ai-toggle-wrapper">
            <label class="toggle-switch">
                <input type="checkbox" v-model="useAI">
                <span class="slider round"></span>
            </label>
            <span class="toggle-label" :class="{ 'active': useAI }">
                Ativar Inteligência Artificial
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!useAI" class="filters-section container">
        <div class="filters-bar slide-up">
            <div class="filters-scroll">
                <div class="filter-group">
                    <i class="fas fa-home filter-icon"></i>
                    <select v-model="filters.tipo" class="form-select">
                        <option value="">Tipo de Imóvel</option>
                        <option value="CASA">Casa</option>
                        <option value="APARTAMENTO">Apartamento</option>
                        <option value="TERRENO">Terreno</option>
                        <option value="SALA_COMERCIAL">Sala Comercial</option>
                        <option value="GALPAO">Galpão</option>
                        <option value="RURAL">Rural</option>
                    </select>
                </div>

                <div class="filter-group">
                    <i class="fas fa-key filter-icon"></i>
                    <select v-model="filters.status" class="form-select">
                        <option value="">Operação</option>
                        <option value="A_VENDA">Comprar</option>
                        <option value="PARA_ALUGAR">Alugar</option>
                    </select>
                </div>

                <div class="filter-group small">
                    <select v-model="filters.quartos_min" class="form-select">
                        <option value="">Quartos</option>
                        <option value="1">1+</option>
                        <option value="2">2+</option>
                        <option value="3">3+</option>
                        <option value="4">4+</option>
                    </select>
                </div>

                <div class="filter-group money-group">
                    <span class="currency">R$</span>
                    <input type="number" v-model="filters.valor_min" placeholder="Mínimo" class="form-input">
                </div>
                <div class="separator">-</div>
                <div class="filter-group money-group">
                    <span class="currency">R$</span>
                    <input type="number" v-model="filters.valor_max" placeholder="Máximo" class="form-input">
                </div>
                
                <button @click="fetchImoveis" class="btn-filter-apply" title="Aplicar Filtros">
                    <i class="fas fa-check"></i>
                </button>
            </div>
        </div>
    </div>

    <div class="container listings-section">
      
      <div v-if="aiMessage" class="ai-feedback fade-in-up">
        <div class="ai-avatar">
            <i class="fas fa-magic"></i>
        </div>
        <div class="ai-content">
            <strong>Assistente Virtual:</strong>
            <p>{{ aiMessage }}</p>
        </div>
        <button @click="aiMessage = ''" class="close-feedback"><i class="fas fa-times"></i></button>
      </div>

      <div v-if="loading" class="imoveis-grid">
        <div v-for="n in 6" :key="n" class="skeleton-card">
            <div class="skeleton-image"></div>
            <div class="skeleton-content">
                <div class="skeleton-line title"></div>
                <div class="skeleton-line subtitle"></div>
                <div class="skeleton-line price"></div>
            </div>
        </div>
      </div>

      <div v-else-if="imoveis.length === 0" class="empty-state fade-in">
        <div class="empty-icon">
            <i class="fas fa-search-location"></i>
        </div>
        <h3>Nenhum imóvel encontrado</h3>
        <p>Tente mudar os filtros ou fazer uma nova busca com a IA.</p>
        <button class="btn-reset" @click="limparFiltros">Limpar Filtros</button>
      </div>

      <div v-else class="imoveis-grid fade-in">
        <ImovelPublicCard 
          v-for="imovel in imoveis" 
          :key="imovel.id" 
          :imovel="imovel" 
        />
      </div>

    </div>

    <a href="https://wa.me/5511999999999" target="_blank" class="floating-whatsapp" title="Fale conosco">
        <i class="fab fa-whatsapp"></i>
    </a>

  </div>

  <div v-else class="landing-page">
    <nav class="navbar" :class="{ 'scrolled': isScrolled }">
      <div class="container nav-content">
        <div class="logo" @click="scrollTo('top')">
          <div class="logo-icon"><i class="fas fa-laptop-house"></i></div>
          <span class="logo-text">Imob<span class="highlight">Home</span></span>
        </div>
        <div class="nav-actions">
          <router-link to="/login" class="btn-login">Entrar</router-link>
          <router-link to="/cadastro" class="btn-cta-small">Criar Conta</router-link>
        </div>
      </div>
    </nav>

    <section id="top" class="hero-section">
      <div class="container hero-content">
        <h1 class="hero-title">Gestão Imobiliária <span class="gradient-text">Simples</span></h1>
        <p class="hero-subtitle">O sistema ideal para corretores e pequenas imobiliárias.</p>
        <div class="hero-buttons">
          <router-link to="/cadastro" class="btn-hero-primary">Começar Agora</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import publicApiClient from '@/services/publicApiClient';
import ImovelPublicCard from '@/components/ImovelPublicCard.vue';

const route = useRoute();

// --- Estados ---
const isScrolled = ref(false);
const imoveis = ref([]);
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

// --- Computed ---
const isAgencyMode = computed(() => {
  const hostname = window.location.hostname;
  const isSubdomain = hostname.split('.').length > 1 && !hostname.startsWith('www') && !hostname.startsWith('localhost');
  const isLocalhostTest = hostname === 'teste.localhost';
  return route.path.startsWith('/site') || isSubdomain || isLocalhostTest;
});

const searchPlaceholder = computed(() => {
    return useAI.value 
        ? "Ex: Casa de praia com 4 suítes e piscina..." 
        : "Busque por cidade, bairro ou código...";
});

// --- Métodos ---
function limparFiltros() {
    filters.value = {
        search: '', tipo: '', status: '', quartos_min: '', vagas_min: '', valor_min: '', valor_max: ''
    };
    fetchImoveis();
}

async function fetchImoveis() {
  loading.value = true;
  aiMessage.value = '';
  
  try {
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    
    // Identificação do Subdomínio
    let subdomain = (parts.length > 1 && parts[0] !== 'www') ? parts[0] : 'estilomusical';
    if (hostname === 'localhost') subdomain = 'estilomusical';
    if (hostname === 'teste.localhost') subdomain = 'teste';

    // ROTA A: Busca com IA
    if (useAI.value && filters.value.search.trim().length > 0) {
        // CORREÇÃO CRÍTICA: Barra '/' no final
        const response = await publicApiClient.post('/public/imoveis/busca-ia/', {
            query: filters.value.search
        }, { 
            params: { subdomain: subdomain } 
        });
        
        imoveis.value = response.data.imoveis || [];
        if (response.data.mensagem) {
            aiMessage.value = response.data.mensagem;
        }

    // ROTA B: Busca Padrão
    } else {
        const params: any = { subdomain: subdomain, publicado: true };
        if (filters.value.search) params.search = filters.value.search; 
        if (filters.value.tipo) params.tipo = filters.value.tipo;
        if (filters.value.status) params.status = filters.value.status;
        if (filters.value.quartos_min) params.quartos_min = filters.value.quartos_min;
        if (filters.value.vagas_min) params.vagas_min = filters.value.vagas_min;
        if (filters.value.valor_min) params.valor_min = filters.value.valor_min;
        if (filters.value.valor_max) params.valor_max = filters.value.valor_max;

        const response = await publicApiClient.get('/public/imoveis/', { params });
        imoveis.value = response.data.results || response.data;
    }

  } catch (error: any) {
    console.error("Erro ao buscar imóveis", error);
    if (error.response && error.response.data && error.response.data.error) {
        aiMessage.value = `⚠️ ${error.response.data.error}`;
    } else {
        aiMessage.value = "Não conseguimos conectar com a busca inteligente agora.";
    }
    // Em caso de erro na IA, tenta mostrar todos os imóveis ou limpa a lista
    if(useAI.value) imoveis.value = [];
  } finally {
    loading.value = false;
  }
}

// Scroll Handler
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

<style scoped>
/* ========================================= */
/* ESTILOS MODERNOS (IMOBCLOUD 2.0)          */
/* ========================================= */

/* HERO SECTION */
.agency-hero {
  position: relative;
  background-image: url('https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&q=80'); /* Imagem Placeholder */
  background-size: cover;
  background-position: center;
  padding: 6rem 1.5rem 8rem;
  color: white;
  text-align: center;
  border-radius: 0 0 30px 30px;
  overflow: hidden;
  margin-bottom: -40px; /* Para a barra de filtros sobrepor */
}

.hero-overlay {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(180deg, rgba(30,27,75,0.7) 0%, rgba(30,27,75,0.9) 100%);
    z-index: 1;
}

.hero-container { position: relative; z-index: 2; max-width: 800px; margin: 0 auto; }

.hero-badge {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(5px);
    padding: 6px 16px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #e9d5ff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: inline-block;
    margin-bottom: 1.5rem;
}

.agency-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  line-height: 1.2;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.agency-subtitle {
  font-size: 1.2rem;
  color: #cbd5e1;
  margin-bottom: 3rem;
  font-weight: 400;
}

/* SEARCH BOX */
.search-box {
  background: white;
  padding: 8px;
  border-radius: 100px;
  display: flex;
  align-items: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  transition: all 0.4s ease;
  border: 4px solid rgba(255,255,255,0.1);
}

.search-box.ai-active {
    border-color: #a855f7;
    box-shadow: 0 0 30px rgba(168, 85, 247, 0.4);
}

.input-icon {
    padding-left: 20px;
    color: #94a3b8;
    font-size: 1.2rem;
}

.search-box input {
  flex: 1;
  border: none;
  padding: 16px;
  font-size: 1.1rem;
  outline: none;
  color: #1e293b;
  background: transparent;
}

.btn-search {
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}
.search-box.ai-active .btn-search {
    background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%);
}
.btn-search:hover { transform: scale(1.05); }

/* TOGGLE IA */
.ai-toggle-wrapper {
    margin-top: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
.toggle-switch { position: relative; width: 50px; height: 28px; display: inline-block; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(255,255,255,0.2); transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: #a855f7; }
input:checked + .slider:before { transform: translateX(22px); }
.toggle-label { color: rgba(255,255,255,0.8); font-size: 0.95rem; font-weight: 500; cursor: pointer; }
.toggle-label.active { color: white; text-shadow: 0 0 10px #a855f7; }

/* FILTROS */
.filters-section { position: relative; z-index: 10; margin-bottom: 3rem; }
.filters-bar {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 15px 30px -10px rgba(0,0,0,0.1);
    border: 1px solid #f1f5f9;
}
.filters-scroll { display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 5px; align-items: center; }
.filters-scroll::-webkit-scrollbar { height: 4px; }
.filters-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }

.filter-group { position: relative; display: flex; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0 10px; min-width: 160px; transition: border 0.3s; }
.filter-group:focus-within { border-color: #4f46e5; background: white; }
.filter-icon { color: #94a3b8; margin-right: 8px; font-size: 0.9rem; }
.form-select, .form-input { border: none; background: transparent; padding: 12px 5px; width: 100%; font-size: 0.95rem; color: #334155; outline: none; cursor: pointer; }
.separator { color: #cbd5e1; font-weight: bold; }
.money-group { min-width: 120px; }
.currency { color: #64748b; font-size: 0.85rem; font-weight: 600; }

.btn-filter-apply {
    background: #1e293b; color: white; width: 45px; height: 45px; border-radius: 10px; border: none; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; transition: background 0.3s;
}
.btn-filter-apply:hover { background: #4f46e5; }

/* AI FEEDBACK */
.ai-feedback {
    background: linear-gradient(135deg, #fff 0%, #f3e8ff 100%);
    border: 1px solid #e9d5ff;
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    gap: 1.5rem;
    align-items: start;
    box-shadow: 0 10px 20px -5px rgba(147, 51, 234, 0.1);
    margin-bottom: 2rem;
}
.ai-avatar {
    width: 48px; height: 48px; background: #9333ea; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; box-shadow: 0 5px 15px rgba(147, 51, 234, 0.3);
}
.ai-content p { margin: 4px 0 0; color: #475569; line-height: 1.5; }
.close-feedback { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 1.1rem; }

/* LISTINGS & SKELETON */
.imoveis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 2rem;
    padding-bottom: 4rem;
}

/* Skeleton Loading CSS */
.skeleton-card { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 420px; }
.skeleton-image { width: 100%; height: 220px; background: #e2e8f0; animation: pulse 1.5s infinite; }
.skeleton-content { padding: 1.5rem; display: flex; flex-direction: column; gap: 10px; }
.skeleton-line { height: 16px; background: #e2e8f0; border-radius: 4px; animation: pulse 1.5s infinite; }
.skeleton-line.title { width: 80%; height: 24px; }
.skeleton-line.subtitle { width: 60%; }
.skeleton-line.price { width: 40%; height: 20px; margin-top: 10px; }

@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

/* EMPTY STATE */
.empty-state { text-align: center; padding: 4rem 1rem; color: #64748b; }
.empty-icon { font-size: 4rem; color: #cbd5e1; margin-bottom: 1.5rem; }
.btn-reset { margin-top: 1.5rem; background: white; border: 1px solid #e2e8f0; padding: 10px 20px; border-radius: 8px; color: #4f46e5; font-weight: 600; cursor: pointer; }
.btn-reset:hover { border-color: #4f46e5; }

/* WHATSAPP FLOAT */
.floating-whatsapp {
    position: fixed; bottom: 30px; right: 30px; background: #25d366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; box-shadow: 0 10px 20px rgba(37, 211, 102, 0.3); z-index: 999; transition: transform 0.3s;
}
.floating-whatsapp:hover { transform: scale(1.1) rotate(10deg); }

/* ANIMATIONS */
.fade-in { animation: fadeIn 0.5s ease-out; }
.slide-up { animation: slideUp 0.6s ease-out; }
.fade-in-up { animation: fadeInUp 0.5s ease-out; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes fadeInUp { from { transform: translateY(10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

/* SAAS Styles (Mantendo o básico para não quebrar) */
.landing-page { font-family: 'Inter', sans-serif; }
.navbar { position: fixed; top: 0; width: 100%; height: 80px; background: white; z-index: 100; display: flex; align-items: center; padding: 0 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.nav-content { width: 100%; max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.logo { font-weight: bold; font-size: 1.5rem; color: #1e1b4b; cursor: pointer; }
.btn-login { color: #4f46e5; font-weight: 600; margin-right: 20px; text-decoration: none; }
.btn-cta-small { background: #4f46e5; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; }
.hero-section { padding-top: 150px; text-align: center; }
.gradient-text { background: linear-gradient(to right, #4f46e5, #9333ea); -webkit-background-clip: text; color: transparent; }
.hero-title { font-size: 3.5rem; margin-bottom: 20px; }
.btn-hero-primary { background: #4f46e5; color: white; padding: 15px 30px; border-radius: 10px; text-decoration: none; font-size: 1.2rem; display: inline-block; margin-top: 20px; }

/* Responsive adjustments */
@media (max-width: 768px) {
    .agency-title { font-size: 2rem; }
    .search-box { flex-direction: column; padding: 15px; border-radius: 20px; }
    .search-box input { width: 100%; text-align: center; margin: 10px 0; }
    .btn-search { width: 100%; }
}
</style>
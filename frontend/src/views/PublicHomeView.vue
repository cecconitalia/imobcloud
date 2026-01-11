<template>
  <div v-if="isAgencyMode" class="agency-home fade-in">
    
    <div class="agency-hero">
      <div class="container hero-container">
        <h2 class="agency-title">Encontre seu novo lar</h2>
        <p class="agency-subtitle">Confira as melhores oportunidades selecionadas para você.</p>
        
        <div class="search-wrapper">
          <div class="search-box" :class="{ 'ai-active': useAI }">
            <input 
              type="text" 
              v-model="filters.search" 
              :placeholder="searchPlaceholder" 
              @keyup.enter="fetchImoveis"
            >
            <button @click="fetchImoveis" class="btn-search">
              <i class="fas" :class="useAI ? 'fa-magic' : 'fa-search'"></i>
              <span class="btn-text">Buscar</span>
            </button>
          </div>

          <div class="ai-toggle-container">
            <label class="toggle-switch">
                <input type="checkbox" v-model="useAI">
                <span class="slider round"></span>
            </label>
            <span class="toggle-label" :class="{ 'active': useAI }">
                <i class="fas fa-robot"></i> Busca com Inteligência Artificial
            </span>
          </div>

        </div>
      </div>
    </div>

    <div v-if="!useAI" class="filters-bar-container container">
        <div class="filters-bar fade-in-down">
            <div class="filters-scroll">
                <div class="filter-group">
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

                <div class="filter-group small">
                    <select v-model="filters.vagas_min" class="form-select">
                        <option value="">Vagas</option>
                        <option value="1">1+</option>
                        <option value="2">2+</option>
                        <option value="3">3+</option>
                    </select>
                </div>

                <div class="filter-group">
                    <input 
                        type="number" 
                        v-model="filters.valor_min" 
                        placeholder="Valor Mín. (R$)" 
                        class="form-input"
                    >
                </div>

                <div class="filter-group">
                    <input 
                        type="number" 
                        v-model="filters.valor_max" 
                        placeholder="Valor Máx. (R$)" 
                        class="form-input"
                    >
                </div>
                
                <button @click="fetchImoveis" class="btn-filter-apply" title="Aplicar Filtros">
                    <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    </div>

    <div class="container listings-section">
      
      <div v-if="aiMessage" class="ai-feedback fade-in">
        <div class="ai-icon-box"><i class="fas fa-robot"></i></div>
        <div class="ai-text-content">
            <span class="ai-title">Análise da IA:</span>
            <span class="ai-msg">{{ aiMessage }}</span>
        </div>
        <button @click="aiMessage = ''" class="close-feedback">&times;</button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p v-if="useAI">A Inteligência Artificial está analisando seu pedido...</p>
        <p v-else>Carregando imóveis...</p>
      </div>

      <div v-else-if="imoveis.length === 0" class="empty-state">
        <i class="fas fa-home"></i>
        <p>Nenhum imóvel encontrado no momento.</p>
        <p class="text-sm text-gray-500 mt-2">Tente ajustar sua pesquisa ou verificar os filtros.</p>
      </div>

      <div v-else class="imoveis-grid">
        <ImovelPublicCard 
          v-for="imovel in imoveis" 
          :key="imovel.id" 
          :imovel="imovel" 
        />
      </div>

    </div>
  </div>

  <div v-else class="landing-page">
    
    <nav class="navbar" :class="{ 'scrolled': isScrolled }">
      <div class="container nav-content">
        <div class="logo" @click="scrollTo('top')">
          <div class="logo-icon">
            <i class="fas fa-laptop-house"></i>
          </div>
          <span class="logo-text">Imob<span class="highlight">Home</span></span>
        </div>

        <div class="desktop-menu">
          <a href="#recursos" class="nav-link">Recursos</a>
          <a href="#planos" class="nav-link">Planos</a>
          <a href="#contato" class="nav-link">Contato</a>
        </div>

        <div class="nav-actions">
          <router-link to="/login" class="btn-login">Entrar</router-link>
          <router-link to="/cadastro" class="btn-cta-small">Teste 7 dias Grátis</router-link>
        </div>

        <button class="mobile-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
          <i class="fas" :class="mobileMenuOpen ? 'fa-times' : 'fa-bars'"></i>
        </button>
      </div>

      <div class="mobile-menu" v-if="mobileMenuOpen">
        <a href="#recursos" @click="mobileMenuOpen = false">Recursos</a>
        <a href="#planos" @click="mobileMenuOpen = false">Planos</a>
        <div class="mobile-actions">
          <router-link to="/login" class="btn-login-mobile">Login</router-link>
          <router-link to="/cadastro" class="btn-cta-mobile">Teste Grátis</router-link>
        </div>
      </div>
    </nav>

    <section id="top" class="hero-section">
      <div class="hero-bg-decoration"></div>
      
      <div class="container hero-content">
        <div class="badge-new">
          <span class="dot"></span> Versão 2.0 Lançada
        </div>
        
        <h1 class="hero-title">
          Gestão Imobiliária <br />
          <span class="gradient-text">Simples e Poderosa</span>
        </h1>
        
        <p class="hero-subtitle">
          Centralize seus imóveis, gere contratos em segundos e tenha seu site próprio. A ferramenta definitiva para corretores de sucesso.
        </p>
        
        <div class="hero-buttons">
          <router-link to="/cadastro" class="btn-hero-primary">
            Começar Teste Grátis <i class="fas fa-arrow-right"></i>
          </router-link>
          <a href="#recursos" class="btn-hero-secondary">
            <i class="fas fa-play-circle"></i> Ver funcionalidades
          </a>
        </div>
        
        <p class="hero-note">
            <i class="fas fa-check-circle"></i> Sem necessidade de cartão de crédito
        </p>

        <div class="dashboard-preview fade-in-up">
          <div class="browser-frame">
             <div class="browser-header">
               <div class="dots">
                 <span class="dot-red"></span>
                 <span class="dot-yellow"></span>
                 <span class="dot-green"></span>
               </div>
               <div class="address-bar">imobhome.com.br/dashboard</div>
             </div>
             <div class="mockup-container">
                <div class="mock-sidebar">
                   <div class="mock-nav-item active"><i class="fas fa-chart-pie"></i></div>
                   <div class="mock-nav-item"><i class="fas fa-home"></i></div>
                   <div class="mock-nav-item"><i class="fas fa-users"></i></div>
                </div>
                <div class="mock-content">
                   <div class="mock-topbar">
                      <div class="mock-search"></div>
                      <div class="mock-user-profile"><div class="mock-avatar"></div></div>
                   </div>
                   <div class="mock-stats-grid">
                      <div class="mock-card">
                         <div class="mock-icon-bg indigo"><i class="fas fa-home"></i></div>
                         <div class="mock-stat-info"><span class="label">Imóveis</span><span class="value">142</span></div>
                      </div>
                      <div class="mock-card">
                         <div class="mock-icon-bg green"><i class="fas fa-check-circle"></i></div>
                         <div class="mock-stat-info"><span class="label">Contratos</span><span class="value">28</span></div>
                      </div>
                      <div class="mock-card">
                         <div class="mock-icon-bg blue"><i class="fas fa-dollar-sign"></i></div>
                         <div class="mock-stat-info"><span class="label">Receita</span><span class="value">R$ 12k</span></div>
                      </div>
                   </div>
                </div>
             </div>
          </div>
        </div>
      </div>
    </section>

    <section id="recursos" class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">Tudo em um só lugar</span>
          <h2>Potencialize suas Vendas</h2>
          <p>Ferramentas desenvolvidas especificamente para o dia a dia do mercado imobiliário.</p>
        </div>
        <div class="features-grid">
          <div class="feature-card">
            <div class="icon-box icon-indigo"><i class="fas fa-home"></i></div>
            <h3>Gestão de Imóveis</h3>
            <p>Cadastre fotos ilimitadas e gere descrições com IA.</p>
          </div>
          <div class="feature-card">
            <div class="icon-box icon-green"><i class="fas fa-globe"></i></div>
            <h3>Site Próprio</h3>
            <p>Tenha um site moderno e responsivo.</p>
          </div>
          <div class="feature-card">
            <div class="icon-box icon-blue"><i class="fas fa-file-contract"></i></div>
            <h3>Contratos Digitais</h3>
            <p>Geração automática de contratos de venda e aluguel.</p>
          </div>
        </div>
      </div>
    </section>

    <footer class="footer">
      <div class="container footer-grid">
        <div class="footer-brand">
            <div class="footer-logo"><i class="fas fa-laptop-house"></i> ImobHome</div>
            <p>Sistema de gestão imobiliária.</p>
        </div>
        <div class="footer-bottom">
          &copy; {{ new Date().getFullYear() }} ImobHome Tecnologia.
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import publicApiClient from '@/services/publicApiClient';
import ImovelPublicCard from '@/components/ImovelPublicCard.vue';

const route = useRoute();

// --- Estados Gerais ---
const mobileMenuOpen = ref(false);
const isScrolled = ref(false);

// --- Estados Modo Agência ---
const isAgencyMode = computed(() => {
  const hostname = window.location.hostname;
  const isSubdomain = hostname.split('.').length > 1 && !hostname.startsWith('www') && !hostname.startsWith('localhost');
  const isLocalhostTest = hostname === 'teste.localhost';
  return route.path.startsWith('/site') || isSubdomain || isLocalhostTest;
});

const imoveis = ref([]);
const loading = ref(false);
const useAI = ref(false);
const aiMessage = ref('');

// Filtros
const filters = ref({
  search: '',
  tipo: '',
  status: '', // Operação (A_VENDA, PARA_ALUGAR)
  quartos_min: '',
  vagas_min: '',
  valor_min: '',
  valor_max: ''
});

const searchPlaceholder = computed(() => {
    return useAI.value 
        ? "Ex: Casa com 3 quartos e piscina no centro..." 
        : "Buscar por cidade, bairro ou código...";
});

// --- Lógica Modo Agência ---
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

    // ROTA A: Busca com Inteligência Artificial
    if (useAI.value && filters.value.search.trim().length > 0) {
        // CORREÇÃO CRÍTICA: Adicionada a barra no final da URL
        const response = await publicApiClient.post('/public/imoveis/busca-ia/', {
            query: filters.value.search
        }, { 
            params: { subdomain: subdomain } 
        });
        
        imoveis.value = response.data.imoveis || [];
        if (response.data.mensagem) {
            aiMessage.value = response.data.mensagem;
        }

    // ROTA B: Busca Padrão com Filtros
    } else {
        const params: any = {
            subdomain: subdomain, 
            publicado: true
        };

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
    // Tenta pegar a mensagem detalhada do backend
    if (error.response && error.response.data && error.response.data.error) {
        aiMessage.value = `Erro: ${error.response.data.error}`;
    } else {
        aiMessage.value = "Ocorreu um erro ao processar sua busca. Tente novamente.";
    }
    imoveis.value = [];
  } finally {
    loading.value = false;
  }
}

// --- Lógica Modo SaaS (Scroll e Menu) ---
const handleScroll = () => {
  isScrolled.value = window.scrollY > 20;
};

const scrollTo = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
  if (isAgencyMode.value) {
    fetchImoveis();
  }
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* ========================================= */
/* ESTILOS MODO AGÊNCIA (TENANT)             */
/* ========================================= */
.agency-home {
  min-height: 80vh;
  padding-bottom: 4rem;
  background-color: #f9fafb;
}

.agency-hero {
  background: linear-gradient(135deg, var(--primary-color, #1e1b4b) 0%, #1e293b 100%);
  color: white;
  padding: 4rem 1.5rem 6rem; 
  text-align: center;
  border-radius: 0 0 2rem 2rem;
  margin-bottom: -3rem; /* Ajustado para encaixar a barra de filtros */
}

.hero-container {
  max-width: 900px;
  margin: 0 auto;
}

.agency-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.agency-subtitle {
  font-size: 1.1rem;
  color: #94a3b8;
  margin-bottom: 2.5rem;
}

/* SEARCH AREA */
.search-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    width: 100%;
    margin: 0 auto;
}

.search-box {
  background: white;
  padding: 0.5rem;
  border-radius: 50px;
  display: flex;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  transition: all 0.3s;
}

/* Efeito Glow quando IA ativa */
.search-box.ai-active {
    box-shadow: 0 0 15px rgba(124, 58, 237, 0.4), 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(124, 58, 237, 0.3);
}

.search-box input {
  flex: 1;
  border: none;
  padding: 1rem 1.5rem;
  border-radius: 50px 0 0 50px;
  outline: none;
  font-size: 1rem;
  color: #374151;
  width: 100%;
}

.btn-search {
  background-color: var(--primary-color, #4f46e5);
  color: white;
  border: none;
  padding: 0 2rem;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.search-box.ai-active .btn-search {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
}
.btn-search:hover { opacity: 0.9; }

/* TOGGLE SWITCH IA */
.ai-toggle-container {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(255, 255, 255, 0.1);
    padding: 8px 16px;
    border-radius: 20px;
    backdrop-filter: blur(5px);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch input { opacity: 0; width: 0; height: 0; }

.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #64748b;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #a855f7; /* Roxo IA */
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.slider.round { border-radius: 34px; }
.slider.round:before { border-radius: 50%; }

.toggle-label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #cbd5e1;
    transition: color 0.3s;
    display: flex;
    align-items: center;
    gap: 6px;
}
.toggle-label.active { color: #e9d5ff; text-shadow: 0 0 10px rgba(168, 85, 247, 0.5); }

/* BARRA DE FILTROS HORIZONTAL */
.filters-bar-container {
    position: relative;
    z-index: 20;
    margin-top: -1.5rem; /* Sobe para sobrepor o Hero */
    margin-bottom: 2rem;
}

.filters-bar {
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    padding: 1rem;
    border: 1px solid #f1f5f9;
}

.filters-scroll {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
    justify-content: center;
}

.filter-group {
    flex: 1;
    min-width: 140px;
}
.filter-group.small {
    min-width: 90px;
    flex: 0.5;
}

.form-select, .form-input {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #334155;
  outline: none;
  transition: border-color 0.2s;
  background-color: #f8fafc;
}
.form-select:focus, .form-input:focus {
  border-color: #4f46e5;
  background-color: white;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
}

.btn-filter-apply {
    background-color: #4f46e5;
    color: white;
    border: none;
    width: 42px;
    height: 42px;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    transition: background 0.2s;
}
.btn-filter-apply:hover { background-color: #4338ca; }

/* FEEDBACK IA */
.ai-feedback {
    background: white;
    border-left: 4px solid #a855f7;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    position: relative;
}
.ai-icon-box {
    background: #f3e8ff;
    color: #9333ea;
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.ai-text-content {
    display: flex;
    flex-direction: column;
}
.ai-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #9333ea;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 2px;
}
.ai-msg {
    font-size: 0.95rem;
    color: #334155;
    line-height: 1.4;
}
.close-feedback {
    margin-left: auto;
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 1.2rem;
    cursor: pointer;
}

/* Grid de Imóveis */
.listings-section {
  position: relative;
  z-index: 10;
  min-height: 400px;
}

.imoveis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 0;
  color: #64748b;
}
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #cbd5e1;
}
.spinner {
  border: 4px solid #e2e8f0;
  border-top: 4px solid var(--primary-color, #4f46e5);
  border-radius: 50%;
  width: 40px; height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* ========================================= */
/* ESTILOS MODO SAAS (LANDING PAGE ORIGINAL) */
/* ========================================= */
.landing-page {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #374151;
  background-color: #f9fafb;
  line-height: 1.5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

a { text-decoration: none; color: inherit; }

/* NAVBAR */
.navbar {
  position: fixed;
  top: 0; left: 0; width: 100%;
  height: 80px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid transparent;
  z-index: 1000;
  transition: all 0.3s ease;
}
.navbar.scrolled {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid #f3f4f6;
}

.nav-content { display: flex; justify-content: space-between; align-items: center; height: 100%; }

.logo { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
.logo-icon { width: 40px; height: 40px; background-color: #4f46e5; color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.logo-text { font-size: 1.25rem; font-weight: 700; color: #111827; }
.logo-text .highlight { color: #4f46e5; }

.desktop-menu { display: none; gap: 2rem; }
@media (min-width: 768px) { .desktop-menu { display: flex; } }
.nav-link { font-size: 0.95rem; font-weight: 500; color: #4b5563; transition: color 0.2s; }
.nav-link:hover { color: #4f46e5; }

.nav-actions { display: none; align-items: center; gap: 1rem; }
@media (min-width: 768px) { .nav-actions { display: flex; } }
.btn-login { font-weight: 600; color: #4f46e5; }
.btn-cta-small { padding: 0.6rem 1.2rem; background-color: #4f46e5; color: white; border-radius: 8px; font-weight: 600; font-size: 0.9rem; transition: all 0.2s; }
.btn-cta-small:hover { background-color: #4338ca; transform: translateY(-1px); }

.mobile-toggle { display: block; background: none; border: none; font-size: 1.5rem; color: #6b7280; cursor: pointer; }
@media (min-width: 768px) { .mobile-toggle { display: none; } }

.mobile-menu { background: white; border-bottom: 1px solid #e5e7eb; padding: 1rem; display: flex; flex-direction: column; gap: 1rem; position: fixed; top: 80px; left: 0; width: 100%; z-index: 999; }
.mobile-actions { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem; }
.btn-login-mobile { text-align: center; padding: 0.8rem; border: 1px solid #4f46e5; color: #4f46e5; border-radius: 8px; font-weight: 600; }
.btn-cta-mobile { text-align: center; padding: 0.8rem; background: #4f46e5; color: white; border-radius: 8px; font-weight: 600; }

/* HERO */
.hero-section { padding-top: 160px; padding-bottom: 80px; text-align: center; position: relative; overflow: hidden; }
.hero-bg-decoration { position: absolute; top: -10%; left: 50%; transform: translateX(-50%); width: 100%; height: 100%; background: radial-gradient(circle at 50% 0%, rgba(79, 70, 229, 0.1) 0%, transparent 50%); z-index: 0; pointer-events: none; }
.hero-content { position: relative; z-index: 1; }

.badge-new { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0.75rem; background: #eef2ff; color: #4f46e5; border-radius: 99px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-bottom: 1.5rem; }
.badge-new .dot { width: 8px; height: 8px; background: #4f46e5; border-radius: 50%; }

.hero-title { font-size: 2.5rem; line-height: 1.2; font-weight: 800; color: #111827; margin-bottom: 1.5rem; }
@media (min-width: 640px) { .hero-title { font-size: 3.5rem; } }
.gradient-text { background: linear-gradient(to right, #4f46e5, #3b82f6); -webkit-background-clip: text; color: transparent; }
.hero-subtitle { font-size: 1.125rem; color: #6b7280; max-width: 600px; margin: 0 auto 2.5rem; }
.hero-note { font-size: 0.85rem; color: #6b7280; margin-top: 1rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.hero-note i { color: #16a34a; }

.hero-buttons { display: flex; flex-direction: column; gap: 1rem; align-items: center; justify-content: center; }
@media (min-width: 640px) { .hero-buttons { flex-direction: row; } }

.btn-hero-primary { padding: 1rem 2rem; background: #4f46e5; color: white; border-radius: 12px; font-weight: 700; font-size: 1.1rem; box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3); transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem; }
.btn-hero-primary:hover { background: #4338ca; transform: translateY(-2px); }

.btn-hero-secondary { padding: 1rem 2rem; background: white; color: #374151; border: 1px solid #e5e7eb; border-radius: 12px; font-weight: 600; font-size: 1.1rem; transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem; }
.btn-hero-secondary:hover { background: #f9fafb; border-color: #d1d5db; }
.btn-hero-secondary i { color: #4f46e5; font-size: 1.2rem; }

/* DASHBOARD PREVIEW */
.dashboard-preview { margin-top: 4rem; max-width: 1000px; margin-left: auto; margin-right: auto; }
.browser-frame { background: white; border-radius: 12px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0,0,0,0.05); overflow: hidden; display: flex; flex-direction: column; }
.browser-header { background: #f1f5f9; padding: 0.75rem 1rem; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 1rem; }
.dots { display: flex; gap: 6px; }
.dot-red { width: 10px; height: 10px; background: #ef4444; border-radius: 50%; }
.dot-yellow { width: 10px; height: 10px; background: #f59e0b; border-radius: 50%; }
.dot-green { width: 10px; height: 10px; background: #10b981; border-radius: 50%; }
.address-bar { flex: 1; background: white; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; color: #94a3b8; text-align: center; border: 1px solid #e2e8f0; }

.mockup-container { display: flex; height: 300px; background: #f8fafc; }
.mock-sidebar { width: 70px; background: #1e1b4b; display: flex; flex-direction: column; align-items: center; padding-top: 1.5rem; gap: 1.5rem; }
.mock-nav-item { color: #6366f1; font-size: 1.2rem; padding: 8px; border-radius: 8px; }
.mock-nav-item.active { background: #4f46e5; color: white; }
.mock-content { flex: 1; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }
.mock-topbar { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.mock-search { width: 200px; height: 32px; background: white; border-radius: 6px; border: 1px solid #e2e8f0; }
.mock-avatar { width: 32px; height: 32px; background: #cbd5e1; border-radius: 50%; }
.mock-stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.mock-card { background: white; padding: 1rem; border-radius: 10px; border: 1px solid #f1f5f9; display: flex; align-items: center; gap: 0.8rem; }
.mock-icon-bg { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1rem; }
.mock-icon-bg.indigo { background: #e0e7ff; color: #4f46e5; }
.mock-icon-bg.green { background: #dcfce7; color: #16a34a; }
.mock-icon-bg.blue { background: #dbeafe; color: #2563eb; }
.mock-stat-info { display: flex; flex-direction: column; }
.mock-stat-info .label { font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }
.mock-stat-info .value { font-size: 1.1rem; font-weight: 700; color: #1e293b; }

/* RECURSOS */
.features-section { padding: 5rem 0; background: white; }
.section-header { text-align: center; max-width: 700px; margin: 0 auto 4rem; }
.section-tag { color: #4f46e5; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }
.section-header h2 { font-size: 2.25rem; font-weight: 800; color: #111827; margin: 0.5rem 0 1rem; }
.section-header p { font-size: 1.1rem; color: #6b7280; }
.features-grid { display: grid; grid-template-columns: 1fr; gap: 2rem; }
@media (min-width: 768px) { .features-grid { grid-template-columns: repeat(3, 1fr); } }
.feature-card { background: #f9fafb; padding: 2rem; border-radius: 1rem; transition: all 0.3s; }
.feature-card:hover { background: white; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); transform: translateY(-5px); }
.icon-box { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; margin-bottom: 1.5rem; }
.icon-indigo { background: #e0e7ff; color: #4f46e5; }
.icon-green { background: #dcfce7; color: #16a34a; }
.icon-blue { background: #dbeafe; color: #2563eb; }
.feature-card h3 { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.75rem; color: #111827; }
.feature-card p { color: #6b7280; line-height: 1.6; }

/* FOOTER */
.footer { background: #111827; color: #d1d5db; padding: 4rem 0 2rem; }
.footer-grid { display: grid; gap: 2rem; }
.footer-logo { font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 1rem; }
.footer-bottom { border-top: 1px solid #1f2937; padding-top: 2rem; text-align: center; font-size: 0.85rem; color: #6b7280; margin-top: 2rem; }
</style>
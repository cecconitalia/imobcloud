<template>
  <div class="landing-page">
    
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
                   <div class="mock-nav-item"><i class="fas fa-file-contract"></i></div>
                   <div class="mock-nav-item"><i class="fas fa-wallet"></i></div>
                </div>

                <div class="mock-content">
                   <div class="mock-topbar">
                      <div class="mock-search"></div>
                      <div class="mock-user-profile">
                         <div class="mock-avatar"></div>
                      </div>
                   </div>

                   <div class="mock-stats-grid">
                      <div class="mock-card">
                         <div class="mock-icon-bg indigo"><i class="fas fa-home"></i></div>
                         <div class="mock-stat-info">
                            <span class="label">Imóveis Ativos</span>
                            <span class="value">142</span>
                         </div>
                      </div>
                      <div class="mock-card">
                         <div class="mock-icon-bg green"><i class="fas fa-check-circle"></i></div>
                         <div class="mock-stat-info">
                            <span class="label">Contratos</span>
                            <span class="value">28</span>
                         </div>
                      </div>
                      <div class="mock-card">
                         <div class="mock-icon-bg orange"><i class="fas fa-users"></i></div>
                         <div class="mock-stat-info">
                            <span class="label">Novos Leads</span>
                            <span class="value">+15</span>
                         </div>
                      </div>
                      <div class="mock-card">
                         <div class="mock-icon-bg blue"><i class="fas fa-dollar-sign"></i></div>
                         <div class="mock-stat-info">
                            <span class="label">Receita (Mês)</span>
                            <span class="value">R$ 12k</span>
                         </div>
                      </div>
                   </div>

                   <div class="mock-panels-grid">
                      <div class="mock-panel chart-panel">
                         <div class="mock-panel-header">Desempenho de Vendas</div>
                         <div class="mock-bars">
                            <div class="bar" style="height: 40%"></div>
                            <div class="bar" style="height: 70%"></div>
                            <div class="bar" style="height: 50%"></div>
                            <div class="bar active" style="height: 85%"></div>
                            <div class="bar" style="height: 60%"></div>
                         </div>
                      </div>
                      <div class="mock-panel list-panel">
                         <div class="mock-panel-header">Últimos Contatos</div>
                         <div class="mock-list-item">
                            <div class="mock-avatar-sm"></div>
                            <div class="mock-line"></div>
                         </div>
                         <div class="mock-list-item">
                            <div class="mock-avatar-sm"></div>
                            <div class="mock-line"></div>
                         </div>
                         <div class="mock-list-item">
                            <div class="mock-avatar-sm"></div>
                            <div class="mock-line"></div>
                         </div>
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
            <p>Cadastre fotos ilimitadas, gere descrições com IA e organize seu portfólio de forma profissional.</p>
          </div>

          <div class="feature-card">
            <div class="icon-box icon-green"><i class="fas fa-globe"></i></div>
            <h3>Site Próprio</h3>
            <p>Tenha um site moderno e responsivo para divulgar seus imóveis automaticamente.</p>
          </div>

          <div class="feature-card">
            <div class="icon-box icon-blue"><i class="fas fa-file-contract"></i></div>
            <h3>Contratos Digitais</h3>
            <p>Geração automática de contratos de venda e aluguel com gestão de assinaturas.</p>
          </div>

          <div class="feature-card">
            <div class="icon-box icon-orange"><i class="fas fa-filter"></i></div>
            <h3>Funil de Vendas (CRM)</h3>
            <p>Acompanhe seus leads desde o primeiro contato até o fechamento. Kanban interativo.</p>
          </div>

          <div class="feature-card">
            <div class="icon-box icon-purple"><i class="fas fa-robot"></i></div>
            <h3>Inteligência Artificial</h3>
            <p>Integração com IA para criar descrições persuasivas e atender clientes de forma inteligente.</p>
          </div>

          <div class="feature-card">
            <div class="icon-box icon-pink"><i class="fas fa-share-alt"></i></div>
            <h3>Redes Sociais</h3>
            <p>Agende publicações e gere cards para Instagram e Facebook diretamente pelo sistema.</p>
          </div>
        </div>
      </div>
    </section>

    <section id="planos" class="pricing-section">
        <div class="container">
            <div class="section-header">
                <span class="section-tag">Investimento</span>
                <h2>Escolha o plano ideal</h2>
                <div class="pricing-toggle">
                    <span>Mensal</span>
                    <div class="toggle-switch"><div class="toggle-knob"></div></div>
                    <span class="highlight-text">Anual (-20%)</span>
                </div>
            </div>

            <div class="pricing-grid">
                <div class="pricing-card">
                    <h3>Corretor Autônomo</h3>
                    <p class="price-desc">Para quem está começando.</p>
                    <div class="price">
                        <span class="amount">R$ 149,90</span>
                        <span class="period">/mês</span>
                    </div>
                    <router-link to="/cadastro" class="btn-plan">Teste 7 dias Grátis</router-link>
                    <ul class="features-list">
                        <li><i class="fas fa-check"></i> Até 50 Imóveis</li>
                        <li><i class="fas fa-check"></i> Site Próprio</li>
                        <li><i class="fas fa-check"></i> Gestão de Contatos</li>
                        <li><i class="fas fa-check"></i> Contratos Básicos</li>
                    </ul>
                </div>

                <div class="pricing-card featured">
                    <div class="featured-badge">Mais Popular</div>
                    <h3>Imobiliária Pro</h3>
                    <p class="price-desc">Para equipas em crescimento.</p>
                    <div class="price">
                        <span class="amount">R$ 249,90</span>
                        <span class="period">/mês</span>
                    </div>
                    <router-link to="/cadastro" class="btn-plan-featured">Teste 7 dias Grátis</router-link>
                    <ul class="features-list">
                        <li><i class="fas fa-check"></i> Imóveis Ilimitados</li>
                        <li><i class="fas fa-check"></i> Até 5 Usuários</li>
                        <li><i class="fas fa-check"></i> CRM Completo</li>
                        <li><i class="fas fa-check"></i> IA Integrada</li>
                        <li><i class="fas fa-check"></i> Gestão de Vistorias</li>
                    </ul>
                </div>

                <div class="pricing-card">
                    <h3>Enterprise</h3>
                    <p class="price-desc">Para grandes operações.</p>
                    <div class="price">
                        <span class="amount">Consulta</span>
                    </div>
                    <a href="#contato" class="btn-plan">Falar com Consultor</a>
                    <ul class="features-list">
                        <li><i class="fas fa-check"></i> Usuários Ilimitados</li>
                        <li><i class="fas fa-check"></i> API Dedicada</li>
                        <li><i class="fas fa-check"></i> Suporte 24/7</li>
                        <li><i class="fas fa-check"></i> Personalização</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <section id="contato" class="cta-section">
        <div class="container text-center">
            <h2>Pronto para transformar sua imobiliária?</h2>
            <p>Junte-se a centenas de corretores que já automatizaram seus processos.</p>
            <div class="cta-buttons">
                <router-link to="/cadastro" class="btn-cta-dark">Começar Agora</router-link>
            </div>
        </div>
    </section>

    <footer class="footer">
      <div class="container footer-grid">
        <div class="footer-brand">
            <div class="footer-logo">
                <i class="fas fa-laptop-house"></i> ImobHome
            </div>
            <p>O sistema de gestão mais completo para o mercado imobiliário brasileiro.</p>
        </div>
        
        <div class="footer-col">
            <h4>Produto</h4>
            <a href="#">Recursos</a>
            <a href="#">Planos</a>
        </div>

        <div class="footer-col">
            <h4>Legal</h4>
            <a href="#">Termos de Uso</a>
            <a href="#">Privacidade</a>
        </div>
      </div>
      <div class="footer-bottom">
        &copy; {{ new Date().getFullYear() }} ImobHome Tecnologia. Todos os direitos reservados.
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const mobileMenuOpen = ref(false);
const isScrolled = ref(false);

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
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* --- VARIÁVEIS & RESET --- */
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

/* --- NAVBAR --- */
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

.nav-content {
  display: flex; justify-content: space-between; align-items: center;
  height: 100%;
}

.logo {
  display: flex; align-items: center; gap: 0.75rem; cursor: pointer;
}
.logo-icon {
  width: 40px; height: 40px; background-color: #4f46e5; color: white;
  border-radius: 12px; display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}
.logo-text { font-size: 1.25rem; font-weight: 700; color: #111827; }
.logo-text .highlight { color: #4f46e5; }

.desktop-menu { display: none; gap: 2rem; }
.nav-link { font-size: 0.95rem; font-weight: 500; color: #4b5563; transition: color 0.2s; }
.nav-link:hover { color: #4f46e5; }

.nav-actions { display: none; align-items: center; gap: 1rem; }
.btn-login { font-weight: 600; color: #4f46e5; }
.btn-cta-small {
  padding: 0.6rem 1.2rem; background-color: #4f46e5; color: white;
  border-radius: 8px; font-weight: 600; font-size: 0.9rem;
  transition: background 0.2s, transform 0.2s;
}
.btn-cta-small:hover { background-color: #4338ca; transform: translateY(-1px); }

.mobile-toggle {
  display: block; background: none; border: none; font-size: 1.5rem; color: #6b7280; cursor: pointer;
}

/* Responsivo Nav */
@media (min-width: 768px) {
  .desktop-menu, .nav-actions { display: flex; }
  .mobile-toggle { display: none; }
}

.mobile-menu {
  background: white; border-bottom: 1px solid #e5e7eb; padding: 1rem;
  display: flex; flex-direction: column; gap: 1rem;
}
.mobile-menu a { padding: 0.5rem; font-weight: 500; color: #374151; }
.mobile-actions { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem; }
.btn-login-mobile { text-align: center; padding: 0.8rem; border: 1px solid #4f46e5; color: #4f46e5; border-radius: 8px; font-weight: 600; }
.btn-cta-mobile { text-align: center; padding: 0.8rem; background: #4f46e5; color: white; border-radius: 8px; font-weight: 600; }

/* --- HERO --- */
.hero-section {
  padding-top: 160px; padding-bottom: 80px; text-align: center;
  position: relative; overflow: hidden;
}
.hero-bg-decoration {
  position: absolute; top: -10%; left: 50%; transform: translateX(-50%);
  width: 100%; height: 100%;
  background: radial-gradient(circle at 50% 0%, rgba(79, 70, 229, 0.1) 0%, transparent 50%);
  z-index: 0; pointer-events: none;
}
.hero-content { position: relative; z-index: 1; }

.badge-new {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.25rem 0.75rem; background: #eef2ff; color: #4f46e5;
  border-radius: 99px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; margin-bottom: 1.5rem;
}
.badge-new .dot { width: 8px; height: 8px; background: #4f46e5; border-radius: 50%; }

.hero-title {
  font-size: 2.5rem; line-height: 1.2; font-weight: 800; color: #111827; margin-bottom: 1.5rem;
}
.gradient-text {
  background: linear-gradient(to right, #4f46e5, #3b82f6);
  -webkit-background-clip: text; color: transparent;
}
.hero-subtitle {
  font-size: 1.125rem; color: #6b7280; max-width: 600px; margin: 0 auto 2.5rem;
}
.hero-note {
    font-size: 0.85rem; color: #6b7280; margin-top: 1rem;
    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
}
.hero-note i { color: #16a34a; }

.hero-buttons {
  display: flex; flex-direction: column; gap: 1rem; align-items: center; justify-content: center;
}
@media (min-width: 640px) {
  .hero-title { font-size: 3.5rem; }
  .hero-buttons { flex-direction: row; }
}

.btn-hero-primary {
  padding: 1rem 2rem; background: #4f46e5; color: white; border-radius: 12px;
  font-weight: 700; font-size: 1.1rem; box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
  transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem;
}
.btn-hero-primary:hover { background: #4338ca; transform: translateY(-2px); }

.btn-hero-secondary {
  padding: 1rem 2rem; background: white; color: #374151; border: 1px solid #e5e7eb;
  border-radius: 12px; font-weight: 600; font-size: 1.1rem;
  transition: all 0.2s; display: inline-flex; align-items: center; gap: 0.5rem;
}
.btn-hero-secondary:hover { background: #f9fafb; border-color: #d1d5db; }
.btn-hero-secondary i { color: #4f46e5; font-size: 1.2rem; }

/* --- DASHBOARD PREVIEW MOCKUP --- */
.dashboard-preview {
  margin-top: 4rem;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
  perspective: 1000px; /* Prepara para animação 3D se quiser */
}

.browser-frame {
  background: white;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0,0,0,0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Barra do Navegador (Browser Header) */
.browser-header {
  background: #f1f5f9;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.dots { display: flex; gap: 6px; }
.dot-red { width: 10px; height: 10px; background: #ef4444; border-radius: 50%; }
.dot-yellow { width: 10px; height: 10px; background: #f59e0b; border-radius: 50%; }
.dot-green { width: 10px; height: 10px; background: #10b981; border-radius: 50%; }

.address-bar {
  flex: 1;
  background: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #94a3b8;
  text-align: center;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.address-bar::before { content: "\f023"; font-family: "Font Awesome 5 Free"; margin-right: 6px; font-weight: 900; font-size: 0.7rem;}

/* Layout Interno do Mockup */
.mockup-container {
  display: flex;
  height: 500px; /* Altura fixa para o preview */
  background: #f8fafc;
}

/* Sidebar */
.mock-sidebar {
  width: 70px;
  background: #1e1b4b; /* Azul escuro da marca */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 1.5rem;
  gap: 1.5rem;
  flex-shrink: 0;
}
.mock-nav-item {
  color: #6366f1;
  font-size: 1.2rem;
  cursor: default;
  padding: 8px;
  border-radius: 8px;
}
.mock-nav-item.active {
  background: #4f46e5;
  color: white;
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}

/* Conteúdo Principal */
.mock-content {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow: hidden;
}

/* Topbar Interna */
.mock-topbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}
.mock-search {
  width: 200px; height: 32px; background: white; border-radius: 6px; border: 1px solid #e2e8f0;
}
.mock-avatar { width: 32px; height: 32px; background: #cbd5e1; border-radius: 50%; }

/* Grid de Stats */
.mock-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}
@media (max-width: 640px) { .mock-stats-grid { grid-template-columns: repeat(2, 1fr); } }

.mock-card {
  background: white;
  padding: 1rem;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.mock-icon-bg {
  width: 40px; height: 40px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; font-size: 1rem;
}
.mock-icon-bg.indigo { background: #e0e7ff; color: #4f46e5; }
.mock-icon-bg.green { background: #dcfce7; color: #16a34a; }
.mock-icon-bg.orange { background: #ffedd5; color: #ea580c; }
.mock-icon-bg.blue { background: #dbeafe; color: #2563eb; }

.mock-stat-info { display: flex; flex-direction: column; }
.mock-stat-info .label { font-size: 0.65rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; }
.mock-stat-info .value { font-size: 1.1rem; font-weight: 700; color: #1e293b; }

/* Paineis Inferiores (Gráfico e Lista) */
.mock-panels-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
  flex: 1;
}
@media (max-width: 640px) { .mock-panels-grid { grid-template-columns: 1fr; } }

.mock-panel {
  background: white;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}
.mock-panel-header {
  font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 1rem;
}

/* Gráfico Simulado (Barras CSS) */
.mock-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  flex: 1;
  padding-bottom: 0.5rem;
}
.bar {
  width: 12%;
  background: #e2e8f0;
  border-radius: 4px;
}
.bar.active { background: #4f46e5; }

/* Lista Simulada */
.mock-list-item {
  display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;
}
.mock-avatar-sm { width: 24px; height: 24px; background: #e2e8f0; border-radius: 50%; }
.mock-line { height: 8px; width: 70%; background: #f1f5f9; border-radius: 4px; }

/* Animação de Entrada */
.fade-in-up { animation: fadeInUp 0.8s ease-out forwards; opacity: 0; transform: translateY(20px); }
@keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }

/* --- RECURSOS --- */
.features-section { padding: 5rem 0; background: white; }
.section-header { text-align: center; max-width: 700px; margin: 0 auto 4rem; }
.section-tag {
  color: #4f46e5; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;
}
.section-header h2 { font-size: 2.25rem; font-weight: 800; color: #111827; margin: 0.5rem 0 1rem; }
.section-header p { font-size: 1.1rem; color: #6b7280; }

.features-grid {
  display: grid; grid-template-columns: 1fr; gap: 2rem;
}
@media (min-width: 768px) { .features-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .features-grid { grid-template-columns: repeat(3, 1fr); } }

.feature-card {
  background: #f9fafb; padding: 2rem; border-radius: 1rem; border: 1px solid transparent;
  transition: all 0.3s;
}
.feature-card:hover {
  background: white; border-color: #e5e7eb; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); transform: translateY(-5px);
}

.icon-box {
  width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
  font-size: 1.25rem; margin-bottom: 1.5rem;
}
.icon-indigo { background: #e0e7ff; color: #4f46e5; }
.icon-green { background: #dcfce7; color: #16a34a; }
.icon-blue { background: #dbeafe; color: #2563eb; }
.icon-orange { background: #ffedd5; color: #ea580c; }
.icon-purple { background: #f3e8ff; color: #9333ea; }
.icon-pink { background: #fce7f3; color: #db2777; }

.feature-card h3 { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.75rem; color: #111827; }
.feature-card p { color: #6b7280; line-height: 1.6; }

/* --- PLANOS --- */
.pricing-section { padding: 5rem 0; background: #f9fafb; }
.pricing-toggle { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1.5rem; }
.toggle-switch {
  width: 44px; height: 24px; background: #4f46e5; border-radius: 99px; position: relative;
}
.toggle-knob {
  width: 18px; height: 18px; background: white; border-radius: 50%;
  position: absolute; top: 3px; right: 3px;
}
.highlight-text { font-weight: 700; color: #111827; }

.pricing-grid {
  display: grid; grid-template-columns: 1fr; gap: 2rem; margin-top: 3rem;
}
@media (min-width: 900px) { .pricing-grid { grid-template-columns: repeat(3, 1fr); } }

.pricing-card {
  background: white; padding: 2rem; border-radius: 1rem; border: 1px solid #e5e7eb;
  display: flex; flex-direction: column; transition: all 0.3s;
}
.pricing-card:hover { border-color: #a5b4fc; }
.pricing-card.featured {
  border: 2px solid #4f46e5; position: relative; box-shadow: 0 10px 20px rgba(79, 70, 229, 0.1);
  transform: translateY(-10px);
}
.featured-badge {
  position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
  background: #4f46e5; color: white; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
}

.pricing-card h3 { font-size: 1.25rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; }
.price-desc { font-size: 0.9rem; color: #6b7280; margin-bottom: 1.5rem; }
.price .amount { font-size: 2.5rem; font-weight: 800; color: #111827; }
.price .period { color: #6b7280; }

.btn-plan {
  display: block; width: 100%; padding: 0.8rem; text-align: center;
  background: #eef2ff; color: #4f46e5; border-radius: 8px; font-weight: 600;
  margin-top: 1.5rem; transition: background 0.2s;
}
.btn-plan:hover { background: #e0e7ff; }

.btn-plan-featured {
  display: block; width: 100%; padding: 0.8rem; text-align: center;
  background: #4f46e5; color: white; border-radius: 8px; font-weight: 600;
  margin-top: 1.5rem; transition: background 0.2s;
}
.btn-plan-featured:hover { background: #4338ca; }

.features-list { list-style: none; padding: 0; margin-top: 2rem; flex: 1; }
.features-list li { margin-bottom: 0.8rem; font-size: 0.9rem; color: #4b5563; display: flex; align-items: center; gap: 0.75rem; }
.features-list i { color: #16a34a; font-size: 0.9rem; }

/* --- CTA --- */
.cta-section { padding: 5rem 0; background: white; border-top: 1px solid #f3f4f6; }
.cta-buttons { margin-top: 2rem; }
.btn-cta-dark {
  padding: 1rem 2.5rem; background: #111827; color: white; border-radius: 8px;
  font-weight: 700; display: inline-block; transition: background 0.2s;
}
.btn-cta-dark:hover { background: #1f2937; }

/* --- FOOTER --- */
.footer { background: #111827; color: #d1d5db; padding: 4rem 0 2rem; }
.footer-grid {
  display: grid; grid-template-columns: 1fr; gap: 3rem; margin-bottom: 3rem;
}
@media (min-width: 768px) { .footer-grid { grid-template-columns: 2fr 1fr 1fr; } }

.footer-logo { font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 1rem; }
.footer-brand p { font-size: 0.9rem; color: #9ca3af; max-width: 300px; }

.footer-col h4 { color: white; font-weight: 700; margin-bottom: 1rem; }
.footer-col a { display: block; color: #9ca3af; margin-bottom: 0.5rem; font-size: 0.9rem; }
.footer-col a:hover { color: white; }

.footer-bottom { border-top: 1px solid #1f2937; padding-top: 2rem; text-align: center; font-size: 0.85rem; color: #6b7280; }
</style>
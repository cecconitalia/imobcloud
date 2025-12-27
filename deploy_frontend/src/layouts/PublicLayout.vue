<template>
  <div class="public-layout">
    <header :class="['public-header', { 'scrolled': isScrolled }]">
      <div class="container header-container">
        
        <a href="/site" class="header-brand">
          <i class="fas fa-home brand-icon"></i>
          <h1 class="brand-name">{{ imobiliariaNome || 'Portal Imobiliário' }}</h1>
        </a>

        <div class="header-actions">
          
          <nav class="desktop-nav">
            <router-link to="/site" class="nav-link" active-class="active">Início</router-link>
            <a href="#" class="nav-link">Imóveis</a>
            <a href="#" class="nav-link">Sobre</a>
            <a href="#" class="nav-link">Contato</a>
          </nav>
          
          <div class="separator desktop-only"></div>

          <a href="/login" class="btn-login desktop-only">
            <i class="fas fa-user-circle"></i>
            <span>Área do Cliente</span>
          </a>

          <div 
            v-if="isMobileMenuOpen" 
            class="menu-backdrop"
            @click="closeMenu"
          ></div>

          <div 
            class="mobile-interaction-wrapper"
            @mouseleave="handleMouseLeave"
          >
            <button 
              class="mobile-toggle" 
              @click.stop="toggleMenu" 
              :class="{ 'active': isMobileMenuOpen }"
            >
              <i :class="isMobileMenuOpen ? 'fas fa-times' : 'fas fa-bars'"></i>
            </button>

            <transition name="dropdown-slide">
              <div v-if="isMobileMenuOpen" class="mobile-dropdown-menu" @click.stop>
                <router-link to="/site" class="mobile-item" @click="closeMenu">
                  Início
                </router-link>
                <a href="#" class="mobile-item" @click="closeMenu">Imóveis</a>
                <a href="#" class="mobile-item" @click="closeMenu">Sobre</a>
                <a href="#" class="mobile-item" @click="closeMenu">Contato</a>
                
                <div class="divider"></div>
                
                <a href="/login" class="mobile-item highlight" @click="closeMenu">
                  <i class="fas fa-user-circle"></i> Área do Cliente
                </a>
              </div>
            </transition>
          </div>
          </div>
      </div>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer class="public-footer">
      <div class="container footer-container">
        <div class="footer-info">
          <h3 class="footer-brand">{{ imobiliariaNome }}</h3>
          <p class="footer-desc">Encontre o imóvel dos seus sonhos com confiança.</p>
        </div>
        <div class="footer-copy">
          <p>&copy; {{ new Date().getFullYear() }} {{ imobiliariaNome }}. Todos os direitos reservados.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import publicApiClient from '@/services/publicApiClient';
import '@fortawesome/fontawesome-free/css/all.css';

const route = useRoute();
const imobiliariaNome = ref('');
const isScrolled = ref(false);
const isMobileMenuOpen = ref(false);

// --- Lógica do Menu ---

function toggleMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

function closeMenu() {
  isMobileMenuOpen.value = false;
}

// Fecha ao tirar o mouse do container (Botão + Menu)
function handleMouseLeave() {
  if (isMobileMenuOpen.value) {
    closeMenu();
  }
}

// Fecha automaticamente ao mudar de rota
watch(() => route.fullPath, () => {
  closeMenu();
});

// --- Scroll & Cores ---
function handleScroll() {
  isScrolled.value = window.scrollY > 10;
}

async function fetchImobiliariaData(subdomain: string) {
  try {
    const response = await publicApiClient.get(`/public/imobiliaria/${subdomain}/`);
    imobiliariaNome.value = response.data.nome;
    const primaryColor = response.data.cor_primaria || '#007bff';
    document.documentElement.style.setProperty('--primary-color', primaryColor);
  } catch (err) {
    imobiliariaNome.value = subdomain === 'localhost' ? 'Imobiliária Demo' : subdomain;
    document.documentElement.style.setProperty('--primary-color', '#111827');
  }
}

onMounted(() => {
  const hostname = window.location.hostname;
  const parts = hostname.split('.');
  let subdomain = parts.length > 1 && parts[0] !== 'www' ? parts[0] : 'estilomusical';
  if (parts.length === 1 || parts[0] === 'localhost') subdomain = 'estilomusical';

  fetchImobiliariaData(subdomain);
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* --- Configurações Globais --- */
.public-layout {
  --nav-height: 80px;
  --text-main: #374151;
  --bg-body: #f9fafb;
  --footer-bg: #1f2937;
  
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, sans-serif;
  background-color: var(--bg-body);
  color: var(--text-main);
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* --- HEADER --- */
.public-header {
  height: var(--nav-height);
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: transparent;
  transition: all 0.3s ease;
}

.public-header.scrolled {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
  height: 70px;
}

.header-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: var(--text-main);
}
.brand-icon { font-size: 1.5rem; color: var(--primary-color); }
.brand-name { font-size: 1.25rem; font-weight: 700; margin: 0; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

/* --- Navegação Desktop --- */
.desktop-nav { display: flex; gap: 2rem; }
.nav-link {
  text-decoration: none;
  color: var(--text-main);
  font-weight: 500;
  transition: color 0.2s;
}
.nav-link:hover, .nav-link.active { color: var(--primary-color); }

.separator { height: 24px; width: 1px; background-color: #e5e7eb; }

.btn-login {
  display: flex; align-items: center; gap: 0.5rem;
  text-decoration: none; color: var(--primary-color);
  font-weight: 600; padding: 0.5rem 1rem;
  border-radius: 8px; transition: background 0.2s;
}
.btn-login:hover { background-color: #f3f4f6; }

/* --- SISTEMA DE MENU MOBILE --- */

/* 1. Wrapper que agrupa Botão e Menu (Zona segura do mouse) */
.mobile-interaction-wrapper {
  position: relative;
  display: none; /* Escondido no Desktop */
}

/* 2. Botão Hambúrguer */
.mobile-toggle {
  background: none; border: none;
  font-size: 1.5rem; color: var(--text-main);
  cursor: pointer; padding: 0.5rem;
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
  z-index: 102; /* Acima do menu e backdrop */
  position: relative;
}
.mobile-toggle:hover, .mobile-toggle.active { background-color: #f3f4f6; }

/* 3. Backdrop Invisível (Para clicar fora) */
.menu-backdrop {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  z-index: 100;
  background: transparent; /* Invisível, mas captura cliques */
  cursor: default;
}

/* 4. Menu Dropdown */
.mobile-dropdown-menu {
  position: absolute;
  top: 100%; /* Logo abaixo do botão */
  right: 0;
  width: 220px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
  border: 1px solid #f3f4f6;
  padding: 0.5rem 0;
  margin-top: 0; /* Sem margem para não quebrar o hover */
  z-index: 101; /* Acima do backdrop */
  display: flex;
  flex-direction: column;
}

.mobile-item {
  padding: 0.75rem 1.25rem;
  text-decoration: none;
  color: var(--text-main);
  font-weight: 500;
  transition: background 0.2s;
  display: block;
}
.mobile-item:hover { background-color: #f9fafb; color: var(--primary-color); }

.mobile-item.highlight {
  color: var(--primary-color);
  font-weight: 600;
  background-color: #f0f9ff;
  margin-top: 0.25rem;
  border-radius: 0 0 12px 12px;
}

.divider { height: 1px; background: #e5e7eb; margin: 0.5rem 0; }

/* Transição Suave */
.dropdown-slide-enter-active, .dropdown-slide-leave-active {
  transition: all 0.2s ease;
}
.dropdown-slide-enter-from, .dropdown-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* --- Responsividade --- */
@media (max-width: 768px) {
  .desktop-nav, .desktop-only { display: none; }
  .mobile-interaction-wrapper { display: block; }
}

/* Conteúdo e Footer */
.main-content { flex: 1; }
.public-footer { background-color: var(--footer-bg); color: #f3f4f6; padding: 2rem 0; margin-top: auto; text-align: center; }
.footer-desc { color: #9ca3af; font-size: 0.9rem; }
.footer-copy { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.8rem; color: #6b7280; }
</style>
<template>
  <div class="dashboard-layout" :class="{ 'sidebar-collapsed': isCollapsed, 'mobile-open': isMobileOpen }">
    
    <aside 
      class="sidebar" 
      :class="{ 'sidebar-hover-expanded': isHovered && isCollapsed }"
      @mouseenter="handleSidebarHover(true)" 
      @mouseleave="handleSidebarHover(false)"
    >
      <div class="sidebar-header">
        <div class="brand-wrapper">
          <div class="brand-icon brand-gradient">
            <i class="fas fa-cube"></i>
          </div>
          <span class="brand-text">ImobCloud</span>
        </div>
        
        <button class="mobile-close-btn" @click="closeMobileSidebar">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="sidebar-content">
        <ul class="nav-list">
          
          <li class="nav-item">
            <router-link to="/dashboard" class="nav-link" active-class="active">
              <i class="fas fa-th-large nav-icon"></i>
              <span class="nav-label">Visão Geral</span>
            </router-link>
          </li>

          <li class="nav-section">NEGÓCIOS</li>
          <li class="divider" v-show="isCollapsed && !isHovered"></li>

          <li class="nav-item-group" :class="{ 'expanded': isMenuOpen('comercial') }">
            <div class="nav-link has-submenu" @click="toggleSubmenu('comercial')">
              <i class="fas fa-handshake nav-icon"></i>
              <span class="nav-label">Comercial</span>
              <i class="fas fa-chevron-down arrow-icon"></i>
            </div>
            <ul class="submenu-list" :style="{ maxHeight: isMenuOpen('comercial') ? '200px' : '0' }">
              <li><router-link to="/clientes" active-class="active">Clientes</router-link></li>
              <li><router-link to="/funil-vendas" active-class="active">Funil de Vendas</router-link></li>
              <li><router-link to="/visitas" active-class="active">Visitas</router-link></li>
              <li><router-link to="/contatos" active-class="active">Leads</router-link></li>
            </ul>
          </li>

          <li class="nav-item-group" :class="{ 'expanded': isMenuOpen('imoveis') }">
            <div class="nav-link has-submenu" @click="toggleSubmenu('imoveis')">
              <i class="fas fa-building nav-icon"></i>
              <span class="nav-label">Imóveis</span>
              <i class="fas fa-chevron-down arrow-icon"></i>
            </div>
            <ul class="submenu-list" :style="{ maxHeight: isMenuOpen('imoveis') ? '150px' : '0' }">
              <li><router-link to="/imoveis" active-class="active">Listar Imóveis</router-link></li>
              <li><router-link to="/relatorios/autorizacoes" active-class="active">Autorizações</router-link></li>
            </ul>
          </li>

          <li class="nav-item-group" :class="{ 'expanded': isMenuOpen('contratos') }">
            <div class="nav-link has-submenu" @click="toggleSubmenu('contratos')">
              <i class="fas fa-file-signature nav-icon"></i>
              <span class="nav-label">Contratos</span>
              <i class="fas fa-chevron-down arrow-icon"></i>
            </div>
            <ul class="submenu-list" :style="{ maxHeight: isMenuOpen('contratos') ? '150px' : '0' }">
              <li><router-link to="/contratos" active-class="active">Gerenciar</router-link></li>
              <li><router-link to="/vistorias" active-class="active">Vistorias</router-link></li>
            </ul>
          </li>

          <li class="nav-section">GESTÃO</li>
          <li class="divider" v-show="isCollapsed && !isHovered"></li>

          <li class="nav-item-group" :class="{ 'expanded': isMenuOpen('financeiro') }">
            <div class="nav-link has-submenu" @click="toggleSubmenu('financeiro')">
              <i class="fas fa-wallet nav-icon"></i>
              <span class="nav-label">Financeiro</span>
              <i class="fas fa-chevron-down arrow-icon"></i>
            </div>
            <ul class="submenu-list" :style="{ maxHeight: isMenuOpen('financeiro') ? '300px' : '0' }">
              <li><router-link to="/financeiro/contas-a-receber" active-class="active">A Receber</router-link></li>
              <li><router-link to="/financeiro/contas-a-pagar" active-class="active">A Pagar</router-link></li>
              <li><router-link to="/financeiro/transacoes" active-class="active">Transações</router-link></li>
              <li><router-link to="/financeiro/remessa-retorno" active-class="active">Remessa/Retorno</router-link></li>
              <li><router-link to="/financeiro/dre" active-class="active">Relatório DRE</router-link></li>
            </ul>
          </li>

          <li class="nav-item">
            <router-link to="/calendario" class="nav-link" active-class="active">
              <i class="fas fa-calendar-check nav-icon"></i>
              <span class="nav-label">Agenda</span>
            </router-link>
          </li>

          <li class="nav-section">SISTEMA</li>
          <li class="divider" v-show="isCollapsed && !isHovered"></li>

          <li class="nav-item-group" :class="{ 'expanded': isMenuOpen('config') }">
            <div class="nav-link has-submenu" @click="toggleSubmenu('config')">
              <i class="fas fa-cogs nav-icon"></i>
              <span class="nav-label">Configurações</span>
              <i class="fas fa-chevron-down arrow-icon"></i>
            </div>
            <ul class="submenu-list" :style="{ maxHeight: isMenuOpen('config') ? '250px' : '0' }">
              <li><router-link to="/corretores" active-class="active">Equipe</router-link></li>
              <li><router-link to="/integracoes" active-class="active">Integrações</router-link></li>
              <li><router-link to="/financeiro/contas" active-class="active">Contas Bancárias</router-link></li>
              <li><router-link to="/financeiro/categorias" active-class="active">Categorias</router-link></li>
            </ul>
          </li>

        </ul>
      </div>

      <div class="sidebar-footer">
        <button class="collapse-toggle" @click="toggleCollapseManual" :title="isCollapsed ? 'Fixar Menu Aberto' : 'Recolher Menu'">
          <i class="fas" :class="isCollapsed ? 'fa-lock' : 'fa-lock-open'"></i>
          <span class="btn-label">{{ isCollapsed ? 'Fixar Menu' : 'Recolher' }}</span>
        </button>
        <button class="logout-btn" @click="logout">
          <i class="fas fa-sign-out-alt"></i>
          <span class="btn-label">Sair</span>
        </button>
      </div>
    </aside>

    <div class="sidebar-overlay" @click="closeMobileSidebar"></div>

    <div class="main-wrapper">
      <header class="top-header">
        <div class="header-left">
          <button class="menu-toggle-btn" @click="openMobileSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <h1 class="page-title">{{ route.meta.title || 'ImobCloud' }}</h1>
        </div>
        <div class="header-right">
          <NotificationBell />
          <div class="user-profile">
            <div class="avatar-circle">
              <i class="fas fa-user"></i>
            </div>
          </div>
        </div>
      </header>

      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import NotificationBell from '@/components/NotificationBell.vue';

const router = useRouter();
const route = useRoute();

// --- Estados ---
const isCollapsed = ref(false); 
const isHovered = ref(false);   
const isMobileOpen = ref(false); 
const activeSubmenu = ref<string | null>(null);
const userManualOverride = ref(false);

const BREAKPOINT_MOBILE = 1024;

// --- Lógica de Hover ---
function handleSidebarHover(value: boolean) {
  if (window.innerWidth > BREAKPOINT_MOBILE) {
    isHovered.value = value;
    if (!value && isCollapsed.value) {
      setTimeout(() => {
        if (!isHovered.value) {
           // Opcional: activeSubmenu.value = null; 
        }
      }, 300);
    }
  }
}

// --- Responsividade Automática ---
function handleResize() {
  const width = window.innerWidth;
  if (width <= BREAKPOINT_MOBILE) {
    isCollapsed.value = false; 
  } else {
    if (!userManualOverride.value) {
      isCollapsed.value = true; 
    }
  }
}

// --- Ações ---
function toggleCollapseManual() {
  isCollapsed.value = !isCollapsed.value;
  userManualOverride.value = true; 
  isHovered.value = false;
}

function openMobileSidebar() { isMobileOpen.value = true; }
function closeMobileSidebar() { isMobileOpen.value = false; }

function toggleSubmenu(menuName: string) {
  if (activeSubmenu.value === menuName) {
    activeSubmenu.value = null;
  } else {
    activeSubmenu.value = menuName;
  }
}

function isMenuOpen(menuName: string) {
  if (isCollapsed.value && !isHovered.value) return false;
  return activeSubmenu.value === menuName;
}

function logout() {
  localStorage.removeItem('authToken');
  router.push('/login');
}

// --- Watchers ---
watch(() => route.fullPath, () => {
  if (window.innerWidth <= BREAKPOINT_MOBILE) {
    closeMobileSidebar();
  } else {
    isHovered.value = false;
  }
});

// --- Lifecycle ---
onMounted(() => {
  handleResize();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* --- Configurações Visuais (Palette & Gradients) --- */
.dashboard-layout {
  --sidebar-width: 260px;
  --sidebar-width-collapsed: 80px; 
  --header-height: 70px;
  
  /* Cores Principais */
  --primary-color: #007bff;
  /* NOVO: Gradiente Principal (Azul moderno para Roxo sutil) */
  --primary-gradient: linear-gradient(135deg, #007bff 0%, #4f46e5 100%);
  
  /* Cores de Fundo e Texto */
  --bg-sidebar: #ffffff;
  --bg-body: #f4f7f6;
  --border-color: #e5e7eb;
  --text-main: #374151;
  --text-muted: #9ca3af;

  /* NOVO: Gradiente Sutil para estado Ativo (quase transparente) */
  --active-gradient-bg: linear-gradient(90deg, rgba(0,123,255,0.08) 0%, rgba(79,70,229,0.02) 100%);
  
  --transition-speed: 0.25s;
  
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background-color: var(--bg-body);
  font-family: 'Inter', sans-serif;
}

/* --- SIDEBAR PRINCIPAL --- */
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  z-index: 50;
  transition: width var(--transition-speed) ease-in-out, box-shadow var(--transition-speed) ease-in-out;
  box-shadow: 2px 0 8px rgba(0,0,0,0.02);
  overflow: hidden;
}

/* ESTADO COLAPSADO (Mini) */
.dashboard-layout.sidebar-collapsed .sidebar {
  width: var(--sidebar-width-collapsed);
}

/* ESTADO EXPANDIDO POR HOVER */
.dashboard-layout.sidebar-collapsed .sidebar.sidebar-hover-expanded {
  width: var(--sidebar-width);
  box-shadow: 6px 0 20px rgba(0,0,0,0.08); /* Sombra mais elegante ao flutuar */
}

/* Esconder textos no modo colapsado (sem hover) */
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .brand-text,
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .nav-label,
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .nav-section,
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .arrow-icon,
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .btn-label {
  display: none;
}

/* Centralizar ícones no modo colapsado */
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .nav-link,
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .collapse-toggle,
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .logout-btn {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
}

.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .nav-icon {
  margin-right: 0;
  font-size: 1.3rem; /* Ícones ligeiramente maiores no modo mini */
}

/* --- HEADER DA SIDEBAR & LOGO INOVADOR --- */
.sidebar-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  white-space: nowrap;
  transition: padding var(--transition-speed);
}
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .sidebar-header {
  padding: 0;
  justify-content: center;
}

.brand-wrapper {
  display: flex; align-items: center; gap: 0.75rem;
}

/* ESTILO DO NOVO ÍCONE COM DEGRADÊ */
.brand-icon.brand-gradient {
  width: 38px; height: 38px;
  /* Aplica o gradiente definido nas variáveis */
  background: var(--primary-gradient);
  color: white; /* Texto branco para contraste */
  border-radius: 10px; /* Bordas ligeiramente mais arredondadas */
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2); /* Sombra suave colorida */
}

.brand-text {
  font-size: 1.25rem; font-weight: 800; color: #111827;
  letter-spacing: -0.02em;
}

/* --- CONTEÚDO --- */
.sidebar-content {
  flex: 1;
  overflow-y: auto; overflow-x: hidden;
  padding: 1.5rem 0.75rem;
  scrollbar-width: thin;
}

/* Navegação */
.nav-list { list-style: none; padding: 0; margin: 0; }
.nav-item, .nav-item-group { margin-bottom: 0.4rem; /* Mais espaçamento vertical */ }

.nav-link {
  display: flex; align-items: center;
  padding: 0.75rem 1rem;
  color: var(--text-main); text-decoration: none;
  border-radius: 10px; /* Bordas mais modernas */
  transition: all 0.2s ease;
  cursor: pointer; white-space: nowrap; font-weight: 500;
  min-height: 46px;
  position: relative; /* Necessário para a barra lateral do ativo */
}

.nav-link:hover { background-color: #f9fafb; color: #111827; }

/* ESTILO DO ITEM ATIVO COM DEGRADÊ SUTIL */
.nav-link.active {
  background: var(--active-gradient-bg); /* Fundo gradiente sutil */
  color: var(--primary-color);
  font-weight: 600;
}

/* Pequena barra lateral colorida no item ativo */
.nav-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 24px;
  width: 3px;
  background: var(--primary-gradient);
  border-radius: 0 4px 4px 0;
}
/* Remove a barra no modo colapsado para não ficar estranho */
.dashboard-layout.sidebar-collapsed .sidebar:not(.sidebar-hover-expanded) .nav-link.active::before {
  display: none;
}


.nav-icon {
  width: 24px; text-align: center; font-size: 1.1rem;
  margin-right: 0.75rem; flex-shrink: 0;
  transition: margin var(--transition-speed), color 0.2s;
  color: var(--text-muted); /* Cor padrão mais suave */
}
.nav-link:hover .nav-icon, .nav-link.active .nav-icon {
  color: var(--primary-color); /* Cor ativa */
}


.arrow-icon { font-size: 0.75rem; margin-left: auto; transition: transform 0.3s; opacity: 0.7; }
.nav-item-group.expanded .arrow-icon { transform: rotate(180deg); }

.nav-section {
  font-size: 0.7rem; font-weight: 700; color: var(--text-muted);
  margin: 1.5rem 0 0.5rem 1rem; letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.divider { height: 1px; background: var(--border-color); margin: 1rem 0.5rem; opacity: 0.6; }

/* Submenus */
.submenu-list {
  list-style: none; padding: 0; margin: 0;
  overflow: hidden; transition: max-height 0.3s ease-in-out;
}
.submenu-list li a {
  display: block; padding: 0.6rem 1rem 0.6rem 3.5rem;
  font-size: 0.9rem; color: var(--text-muted); text-decoration: none;
  transition: color 0.2s, background-color 0.2s; 
  white-space: nowrap;
  border-radius: 8px;
  margin-left: 0.5rem; /* Pequeno recuo */
}
.submenu-list li a:hover { color: #111827; background-color: #f9fafb; }
.submenu-list li a.active { 
  color: var(--primary-color); 
  font-weight: 600;
  background-color: var(--active-gradient-bg); /* Fundo sutil também no submenu */
}

/* Footer */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex; flex-direction: column; gap: 0.5rem;
}
.collapse-toggle, .logout-btn {
  width: 100%; display: flex; align-items: center; justify-content: flex-start;
  gap: 0.75rem; padding: 0.75rem 1rem;
  border: none; background: transparent; border-radius: 10px;
  cursor: pointer; color: var(--text-main); font-size: 0.95rem;
  transition: background 0.2s, color 0.2s; white-space: nowrap;
}
.collapse-toggle:hover, .logout-btn:hover { background-color: #f3f4f6; color: #111827; }
.logout-btn:hover { color: #ef4444; background-color: #fef2f2; }

/* --- MAIN WRAPPER --- */
.main-wrapper {
  flex: 1; display: flex; flex-direction: column;
  margin-left: var(--sidebar-width);
  transition: margin-left var(--transition-speed) ease-in-out;
  width: 100%;
}

.dashboard-layout.sidebar-collapsed .main-wrapper {
  margin-left: var(--sidebar-width-collapsed);
}

/* --- HEADER --- */
.top-header {
  height: var(--header-height); background: #fff;
  /* Sombra sutil em vez de borda para um look mais moderno */
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border-bottom: none;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 2rem; position: sticky; top: 0; z-index: 40;
}
.header-left { display: flex; align-items: center; gap: 1rem; }
.menu-toggle-btn { display: none; background: none; border: none; font-size: 1.25rem; cursor: pointer; }
.page-title { font-size: 1.35rem; font-weight: 700; margin: 0; color: #111827; letter-spacing: -0.01em; }
.header-right { display: flex; align-items: center; gap: 1.5rem; }
.avatar-circle {
  width: 40px; height: 40px; background: #f3f4f6; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; color: #6b7280;
  transition: box-shadow 0.2s;
}
.avatar-circle:hover { box-shadow: 0 0 0 2px var(--primary-light); }

.page-content { flex: 1; padding: 2rem; overflow-y: auto; background-color: var(--bg-body); }

/* --- MOBILE --- */
.mobile-close-btn { display: none; background: none; border: none; font-size: 1.25rem; cursor: pointer; color: var(--text-muted); }
.sidebar-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.4); z-index: 45;
  opacity: 0; visibility: hidden; transition: opacity 0.3s;
  backdrop-filter: blur(3px); /* Blur no fundo mobile */
}

@media (max-width: 1024px) {
  .sidebar { transform: translateX(-100%); width: var(--sidebar-width) !important; }
  .dashboard-layout.mobile-open .sidebar { transform: translateX(0); box-shadow: 4px 0 15px rgba(0,0,0,0.1); }
  
  /* Desativa lógica de collapse no mobile */
  .dashboard-layout.sidebar-collapsed .sidebar { width: var(--sidebar-width); }
  
  /* Garante visibilidade de itens no mobile */
  .brand-text, .nav-label, .nav-section, .arrow-icon, .btn-label { display: block !important; }
  .nav-link, .collapse-toggle, .logout-btn { justify-content: flex-start !important; padding-left: 1rem !important; }
  .nav-link.active::before { display: block !important; }
  
  .main-wrapper { margin-left: 0 !important; }
  
  .menu-toggle-btn { display: block; }
  .sidebar-header { justify-content: space-between; padding: 0 1.5rem !important; }
  .mobile-close-btn { display: block; }
  .collapse-toggle { display: none; }
  
  .dashboard-layout.mobile-open .sidebar-overlay { opacity: 1; visibility: visible; }
  .page-content { padding: 1rem; }
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
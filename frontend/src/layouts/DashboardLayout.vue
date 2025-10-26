<template>
  <div class="dashboard-layout" :class="{ 'sidebar-open': isSidebarOpen }">
    <nav class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-brand">
          <i class="fas fa-feather-alt"></i>
          <span class="brand-text">ImobCloud</span>
        </div>
      </div>

      <ul class="sidebar-nav">
        <li>
          <router-link to="/dashboard" active-class="active" title="Dashboard">
            <i class="fas fa-tachometer-alt fa-fw"></i> <span class="nav-text">Dashboard</span>
          </router-link>
        </li>

        <li class="nav-item-dropdown" :class="{ open: isMenuOpen('imoveis') }">
          <a @click.prevent="toggleMenu('imoveis')" href="#">
            <i class="fas fa-home fa-fw"></i> <span class="nav-text">Imóveis</span>
            <i class="fas fa-chevron-right dropdown-caret"></i>
          </a>
          <ul class="submenu">
            <li><router-link to="/imoveis" active-class="active" exact-active-class="active">Listar Imóveis</router-link></li>
            <li><router-link to="/imoveis/novo" active-class="active">Adicionar Imóvel</router-link></li>
            <li><router-link to="/autorizacoes" active-class="active">Autorizações</router-link></li>
            <li><router-link to="/contatos" active-class="active">Contatos do Site</router-link></li>
          </ul>
        </li>

        <li class="nav-item-dropdown" :class="{ open: isMenuOpen('clientes') }">
          <a @click.prevent="toggleMenu('clientes')" href="#">
            <i class="fas fa-users fa-fw"></i> <span class="nav-text">Clientes & CRM</span>
            <i class="fas fa-chevron-right dropdown-caret"></i>
          </a>
          <ul class="submenu">
            <li><router-link to="/clientes" active-class="active" exact-active-class="active">Listar Clientes</router-link></li>
            <li><router-link to="/clientes/novo" active-class="active">Adicionar Cliente</router-link></li>
            <li><router-link to="/funil-vendas" active-class="active">Funil de Vendas</router-link></li>
            <li><router-link to="/oportunidades/nova" active-class="active">Nova Oportunidade</router-link></li>
          </ul>
        </li>

        <li class="nav-item-dropdown" :class="{ open: isMenuOpen('admin') }">
          <a @click.prevent="toggleMenu('admin')" href="#">
            <i class="fas fa-file-invoice-dollar fa-fw"></i> <span class="nav-text">Administrativo</span>
            <i class="fas fa-chevron-right dropdown-caret"></i>
          </a>
          <ul class="submenu">
            <li><router-link to="/financeiro/dashboard" active-class="active">Dashboard Financeiro</router-link></li>
            <li><router-link to="/financeiro/contas-a-pagar" active-class="active">Contas a Pagar</router-link></li>
            <li><router-link to="/financeiro/contas-a-receber" active-class="active">Contas a Receber</router-link></li>
            <li><router-link to="/financeiro/transacoes" active-class="active">Extrato (Transações)</router-link></li>
            <li><router-link to="/financeiro/dre" active-class="active">Relatório DRE</router-link></li>
            <li><router-link to="/contratos" active-class="active">Contratos</router-link></li>
            <li><router-link to="/alugueis/dashboard" active-class="active">Gerenciar Aluguéis</router-link></li>
          </ul>
        </li>

        <li class="nav-item-dropdown" :class="{ open: isMenuOpen('marketing') }">
          <a @click.prevent="toggleMenu('marketing')" href="#">
            <i class="fas fa-share-square fa-fw"></i> <span class="nav-text">Marketing</span>
            <i class="fas fa-chevron-right dropdown-caret"></i>
          </a>
          <ul class="submenu">
            <li><router-link to="/publicacoes" active-class="active">Gerenciar Publicações</router-link></li>
            <li><router-link :to="{ name: 'calendario-publicacoes' }" active-class="active">Calendário de Posts</router-link></li>
          </ul>
        </li>

        <li>
          <router-link to="/calendario" active-class="active" title="Calendário">
            <i class="fas fa-calendar-alt fa-fw"></i> <span class="nav-text">Agenda / Tarefas</span>
          </router-link>
        </li>

        <li class="nav-section-title"><span class="nav-text">Configurações</span></li>

        <li class="nav-item-dropdown" :class="{ open: isMenuOpen('config_geral') }">
          <a @click.prevent="toggleMenu('config_geral')" href="#">
            <i class="fas fa-cogs fa-fw"></i> <span class="nav-text">Geral</span>
            <i class="fas fa-chevron-right dropdown-caret"></i>
          </a>
          <ul class="submenu">
            <li><router-link to="/corretores" active-class="active">Utilizadores</router-link></li>
            <li><router-link to="/integracoes" active-class="active">Integrações</router-link></li>
            <li><router-link to="/configuracoes-ia" active-class="active">Configurações da IA</router-link></li>
          </ul>
        </li>

        <li class="nav-item-dropdown" :class="{ open: isMenuOpen('config_financeiro') }">
          <a @click.prevent="toggleMenu('config_financeiro')" href="#">
            <i class="fas fa-wallet fa-fw"></i> <span class="nav-text">Financeiro</span>
            <i class="fas fa-chevron-right dropdown-caret"></i>
          </a>
          <ul class="submenu">
            <li><router-link to="/financeiro/categorias" active-class="active">Categorias</router-link></li>
            <li><router-link to="/financeiro/contas" active-class="active">Contas Bancárias</router-link></li>
            <li><router-link to="/financeiro/formas-pagamento" active-class="active">Formas de Pagamento</router-link></li>
            <li><router-link to="/financeiro/config-boleto" active-class="active">Configuração Boleto</router-link></li>
          </ul>
        </li>
      </ul>
      <div class="sidebar-footer">
        <button @click="logout" class="logout-button" title="Sair">
          <i class="fas fa-sign-out-alt fa-fw"></i> <span class="nav-text">Sair</span>
        </button>
      </div>
    </nav>

    <div v-if="isSidebarOpen" class="sidebar-overlay" @click="toggleSidebar"></div>

    <div class="content-wrapper">
      <header class="content-header">
        <div class="header-left">
          <button @click="toggleSidebar" class="sidebar-toggle-button" title="Alternar menu">
            <div class="hamburger-box">
              <span class="hamburger-bar"></span>
              <span class="hamburger-bar"></span>
              <span class="hamburger-bar"></span>
            </div>
          </button>
          <h1 class="page-title">{{ route.meta.title || 'Página' }}</h1>
        </div>
        <div class="header-actions">
          <NotificationBell />
        </div>
      </header>

      <main class="router-view-wrapper">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import NotificationBell from '@/components/NotificationBell.vue';

const router = useRouter();
const route = useRoute();

const isSidebarOpen = ref(false);
const openMenu = ref<string | null>(null); // ESTADO PARA O MENU ABERTO

// Função para alternar a sidebar
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
  if (!isSidebarOpen.value) {
    openMenu.value = null; // Fecha submenus ao fechar a sidebar
  }
};

// Função para alternar os submenus
const toggleMenu = (menuName: string) => {
  if (openMenu.value === menuName) {
    openMenu.value = null; // Fecha o menu se já estiver aberto
  } else {
    openMenu.value = menuName; // Abre o novo menu
  }
};

// Função para verificar se o menu está aberto
const isMenuOpen = (menuName: string) => {
  return openMenu.value === menuName;
};

// Observador para fechar sidebar e menus ao navegar
watch(route, () => {
  if (isSidebarOpen.value) {
    isSidebarOpen.value = false;
  }
  openMenu.value = null; // Fecha submenus ao navegar
});

const logout = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('userCargo');
  router.push('/login');
};
</script>

<style scoped>
/* ESTILOS COM ANIMAÇÕES MAIS RÁPIDAS E CRIATIVAS */
:root {
  --sidebar-width: 260px;
  --header-height: 60px;
  --transition-speed: 0.35s;
  --transition-easing: cubic-bezier(0.6, 0.04, 0.98, 0.335);
}

.dashboard-layout {
  height: 100vh;
  width: 100vw;
  background-color: #f8f9fa;
  position: relative;
  overflow: hidden;
  /* FONTE MODERNA */
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
}

/* --- SIDEBAR --- */
.sidebar {
  width: var(--sidebar-width);
  height: 100%;
  background-color: #ffffff;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1001;
  transform: translateX(-100%);
  transition: transform var(--transition-speed) var(--transition-easing);
}
.dashboard-layout.sidebar-open .sidebar {
  transform: translateX(0);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
  height: var(--header-height);
  border-bottom: 1px solid #e9ecef;
}
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  color: #007bff;
  font-size: 1.5rem;
  font-weight: 700;
}
.sidebar-brand i { font-size: 1.6rem; }

.sidebar-nav {
  list-style: none;
  padding: 1rem 0;
  margin: 0;
  overflow-y: auto;
  flex-grow: 1;
}

/* --- LÓGICA DA ANIMAÇÃO EM CASCATA (MODIFICADO) --- */
/* Aplica animação apenas aos LIs de nível superior (filhos diretos) */
.sidebar-nav > li {
  opacity: 0;
  transform: translateX(-15px);
  transition: opacity 0.3s var(--transition-easing), transform 0.3s var(--transition-easing);
}
.dashboard-layout.sidebar-open .sidebar-nav > li {
  opacity: 1;
  transform: translateX(0);
}

/* Atraso para cada item da lista */
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(1) { transition-delay: 0.08s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(2) { transition-delay: 0.10s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(3) { transition-delay: 0.12s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(4) { transition-delay: 0.14s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(5) { transition-delay: 0.16s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(6) { transition-delay: 0.18s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(7) { transition-delay: 0.20s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(8) { transition-delay: 0.22s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(9) { transition-delay: 0.24s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(10) { transition-delay: 0.26s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(11) { transition-delay: 0.28s; }
.dashboard-layout.sidebar-open .sidebar-nav > li:nth-child(12) { transition-delay: 0.30s; }


.sidebar-nav a {
  display: flex;
  align-items: center;
  height: 50px;
  padding: 0 24px;
  color: #4a5568;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  white-space: nowrap;
  transition: background-color 0.2s, color 0.2s;
  position: relative; /* Adicionado para o caret */
}
.sidebar-nav a:hover { background-color: #f8f9fa; }
/* Aplica estilo ativo apenas para links diretos */
.sidebar-nav > li > a.router-link-active.router-link-exact-active,
.sidebar-nav > li > a.router-link-active {
  background-color: #e9ecef;
  color: #0056b3;
  font-weight: 600;
}
.sidebar-nav a i {
  font-size: 1.1rem;
  width: 25px;
  text-align: center;
  margin-right: 1rem;
  color: #718096;
}
/* Aplica estilo ativo aos ícones apenas para links diretos */
.sidebar-nav > li > a.router-link-active.router-link-exact-active i,
.sidebar-nav > li > a.router-link-active i {
  color: #007bff;
}

.nav-section-title {
  padding: 1.5rem 24px 0.5rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: #a0aec0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e9ecef;
}
.logout-button {
  width: 100%; padding: 0.75rem; background: transparent; border: none;
  border-radius: 6px; cursor: pointer; color: #4a5568; font-weight: 600;
  display: flex; align-items: center; gap: 0.8rem;
}
.logout-button:hover { background-color: #f1f3f5; }
.logout-button i { font-size: 1.1rem; width: 25px; text-align: center; margin-right: 1rem; }


/* --- NOVOS ESTILOS DE SUBMENU --- */
.nav-item-dropdown > a {
  cursor: pointer;
}
.dropdown-caret {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%) rotate(0deg);
  font-size: 0.8rem;
  color: #a0aec0;
  transition: transform 0.3s ease-in-out;
}
.nav-item-dropdown.open > a {
  background-color: #f8f9fa;
  color: #0056b3;
  font-weight: 600;
}
.nav-item-dropdown.open > a .nav-text {
  color: #0056b3;
}
.nav-item-dropdown.open > a i {
  color: #007bff;
}
.nav-item-dropdown.open .dropdown-caret {
  transform: translateY(-50%) rotate(90deg);
  color: #007bff;
}
.submenu {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: #f8f9fa; /* Fundo ligeiramente diferente */
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  visibility: hidden;
  transition: max-height 0.4s ease-in-out, opacity 0.3s ease-in-out, visibility 0.4s, padding 0.4s ease-in-out;
}
.nav-item-dropdown.open .submenu {
  max-height: 500px; /* Altura máxima para animação */
  opacity: 1;
  visibility: visible;
  padding: 0.5rem 0;
}
/* Estilo dos links do submenu */
.submenu a {
  height: 44px;
  /* (Padding Pai) + (Largura Icone Pai) + (Margem Icone Pai) */
  padding-left: calc(24px + 25px + 1rem);
  font-size: 0.9rem;
  font-weight: 500;
  color: #4a5568;
}
.submenu a:hover {
  background-color: #f1f3f5;
}
/* Estilo ativo para links DENTRO do submenu */
.submenu a.router-link-active.router-link-exact-active,
.submenu a.router-link-active {
  background-color: transparent; /* Sem fundo diferente */
  color: #0056b3;
  font-weight: 600;
}
/* --- FIM DOS NOVOS ESTILOS DE SUBMENU --- */


/* --- OVERLAY --- */
.sidebar-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.4); z-index: 1000;
  opacity: 0; visibility: hidden;
  transition: opacity var(--transition-speed) ease-in-out, visibility var(--transition-speed) ease-in-out;
}
.dashboard-layout.sidebar-open .sidebar-overlay {
  opacity: 1;
  visibility: visible;
}

/* --- CONTENT WRAPPER --- */
.content-wrapper {
  width: 100%; height: 100vh; display: flex; flex-direction: column;
  transition: filter var(--transition-speed) ease, transform var(--transition-speed) ease;
}
.dashboard-layout.sidebar-open .content-wrapper {
    filter: blur(4px) brightness(0.9);
    transform: scale(0.99);
}

.content-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 1.5rem; background-color: #ffffff;
  border-bottom: 1px solid #e9ecef; flex-shrink: 0;
  height: var(--header-height); width: 100%;
}
.header-left { display: flex; align-items: center; gap: 1rem; }

/* --- ANIMAÇÃO DO BOTÃO HAMBURGER -> X --- */
.sidebar-toggle-button {
  background: none; border: none; cursor: pointer;
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}
.sidebar-toggle-button:hover { background-color: #e9ecef; }
.hamburger-box {
    width: 22px; height: 16px; position: relative;
}
.hamburger-bar {
    display: block; position: absolute;
    width: 100%; height: 2px;
    background-color: #4a5568; border-radius: 2px;
    left: 0;
    transition: all 0.25s ease-in-out;
}
.hamburger-bar:nth-child(1) { top: 0; }
.hamburger-bar:nth-child(2) { top: 50%; transform: translateY(-50%); }
.hamburger-bar:nth-child(3) { bottom: 0; }
.dashboard-layout.sidebar-open .hamburger-bar:nth-child(1) {
    transform: translateY(7px) rotate(45deg);
}
.dashboard-layout.sidebar-open .hamburger-bar:nth-child(2) {
    opacity: 0;
}
.dashboard-layout.sidebar-open .hamburger-bar:nth-child(3) {
    transform: translateY(-7px) rotate(-45deg);
}


.page-title {
  font-size: 1.25rem;
  margin: 0;
  font-weight: 600;
  color: #2d3748;
}
.header-actions {
  display: flex; align-items: center; gap: 1rem;
}
.router-view-wrapper {
  overflow-y: auto;
  padding: 1.5rem;
  height: calc(100vh - var(--header-height));
}
</style>
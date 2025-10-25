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
        <li><router-link to="/dashboard" active-class="active" title="Dashboard"><i class="fas fa-tachometer-alt fa-fw"></i> <span class="nav-text">Dashboard</span></router-link></li>
        <li><router-link to="/imoveis" active-class="active" title="Imóveis"><i class="fas fa-home fa-fw"></i> <span class="nav-text">Imóveis</span></router-link></li>
        <li><router-link to="/clientes" active-class="active" title="Clientes"><i class="fas fa-users fa-fw"></i> <span class="nav-text">Clientes</span></router-link></li>
        <li><router-link to="/contratos" active-class="active" title="Contratos"><i class="fas fa-file-signature fa-fw"></i> <span class="nav-text">Contratos</span></router-link></li>
        <li><router-link to="/alugueis/dashboard" active-class="active" title="Aluguéis"><i class="fas fa-cash-register fa-fw"></i> <span class="nav-text">Aluguéis</span></router-link></li>
        <li><router-link to="/financeiro/dashboard" active-class="active" title="Financeiro"><i class="fas fa-wallet fa-fw"></i> <span class="nav-text">Financeiro</span></router-link></li>
        <li><router-link to="/funil-vendas" active-class="active" title="Funil de Vendas"><i class="fas fa-filter fa-fw"></i> <span class="nav-text">Funil de Vendas</span></router-link></li>
        <li><router-link to="/calendario" active-class="active" title="Calendário"><i class="fas fa-calendar-alt fa-fw"></i> <span class="nav-text">Calendário</span></router-link></li>
        <li><router-link to="/publicacoes" active-class="active" title="Publicações"><i class="fas fa-share-square fa-fw"></i> <span class="nav-text">Publicações</span></router-link></li>
        <li class="nav-section-title"><span class="nav-text">Configurações</span></li>
        <li><router-link to="/integracoes" active-class="active" title="Integrações"><i class="fas fa-cogs fa-fw"></i> <span class="nav-text">Integrações</span></router-link></li>
        <li><router-link to="/corretores" active-class="active" title="Utilizadores"><i class="fas fa-user-tie fa-fw"></i> <span class="nav-text">Utilizadores</span></router-link></li>
      </ul>
      <div class="sidebar-footer">
        <button @click="logout" class="logout-button" title="Sair">
          <i class="fas fa-sign-out-alt fa-fw"></i> <span class="nav-text">Sair</span>
        </button>
      </div>
    </nav>
    
    <div v-if="isSidebarOpen" class="sidebar-overlay" @click="isSidebarOpen = false"></div>

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

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

watch(route, () => {
  if (isSidebarOpen.value) {
    isSidebarOpen.value = false;
  }
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

/* --- LÓGICA DA ANIMAÇÃO EM CASCATA --- */
.sidebar-nav li {
  opacity: 0;
  transform: translateX(-15px);
  transition: opacity 0.3s var(--transition-easing), transform 0.3s var(--transition-easing);
}
.dashboard-layout.sidebar-open .sidebar-nav li {
  opacity: 1;
  transform: translateX(0);
}

/* Atraso para cada item da lista */
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(1) { transition-delay: 0.08s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(2) { transition-delay: 0.10s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(3) { transition-delay: 0.12s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(4) { transition-delay: 0.14s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(5) { transition-delay: 0.16s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(6) { transition-delay: 0.18s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(7) { transition-delay: 0.20s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(8) { transition-delay: 0.22s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(9) { transition-delay: 0.24s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(10) { transition-delay: 0.26s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(11) { transition-delay: 0.28s; }
.dashboard-layout.sidebar-open .sidebar-nav li:nth-child(12) { transition-delay: 0.30s; }


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
}
.sidebar-nav a:hover { background-color: #f8f9fa; }
.sidebar-nav a.active {
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
.sidebar-nav a.active i { color: #007bff; }

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
  font-size: 1.5rem; margin: 0; font-weight: 600; color: #2d3748;
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
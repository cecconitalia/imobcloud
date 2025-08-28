<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <router-link to="/dashboard">
          <img src="@/assets/vue.svg" alt="ImobCloud Logo" class="logo" />
        </router-link>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li>
            <router-link to="/dashboard" class="nav-item">
              <i class="fas fa-home"></i>
              <span>Dashboard</span>
            </router-link>
          </li>
        </ul>

        <div class="menu-group">
          <h4><i class="fas fa-folder-open group-icon"></i> Gestão Imóveis & Clientes</h4>
          <ul>
            <li>
              <router-link to="/imoveis" class="nav-item">
                <i class="fas fa-building"></i>
                <span>Imóveis</span>
              </router-link>
            </li>
            <li>
              <router-link to="/clientes" class="nav-item">
                <i class="fas fa-users"></i>
                <span>Clientes</span>
              </router-link>
            </li>
            <li>
              <router-link to="/contratos" class="nav-item">
                <i class="fas fa-file-signature"></i>
                <span>Contratos</span>
              </router-link>
            </li>
            <li>
              <router-link to="/visitas" class="nav-item">
                <i class="fas fa-calendar-check"></i>
                <span>Visitas</span>
              </router-link>
            </li>
            <li>
              <router-link to="/autorizacoes" class="nav-item">
                <i class="fas fa-user-lock"></i>
                <span>Autorizações</span>
              </router-link>
            </li>
          </ul>
        </div>

        <div class="menu-group">
          <h4><i class="fas fa-chart-line group-icon"></i> Gestão Comercial</h4>
          <ul>
            <li>
              <router-link to="/funil-vendas" class="nav-item">
                <i class="fas fa-filter"></i>
                <span>Funil de Vendas</span>
              </router-link>
            </li>
            <li>
              <router-link to="/oportunidades/nova" class="nav-item">
                <i class="fas fa-bullseye"></i>
                <span>Nova Oportunidade</span>
              </router-link>
            </li>
          </ul>
        </div>

        <div class="menu-group">
          <h4><i class="fas fa-dollar-sign group-icon"></i> Financeiro</h4>
          <ul>
            <li>
              <router-link to="/financeiro/dashboard" class="nav-item">
                <i class="fas fa-chart-pie"></i>
                <span>Dashboard Financeiro</span>
              </router-link>
            </li>
            <li>
              <router-link to="/financeiro/transacoes" class="nav-item">
                <i class="fas fa-exchange-alt"></i>
                <span>Transações</span>
              </router-link>
            </li>
            <li>
              <router-link to="/financeiro/contas-a-pagar" class="nav-item">
                <i class="fas fa-money-bill-wave"></i>
                <span>Contas a Pagar</span>
              </router-link>
            </li>
            <li>
              <router-link to="/financeiro/contas-a-receber" class="nav-item">
                <i class="fas fa-hand-holding-usd"></i>
                <span>Contas a Receber</span>
              </router-link>
            </li>
             <li>
              <router-link to="/financeiro/remessa-retorno" class="nav-item">
                <i class="fas fa-exchange-alt"></i>
                <span>Remessa e Retorno</span>
              </router-link>
            </li>
            <li>
              <router-link to="/financeiro/contas" class="nav-item">
                <i class="fas fa-university"></i>
                <span>Contas Bancárias</span>
              </router-link>
            </li>
            <li>
              <router-link to="/financeiro/categorias" class="nav-item">
                <i class="fas fa-tags"></i>
                <span>Categorias</span>
              </router-link>
            </li>
            <li>
              <router-link to="/financeiro/formas-pagamento" class="nav-item">
                <i class="fas fa-credit-card"></i>
                <span>Formas de Pagamento</span>
              </router-link>
            </li>
          </ul>
        </div>

        <div class="menu-group">
          <h4><i class="fas fa-bullhorn group-icon"></i> Marketing & IA</h4>
          <ul>
            <li>
              <router-link to="/publicacoes" class="nav-item">
                <i class="fas fa-share-alt"></i>
                <span>Central de Publicações</span>
              </router-link>
            </li>
            <li>
              <router-link to="/calendario-publicacoes" class="nav-item">
                <i class="fas fa-calendar-alt"></i>
                <span>Calendário de Posts</span>
              </router-link>
            </li>
            <li>
              <router-link to="/integracoes" class="nav-item">
                <i class="fas fa-cogs"></i>
                <span>Integrações</span>
              </router-link>
            </li>
            <li>
              <router-link to="/configuracoes-ia" class="nav-item">
                <i class="fas fa-brain"></i>
                <span>Configurações da IA</span>
              </router-link>
            </li>
          </ul>
        </div>
        
        <div class="menu-group">
          <h4><i class="fas fa-chart-bar group-icon"></i> Relatórios</h4>
          <ul>
             <li>
              <router-link to="/relatorios" class="nav-item">
                <i class="fas fa-chart-line"></i>
                <span>Relatórios Gerais</span>
              </router-link>
            </li>
            <li>
              <router-link to="/alugueis/dashboard" class="nav-item">
                <i class="fas fa-house-user"></i>
                <span>Dashboard de Aluguéis</span>
              </router-link>
            </li>
            <li>
              <router-link to="/financeiro/dre" class="nav-item">
                <i class="fas fa-file-alt"></i>
                <span>Relatório DRE</span>
              </router-link>
            </li>
          </ul>
        </div>
      </nav>
      <div class="profile-section">
        <div class="user-info">
          <span class="user-name">{{ user.nome }}</span>
          <small class="user-role">{{ user.cargo }}</small>
        </div>
        <button @click="logout" class="logout-btn">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <header class="topbar">
        <h2 class="page-title">{{ routeTitle }}</h2>
        <div class="header-right">
          <NotificationBell />
          <router-link to="/settings" class="settings-link" title="Configurações">
            <i class="fas fa-cog"></i>
          </router-link>
        </div>
      </header>
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import NotificationBell from '@/components/NotificationBell.vue';

const router = useRouter();
const route = useRoute();
const user = ref({ nome: 'Usuário', cargo: 'Corretor' });

const routeTitle = computed(() => route.meta.title || 'Dashboard');

onMounted(() => {
    const userName = localStorage.getItem('userName');
    const userCargo = localStorage.getItem('userCargo');
    if (userName && userCargo) {
        user.value.nome = userName;
        user.value.cargo = userCargo === 'ADMIN' ? 'Administrador' : 'Corretor';
    }
});

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userCargo');
    router.push('/login');
}
</script>

<style scoped>
/* Estilos globais e de layout para o dashboard */
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f4f7f9;
  font-family: 'Arial', sans-serif;
}

.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: #ecf0f1;
  display: flex;
  flex-direction: column;
  padding: 1rem 0;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.sidebar-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 0 1rem;
}

.logo {
  max-width: 150px;
  height: auto;
}

.sidebar-nav {
  flex-grow: 1;
  overflow-y: auto;
}

/* Novo estilo para os grupos de menu */
.menu-group {
  margin-bottom: 1.5rem;
  padding: 0 1rem;
}

.menu-group h4 {
  color: #a0a0a0;
  font-size: 0.9rem;
  font-weight: bold;
  margin-bottom: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.group-icon {
  font-size: 1rem;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  color: #ecf0f1;
  text-decoration: none;
  font-size: 1rem;
  border-radius: 5px;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.nav-item:hover, .nav-item.router-link-exact-active {
  background-color: #34495e;
  color: #ffffff;
  transform: translateX(5px);
}

.nav-item i {
  margin-right: 12px;
  width: 20px;
  text-align: center;
}

.profile-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-top: 1px solid #34495e;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: bold;
  font-size: 1rem;
}

.user-role {
  font-size: 0.8rem;
  color: #bdc3c7;
}

.logout-btn {
  background: none;
  border: none;
  color: #ecf0f1;
  cursor: pointer;
  font-size: 1.2rem;
  transition: color 0.2s ease;
}

.logout-btn:hover {
  color: #e74c3c;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.topbar {
  background-color: #ffffff;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.settings-link {
  color: #555;
  font-size: 1.2rem;
  transition: color 0.2s ease;
}

.settings-link:hover {
  color: #007bff;
}

.content-wrapper {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto;
}
</style>
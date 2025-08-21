<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <router-link to="/dashboard" class="header-link">
          <h2 v-if="imobiliariaName">{{ imobiliariaName }}</h2>
          <h2 v-else>ImobCloud</h2>
        </router-link>
        <p v-if="userName" class="user-name">{{ userName }}</p>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-link">
          <i class="icon-dashboard"></i>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/funil-vendas" class="nav-link">
          <i class="icon-funil"></i>
          <span>Funil de Vendas</span>
        </router-link>
        <router-link to="/calendario" class="nav-link">
          <i class="icon-calendario"></i>
          <span>Calendário</span>
        </router-link>
        
        <router-link to="/publicacoes" class="nav-link">
          <i class="icon-publicacoes"></i>
          <span>Publicações</span>
        </router-link>

        <router-link to="/calendario-publicacoes" class="nav-link">
          <i class="icon-calendario-publicacoes"></i>
          <span>Calendário Editorial</span>
        </router-link>
        
        <router-link to="/imoveis" class="nav-link">
          <i class="icon-imoveis"></i>
          <span>Imóveis</span>
        </router-link>
        <router-link to="/clientes" class="nav-link">
          <i class="icon-clientes"></i>
          <span>Clientes</span>
        </router-link>
        <router-link to="/contratos" class="nav-link">
          <i class="icon-contratos"></i>
          <span>Contratos</span>
        </router-link>
        <router-link to="/visitas" class="nav-link">
          <i class="icon-visitas"></i>
          <span>Visitas</span>
        </router-link>

        <div class="nav-section-header">
          <span>Financeiro</span>
        </div>
        <router-link to="/financeiro/dashboard" class="nav-link">
          <i class="icon-financeiro"></i>
          <span>Dashboard</span>
        </router-link>
        
        <router-link to="/financeiro/contas-pendentes" class="nav-link">
          <i class="icon-pendentes"></i>
          <span>Contas a Pagar/Receber</span>
        </router-link>
        
        <router-link to="/alugueis/dashboard" class="nav-link">
          <i class="icon-alugueis"></i>
          <span>Aluguéis</span>
        </router-link>

        <router-link to="/financeiro/transacoes" class="nav-link">
          <i class="icon-transacoes"></i>
          <span>Transações</span>
        </router-link>
        <router-link to="/financeiro/dre" class="nav-link">
          <i class="icon-dre"></i>
          <span>Relatório DRE</span>
        </router-link>
        <router-link to="/financeiro/contas" class="nav-link">
          <i class="icon-contas"></i>
          <span>Gerir Contas</span>
        </router-link>
        <router-link to="/financeiro/categorias" class="nav-link">
          <i class="icon-categorias"></i>
          <span>Gerir Categorias</span>
        </router-link>

        <div v-if="userCargo === 'ADMIN'" class="nav-section-header">
          <span>Administração</span>
        </div>
        <router-link v-if="userCargo === 'ADMIN'" to="/autorizacoes" class="nav-link">
          <i class="icon-autorizacoes"></i>
          <span>Gestão de Autorizações</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/contatos" class="nav-link">
          <i class="icon-contatos"></i>
          <span>Contatos</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/corretores" class="nav-link">
          <i class="icon-users"></i>
          <span>Gerir Utilizadores</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/relatorios" class="nav-link">
          <i class="icon-relatorios"></i>
          <span>Relatórios</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/configuracoes-ia" class="nav-link">
          <i class="icon-ia"></i>
          <span>Configurações da IA</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/integracoes" class="nav-link">
          <i class="icon-integracoes"></i>
          <span>Integrações</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button @click="handleLogout" class="logout-button">
          Sair
        </button>
      </div>
    </aside>

    <div class="main-container">
      <header class="main-header">
        <div class="header-content">
          <div class="spacer"></div>
          <NotificationBell />
        </div>
      </header>
      <main class="main-content">
        <div class="content-wrapper">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import NotificationBell from '@/components/NotificationBell.vue';

const router = useRouter();
const userCargo = ref('');
const imobiliariaName = ref('');
const userName = ref('');

function handleLogout() {
  localStorage.removeItem('authToken');
  localStorage.removeItem('userCargo');
  localStorage.removeItem('imobiliariaName');
  localStorage.removeItem('userName');
  router.push({ name: 'login' });
}

onMounted(() => {
  userCargo.value = localStorage.getItem('userCargo') || '';
  imobiliariaName.value = localStorage.getItem('imobiliariaName') || '';
  userName.value = localStorage.getItem('userName') || '';
});
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.nav-link i::before {
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  margin-right: 10px;
  width: 20px;
  text-align: center;
}
.icon-dashboard::before { content: "\f3fd"; }
.icon-funil::before { content: "\f1de"; }
.icon-calendario::before { content: "\f073"; }
.icon-imoveis::before { content: "\f279"; }
.icon-clientes::before { content: "\f0c0"; }
.icon-contratos::before { content: "\f15c"; }
.icon-visitas::before { content: "\f0f3"; }
.icon-contatos::before { content: "\f0e0"; }
.icon-users::before { content: "\f500"; }
.icon-relatorios::before { content: "\f080"; }
.icon-autorizacoes::before { content: "\f2b5"; }
/* Ícones do Módulo Financeiro */
.icon-financeiro::before { content: "\f53c"; }
.icon-transacoes::before { content: "\f0d6"; }
.icon-dre::before { content: "\f200"; }
.icon-contas::before { content: "\f53d"; }
.icon-categorias::before { content: "\f02d"; }
.icon-pendentes::before { content: "\f252"; }

/* Ícones de Administração e Novos */
.icon-ia::before { content: "\f544"; } 
.icon-integracoes::before { content: "\f368"; }
.icon-publicacoes::before { content: "\f1d8"; }
.icon-calendario-publicacoes::before { content: "\f133"; }
.icon-alugueis::before { content: "\f0a9"; }

.dashboard-layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  flex-shrink: 0;
}
.sidebar-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid #34495e;
  text-align: center;
}
.header-link {
  text-decoration: none;
  color: white;
}
.sidebar-header h2 {
  margin: 0;
}
.user-name {
  margin-top: 0.5rem;
  color: #bdc3c7;
  font-size: 0.9em;
}
.sidebar-nav {
  margin-top: 1.5rem;
  flex-grow: 1;
}
.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  color: #ecf0f1;
  text-decoration: none;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  transition: background-color 0.2s, color 0.2s;
}
.nav-link:hover {
  background-color: #34495e;
}
.nav-link.router-link-exact-active {
  background-color: #3498db;
  color: white;
  font-weight: bold;
}
.nav-section-header {
  color: #95a5a6;
  font-weight: bold;
  padding: 12px 15px;
  margin-top: 1rem;
  text-transform: uppercase;
  font-size: 0.8em;
  border-top: 1px solid #34495e;
}
.sidebar-footer {
  margin-top: auto;
}
.logout-button {
  width: 100%;
  padding: 10px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
.main-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #f4f7f6;
}
.main-header {
  background-color: #fff;
  padding: 0 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  z-index: 50;
  flex-shrink: 0;
}
.header-content {
  display: flex;
  align-items: center;
  height: 60px;
}
.spacer {
  flex-grow: 1;
}
.main-content {
  flex-grow: 1;
  overflow-y: auto;
}
.content-wrapper {
  max-width: 1300px;
  margin: 0 auto;
  padding: 2rem;
}
</style>
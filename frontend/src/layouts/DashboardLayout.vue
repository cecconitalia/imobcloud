<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <router-link to="/dashboard" class="header-link">
          <h2 class="full-text">ImobCloud</h2>
          <i class="icon-logo compact-icon"></i>
        </router-link>
        <p class="user-name full-text">{{ userName }}</p>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-link">
          <i class="icon-dashboard"></i>
          <span class="nav-link-text">Dashboard</span>
        </router-link>
        <router-link to="/funil-vendas" class="nav-link">
          <i class="icon-funil"></i>
          <span class="nav-link-text">Funil de Vendas</span>
        </router-link>
        <router-link to="/calendario" class="nav-link">
          <i class="icon-calendario"></i>
          <span class="nav-link-text">Calendário</span>
        </router-link>
        
        <router-link to="/publicacoes" class="nav-link">
          <i class="icon-publicacoes"></i>
          <span class="nav-link-text">Publicações</span>
        </router-link>

        <router-link to="/calendario-publicacoes" class="nav-link">
          <i class="icon-calendario-publicacoes"></i>
          <span class="nav-link-text">Calendário Editorial</span>
        </router-link>
        
        <router-link to="/imoveis" class="nav-link">
          <i class="icon-imoveis"></i>
          <span class="nav-link-text">Imóveis</span>
        </router-link>
        <router-link to="/clientes" class="nav-link">
          <i class="icon-clientes"></i>
          <span class="nav-link-text">Clientes</span>
        </router-link>
        <router-link to="/contratos" class="nav-link">
          <i class="icon-contratos"></i>
          <span class="nav-link-text">Contratos</span>
        </router-link>
        <router-link to="/visitas" class="nav-link">
          <i class="icon-visitas"></i>
          <span class="nav-link-text">Visitas</span>
        </router-link>

        <div v-if="userCargo === 'ADMIN'" class="nav-section-header">
          <span class="nav-link-text">Financeiro</span>
        </div>
        <router-link to="/financeiro/dashboard" class="nav-link">
          <i class="icon-financeiro"></i>
          <span class="nav-link-text">Dashboard</span>
        </router-link>
        
        <router-link to="/financeiro/contas-a-receber" class="nav-link">
          <i class="fas fa-hand-holding-usd"></i>
          <span class="nav-link-text">Contas a Receber</span>
        </router-link>
        <router-link to="/financeiro/contas-a-pagar" class="nav-link">
          <i class="fas fa-file-invoice-dollar"></i>
          <span class="nav-link-text">Contas a Pagar</span>
        </router-link>
        <router-link to="/alugueis/dashboard" class="nav-link">
          <i class="icon-alugueis"></i>
          <span class="nav-link-text">Aluguéis</span>
        </router-link>

        <router-link to="/financeiro/transacoes" class="nav-link">
          <i class="icon-transacoes"></i>
          <span class="nav-link-text">Transações</span>
        </router-link>
        <router-link to="/financeiro/dre" class="nav-link">
          <i class="icon-dre"></i>
          <span class="nav-link-text">Relatório DRE</span>
        </router-link>
        <router-link to="/financeiro/contas" class="nav-link">
          <i class="icon-contas"></i>
          <span class="nav-link-text">Gerir Contas</span>
        </router-link>
        <router-link to="/financeiro/categorias" class="nav-link">
          <i class="icon-categorias"></i>
          <span class="nav-link-text">Gerir Categorias</span>
        </router-link>
        <router-link to="/financeiro/formas-pagamento" class="nav-link">
          <i class="fas fa-wallet"></i>
          <span class="nav-link-text">Gerir Formas de Pagamento</span>
        </router-link>
        <router-link to="/financeiro/remessa-retorno" class="nav-link">
          <i class="fas fa-exchange-alt"></i>
          <span class="nav-link-text">Remessa/Retorno</span>
        </router-link>


        <div v-if="userCargo === 'ADMIN'" class="nav-section-header">
          <span class="nav-link-text">Administração</span>
        </div>
        <router-link v-if="userCargo === 'ADMIN'" to="/autorizacoes" class="nav-link">
          <i class="icon-autorizacoes"></i>
          <span class="nav-link-text">Gestão de Autorizações</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/contatos" class="nav-link">
          <i class="icon-contatos"></i>
          <span class="nav-link-text">Contatos</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/corretores" class="nav-link">
          <i class="icon-users"></i>
          <span class="nav-link-text">Gerir Utilizadores</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/relatorios" class="nav-link">
          <i class="icon-relatorios"></i>
          <span class="nav-link-text">Relatórios</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/configuracoes-ia" class="nav-link">
          <i class="icon-ia"></i>
          <span class="nav-link-text">Configurações da IA</span>
        </router-link>
        <router-link v-if="userCargo === 'ADMIN'" to="/integracoes" class="nav-link">
          <i class="icon-integracoes"></i>
          <span class="nav-link-text">Integrações</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button @click="handleLogout" class="logout-button">
          <i class="fas fa-sign-out-alt"></i>
          <span class="full-text">Sair</span>
        </button>
      </div>
    </aside>

    <div class="main-container">
      <header class="main-header">
        <div class="header-content">
          <h1 class="page-title">{{ route.meta.title || 'Dashboard' }}</h1>
          <div class="spacer"></div>
          <NotificationBell />
        </div>
      </header>
      <main class="main-content">
        <div class="dashboard-grid">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import NotificationBell from '@/components/NotificationBell.vue';
import '@fortawesome/fontawesome-free/css/all.min.css';

const router = useRouter();
const route = useRoute();
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

/* Icones */
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
.icon-financeiro::before { content: "\f53c"; }
.icon-transacoes::before { content: "\f0d6"; }
.icon-dre::before { content: "\f200"; }
.icon-contas::before { content: "\f53d"; }
.icon-categorias::before { content: "\f02d"; }
.icon-pendentes::before { content: "\f252"; }
.icon-ia::before { content: "\f544"; } 
.icon-integracoes::before { content: "\f368"; }
.icon-publicacoes::before { content: "\f1d8"; }
.icon-calendario-publicacoes::before { content: "\f133"; }
.icon-alugueis::before { content: "\f0a9"; }

.icon-logo::before { content: "\f279"; } /* Ícone para o logo quando recolhido */

/* Layout principal */
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar - Estado recolhido */
.sidebar {
  width: 64px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 0.8rem 0.4rem;
  flex-shrink: 0;
  transition: width 0.3s ease;
  overflow-x: hidden;
  position: sticky;
  top: 0;
  height: 100vh;
}

/* Sidebar - Estado expandido ao passar o mouse */
.sidebar:hover {
  width: 200px;
}

/* Conteúdo que deve ser escondido/mostrado com transição */
.full-text, .nav-link-text, .nav-section-header {
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.1s ease, visibility 0.1s ease;
  overflow: hidden;
}

/* Mostra o conteúdo ao expandir */
.sidebar:hover .full-text, .sidebar:hover .nav-link-text, .sidebar:hover .nav-section-header {
  opacity: 1;
  visibility: visible;
  transition: opacity 0.3s ease 0.1s, visibility 0.3s ease 0.1s;
}

.sidebar-header {
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #34495e;
  text-align: center;
}
.header-link {
  text-decoration: none;
  color: white;
}
.sidebar-header h2 {
  font-size: 1.2rem;
  margin: 0;
}
.user-name {
  margin-top: 0.4rem;
  color: #bdc3c7;
  font-size: 0.72em;
}
.sidebar-nav {
  margin-top: 1.2rem;
  flex-grow: 1;
}
.nav-link {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 9.6px;
  color: #ecf0f1;
  text-decoration: none;
  border-radius: 4px;
  margin-bottom: 0.4rem;
  transition: background-color 0.2s, color 0.2s;
}
.sidebar:hover .nav-link {
  justify-content: flex-start;
  padding: 9.6px 12px;
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
  padding: 9.6px 12px;
  margin-top: 0.8rem;
  text-transform: uppercase;
  font-size: 0.64em;
  border-top: 1px solid #34495e;
}
.sidebar-footer {
  margin-top: auto;
  text-align: center;
}
.logout-button {
  width: 100%;
  padding: 8px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6.4px;
}
.sidebar:hover .logout-button {
  justify-content: flex-start;
}

/* O corpo principal do sistema */
.main-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #f4f7f6;
  transition: margin-left 0.3s ease;
}

/* O cabeçalho do corpo principal */
.main-header {
  background-color: #fff;
  padding: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  z-index: 50;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  height: 48px;
  margin-left: 64px;
  transition: margin-left 0.3s ease;
}

/* O header-content foi atualizado para ocupar toda a largura e ter o padding interno */
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Alinhamento dos elementos */
  width: 100%;
  height: 100%;
  padding: 0 1.6rem; /* Adicionado o padding interno aqui */
}

/* Título da página no cabeçalho */
.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #343a40;
  margin: 0;
  line-height: 1; /* Garante alinhamento com o sino */
}

/* Ajuste do cabeçalho quando o menu expande */
.sidebar:hover ~ .main-container .main-header {
  margin-left: 200px;
}

/* O conteúdo dentro do corpo principal */
.main-content {
  flex-grow: 1;
  overflow-y: auto;
}

/* A nova grelha de dashboard */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

/* Ícones do logo no estado recolhido/expandido */
.full-text { display: block; }
.compact-icon { display: none; }
.sidebar:hover .full-text { display: block; }
.sidebar:hover .compact-icon { display: none; }
.sidebar .full-text { display: none; }
.sidebar .compact-icon { display: block; }
</style>
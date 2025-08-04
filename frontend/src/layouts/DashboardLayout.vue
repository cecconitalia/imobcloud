<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>ImobCloud</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-link">
          <i class="icon-dashboard"></i>
          <span>Dashboard</span>
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
      </nav>
      <div class="sidebar-footer">
        <button @click="handleLogout" class="logout-button">
          Sair
        </button>
      </div>
    </aside>

    <main class="main-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

function handleLogout() {
  localStorage.removeItem('authToken');
  // Redireciona para a página de login após o logout
  router.push({ name: 'login' });
}
</script>

<style scoped>
/* O seu CSS existente não precisa de alterações */
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f4f7f6;
}
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}
.sidebar-header h2 {
  text-align: center;
  margin: 0;
  padding-bottom: 1rem;
  border-bottom: 1px solid #34495e;
}
.sidebar-nav {
  margin-top: 2rem;
  flex-grow: 1;
}
.nav-link {
  display: block;
  padding: 12px 15px;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  transition: background-color 0.3s;
}
.nav-link:hover, .router-link-exact-active {
  background-color: #34495e;
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
.logout-button:hover {
  background-color: #c0392b;
}
.main-content {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto;
}
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
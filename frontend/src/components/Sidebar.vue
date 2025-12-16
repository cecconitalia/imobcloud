<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="logo-icon">
        <i class="fas fa-cloud"></i>
      </div>
      <span class="logo-text">ImobCloud</span>
    </div>

    <nav class="sidebar-nav">
      <ul class="nav-list">
        
        <li>
          <router-link :to="{ name: 'dashboard' }" class="nav-link" active-class="active">
            <i class="fas fa-home"></i>
            <span>Dashboard</span>
          </router-link>
        </li>

        <li>
          <router-link to="/vistorias" class="nav-link" active-class="active">
            <i class="fas fa-clipboard-check"></i>
            <span>Vistorias</span>
          </router-link>
        </li>

        <li>
          <router-link to="/imoveis" class="nav-link" active-class="active">
            <i class="fas fa-building"></i>
            <span>Imóveis</span>
          </router-link>
        </li>

        <li>
          <router-link to="/contratos" class="nav-link" active-class="active">
            <i class="fas fa-file-contract"></i>
            <span>Contratos</span>
          </router-link>
        </li>

      </ul>
    </nav>

    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          <i class="fas fa-user"></i>
        </div>
        <div class="user-details">
          <span class="user-name">{{ userName }}</span>
          <span class="user-role">{{ userCargo }}</span>
        </div>
      </div>
      
      <button @click="handleLogout" class="logout-btn" title="Sair do Sistema">
        <i class="fas fa-sign-out-alt"></i>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const userName = ref('Usuário');
const userCargo = ref('Corretor');

// Carrega dados do usuário ao montar o componente
onMounted(() => {
  const storedName = localStorage.getItem('userName');
  const storedCargo = localStorage.getItem('userCargo');
  if (storedName) userName.value = storedName;
  if (storedCargo) userCargo.value = storedCargo;
});

// --- FUNÇÃO DE LOGOUT CORRIGIDA ---
function handleLogout() {
  // 1. Limpa todos os dados de sessão
  localStorage.removeItem('authToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('userCargo');
  localStorage.removeItem('imobiliariaName');
  localStorage.removeItem('userName');

  // 2. Força o redirecionamento para a tela de Login
  router.replace({ name: 'login' });
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  background-color: #111827; /* Dark theme */
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 4px 0 10px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

/* Header */
.sidebar-header {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #1f2937;
}
.logo-icon {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}
.logo-text {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 24px 16px;
  overflow-y: auto;
}
.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.nav-list li {
  margin-bottom: 8px;
}
.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  color: #9ca3af;
  text-decoration: none;
  transition: all 0.2s;
  font-weight: 500;
}
.nav-link:hover {
  background-color: #1f2937;
  color: white;
}
.nav-link.active {
  background-color: #3b82f6;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.nav-link i {
  width: 24px;
  margin-right: 12px;
  text-align: center;
}

/* Footer (User & Logout) */
.sidebar-footer {
  border-top: 1px solid #1f2937;
  padding: 20px;
  background-color: #0f1521;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}
.user-avatar {
  width: 36px;
  height: 36px;
  background: #374151;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d1d5db;
}
.user-details {
  display: flex;
  flex-direction: column;
}
.user-name {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}
.user-role {
  font-size: 11px;
  color: #9ca3af;
}

.logout-btn {
  background: transparent;
  border: none;
  color: #ef4444; /* Vermelho */
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.2s;
}
.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}
</style>
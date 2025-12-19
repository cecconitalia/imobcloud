<template>
  <aside class="sidebar-root" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-header">
      <div class="logo-box"><i class="fas fa-feather-alt"></i></div>
      <span v-if="!isCollapsed" class="logo-text">ImobCloud</span>
    </div>

    <nav class="sidebar-nav">
      <div v-for="group in menuItems" :key="group.label" class="nav-group">
        <label v-if="!isCollapsed" class="group-title">{{ group.label }}</label>
        
        <ul class="nav-list">
          <li v-for="item in group.items" :key="item.path">
            <router-link v-if="!item.children" :to="item.path" class="nav-link" active-class="active">
              <div class="nav-icon"><i :class="item.icon"></i></div>
              <span v-if="!isCollapsed" class="nav-label">{{ item.title }}</span>
            </router-link>

            <div v-else class="nav-dropdown">
              <button @click="toggleMenu(item.title)" class="nav-link" :class="{ 'active': isChildActive(item) }">
                <div class="nav-icon"><i :class="item.icon"></i></div>
                <span v-if="!isCollapsed" class="nav-label">{{ item.title }}</span>
                <i v-if="!isCollapsed" class="fas fa-chevron-right arrow" :class="{ 'rotate': openMenus.includes(item.title) }"></i>
              </button>
              
              <ul v-if="!isCollapsed && openMenus.includes(item.title)" class="submenu">
                <li v-for="child in item.children" :key="child.path">
                  <router-link :to="child.path" active-class="active-child">{{ child.title }}</router-link>
                </li>
              </ul>
            </div>
          </li>
        </ul>
      </div>
    </nav>

    <div class="sidebar-footer">
      <div v-if="!isCollapsed" class="user-pill">
        <div class="avatar">{{ userName.charAt(0) }}</div>
        <div class="user-info">
          <span class="u-name">{{ userName }}</span>
          <span class="u-role">{{ userCargo }}</span>
        </div>
      </div>
      <button @click="logout" class="btn-logout" title="Sair"><i class="fas fa-power-off"></i></button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

defineProps<{ isCollapsed: boolean }>();

const router = useRouter();
const route = useRoute();
const userName = ref('Usuário');
const userCargo = ref('Acesso');
const openMenus = ref<string[]>(['Negócios']);

const menuItems = [
  { label: 'Geral', items: [
    { title: 'Painel Geral', path: '/dashboard', icon: 'fas fa-th-large' },
    { title: 'Agenda', path: '/calendario', icon: 'fas fa-calendar-alt' }
  ]},
  { label: 'Operacional', items: [
    { title: 'Negócios', icon: 'fas fa-handshake', children: [
      { title: 'Clientes', path: '/clientes' },
      { title: 'Funil de Vendas', path: '/funil-vendas' },
      { title: 'Agenda Visitas', path: '/visitas' }
    ]},
    { title: 'Imóveis', path: '/imoveis', icon: 'fas fa-building' },
    { title: 'Vistorias', path: '/vistorias', icon: 'fas fa-tasks' },
    { title: 'Contratos', path: '/contratos', icon: 'fas fa-file-signature' }
  ]},
  { label: 'Gestão', items: [
    { title: 'Financeiro', icon: 'fas fa-chart-line', children: [
      { title: 'Dashboard', path: '/financeiro/dashboard' },
      { title: 'A Receber', path: '/financeiro/contas-a-receber' },
      { title: 'A Pagar', path: '/financeiro/contas-a-pagar' },
      { title: 'DRE', path: '/financeiro/dre' }
    ]},
    { title: 'Marketing AI', path: '/publicacoes', icon: 'fas fa-magic' }
  ]}
];

const toggleMenu = (title: string) => {
  const index = openMenus.value.indexOf(title);
  if (index > -1) openMenus.value.splice(index, 1);
  else openMenus.value.push(title);
};

const isChildActive = (item: any) => item.children?.some((c: any) => route.path.startsWith(c.path));

onMounted(() => {
  userName.value = localStorage.getItem('userName') || 'Usuário';
  userCargo.value = localStorage.getItem('userCargo') || 'Acesso';
});

const logout = () => { localStorage.clear(); router.push('/login'); };
</script>

<style scoped>
.sidebar-root {
  width: 260px; height: 100vh; background: #0f172a; color: #f1f5f9;
  display: flex; flex-direction: column; position: fixed; left: 0; top: 0;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 1000; border-right: 1px solid #1e293b;
}
.sidebar-root.collapsed { width: 70px; }

.sidebar-header { height: 64px; padding: 0 20px; display: flex; align-items: center; gap: 12px; }
.logo-box { 
  width: 32px; height: 32px; background: linear-gradient(135deg, #6366f1, #4f46e5); 
  border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white;
}
.logo-text { font-weight: 800; font-size: 1.1rem; letter-spacing: -0.5px; }

.sidebar-nav { flex: 1; padding: 10px; overflow-y: auto; }
.nav-group { margin-bottom: 20px; }
.group-title { font-size: 0.6rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-left: 12px; margin-bottom: 8px; display: block; }

.nav-list { list-style: none; padding: 0; margin: 0; }
.nav-link { 
  display: flex; align-items: center; padding: 10px 12px; color: #94a3b8; text-decoration: none; 
  border-radius: 8px; font-size: 0.85rem; font-weight: 500; cursor: pointer; background: none; border: none; width: 100%; text-align: left;
}
.nav-link:hover { background: rgba(255, 255, 255, 0.03); color: #f1f5f9; }
.nav-link.active { background: rgba(99, 102, 241, 0.1); color: #818cf8; font-weight: 600; }

.nav-icon { width: 24px; display: flex; justify-content: center; margin-right: 10px; font-size: 1rem; }
.arrow { margin-left: auto; font-size: 0.7rem; transition: transform 0.2s; }
.arrow.rotate { transform: rotate(90deg); }

.submenu { list-style: none; padding: 4px 0 4px 34px; }
.submenu a { display: block; padding: 6px 0; color: #64748b; text-decoration: none; font-size: 0.8rem; transition: color 0.2s; }
.submenu a:hover, .active-child { color: #818cf8 !important; }

.sidebar-footer { padding: 16px; border-top: 1px solid #1e293b; display: flex; align-items: center; justify-content: space-between; }
.user-pill { display: flex; align-items: center; gap: 10px; }
.avatar { width: 30px; height: 30px; background: #334155; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #818cf8; font-size: 0.8rem; }
.user-info { display: flex; flex-direction: column; line-height: 1.2; }
.u-name { font-size: 0.75rem; font-weight: 600; }
.u-role { font-size: 0.6rem; color: #64748b; }
.btn-logout { background: none; border: none; color: #64748b; cursor: pointer; }
.btn-logout:hover { color: #ef4444; }

.sidebar-nav::-webkit-scrollbar { width: 4px; }
.sidebar-nav::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
</style>
<template>
  <aside 
    class="bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 h-screen fixed left-0 top-0 z-40 transition-all duration-300 ease-in-out flex flex-col shadow-sm"
    :class="[isCollapsed ? 'w-20' : 'w-64']"
  >
    <div class="h-16 flex items-center justify-between px-4 border-b border-slate-100 dark:border-slate-800">
      <div v-show="!isCollapsed" class="flex items-center gap-2 overflow-hidden whitespace-nowrap transition-opacity duration-300">
        <div class="bg-gradient-to-tr from-primary-600 to-primary-500 p-1.5 rounded-lg shadow-sm">
          <div class="i-lucide-sparkles text-white text-lg"></div>
        </div>
        <span class="font-bold text-xl text-slate-800 dark:text-slate-100 tracking-tight">
          Imob<span class="text-primary-600">Home</span>
        </span>
      </div>
      
      <button 
        @click="toggleCollapse"
        class="btn-icon ml-auto hidden lg:flex"
        :title="isCollapsed ? 'Expandir' : 'Recolher'"
      >
        <div :class="isCollapsed ? 'i-lucide-chevron-right' : 'i-lucide-chevron-left'" class="text-lg"></div>
      </button>
    </div>

    <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-700">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path"
        :to="item.path"
        class="nav-item group"
        active-class="nav-item-active"
        :class="[!$route.path.startsWith(item.path) && 'nav-item-inactive']"
      >
        <div class="flex-shrink-0 flex items-center justify-center transition-colors">
          <div :class="[item.icon, 'text-xl']"></div>
        </div>

        <span 
          v-show="!isCollapsed"
          class="whitespace-nowrap truncate transition-opacity duration-200"
        >
          {{ item.title }}
        </span>

        <div 
          v-if="isCollapsed"
          class="absolute left-16 bg-slate-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 whitespace-nowrap shadow-lg ml-2"
        >
          {{ item.title }}
        </div>
      </router-link>
    </nav>

    <div class="p-3 border-t border-slate-100 dark:border-slate-800">
      <div 
        class="flex items-center gap-3 p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors group"
        @click="handleLogout"
      >
        <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex-center overflow-hidden shrink-0 border border-slate-300 dark:border-slate-600">
          <div class="i-lucide-user text-slate-500 dark:text-slate-400"></div>
        </div>
        
        <div v-show="!isCollapsed" class="flex-1 overflow-hidden">
          <p class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">Admin User</p>
          <p class="text-xs text-slate-500 dark:text-slate-400 truncate">Sair do sistema</p>
        </div>

        <div v-show="!isCollapsed" class="i-lucide-log-out text-slate-400 group-hover:text-red-500 transition-colors"></div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Definição de Tipos para o Menu
interface MenuItem {
  title: string;
  icon: string; // String para classes do UnoCSS (ex: i-lucide-home)
  path: string;
  domain: 'ia' | 'clientes' | 'imoveis' | 'financeiro' | 'vistorias' | 'config';
}

const router = useRouter();
const authStore = useAuthStore();
const isCollapsed = ref(false);

const menuItems: MenuItem[] = [
  { title: 'Dashboard', icon: 'i-lucide-layout-dashboard', path: '/dashboard', domain: 'ia' },
  { title: 'CRM / Funil', icon: 'i-lucide-users', path: '/clientes', domain: 'clientes' },
  { title: 'Catálogo', icon: 'i-lucide-home', path: '/imoveis', domain: 'imoveis' },
  { title: 'Contratos', icon: 'i-lucide-file-text', path: '/contratos', domain: 'imoveis' },
  { title: 'Vistorias', icon: 'i-lucide-clipboard-check', path: '/vistorias', domain: 'vistorias' },
  { title: 'Publicações', icon: 'i-lucide-share-2', path: '/publicacoes', domain: 'ia' },
  { title: 'Financeiro', icon: 'i-lucide-dollar-sign', path: '/financeiro', domain: 'financeiro' },
  { title: 'Configurações', icon: 'i-lucide-settings', path: '/configuracoes', domain: 'config' },
];

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value;
}

function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>

<style scoped>
/* Transição suave para largura */
aside {
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
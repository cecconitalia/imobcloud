<template>
  <aside 
    class="bg-white border-r border-slate-200 h-screen fixed left-0 top-0 z-40 transition-all duration-300 flex flex-col shadow-sm"
    :class="[isCollapsed ? 'w-20' : 'w-64']"
  >
    <div class="h-16 flex items-center justify-between px-4 border-b border-slate-100">
      <div v-show="!isCollapsed" class="flex items-center gap-2 overflow-hidden">
        <div class="bg-blue-600 p-1.5 rounded-lg">
          <Sparkles class="w-5 h-5 text-white" />
        </div>
        <span class="font-bold text-xl text-slate-800 tracking-tight">ImobHome</span>
      </div>
      
      <button 
        @click="toggleSidebar"
        class="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 transition-colors"
      >
        <ChevronRight v-if="isCollapsed" class="w-5 h-5" />
        <ChevronLeft v-else class="w-5 h-5" />
      </button>
    </div>

    <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1 custom-scrollbar">
      <template v-for="item in menuItems" :key="item.path">
        <router-link 
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative"
          :class="[
            route.path === item.path 
              ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' 
              : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
          ]"
        >
          <component 
            :is="item.icon" 
            class="w-5 h-5 flex-shrink-0 transition-colors duration-200"
            :class="[route.path === item.path ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600']"
          />
          
          <span v-show="!isCollapsed" class="whitespace-nowrap origin-left">
            {{ item.title }}
          </span>

          <div 
            v-if="isCollapsed"
            class="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 whitespace-nowrap"
          >
            {{ item.title }}
          </div>
        </router-link>
      </template>
    </nav>

    <div class="p-3 border-t border-slate-100 bg-slate-50/50">
      <div class="flex items-center gap-3 p-2 rounded-xl transition-colors hover:bg-white hover:shadow-sm border border-transparent hover:border-slate-100">
        <div class="w-9 h-9 rounded-full bg-slate-200 border-2 border-white shadow-sm ring-1 ring-slate-700 flex-shrink-0 flex items-center justify-center">
          <Users class="w-5 h-5 text-slate-500" />
        </div>
        
        <div v-show="!isCollapsed" class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-slate-700 dark:text-slate-200 truncate">
            {{ authStore.user?.username || 'Consultor' }}
          </p>
          <p class="text-xs text-slate-500 truncate">
            Imobiliária Parceira
          </p>
        </div>

        <button 
          v-show="!isCollapsed"
          @click="handleLogout"
          class="p-2 text-slate-400 hover:text-red-500 transition-colors active:scale-90"
          title="Sair do sistema"
        >
          <LogOut class="w-5 h-5" />
        </button>
      </div>
      
      <button 
        v-if="isCollapsed"
        @click="handleLogout"
        class="mt-4 w-full flex justify-center text-slate-400 hover:text-red-500"
        title="Sair"
      >
        <LogOut class="w-6 h-6" />
      </button>
    </div>
  </aside>

  <div 
    v-if="!isCollapsed" 
    class="fixed inset-0 bg-black/20 z-30 lg:hidden glass-effect"
    @click="isCollapsed = true"
  ></div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router'; // Importe useRouter
import { 
  LayoutDashboard, 
  Users, 
  Home, 
  DollarSign, 
  FileText, 
  ClipboardCheck, 
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Sparkles
} from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';

/**
 * Interface estrita para itens de menu do ImobHome
 */
interface MenuItem {
  title: string;
  icon: any;
  path: string;
  domain: 'clientes' | 'imoveis' | 'financeiro' | 'boletos' | 'vistorias' | 'ia' | 'config';
}

const route = useRoute();
const router = useRouter(); // Instancie o roteador
const authStore = useAuthStore();

// Estado de colapso do menu (Mobile-first e responsivo)
const isCollapsed = ref(false);

/**
 * Mapeamento do Domínio Funcional conforme Protocolo ImobHome
 */
const menuItems: MenuItem[] = [
  { title: 'Dashboard', icon: LayoutDashboard, path: '/dashboard', domain: 'ia' },
  { title: 'CRM / Funil', icon: Users, path: '/clientes', domain: 'clientes' },
  { title: 'Catálogo', icon: Home, path: '/imoveis', domain: 'imoveis' },
  { title: 'Contratos', icon: FileText, path: '/contratos', domain: 'imoveis' }, // Ajustado domínio
  { title: 'Vistorias', icon: ClipboardCheck, path: '/vistorias', domain: 'vistorias' },
  { title: 'Financeiro', icon: DollarSign, path: '/financeiro', domain: 'financeiro' },
  { title: 'Configurações', icon: Settings, path: '/configuracoes', domain: 'config' },
];

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value;
}

// Função de logout corrigida com redirecionamento
function handleLogout() {
  authStore.logout();
  router.push('/login'); // Redireciona explicitamente para o login
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
.glass-effect {
  backdrop-filter: blur(2px);
}
</style>
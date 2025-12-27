<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
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
 * Interface estrita para itens de menu do ImobCloud
 */
interface MenuItem {
  title: string;
  icon: any;
  path: string;
  domain: 'clientes' | 'imoveis' | 'financeiro' | 'boletos' | 'vistorias' | 'ia' | 'config';
}

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

// Estado de colapso do menu (Mobile-first e responsivo)
const isCollapsed = ref(false);

/**
 * Mapeamento do Domínio Funcional conforme Protocolo ImobCloud
 */
const menuItems: MenuItem[] = [
  { title: 'Dashboard', icon: LayoutDashboard, path: '/dashboard', domain: 'ia' },
  { title: 'CRM / Funil', icon: Users, path: '/clientes', domain: 'clientes' },
  { title: 'Catálogo', icon: Home, path: '/imoveis', domain: 'imoveis' },
  { title: 'Financeiro / DRE', icon: DollarSign, path: '/financeiro', domain: 'financeiro' },
  { title: 'Boletos Bradesco', icon: FileText, path: '/boletos', domain: 'boletos' },
  { title: 'Vistorias / Laudos', icon: ClipboardCheck, path: '/vistorias', domain: 'vistorias' },
  { title: 'IA Generativa', icon: Sparkles, path: '/publicacoes', domain: 'ia' },
  { title: 'Configurações', icon: Settings, path: '/configuracoes', domain: 'config' },
];

/**
 * Validação de rota ativa
 */
const isActive = (path: string): boolean => {
  return route.path.startsWith(path);
};

/**
 * Protocolo de Navegação
 */
const navigateTo = (path: string): void => {
  router.push(path);
};

/**
 * Logout Seguro
 */
const handleLogout = async (): Promise<void> => {
  try {
    await authStore.logout();
    router.push('/login');
  } catch (error) {
    console.error('Falha ao deslogar:', error);
  }
};

/**
 * NOTA TÉCNICA: A funcionalidade "Fixar Menu" (isPinned) foi removida 
 * para simplificar a experiência do usuário e otimizar o espaço em tela 
 * seguindo a abordagem mobile-first real.
 */
const toggleSidebar = (): void => {
  isCollapsed.value = !isCollapsed.value;
};
</script>

<template>
  <aside
    :class="[
      'fixed top-0 left-0 z-50 h-screen transition-all duration-300 ease-in-out bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col',
      isCollapsed ? 'w-20' : 'w-64'
    ]"
  >
    <div class="flex items-center h-16 px-4 border-b border-slate-100 dark:border-slate-800">
      <div class="flex items-center gap-3 overflow-hidden">
        <div class="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-lg">I</span>
        </div>
        <span 
          v-show="!isCollapsed" 
          class="font-bold text-xl tracking-tight text-slate-800 dark:text-white transition-opacity duration-200"
        >
          ImobCloud
        </span>
      </div>
      
      <button
        @click="toggleSidebar"
        class="hidden md:flex ml-auto p-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-500 hover:text-blue-600 active:scale-95 transition-all"
        aria-label="Toggle Sidebar"
      >
        <component :is="isCollapsed ? ChevronRight : ChevronLeft" class="w-5 h-5" />
      </button>
    </div>

    <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
      <button
        v-for="item in menuItems"
        :key="item.path"
        @click="navigateTo(item.path)"
        :class="[
          'flex items-center w-full p-3 rounded-xl transition-all group active:scale-95 relative',
          isActive(item.path) 
            ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium' 
            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
        ]"
      >
        <component 
          :is="item.icon" 
          :class="[
            'flex-shrink-0 w-6 h-6 transition-colors',
            isActive(item.path) ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'
          ]"
        />
        
        <span 
          v-show="!isCollapsed" 
          class="ml-3 whitespace-nowrap overflow-hidden text-sm"
        >
          {{ item.title }}
        </span>

        <div 
          v-if="isActive(item.path)"
          class="absolute left-0 w-1 h-6 bg-blue-600 rounded-r-full"
        ></div>

        <div 
          v-if="isCollapsed"
          class="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-[60]"
        >
          {{ item.title }}
        </div>
      </button>
    </nav>

    <div class="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
      <div 
        :class="[
          'flex items-center gap-3 overflow-hidden transition-all',
          isCollapsed ? 'justify-center' : ''
        ]"
      >
        <div class="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex-shrink-0 flex items-center justify-center">
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
        >
          <LogOut class="w-5 h-5" />
        </button>
      </div>
      
      <button 
        v-if="isCollapsed"
        @click="handleLogout"
        class="mt-4 w-full flex justify-center text-slate-400 hover:text-red-500"
      >
        <LogOut class="w-6 h-6" />
      </button>
    </div>
  </aside>

  <div 
    v-if="!isCollapsed" 
    class="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden"
    @click="isCollapsed = true"
  ></div>
</template>

<style scoped>
/* Estilização da barra de rolagem para o nav */
nav::-webkit-scrollbar {
  width: 4px;
}
nav::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 10px;
}
nav:hover::-webkit-scrollbar-thumb {
  background: #e2e8f0;
}
.dark nav:hover::-webkit-scrollbar-thumb {
  background: #334155;
}
</style>
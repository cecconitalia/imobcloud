<template>
  <div class="space-y-6">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Configurações do Sistema</h1>
        <p class="text-slate-500">Gerencie as variáveis globais de ambiente (Email, Integrações, URLs).</p>
      </div>
      <div class="flex gap-3">
        <button 
          @click="saveConfig" 
          :disabled="loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <div v-if="!loading" class="i-fas-save w-4 h-4"></div>
          <div v-else class="i-fas-spinner animate-spin w-4 h-4"></div>
          {{ loading ? 'Salvando...' : 'Salvar Alterações' }}
        </button>
      </div>
    </header>

    <div v-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
      <div class="i-fas-exclamation-triangle w-5 h-5"></div>
      {{ error }}
    </div>

    <div class="flex space-x-1 border-b border-slate-200 mb-6">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        class="px-4 py-2 text-sm font-medium transition-colors relative cursor-pointer"
        :class="currentTab === tab.id ? 'text-blue-600' : 'text-slate-500 hover:text-slate-700'"
      >
        {{ tab.label }}
        <div 
          v-if="currentTab === tab.id" 
          class="absolute bottom-0 left-0 w-full h-0.5 bg-blue-600"
        ></div>
      </button>
    </div>

    <div v-if="loadingData" class="flex justify-center py-12">
      <div class="i-fas-spinner w-8 h-8 text-blue-600 animate-spin"></div>
    </div>

    <form v-else class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 space-y-6">
      
      <div v-show="currentTab === 'geral'" class="space-y-4">
        <h3 class="text-lg font-semibold text-slate-800 border-b pb-2">URLs e Manutenção</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">URL do Sistema</label>
            <input v-model="form.site_url" type="text" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="https://imobhome.com.br" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">URL Pública Base</label>
            <input v-model="form.base_public_url" type="text" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="https://imobhome.com.br" />
          </div>
        </div>

        <div class="flex items-center gap-3 bg-yellow-50 p-4 rounded-lg border border-yellow-100 mt-4">
          <input v-model="form.modo_manutencao" type="checkbox" id="manutencao" class="w-5 h-5 text-blue-600 rounded focus:ring-blue-500 cursor-pointer" />
          <div>
            <label for="manutencao" class="font-medium text-slate-800 cursor-pointer">Ativar Modo Manutenção</label>
            <p class="text-xs text-slate-500">Se ativo, apenas Superusuários conseguirão acessar o sistema.</p>
          </div>
        </div>
      </div>

      <div v-show="currentTab === 'email'" class="space-y-4">
        <h3 class="text-lg font-semibold text-slate-800 border-b pb-2">Configurações de E-mail (SMTP)</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Host SMTP</label>
            <input v-model="form.email_host" type="text" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="smtp.gmail.com" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Porta SMTP</label>
            <input v-model.number="form.email_port" type="number" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="587" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Usuário (E-mail)</label>
            <input v-model="form.email_host_user" type="email" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Senha (App Password)</label>
            <input v-model="form.email_host_password" type="password" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-slate-700 mb-1">Remetente Padrão</label>
            <input v-model="form.default_from_email" type="text" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Nome <email@dominio.com>" />
          </div>
        </div>
      </div>

      <div v-show="currentTab === 'integracoes'" class="space-y-4">
        <h3 class="text-lg font-semibold text-slate-800 border-b pb-2">Google & IA</h3>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Google API Key (Maps/Gemini Global)</label>
          <input v-model="form.google_api_key" type="password" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          <p class="text-xs text-slate-500 mt-1">Usada como fallback se a imobiliária não tiver sua própria chave.</p>
        </div>

        <h3 class="text-lg font-semibold text-slate-800 border-b pb-2 pt-4">Cloudinary (Uploads)</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Cloud Name</label>
            <input v-model="form.cloudinary_cloud_name" type="text" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">API Key</label>
            <input v-model="form.cloudinary_api_key" type="text" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">API Secret</label>
            <input v-model="form.cloudinary_api_secret" type="password" class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();

const currentTab = ref('geral');
const tabs = [
  { id: 'geral', label: 'Geral' },
  { id: 'email', label: 'E-mail' },
  { id: 'integracoes', label: 'Integrações' },
];

const loading = ref(false);
const loadingData = ref(true);
const error = ref('');

const form = ref({
  site_url: '',
  base_public_url: '',
  email_host: '',
  email_port: 587,
  email_host_user: '',
  email_host_password: '',
  default_from_email: '',
  google_api_key: '',
  cloudinary_cloud_name: '',
  cloudinary_api_key: '',
  cloudinary_api_secret: '',
  modo_manutencao: false
});

onMounted(async () => {
  // REMOVIDA A VERIFICAÇÃO DE SUPERADMIN QUE CAUSAVA O REDIRECT
  await fetchConfig();
});

async function fetchConfig() {
  try {
    loadingData.value = true;
    const response = await api.get('/v1/core/configuracao-global/');
    if (response.data) {
        form.value = { ...form.value, ...response.data };
    }
  } catch (err: any) {
    console.error(err);
    // Se der 403 (proibido), aí sim avisamos, mas não redirecionamos forçado
    if (err.response?.status === 403) {
        error.value = "Você não tem permissão para visualizar estas configurações.";
    } else {
        error.value = "Erro ao carregar configurações.";
    }
  } finally {
    loadingData.value = false;
  }
}

async function saveConfig() {
  try {
    loading.value = true;
    error.value = '';
    await api.put('/v1/core/configuracao-global/', form.value);
    alert('Configurações salvas com sucesso!');
  } catch (err: any) {
    console.error(err);
    error.value = "Erro ao salvar configurações.";
  } finally {
    loading.value = false;
  }
}
</script>
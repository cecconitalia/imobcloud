<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue';
import api from '../services/api';
import Swal from 'sweetalert2';

// --- INTERFACES & ESTADO ---
interface Imobiliaria {
  id: string;
  nome_fantasia: string;
  razao_social: string;
  cnpj: string;
  creci: string;
  tipo_pessoa: string;
  logo: string | null;
  cor_primaria: string;
  voz_da_marca_preferida: string;
  email_contato: string;
  telefone: string;
  telefone_celular: string;
  whatsapp: string;
  website: string;
  cep: string;
  logradouro: string;
  numero: string;
  complemento: string;
  bairro: string;
  cidade: string;
  estado: string;
  responsavel_nome: string;
  responsavel_cpf: string;
  responsavel_email: string;
  responsavel_telefone: string;
  facebook: string;
  instagram: string;
  linkedin: string;
  facebook_page_access_token: string;
  facebook_user_access_token: string;
  instagram_business_account_id: string;
  google_gemini_api_key: string;
}

const imobiliaria = reactive<Imobiliaria>({
  id: '',
  nome_fantasia: '', razao_social: '', cnpj: '', creci: '', tipo_pessoa: 'PJ',
  logo: null, cor_primaria: '#3b82f6', voz_da_marca_preferida: 'formal',
  email_contato: '', telefone: '', telefone_celular: '', whatsapp: '', website: '',
  cep: '', logradouro: '', numero: '', complemento: '', bairro: '', cidade: '', estado: '',
  responsavel_nome: '', responsavel_cpf: '', responsavel_email: '', responsavel_telefone: '',
  facebook: '', instagram: '', linkedin: '',
  facebook_page_access_token: '', facebook_user_access_token: '',
  instagram_business_account_id: '', google_gemini_api_key: ''
});

const activeTab = ref('geral');
const loading = ref(false);
const saving = ref(false);
const searchingCep = ref(false);
const logoFile = ref<File | null>(null);
const logoPreview = ref<string | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

const tabs = [
  { id: 'geral', label: 'Geral & Identidade', icon: 'i-mdi-domain' },
  { id: 'contato', label: 'Endereço & Contato', icon: 'i-mdi-map-marker' },
  { id: 'config', label: 'Integrações & IA', icon: 'i-mdi-cogs' },
];

const voiceOptions = [
  { value: 'formal', label: 'Formal', desc: 'Sério e jurídico.', icon: 'i-mdi-briefcase' },
  { value: 'casual', label: 'Casual', desc: 'Leve e amigável.', icon: 'i-mdi-emoticon-happy' },
  { value: 'entusiasta', label: 'Vibrante', desc: 'Alta energia.', icon: 'i-mdi-rocket' },
  { value: 'luxuoso', label: 'Luxuoso', desc: 'Sofisticado.', icon: 'i-mdi-diamond' },
];

// --- MÁSCARAS ---
const maskCnpj = (v: string) => v.replace(/\D/g, '').substring(0, 14).replace(/^(\d{2})(\d)/, '$1.$2').replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3').replace(/\.(\d{3})(\d)/, '.$1/$2').replace(/(\d{4})(\d)/, '$1-$2');
const maskCpf = (v: string) => v.replace(/\D/g, '').substring(0, 11).replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d{1,2})$/, '$1-$2');
const maskPhone = (v: string) => { let r = v.replace(/\D/g, "").substring(0, 11); return r.length > 10 ? r.replace(/^(\d{2})(\d{5})(\d{4})/, '($1) $2-$3') : r.replace(/^(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3'); };
const maskCep = (v: string) => v.replace(/\D/g, '').substring(0, 8).replace(/^(\d{5})(\d)/, '$1-$2');

watch(() => imobiliaria.cnpj, (v) => { if(v) imobiliaria.cnpj = maskCnpj(v) });
watch(() => imobiliaria.responsavel_cpf, (v) => { if(v) imobiliaria.responsavel_cpf = maskCpf(v) });
watch(() => imobiliaria.telefone, (v) => { if(v) imobiliaria.telefone = maskPhone(v) });
watch(() => imobiliaria.whatsapp, (v) => { if(v) imobiliaria.whatsapp = maskPhone(v) });
watch(() => imobiliaria.cep, (v) => { if(v) imobiliaria.cep = maskCep(v) });

// --- LÓGICA ---
onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await api.get('/v1/core/imobiliarias/me/');
    Object.assign(imobiliaria, data);
    if (imobiliaria.logo) logoPreview.value = imobiliaria.logo;
    if (!imobiliaria.cor_primaria) imobiliaria.cor_primaria = '#3b82f6';
  } catch (error) {
    console.error(error);
    Swal.fire('Erro', 'Não foi possível carregar os dados.', 'error');
  } finally {
    loading.value = false;
  }
});

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files?.[0]) {
    const file = target.files[0];
    if (file.size > 2 * 1024 * 1024) return Swal.fire('Erro', 'Imagem muito grande (Max 2MB).', 'warning');
    logoFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => logoPreview.value = e.target?.result as string;
    reader.readAsDataURL(file);
  }
};

const buscarCep = async () => {
  const cepLimpo = imobiliaria.cep.replace(/\D/g, '');
  if (cepLimpo.length !== 8) return;
  searchingCep.value = true;
  try {
    const res = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`);
    const data = await res.json();
    if (!data.erro) {
      imobiliaria.logradouro = data.logradouro;
      imobiliaria.bairro = data.bairro;
      imobiliaria.cidade = data.localidade;
      imobiliaria.estado = data.uf;
    }
  } finally {
    searchingCep.value = false;
  }
};

const salvar = async () => {
  saving.value = true;
  try {
    await api.patch('/v1/core/imobiliarias/me/', { ...imobiliaria, logo: undefined });
    if (logoFile.value) {
      const fd = new FormData();
      fd.append('logo', logoFile.value);
      await api.patch('/v1/core/imobiliarias/me/', fd, { headers: { 'Content-Type': 'multipart/form-data' }});
    }
    Swal.fire({ icon: 'success', title: 'Salvo!', text: 'Dados da empresa atualizados.', timer: 1500, showConfirmButton: false });
  } catch (e) {
    Swal.fire('Erro', 'Falha ao salvar alterações.', 'error');
  } finally {
    saving.value = false;
  }
};

const headerPreviewStyle = computed(() => ({
  backgroundColor: imobiliaria.cor_primaria,
  color: getContrastYIQ(imobiliaria.cor_primaria)
}));

function getContrastYIQ(hex: string){
  if (!hex) return 'black';
  hex = hex.replace("#", "");
  const r = parseInt(hex.substr(0,2),16), g = parseInt(hex.substr(2,2),16), b = parseInt(hex.substr(4,2),16);
  return (((r*299)+(g*587)+(b*114))/1000) >= 128 ? 'black' : 'white';
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300 p-4 md:p-8">
    
    <div class="max-w-6xl mx-auto mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 animate-fade-in-down">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-white dark:bg-gray-800 flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700 text-primary-600">
            <i class="i-mdi-cog text-xl" />
          </div>
          Configurações do Sistema
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 ml-14">Personalize a identidade e os recursos da sua empresa.</p>
      </div>

      <button 
        @click="salvar" 
        :disabled="saving || loading"
        class="flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-600/20 transition-all duration-200 active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
      >
        <i v-if="saving" class="i-mdi-loading animate-spin text-lg" />
        <i v-else class="i-mdi-content-save-check text-lg" />
        <span>{{ saving ? 'Salvando...' : 'Salvar Alterações' }}</span>
      </button>
    </div>

    <div class="max-w-6xl mx-auto mb-6">
      <div class="inline-flex p-1 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 gap-1">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          class="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="activeTab === tab.id 
            ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 ring-1 ring-primary-200 dark:ring-primary-700' 
            : 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'"
        >
          <i :class="tab.icon" class="text-lg" />
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="max-w-6xl mx-auto h-96 bg-gray-200 dark:bg-gray-800 rounded-2xl animate-pulse"></div>

    <div v-else class="max-w-6xl mx-auto animate-fade-in-up">
      
      <div v-show="activeTab === 'geral'" class="space-y-6">
        
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2 mb-6 border-b border-gray-100 dark:border-gray-700 pb-2">
            <span class="p-1.5 rounded-lg bg-blue-50 text-blue-600"><i class="i-mdi-palette" /></span>
            <h2 class="text-lg font-bold text-gray-800 dark:text-white">Identidade Visual</h2>
          </div>

          <div class="flex flex-col md:flex-row gap-8 items-start">
            <div class="flex-shrink-0 flex flex-col items-center gap-3">
              <div 
                class="relative group w-32 h-32 rounded-2xl border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/10 transition-all cursor-pointer flex items-center justify-center overflow-hidden bg-gray-50 dark:bg-gray-900"
                @click="fileInput?.click()"
              >
                <img v-if="logoPreview" :src="logoPreview" class="w-full h-full object-contain p-2" />
                <div v-else class="flex flex-col items-center text-gray-400">
                  <i class="i-mdi-image-plus text-3xl mb-1" />
                  <span class="text-[10px] uppercase font-bold">Logo</span>
                </div>
                <div class="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <i class="i-mdi-pencil text-white text-2xl" />
                </div>
              </div>
              <input ref="fileInput" type="file" class="hidden" accept="image/*" @change="handleFileUpload" />
              <p class="text-xs text-gray-400 text-center w-32">PNG/JPG até 2MB</p>
            </div>

            <div class="flex-1 w-full space-y-5">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div>
                  <label class="label-std">Cor do Sistema</label>
                  <div class="flex items-center gap-3 p-1.5 border border-gray-200 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-900">
                    <input type="color" v-model="imobiliaria.cor_primaria" class="w-10 h-10 rounded-lg cursor-pointer border-0 p-0" />
                    <input type="text" v-model="imobiliaria.cor_primaria" class="bg-transparent uppercase font-mono text-sm outline-none w-full" maxlength="7" />
                  </div>
                </div>
                <div>
                  <label class="label-std">Preview do Topo</label>
                  <div class="h-[54px] rounded-xl shadow-inner flex items-center px-4 gap-3 transition-colors" :style="headerPreviewStyle">
                    <div class="w-8 h-8 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center">
                      <i class="i-mdi-domain text-current" />
                    </div>
                    <span class="font-bold text-sm tracking-wide">{{ imobiliaria.nome_fantasia || 'Nome da Empresa' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2 mb-6 border-b border-gray-100 dark:border-gray-700 pb-2">
            <span class="p-1.5 rounded-lg bg-emerald-50 text-emerald-600"><i class="i-mdi-card-account-details" /></span>
            <h2 class="text-lg font-bold text-gray-800 dark:text-white">Dados da Empresa</h2>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2">
              <label class="label-std">Nome Fantasia <span class="text-red-500">*</span></label>
              <div class="relative">
                <input v-model="imobiliaria.nome_fantasia" type="text" class="input-std pl-10" placeholder="Nome comercial da imobiliária" />
                <i class="i-mdi-store absolute left-3 top-3 text-gray-400 text-lg" />
              </div>
            </div>
            <div>
              <label class="label-std">Razão Social</label>
              <input v-model="imobiliaria.razao_social" type="text" class="input-std" placeholder="Razão Social Ltda" />
            </div>
            <div>
              <label class="label-std">CNPJ</label>
              <input v-model="imobiliaria.cnpj" type="text" class="input-std" placeholder="00.000.000/0000-00" maxlength="18" />
            </div>
            <div>
              <label class="label-std">CRECI Jurídico</label>
              <input v-model="imobiliaria.creci" type="text" class="input-std" placeholder="J-12345" />
            </div>
            <div>
              <label class="label-std">Responsável Legal (Nome)</label>
              <input v-model="imobiliaria.responsavel_nome" type="text" class="input-std" />
            </div>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'contato'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-bold text-gray-800 dark:text-white mb-6">Canais de Contato</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-1">
              <label class="label-std">Email Oficial</label>
              <div class="relative">
                <input v-model="imobiliaria.email_contato" type="email" class="input-std pl-10" />
                <i class="i-mdi-email absolute left-3 top-3 text-gray-400" />
              </div>
            </div>
            <div>
              <label class="label-std">Telefone Fixo</label>
              <input v-model="imobiliaria.telefone" type="tel" class="input-std" />
            </div>
            <div>
              <label class="label-std">WhatsApp</label>
              <input v-model="imobiliaria.whatsapp" type="tel" class="input-std" />
            </div>
            <div class="md:col-span-3">
              <label class="label-std">Website</label>
              <div class="relative">
                <input v-model="imobiliaria.website" type="url" class="input-std pl-10" placeholder="https://" />
                <i class="i-mdi-web absolute left-3 top-3 text-gray-400" />
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-bold text-gray-800 dark:text-white">Endereço</h2>
            <div v-if="searchingCep" class="text-xs text-primary-600 flex items-center gap-1 animate-pulse">
              <i class="i-mdi-loading animate-spin" /> Buscando...
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div class="md:col-span-1">
              <label class="label-std">CEP</label>
              <div class="relative">
                <input v-model="imobiliaria.cep" @blur="buscarCep" type="text" class="input-std pl-10" placeholder="00000-000" maxlength="9" />
                <i class="i-mdi-magnify absolute left-3 top-3 text-gray-400" />
              </div>
            </div>
            <div class="md:col-span-2">
              <label class="label-std">Logradouro</label>
              <input v-model="imobiliaria.logradouro" type="text" class="input-std" />
            </div>
            <div class="md:col-span-1">
              <label class="label-std">Número</label>
              <input v-model="imobiliaria.numero" type="text" class="input-std" />
            </div>
            <div class="md:col-span-2">
              <label class="label-std">Complemento</label>
              <input v-model="imobiliaria.complemento" type="text" class="input-std" />
            </div>
            <div class="md:col-span-1">
              <label class="label-std">Bairro</label>
              <input v-model="imobiliaria.bairro" type="text" class="input-std" />
            </div>
            <div class="md:col-span-1">
              <label class="label-std">Cidade/UF</label>
              <div class="flex gap-2">
                <input v-model="imobiliaria.cidade" type="text" class="input-std flex-1" />
                <input v-model="imobiliaria.estado" type="text" class="input-std w-14 text-center uppercase" maxlength="2" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'config'" class="space-y-6">
        
        <div class="bg-gradient-to-br from-purple-50 to-white dark:from-gray-800 dark:to-gray-800/50 rounded-2xl p-6 shadow-sm border border-purple-100 dark:border-gray-700">
          <h2 class="text-lg font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
            <i class="i-mdi-robot text-purple-600" /> Inteligência Artificial
          </h2>
          
          <div class="grid grid-cols-1 gap-6">
            <div>
              <label class="label-std text-purple-800 dark:text-purple-300">Google Gemini API Key</label>
              <div class="relative">
                <input v-model="imobiliaria.google_gemini_api_key" type="password" class="input-std pl-10 border-purple-200 focus:border-purple-500 focus:ring-purple-500/20" placeholder="sk-..." />
                <i class="i-mdi-key absolute left-3 top-3 text-purple-400" />
              </div>
              <p class="text-xs text-gray-500 mt-1">Necessário para descrições automáticas e chatbot.</p>
            </div>

            <div>
              <label class="label-std mb-2 block">Tom de Voz da IA</label>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div 
                  v-for="opt in voiceOptions" :key="opt.value"
                  @click="imobiliaria.voz_da_marca_preferida = opt.value"
                  class="border rounded-xl p-3 cursor-pointer transition-all hover:shadow-md text-center bg-white dark:bg-gray-800"
                  :class="imobiliaria.voz_da_marca_preferida === opt.value 
                    ? 'border-purple-500 ring-1 ring-purple-500 text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-900/20' 
                    : 'border-gray-200 dark:border-gray-700'"
                >
                  <i :class="opt.icon + ' text-2xl mb-1'" />
                  <div class="text-xs font-bold">{{ opt.label }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-bold text-gray-800 dark:text-white mb-6">Integrações Sociais</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="label-std">Facebook Page Token</label>
              <input v-model="imobiliaria.facebook_page_access_token" type="password" class="input-std" />
            </div>
            <div>
              <label class="label-std">Instagram Business ID</label>
              <input v-model="imobiliaria.instagram_business_account_id" type="text" class="input-std" />
            </div>
            <div>
              <label class="label-std">Link Facebook</label>
              <input v-model="imobiliaria.facebook" type="url" class="input-std" placeholder="facebook.com/..." />
            </div>
            <div>
              <label class="label-std">Link Instagram</label>
              <input v-model="imobiliaria.instagram" type="url" class="input-std" placeholder="instagram.com/..." />
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ESTILO DOS INPUTS - Estilo "Edit Form" Moderno */
.label-std {
  @apply block text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1.5 ml-0.5;
}

.input-std {
  @apply w-full rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-800 dark:text-white px-4 py-2.5 text-sm outline-none transition-all placeholder:text-gray-400 shadow-sm;
}

.input-std:focus {
  @apply border-primary-500 ring-2 ring-primary-500/20;
}

.input-std:hover:not(:focus) {
  @apply border-gray-300 dark:border-gray-500;
}

/* ANIMAÇÕES */
.animate-fade-in-up {
  animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.animate-fade-in-down {
  animation: fadeInDown 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
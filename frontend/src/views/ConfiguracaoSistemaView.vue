<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import api from '../services/api';
import Swal from 'sweetalert2';

// --- ESTADO E CONFIGURAÇÃO ---
const loading = ref(false);
const saving = ref(false);
const activeTab = ref('empresa'); // Abas: empresa, contato, juridico, sistema

// --- DADOS DO FORMULÁRIO (Espelho do Serializer Django) ---
const form = reactive({
  // Identificação
  nome_fantasia: '',
  razao_social: '',
  tipo_pessoa: 'PJ',
  cnpj_cpf: '',
  inscricao_estadual: '',
  inscricao_municipal: '',
  data_fundacao: '',
  natureza_juridica: '',
  cnae_principal: '',
  status: 'ATIVA',

  // Contato
  email_contato: '',
  email_financeiro: '',
  email_suporte: '',
  telefone_fixo: '',
  telefone_celular: '',
  whatsapp: '',
  website: '',
  instagram: '',
  facebook: '',
  linkedin: '',

  // Endereço
  cep: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
  pais: 'Brasil',
  latitude: '',
  longitude: '',

  // Responsável Legal
  responsavel_nome: '',
  responsavel_cpf: '',
  responsavel_rg: '',
  responsavel_orgao_emissor: '',
  responsavel_data_nascimento: '',
  responsavel_cargo: '',
  responsavel_email: '',
  responsavel_telefone: '',
  responsavel_whatsapp: '',

  // CRECI e Regulamentação
  creci_numero: '',
  creci_uf: '',
  creci_tipo: 'JURIDICO',
  creci_situacao: 'Ativo',
  creci_validade: '',
  outros_registros: '',

  // Sistema & Configurações
  cor_primaria: '#007bff',
  google_gemini_api_key: '',
  voz_da_marca_preferida: null,
  
  // URLs de arquivos existentes (apenas leitura para mostrar links)
  foto_perfil: null as string | null,
  responsavel_assinatura: null as string | null,
  responsavel_documento: null as string | null,
  creci_documento: null as string | null,
});

// --- CONTROLE DE ARQUIVOS (UPLOADS) ---
const files = reactive({
  foto_perfil: null as File | null,
  responsavel_assinatura: null as File | null,
  responsavel_documento: null as File | null,
  creci_documento: null as File | null,
});

const previewLogo = ref<string | null>(null);

// --- MÉTODOS ---

// 1. Carregar Dados da API
const fetchImobiliaria = async () => {
  loading.value = true;
  try {
    const response = await api.get('v1/core/imobiliarias/me/');
    const data = response.data;

    // Popula o formulário com os dados recebidos
    Object.keys(form).forEach(key => {
      if (data[key] !== undefined && data[key] !== null) {
        // @ts-ignore
        form[key] = data[key];
      }
    });

    // Preview da Logo existente
    if (form.foto_perfil) {
      previewLogo.value = form.foto_perfil;
    }

  } catch (error: any) {
    console.error("Erro ao carregar dados:", error);
    if (error.response && error.response.status === 404) {
      Swal.fire({
        icon: 'info',
        title: 'Bem-vindo!',
        text: 'Preencha os dados abaixo para configurar sua imobiliária.'
      });
    } else {
      Swal.fire('Erro', 'Não foi possível carregar as configurações.', 'error');
    }
  } finally {
    loading.value = false;
  }
};

// 2. Buscar CEP (ViaCEP)
const buscarCep = async () => {
  const cepLimpo = form.cep.replace(/\D/g, '');
  if (cepLimpo.length !== 8) return;

  try {
    const res = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`);
    const data = await res.json();
    if (!data.erro) {
      form.logradouro = data.logradouro;
      form.bairro = data.bairro;
      form.cidade = data.localidade;
      form.estado = data.uf;
      // Focar no número após buscar
      document.getElementById('numero')?.focus();
    } else {
      // Toast de erro discreto
      const Toast = Swal.mixin({ toast: true, position: 'top-end', showConfirmButton: false, timer: 3000 });
      Toast.fire({ icon: 'error', title: 'CEP não encontrado' });
    }
  } catch (e) {
    console.error('Erro CEP', e);
  }
};

// 3. Manipular Upload de Arquivos
const handleFileUpload = (event: Event, fieldName: keyof typeof files) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    files[fieldName] = input.files[0];

    // Se for a logo, atualiza o preview visual
    if (fieldName === 'foto_perfil') {
      previewLogo.value = URL.createObjectURL(input.files[0]);
    }
  }
};

// 4. Salvar Dados (FormData)
const saveImobiliaria = async () => {
  saving.value = true;
  try {
    const formData = new FormData();

    // Adiciona campos de texto
    Object.keys(form).forEach(key => {
      // Ignora campos de URL de arquivo (só enviamos se tiver novo arquivo no 'files')
      if (['foto_perfil', 'responsavel_assinatura', 'responsavel_documento', 'creci_documento'].includes(key)) return;
      
      // @ts-ignore
      const value = form[key];
      if (value !== null && value !== undefined) {
        formData.append(key, value as string);
      }
    });

    // Adiciona arquivos se houver novos uploads
    Object.keys(files).forEach(key => {
      // @ts-ignore
      const file = files[key];
      if (file) {
        formData.append(key, file);
      }
    });

    // Envia para o backend (PATCH para atualização parcial)
    // Se for a primeira vez (404 no load), o backend deve tratar ou usamos POST em outra lógica, 
    // mas o ViewSet 'me' geralmente aceita PUT/PATCH se o user já estiver criado.
    // Se o usuário não tiver imobiliária, o ideal seria o backend criar.
    // *Assumindo que o usuário JÁ FOI vinculado a uma imobiliária (conforme passo anterior)*
    
    await api.patch('v1/core/imobiliarias/me/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    Swal.fire({
      icon: 'success',
      title: 'Sucesso!',
      text: 'Dados da imobiliária atualizados.',
      timer: 2000,
      showConfirmButton: false
    });
    
    // Recarrega para atualizar links de arquivos
    fetchImobiliaria();

  } catch (error) {
    console.error(error);
    Swal.fire('Erro', 'Falha ao salvar as alterações. Verifique os dados.', 'error');
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchImobiliaria();
});
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto">
    
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <i class="i-mdi-domain text-blue-600"></i>
          Configuração da Imobiliária
        </h1>
        <p class="text-gray-500 text-sm mt-1">Gerencie os dados cadastrais, fiscais, responsáveis e aparências do sistema.</p>
      </div>
      
      <button 
        @click="saveImobiliaria" 
        :disabled="saving"
        class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg shadow-sm transition-all flex items-center gap-2 font-medium disabled:opacity-70 disabled:cursor-not-allowed"
      >
        <i v-if="saving" class="i-mdi-loading animate-spin text-lg"></i>
        <i v-else class="i-mdi-content-save text-lg"></i>
        <span>{{ saving ? 'Salvando...' : 'Salvar Alterações' }}</span>
      </button>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20 bg-white rounded-xl shadow-sm">
      <div class="i-mdi-loading animate-spin text-5xl text-blue-600 mb-4"></div>
      <p class="text-gray-500">Carregando informações da empresa...</p>
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      
      <div class="flex overflow-x-auto border-b border-gray-200 bg-gray-50/50">
        <button 
          v-for="tab in [
            { id: 'empresa', label: 'Dados da Empresa', icon: 'i-mdi-office-building' },
            { id: 'contato', label: 'Endereço & Contato', icon: 'i-mdi-map-marker-radius' },
            { id: 'juridico', label: 'Jurídico & Responsável', icon: 'i-mdi-gavel' },
            { id: 'sistema', label: 'Sistema & Integrações', icon: 'i-mdi-cogs' }
          ]" 
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-6 py-4 text-sm font-medium transition-all flex items-center gap-2 border-b-2 whitespace-nowrap hover:bg-white focus:outline-none"
          :class="activeTab === tab.id 
            ? 'border-blue-600 text-blue-700 bg-white' 
            : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          <i :class="tab.icon" class="text-lg"></i>
          {{ tab.label }}
        </button>
      </div>

      <div class="p-6 md:p-8">

        <div v-show="activeTab === 'empresa'" class="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-fade-in">
          
          <div class="lg:col-span-3 flex flex-col items-center space-y-4">
            <div class="relative group">
              <div class="w-48 h-48 rounded-full border-4 border-white shadow-lg bg-gray-100 overflow-hidden flex items-center justify-center">
                <img v-if="previewLogo" :src="previewLogo" class="w-full h-full object-cover" />
                <div v-else class="text-gray-400 flex flex-col items-center">
                  <i class="i-mdi-image-plus text-4xl mb-2"></i>
                  <span class="text-xs">Sem Logo</span>
                </div>
              </div>
              <label class="absolute bottom-2 right-2 bg-blue-600 text-white p-2 rounded-full cursor-pointer shadow-md hover:bg-blue-700 transition-colors" title="Alterar Logo">
                <i class="i-mdi-camera text-lg"></i>
                <input type="file" accept="image/*" class="hidden" @change="(e) => handleFileUpload(e, 'foto_perfil')" />
              </label>
            </div>
            <p class="text-xs text-gray-500 text-center px-4">
              Recomendado: Imagem quadrada (PNG/JPG), máx 2MB. Essa imagem será usada em relatórios e no site.
            </p>
          </div>

          <div class="lg:col-span-9 grid grid-cols-1 md:grid-cols-2 gap-5">
            <div class="col-span-2 md:col-span-1">
              <label class="form-label">Nome Fantasia <span class="text-red-500">*</span></label>
              <input v-model="form.nome_fantasia" type="text" class="form-input" placeholder="Ex: ImobHome Soluções" />
            </div>
            <div class="col-span-2 md:col-span-1">
              <label class="form-label">Razão Social</label>
              <input v-model="form.razao_social" type="text" class="form-input" />
            </div>

            <div class="col-span-1">
              <label class="form-label">Tipo de Pessoa</label>
              <select v-model="form.tipo_pessoa" class="form-select">
                <option value="PJ">Pessoa Jurídica (CNPJ)</option>
                <option value="PF">Pessoa Física (CPF)</option>
              </select>
            </div>
            <div class="col-span-1">
              <label class="form-label">CNPJ / CPF</label>
              <input v-model="form.cnpj_cpf" type="text" class="form-input" placeholder="Apenas números" />
            </div>

            <div class="col-span-1">
              <label class="form-label">Inscrição Estadual</label>
              <input v-model="form.inscricao_estadual" type="text" class="form-input" />
            </div>
            <div class="col-span-1">
              <label class="form-label">Inscrição Municipal</label>
              <input v-model="form.inscricao_municipal" type="text" class="form-input" />
            </div>

            <div class="col-span-1">
              <label class="form-label">Data de Fundação</label>
              <input v-model="form.data_fundacao" type="date" class="form-input" />
            </div>
            <div class="col-span-1">
              <label class="form-label">Status da Empresa</label>
              <select v-model="form.status" class="form-select">
                <option value="ATIVA">Ativa</option>
                <option value="SUSPENSA">Suspensa</option>
                <option value="INATIVA">Inativa</option>
              </select>
            </div>

            <div class="col-span-2">
              <label class="form-label">CNAE Principal</label>
              <input v-model="form.cnae_principal" type="text" class="form-input" placeholder="Código da atividade econômica" />
            </div>
          </div>
        </div>

        <div v-show="activeTab === 'contato'" class="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in">
          
          <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
            <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <i class="i-mdi-map-marker text-blue-600"></i> Endereço Comercial
            </h3>
            
            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-1">
                <label class="form-label">CEP</label>
                <input v-model="form.cep" @blur="buscarCep" type="text" class="form-input" placeholder="00000-000" />
              </div>
              <div class="col-span-2 flex items-end">
                <button type="button" @click="buscarCep" class="text-sm text-blue-600 hover:text-blue-800 font-medium mb-2.5 underline">
                  Buscar CEP
                </button>
              </div>

              <div class="col-span-3">
                <label class="form-label">Logradouro</label>
                <input v-model="form.logradouro" type="text" class="form-input" />
              </div>

              <div class="col-span-1">
                <label class="form-label">Número</label>
                <input v-model="form.numero" id="numero" type="text" class="form-input" />
              </div>
              <div class="col-span-2">
                <label class="form-label">Complemento</label>
                <input v-model="form.complemento" type="text" class="form-input" />
              </div>

              <div class="col-span-1">
                <label class="form-label">Bairro</label>
                <input v-model="form.bairro" type="text" class="form-input" />
              </div>
              <div class="col-span-1">
                <label class="form-label">Cidade</label>
                <input v-model="form.cidade" type="text" class="form-input" />
              </div>
              <div class="col-span-1">
                <label class="form-label">UF</label>
                <input v-model="form.estado" type="text" class="form-input uppercase" maxlength="2" />
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <i class="i-mdi-phone text-green-600"></i> Contatos Principais
              </h3>
              
              <div class="space-y-4">
                <div>
                  <label class="form-label">E-mail Principal</label>
                  <input v-model="form.email_contato" type="email" class="form-input" />
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="form-label">E-mail Financeiro</label>
                    <input v-model="form.email_financeiro" type="email" class="form-input" />
                  </div>
                  <div>
                    <label class="form-label">E-mail Suporte</label>
                    <input v-model="form.email_suporte" type="email" class="form-input" />
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="form-label">Telefone Fixo</label>
                    <input v-model="form.telefone_fixo" type="tel" class="form-input" />
                  </div>
                  <div>
                    <label class="form-label">WhatsApp / Celular</label>
                    <input v-model="form.whatsapp" type="tel" class="form-input" />
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <i class="i-mdi-web text-purple-600"></i> Presença Digital
              </h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="col-span-2">
                  <label class="form-label">Website</label>
                  <input v-model="form.website" type="url" placeholder="https://" class="form-input" />
                </div>
                <div>
                  <label class="form-label">Instagram</label>
                  <div class="flex">
                    <span class="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-100 text-gray-500">@</span>
                    <input v-model="form.instagram" type="text" class="form-input !rounded-l-none" />
                  </div>
                </div>
                <div>
                  <label class="form-label">Facebook</label>
                  <input v-model="form.facebook" type="text" class="form-input" placeholder="URL completa" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-show="activeTab === 'juridico'" class="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in">
          
          <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
            <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <i class="i-mdi-account-tie text-blue-600"></i> Responsável Legal
            </h3>
            
            <div class="grid grid-cols-2 gap-4">
              <div class="col-span-2">
                <label class="form-label">Nome Completo</label>
                <input v-model="form.responsavel_nome" type="text" class="form-input" />
              </div>
              <div>
                <label class="form-label">CPF</label>
                <input v-model="form.responsavel_cpf" type="text" class="form-input" />
              </div>
              <div>
                <label class="form-label">RG</label>
                <input v-model="form.responsavel_rg" type="text" class="form-input" />
              </div>
              <div>
                <label class="form-label">Órgão Emissor</label>
                <input v-model="form.responsavel_orgao_emissor" type="text" class="form-input" />
              </div>
              <div>
                <label class="form-label">Data Nasc.</label>
                <input v-model="form.responsavel_data_nascimento" type="date" class="form-input" />
              </div>
              <div class="col-span-2">
                <label class="form-label">E-mail Pessoal</label>
                <input v-model="form.responsavel_email" type="email" class="form-input" />
              </div>
            </div>

            <div class="mt-6 pt-4 border-t border-gray-200">
              <h4 class="text-sm font-bold text-gray-700 mb-3">Documentos do Responsável</h4>
              
              <div class="grid grid-cols-2 gap-4">
                <div class="col-span-1">
                  <label class="block text-xs font-medium text-gray-700 mb-1">Assinatura Digital</label>
                  <input type="file" @change="(e) => handleFileUpload(e, 'responsavel_assinatura')" class="block w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
                  <a v-if="form.responsavel_assinatura" :href="form.responsavel_assinatura" target="_blank" class="text-xs text-blue-600 underline mt-1 block">Ver atual</a>
                </div>

                <div class="col-span-1">
                  <label class="block text-xs font-medium text-gray-700 mb-1">Doc. Identificação (PDF/IMG)</label>
                  <input type="file" @change="(e) => handleFileUpload(e, 'responsavel_documento')" class="block w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
                  <a v-if="form.responsavel_documento" :href="form.responsavel_documento" target="_blank" class="text-xs text-blue-600 underline mt-1 block">Ver atual</a>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-gray-50 p-5 rounded-lg border border-gray-200 h-fit">
            <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <i class="i-mdi-certificate text-yellow-600"></i> CRECI e Regulamentação
            </h3>
            
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="form-label">Número CRECI</label>
                  <input v-model="form.creci_numero" type="text" class="form-input" />
                </div>
                <div>
                  <label class="form-label">UF</label>
                  <input v-model="form.creci_uf" type="text" class="form-input uppercase" maxlength="2" />
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="form-label">Tipo de Inscrição</label>
                  <select v-model="form.creci_tipo" class="form-select">
                    <option value="JURIDICO">Jurídico (PJ)</option>
                    <option value="FISICO">Físico (PF)</option>
                  </select>
                </div>
                <div>
                  <label class="form-label">Situação</label>
                  <input v-model="form.creci_situacao" type="text" class="form-input" />
                </div>
              </div>

              <div>
                <label class="form-label">Validade</label>
                <input v-model="form.creci_validade" type="date" class="form-input" />
              </div>

              <div class="pt-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">Cópia do CRECI (Upload)</label>
                <div class="flex items-center gap-3">
                  <input type="file" @change="(e) => handleFileUpload(e, 'creci_documento')" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-yellow-50 file:text-yellow-700 hover:file:bg-yellow-100"/>
                </div>
                <a v-if="form.creci_documento" :href="form.creci_documento" target="_blank" class="text-xs text-blue-600 underline mt-1 block">Visualizar documento atual</a>
              </div>
            </div>
          </div>
        </div>

        <div v-show="activeTab === 'sistema'" class="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in">
          
          <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
            <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <i class="i-mdi-palette text-pink-600"></i> Personalização
            </h3>
            
            <div class="mb-4">
              <label class="form-label">Cor Primária do Site</label>
              <div class="flex items-center gap-3">
                <input v-model="form.cor_primaria" type="color" class="h-12 w-20 p-1 border border-gray-300 rounded shadow-sm cursor-pointer" />
                <div>
                  <span class="text-sm font-medium text-gray-700 block">Cor selecionada</span>
                  <span class="text-xs text-gray-500">{{ form.cor_primaria }}</span>
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-2">Esta cor será utilizada em botões, links e destaques no seu site público.</p>
            </div>
          </div>

          <div class="bg-gray-50 p-5 rounded-lg border border-gray-200">
            <h3 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <i class="i-mdi-robot text-indigo-600"></i> Inteligência Artificial
            </h3>
            
            <div class="mb-4">
              <label class="form-label">Chave API Google Gemini</label>
              <input v-model="form.google_gemini_api_key" type="password" class="form-input" placeholder="sk-..." />
              <p class="text-xs text-gray-500 mt-1">
                Necessária para geração automática de descrições de imóveis e atendimento via IA.
                <a href="https://aistudio.google.com/app/apikey" target="_blank" class="text-blue-600 underline">Obter chave</a>
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* Classes utilitárias personalizadas para inputs */
.form-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}
.form-input {
  @apply w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm py-2 px-3;
}
.form-select {
  @apply w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-sm py-2 px-3 bg-white;
}

/* Animação simples */
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
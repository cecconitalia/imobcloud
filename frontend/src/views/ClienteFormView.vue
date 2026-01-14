<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <router-link to="/">Início</router-link>
              <i class="fas fa-chevron-right separator"></i> 
              <router-link to="/clientes">Clientes</router-link>
              <i class="fas fa-chevron-right separator"></i>
              <span class="active">{{ isEditing ? 'Editar' : 'Novo' }}</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Cliente' : 'Novo Cliente' }}</h1>
        </div>
      </div>
    </header>

    <div v-if="isLoadingData" class="loading-state">
         <div class="spinner"></div>
         <p>A carregar dados...</p>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="main-content-grid">
      
      <div class="left-column">
        <div class="card form-card">
            
            <div class="form-section">
                <div class="tipo-pessoa-toggle">
                    <label class="radio-label" :class="{ active: cliente.tipo_pessoa === 'FISICA' }">
                        <input type="radio" value="FISICA" v-model="cliente.tipo_pessoa">
                        <i class="fas fa-user"></i> Pessoa Física
                    </label>
                    <label class="radio-label" :class="{ active: cliente.tipo_pessoa === 'JURIDICA' }">
                        <input type="radio" value="JURIDICA" v-model="cliente.tipo_pessoa">
                        <i class="fas fa-building"></i> Pessoa Jurídica
                    </label>
                </div>
            </div>

            <div class="form-section compact-section">
                <h3 class="section-title">
                    <i class="far fa-id-card"></i> {{ cliente.tipo_pessoa === 'FISICA' ? 'Dados Pessoais' : 'Dados Empresariais' }}
                </h3>
                
                <div class="form-grid">
                    <template v-if="cliente.tipo_pessoa === 'FISICA'">
                        <div class="form-group full-width">
                            <label>Nome Completo <span class="required">*</span></label>
                            <div class="input-wrapper">
                                <i class="far fa-user input-icon"></i>
                                <input type="text" v-model="cliente.nome" required class="form-input has-icon" placeholder="Nome do cliente" />
                            </div>
                        </div>
                        <div class="form-group">
                            <label>CPF <span class="required">*</span></label>
                            <input type="text" v-model="maskedDocument" required class="form-input" placeholder="000.000.000-00" />
                            <small v-if="documentoError" class="text-danger">{{ documentoError }}</small>
                        </div>
                        <div class="form-group">
                            <label>RG</label>
                            <input type="text" v-model="cliente.rg" class="form-input" />
                        </div>
                        <div class="form-group">
                            <label>Data de Nascimento</label>
                            <input type="date" v-model="cliente.data_nascimento" class="form-input" />
                        </div>
                        <div class="form-group">
                            <label>Estado Civil</label>
                            <div class="input-wrapper">
                                <select v-model="cliente.estado_civil" class="form-select">
                                    <option :value="null">Selecione...</option>
                                    <option value="SOLTEIRO">Solteiro(a)</option>
                                    <option value="CASADO">Casado(a)</option>
                                    <option value="DIVORCIADO">Divorciado(a)</option>
                                    <option value="VIUVO">Viúvo(a)</option>
                                    <option value="UNIAO_ESTAVEL">União Estável</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Profissão</label>
                            <input type="text" v-model="cliente.profissao" class="form-input" />
                        </div>
                    </template>

                    <template v-else>
                        <div class="form-group">
                            <label>Razão Social <span class="required">*</span></label>
                            <div class="input-wrapper">
                                <i class="far fa-building input-icon"></i>
                                <input type="text" v-model="cliente.razao_social" required class="form-input has-icon" />
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Nome Fantasia <span class="required">*</span></label>
                            <input type="text" v-model="cliente.nome" required class="form-input" />
                        </div>
                        <div class="form-group">
                            <label>CNPJ <span class="required">*</span></label>
                            <input type="text" v-model="maskedDocument" required class="form-input" placeholder="00.000.000/0000-00" />
                            <small v-if="documentoError" class="text-danger">{{ documentoError }}</small>
                        </div>
                        <div class="form-group">
                            <label>Inscrição Estadual</label>
                            <input type="text" v-model="cliente.inscricao_estadual" class="form-input" />
                        </div>
                    </template>

                    <div class="form-group">
                        <label>Email</label>
                        <div class="input-wrapper">
                            <i class="far fa-envelope input-icon"></i>
                            <input type="email" v-model="cliente.email" class="form-input has-icon" />
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Telefone Principal <span class="required">*</span></label>
                        <div class="input-wrapper">
                            <i class="fas fa-phone-alt input-icon"></i>
                            <input type="text" v-model="maskedTelefone" required class="form-input has-icon" placeholder="(99) 99999-9999" />
                        </div>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3 class="section-title"><i class="fas fa-map-marker-alt"></i> Endereço</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label>CEP</label>
                        <div class="input-wrapper">
                            <i class="fas fa-search-location input-icon"></i>
                            <input type="text" v-model="maskedCEP" @blur="fetchAddressFromCEP" class="form-input has-icon" placeholder="00000-000" />
                        </div>
                    </div>
                    <div class="form-group full-width">
                        <label>Logradouro</label>
                        <input type="text" v-model="cliente.logradouro" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Número</label>
                        <input type="text" v-model="cliente.numero" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Complemento</label>
                        <input type="text" v-model="cliente.complemento" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Bairro</label>
                        <input type="text" v-model="cliente.bairro" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Cidade</label>
                        <input type="text" v-model="cliente.cidade" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Estado (UF)</label>
                        <input type="text" v-model="cliente.estado" maxlength="2" class="form-input" />
                    </div>
                </div>
            </div>

            <div class="form-section compact-section">
                <h3 class="section-title"><i class="fas fa-info-circle"></i> Perfil e Detalhes</h3>
                
                <div class="form-group full-width">
                    <label>Perfil do Cliente</label>
                    <div class="badges-selector">
                        <label class="badge-checkbox" :class="{ active: isPerfilChecked('INTERESSADO') }">
                            <input type="checkbox" @change="updatePerfilCliente('INTERESSADO', $event.target.checked)" :checked="isPerfilChecked('INTERESSADO')">
                            Interessado
                        </label>
                        <label class="badge-checkbox" :class="{ active: isPerfilChecked('PROPRIETARIO') }">
                            <input type="checkbox" @change="updatePerfilCliente('PROPRIETARIO', $event.target.checked)" :checked="isPerfilChecked('PROPRIETARIO')">
                            Proprietário
                        </label>
                        <label class="badge-checkbox" :class="{ active: isPerfilChecked('COMPRADOR') }">
                            <input type="checkbox" @change="updatePerfilCliente('COMPRADOR', $event.target.checked)" :checked="isPerfilChecked('COMPRADOR')">
                            Comprador
                        </label>
                        <label class="badge-checkbox" :class="{ active: isPerfilChecked('LOCADOR') }">
                            <input type="checkbox" @change="updatePerfilCliente('LOCADOR', $event.target.checked)" :checked="isPerfilChecked('LOCADOR')">
                            Locador
                        </label>
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group full-width">
                        <label>Preferências de Imóvel</label>
                        <textarea v-model="cliente.preferencias_imovel" rows="3" class="form-textarea" placeholder="O que o cliente procura?"></textarea>
                    </div>
                    <div class="form-group full-width">
                        <label>Observações</label>
                        <textarea v-model="cliente.observacoes" rows="3" class="form-textarea"></textarea>
                    </div>
                </div>
            </div>

            <div class="form-actions-footer">
                <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
                <button type="submit" class="btn-primary" :disabled="isSubmitting">
                    <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
                    <span v-else>{{ isEditing ? 'Salvar Cliente' : 'Criar Cliente' }}</span>
                </button>
            </div>

        </div>
      </div> 
      
      <div class="right-column">
            <div class="card info-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-camera"></i> Foto de Perfil</h3>
                 </div>
                 <div class="profile-upload-area">
                    <div class="profile-preview">
                        <img v-if="profilePicPreview" :src="profilePicPreview" alt="Foto" />
                        <div v-else class="placeholder-icon"><i class="fas fa-user"></i></div>
                    </div>
                    
                    <div class="upload-controls">
                        <label for="foto_upload" class="btn-upload">
                            <i class="fas fa-cloud-upload-alt"></i> Escolher
                        </label>
                        <input type="file" id="foto_upload" @change="handleProfilePicChange" accept="image/*" hidden />
                        
                        <button type="button" v-if="profilePicPreview" @click="removeProfilePic" class="btn-remove" title="Remover">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                 </div>
            </div>

            <div class="card info-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-toggle-on"></i> Situação</h3>
                 </div>
                 <div class="status-toggle-wrapper">
                    <label class="switch-container">
                        <input type="checkbox" v-model="cliente.ativo">
                        <span class="slider round"></span>
                    </label>
                    <span class="status-label" :class="{ 'text-success': cliente.ativo, 'text-muted': !cliente.ativo }">
                        {{ cliente.ativo ? 'Ativo' : 'Inativo' }}
                    </span>
                 </div>
                 <p class="helper-text-widget">Clientes inativos não aparecem nas buscas rápidas do sistema.</p>
            </div>
      </div> 

    </form>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();

const clienteId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!clienteId.value);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

const profilePicFile = ref<File | null>(null);
const profilePicPreview = ref<string | null>(null);
const documentoError = ref(''); 

const createEmptyCliente = () => ({
  id: null,
  tipo_pessoa: 'FISICA' as 'FISICA' | 'JURIDICA', 
  nome: '', 
  razao_social: null as string | null,
  inscricao_estadual: null as string | null,
  documento: '', 
  rg: null as string | null, 
  data_nascimento: null as string | null, 
  estado_civil: null as string | null, 
  profissao: null as string | null, 
  email: null as string | null,
  telefone: '', 
  foto_perfil: null as string | null,
  perfil_cliente: ['INTERESSADO'] as string[], 
  observacoes: null as string | null, 
  preferencias_imovel: null as string | null, 
  cep: null as string | null, 
  logradouro: null as string | null, 
  numero: null as string | null, 
  complemento: null as string | null, 
  bairro: null as string | null, 
  cidade: null as string | null, 
  estado: null as string | null, 
  ativo: true,
});

const cliente = ref(createEmptyCliente());

// =========================================================================
// UTILITÁRIOS & MÁSCARAS
// =========================================================================
const clean = (value: string | null | undefined): string => String(value || '').replace(/\D/g, '');

function isPerfilChecked(perfil: string): boolean {
    return cliente.value.perfil_cliente.includes(perfil);
}

function updatePerfilCliente(perfil: string, isChecked: boolean) {
    if (isChecked) {
        if (!cliente.value.perfil_cliente.includes(perfil)) cliente.value.perfil_cliente.push(perfil);
    } else {
        cliente.value.perfil_cliente = cliente.value.perfil_cliente.filter(p => p !== perfil);
    }
}

const formatCPFCNPJ = (value: string, isPJ: boolean): string => {
  const cleaned = clean(value).substring(0, 14);
  if (isPJ) {
    if (cleaned.length <= 11) return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
  } else {
    return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  }
};

const maskedDocument = computed({
  get() {
    const isPJ = cliente.value.tipo_pessoa === 'JURIDICA';
    return formatCPFCNPJ(cliente.value.documento, isPJ);
  },
  set(newValue) {
    cliente.value.documento = clean(newValue);
    documentoError.value = '';
  },
});

const formatTelefone = (value: string): string => {
  const cleaned = clean(value).substring(0, 11);
  if (cleaned.length <= 10) return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
  return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
};

const maskedTelefone = computed({
  get() { return formatTelefone(cliente.value.telefone); },
  set(newValue) { cliente.value.telefone = clean(newValue); },
});

const maskedCEP = computed({
  get() {
    const cleaned = clean(cliente.value.cep).substring(0, 8);
    return cleaned.replace(/(\d{5})(\d{3})/, '$1-$2');
  },
  set(newValue) { cliente.value.cep = clean(newValue); },
});

// =========================================================================
// LÓGICA DE NEGÓCIO
// =========================================================================

watch(() => cliente.value.tipo_pessoa, (newTipo, oldTipo) => {
    // CORREÇÃO CRÍTICA: Se estiver carregando dados, não limpa os campos!
    if (isLoadingData.value) return; 

    if (newTipo === 'FISICA') {
        cliente.value.razao_social = null;
        cliente.value.inscricao_estadual = null;
    } else {
        cliente.value.data_nascimento = null;
        cliente.value.rg = null; 
        cliente.value.estado_civil = null;
        cliente.value.profissao = null;
    }
    // Apenas limpa se for uma mudança real pelo usuário (oldTipo existe)
    if (oldTipo && newTipo !== oldTipo) { 
        cliente.value.nome = ''; 
        cliente.value.documento = ''; 
    }
    documentoError.value = '';
}, { immediate: true }); 

watch(clienteId, (newId) => {
  if (newId) {
    fetchClienteData(newId);
  } else {
    cliente.value = createEmptyCliente();
    profilePicFile.value = null;
    profilePicPreview.value = null;
  }
}, { immediate: true }); 

async function fetchClienteData(id: string) {
  if (!id) return; 
  isLoadingData.value = true;
  try {
    const { data } = await apiClient.get(`/v1/clientes/${id}/`);
    
    let tipoPessoaCorreta: 'FISICA' | 'JURIDICA' = 'FISICA';
    const tipoPessoaFetched = data.tipo_pessoa || 'FISICA';
    if (tipoPessoaFetched === 'JURIDICA' || tipoPessoaFetched === 'PJ') tipoPessoaCorreta = 'JURIDICA';
    else if (tipoPessoaFetched === 'FISICA' || tipoPessoaFetched === 'PF') tipoPessoaCorreta = 'FISICA';

    if (data.data_nascimento) data.data_nascimento = data.data_nascimento.split('T')[0];
    const perfilClienteData = Array.isArray(data.perfil_cliente) ? data.perfil_cliente : ['INTERESSADO'];
    
    // Atribuição reativa mantendo isLoadingData = true para o watcher não limpar
    cliente.value = { 
        ...createEmptyCliente(), 
        ...data, 
        id: data.id,
        tipo_pessoa: tipoPessoaCorreta,
        perfil_cliente: perfilClienteData,
    }; 
    profilePicPreview.value = cliente.value.foto_perfil || null; 
  } catch (error) {
    console.error('Erro ao carregar dados:', error);
    router.push({ name: 'clientes' }); 
  } finally {
    // Pequeno delay para garantir que o watcher já rodou (se necessário) antes de liberar
    setTimeout(() => {
        isLoadingData.value = false;
    }, 100);
  }
}

async function fetchAddressFromCEP() {
    const cep = clean(cliente.value.cep);
    if (cep && cep.length === 8) {
        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            if (!response.ok) throw new Error('Erro');
            const data = await response.json();
            if (data.erro) throw new Error('Inválido');

            cliente.value.logradouro = data.logradouro;
            cliente.value.bairro = data.bairro;
            cliente.value.cidade = data.localidade;
            cliente.value.estado = data.uf;
            cliente.value.cep = clean(data.cep);
        } catch (error) { console.warn("CEP não encontrado"); }
    }
}

function handleProfilePicChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    profilePicFile.value = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => { profilePicPreview.value = e.target?.result as string; };
    reader.readAsDataURL(profilePicFile.value);
  }
}

function removeProfilePic() {
  profilePicFile.value = null;
  profilePicPreview.value = null;
  cliente.value.foto_perfil = null; 
}

async function handleSubmit() {
  isSubmitting.value = true;
  documentoError.value = '';
  
  if (!cliente.value.nome || !cliente.value.documento || !cliente.value.telefone) {
      isSubmitting.value = false;
      alert(`Os campos Nome/Fantasia, CPF/CNPJ e Telefone são obrigatórios.`);
      return;
  }
  
  if (cliente.value.tipo_pessoa === 'JURIDICA' && !cliente.value.razao_social) {
      isSubmitting.value = false;
      alert("A Razão Social é obrigatória para Pessoa Jurídica.");
      return;
  }
  
  const docLen = cliente.value.documento.length;
  if (cliente.value.tipo_pessoa === 'FISICA' && docLen !== 11) {
      documentoError.value = 'CPF deve conter 11 dígitos.';
      isSubmitting.value = false;
      return;
  }
  if (cliente.value.tipo_pessoa === 'JURIDICA' && docLen !== 14) {
      documentoError.value = 'CNPJ deve conter 14 dígitos.';
      isSubmitting.value = false;
      return;
  }

  const formData = new FormData();
  
  for (const key in cliente.value) {
    if (key === 'id' || key === 'foto_perfil') continue;
    const value = cliente.value[key as keyof typeof cliente.value];
    
    if (key === 'perfil_cliente' && Array.isArray(value)) {
         formData.append(key, JSON.stringify(value));
         continue;
    }
    
    if (value === null || value === undefined || value === '') {
      formData.append(key, '');
    } else if (typeof value === 'boolean') {
      formData.append(key, value ? 'true' : 'false');
    } else {
      formData.append(key, String(value));
    }
  }

  if (profilePicFile.value) {
    formData.append('foto_perfil', profilePicFile.value);
  } else if (cliente.value.foto_perfil === null && isEditing.value) {
    formData.append('foto_perfil', '');
  }

  try {
    if (isEditing.value && clienteId.value) {
      await apiClient.patch(`/v1/clientes/${clienteId.value}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' }});
    } else {
      await apiClient.post('/v1/clientes/', formData, { headers: { 'Content-Type': 'multipart/form-data' }});
    }
    router.push({ name: 'clientes' });
  } catch (error: any) {
    console.error("Erro ao guardar:", error.response?.data || error);
    let errorMessage = `Erro ao salvar cliente.`;
    if (error.response?.data) {
        const errors = error.response.data;
        const firstErrorKey = Object.keys(errors)[0];
        if (firstErrorKey && Array.isArray(errors[firstErrorKey])) errorMessage = `Erro em '${firstErrorKey}': ${errors[firstErrorKey][0]}`;
        else if (typeof errors === 'string') errorMessage += ` ${errors}`;
    }
    alert(errorMessage);
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() { router.push({ name: 'clientes' }); }

onMounted(() => { fetchClienteData(clienteId.value || ''); });
</script>

<style scoped>
/* =========================================================
   1. GERAL & LAYOUT
   ========================================================= */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  display: flex; flex-direction: column;
}

.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
.breadcrumb a:hover { color: #2563eb; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.main-content-grid { 
    display: grid; grid-template-columns: 1fr 320px; gap: 1.5rem; align-items: start; 
}
@media (max-width: 1100px) { .main-content-grid { grid-template-columns: 1fr; } }

/* =========================================================
   2. CARDS & SEÇÕES
   ========================================================= */
.card {
  background-color: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
  padding: 1.5rem; border: 1px solid #e5e7eb;
}
.form-card { min-height: 400px; }
.info-card { padding: 1.2rem; margin-bottom: 1rem; border-left: 3px solid #e5e7eb; }

.form-section { margin-bottom: 2rem; }
.section-title {
    font-size: 1rem; color: #1f2937; margin-bottom: 1.2rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9; font-weight: 600; display: flex; align-items: center; gap: 0.6rem;
}
.compact-section { margin-bottom: 0; }

/* Grid de Campos */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 500; font-size: 0.85rem; color: #4b5563; }
.required { color: #ef4444; }
.text-danger { color: #ef4444; font-size: 0.75rem; margin-top: 2px; }

/* Inputs */
.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; font-size: 0.85rem; pointer-events: none; }
.form-input, .form-select, .form-textarea {
    width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.9rem; transition: all 0.2s; background-color: #fff; box-sizing: border-box; color: #1f2937;
}
.form-input.has-icon { padding-left: 2.2rem; }
.form-input:focus, .form-select:focus, .form-textarea:focus { 
    border-color: #3b82f6; outline: none; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
.form-textarea { resize: vertical; min-height: 80px; font-family: inherit; }

/* =========================================================
   3. COMPONENTES ESPECÍFICOS
   ========================================================= */
/* Toggle Tipo Pessoa */
.tipo-pessoa-toggle { display: flex; gap: 1rem; padding: 0.5rem; background: #f9fafb; border-radius: 8px; border: 1px solid #f3f4f6; width: fit-content; }
.radio-label {
    padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; color: #6b7280; font-size: 0.9rem; font-weight: 500; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem;
}
.radio-label:hover { background: #e5e7eb; }
.radio-label.active { background: white; color: #2563eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-weight: 600; }
.radio-label input { display: none; }

/* Badges de Perfil */
.badges-selector { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.badge-checkbox {
    padding: 0.4rem 0.8rem; border-radius: 20px; border: 1px solid #e5e7eb; cursor: pointer;
    font-size: 0.8rem; color: #6b7280; transition: all 0.2s; background: white;
}
.badge-checkbox:hover { border-color: #cbd5e1; }
.badge-checkbox.active { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; font-weight: 500; }
.badge-checkbox input { display: none; }

/* Widget Foto */
.widget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f1f5f9; }
.widget-title { font-size: 0.9rem; font-weight: 600; margin: 0; color: #374151; }

.profile-upload-area { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 1rem 0; }
.profile-preview {
    width: 120px; height: 120px; border-radius: 50%; overflow: hidden; background: #f3f4f6;
    display: flex; align-items: center; justify-content: center; border: 4px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.profile-preview img { width: 100%; height: 100%; object-fit: cover; }
.placeholder-icon { font-size: 3rem; color: #d1d5db; }

.upload-controls { display: flex; gap: 0.5rem; }
.btn-upload {
    padding: 0.4rem 0.8rem; background: #2563eb; color: white; border-radius: 6px; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; gap: 0.4rem; transition: background 0.2s;
}
.btn-upload:hover { background: #1d4ed8; }
.btn-remove {
    padding: 0.4rem 0.8rem; background: white; border: 1px solid #e5e7eb; color: #ef4444; border-radius: 6px; cursor: pointer; font-size: 0.8rem; transition: all 0.2s;
}
.btn-remove:hover { background: #fef2f2; border-color: #fecaca; }

/* Widget Status (Switch) */
.status-toggle-wrapper { display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem; }
.status-label { font-size: 0.9rem; font-weight: 600; }
.text-success { color: #16a34a; }
.text-muted { color: #9ca3af; }
.helper-text-widget { font-size: 0.75rem; color: #9ca3af; margin-top: 0.8rem; font-style: italic; }

.switch-container { position: relative; display: inline-block; width: 44px; height: 24px; }
.switch-container input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; }
input:checked + .slider { background-color: #2563eb; }
input:checked + .slider:before { transform: translateX(20px); }
.slider.round { border-radius: 24px; }
.slider.round:before { border-radius: 50%; }

/* Footer Actions */
.form-actions-footer { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f1f5f9; }
.btn-primary, .btn-secondary { padding: 0.5rem 1.2rem; border-radius: 6px; border: none; font-weight: 500; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; }
.btn-primary { background-color: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.1); }
.btn-primary:hover { background-color: #1d4ed8; transform: translateY(-1px); }
.btn-secondary { background-color: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.btn-secondary:hover { background-color: #f1f5f9; border-color: #cbd5e1; color: #334155; }

/* Loading */
.loading-state { text-align: center; padding: 4rem; color: #64748b; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
}
</style>
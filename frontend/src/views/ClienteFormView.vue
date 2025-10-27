<template>
<div class="form-container">
<div v-if="isLoadingData" class="loading-message">
A carregar dados do cliente...
</div>

<form v-else @submit.prevent="handleSubmit" class="cliente-form">
<div class="form-card">
<div class="tipo-pessoa-selector">
<label class="tipo-pessoa-label">Tipo de Pessoa</label>
<div class="tipo-pessoa-options">
<label class="radio-option">
<input type="radio" value="FISICA" :checked="cliente.tipo_pessoa === 'FISICA'" @change="onTipoPessoaChange">
<span>Pessoa Física</span>
</label>
<label class="radio-option">
<input type="radio" value="JURIDICA" :checked="cliente.tipo_pessoa === 'JURIDICA'" @change="onTipoPessoaChange">
<span>Pessoa Jurídica</span>
</label>
</div>
</div>
</div>

<div class="main-form-grid">

<div class="form-card grid-col-span-2"> 
<h3 class="card-title">
{{ cliente.tipo_pessoa === 'FISICA' ? 'Dados Pessoais' : 'Dados Empresariais' }}
</h3>
<div class="card-content-grid">
<div class="profile-pic-area">
<div class="profile-pic-preview">
<img v-if="profilePicPreview" :src="profilePicPreview" alt="Pré-visualização da Foto de Perfil" class="profile-img"/>
<i v-else class="fas fa-user-circle profile-icon"></i>
</div>
<label for="foto_perfil_input" class="btn-action upload-btn">
<i class="fas fa-upload"></i> Carregar Foto
</label>
<input type="file" id="foto_perfil_input" @change="handleProfilePicChange" accept="image/*" />
<button type="button" v-if="profilePicPreview" @click="removeProfilePic" class="btn-action remove-btn">
<i class="fas fa-trash-alt"></i> Remover Foto
</button>
</div>

<div class="fields-area">
<template v-if="cliente.tipo_pessoa === 'FISICA'">
<div class="form-group">
<label for="nome">Nome Completo</label>
<input type="text" id="nome" v-model="cliente.nome" required />
</div>
<div class="form-group">
<label for="documento_pf">CPF</label>
<input type="text" id="documento_pf" v-model="maskedDocument" required placeholder="000.000.000-00" />
<small v-if="documentoError" class="error-message-small">{{ documentoError }}</small>
</div>
<div class="form-group">
<label for="data_nascimento">Data de Nascimento</label>
<input type="date" id="data_nascimento" v-model="cliente.data_nascimento" />
</div>
<div class="form-group">
<label for="rg">RG</label>
<input type="text" id="rg" v-model="cliente.rg" />
</div>
<div class="form-group">
<label for="estado_civil">Estado Civil</label>
<input type="text" id="estado_civil" v-model="cliente.estado_civil" />
</div>
<div class="form-group">
<label for="profissao">Profissão</label>
<input type="text" id="profissao" v-model="cliente.profissao" />
</div>
</template>

<template v-else>
<div class="form-group">
<label for="razao_social">Razão Social</label>
<input type="text" id="razao_social" v-model="cliente.razao_social" required />
</div>
<div class="form-group">
<label for="nome_fantasia">Nome Fantasia</label>
<input type="text" id="nome_fantasia" v-model="cliente.nome" required />
</div>
<div class="form-group">
<label for="documento_pj">CNPJ</label>
<input type="text" id="documento_pj" v-model="maskedDocument" required placeholder="00.000.000/0000-00" />
<small v-if="documentoError" class="error-message-small">{{ documentoError }}</small>
</div>
<div class="form-group">
<label for="inscricao_estadual">Inscrição Estadual</label>
<input type="text" id="inscricao_estadual" v-model="cliente.inscricao_estadual" />
</div>
</template>

<div class="form-group">
<label for="email">Email</label>
<input type="email" id="email" v-model="cliente.email" />
</div>
<div class="form-group">
<label for="telefone">Telefone Principal</label>
<input type="text" id="telefone" v-model="maskedTelefone" required placeholder="(99) 99999-9999" />
</div>
</div>
</div>
</div>

<div class="form-card">
<h3 class="card-title">Endereço</h3>
<div class="card-content">
<div class="form-group">
<label for="cep">CEP</label>
<input type="text" id="cep" v-model="maskedCEP" @blur="fetchAddressFromCEP" placeholder="00000-000" />
</div>
<div class="form-group">
<label for="logradouro">Logradouro</label>
<input type="text" id="logradouro" v-model="cliente.logradouro" />
</div>
<div class="form-group">
<label for="numero">Número</label>
<input type="text" id="numero" v-model="cliente.numero" />
</div>
<div class="form-group">
<label for="complemento">Complemento</label>
<input type="text" id="complemento" v-model="cliente.complemento" />
</div>
<div class="form-group">
<label for="bairro">Bairro</label>
<input type="text" id="bairro" v-model="cliente.bairro" />
</div>
<div class="form-group">
<label for="cidade">Cidade</label>
<input type="text" id="cidade" v-model="cliente.cidade" />
</div>
<div class="form-group">
<label for="estado">Estado (UF)</label>
<input type="text" id="estado" v-model="cliente.estado" maxlength="2" />
</div>
</div>
</div>

<div class="form-card">
<h3 class="card-title">Outras Informações</h3>
<div class="card-content">
<div class="form-group">
<label for="preferencias_imovel">Preferências de Imóvel</label>
<textarea id="preferencias_imovel" v-model="cliente.preferencias_imovel" rows="4"></textarea>
</div>
<div class="form-group">
<label for="observacoes">Observações</label>
<textarea id="observacoes" v-model="cliente.observacoes" rows="4"></textarea>
</div>
<div class="checkbox-group">
<input type="checkbox" id="ativo" v-model="cliente.ativo">
<label for="ativo">Cliente Ativo</label>
</div>
</div>
</div>
</div> 
<div class="form-actions">
<button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
<button type="submit" class="btn-primary" :disabled="isSubmitting">
{{ isSubmitting ? 'A guardar...' : (isEditing ? 'Atualizar Cliente' : 'Guardar Cliente') }}
</button>
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

// Definição completa do estado do cliente
const createEmptyCliente = () => ({
  id: null,
  tipo_pessoa: 'FISICA' as 'FISICA' | 'JURIDICA', 
  nome: '', 
  razao_social: null as string | null,
  inscricao_estadual: null as string | null,
  documento: '', // MANTÉM APENAS NÚMEROS
  rg: null as string | null, 
  data_nascimento: null as string | null, 
  estado_civil: null as string | null, 
  profissao: null as string | null, 
  email: null as string | null,
  telefone: '', // MANTÉM APENAS NÚMEROS
  foto_perfil: null as string | null,
  tipo: 'INTERESSADO',
  observacoes: null as string | null, 
  preferencias_imovel: null as string | null, 
  cep: null as string | null, // MANTÉM APENAS NÚMEROS
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
// LÓGICA DE MÁSCARAS
// Nota: Em um projeto real, use uma biblioteca como 'vue-the-mask' ou 'v-mask'.
// Esta lógica é um exemplo funcional de como controlar o v-model.
// =========================================================================

/**
 * Retorna uma string contendo apenas números.
 */
const clean = (value: string | null | undefined): string => String(value || '').replace(/\D/g, '');


// --- 1. MÁSCARA CPF/CNPJ ---
const formatCPFCNPJ = (value: string, isPJ: boolean): string => {
  const cleaned = clean(value).substring(0, 14);
  if (isPJ) {
    if (cleaned.length <= 11) return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4'); // Trata como CPF
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
    // Atualiza o valor cru no objeto cliente
    cliente.value.documento = clean(newValue);
  },
});

// --- 2. MÁSCARA TELEFONE (com 9º dígito opcional) ---
const formatTelefone = (value: string): string => {
  const cleaned = clean(value).substring(0, 11);
  if (cleaned.length <= 10) {
    // (99) 9999-9999
    return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
  } else {
    // (99) 99999-9999
    return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  }
};

const maskedTelefone = computed({
  get() {
    return formatTelefone(cliente.value.telefone);
  },
  set(newValue) {
    // Atualiza o valor cru no objeto cliente
    cliente.value.telefone = clean(newValue);
  },
});

// --- 3. MÁSCARA CEP ---
const maskedCEP = computed({
  get() {
    const cleaned = clean(cliente.value.cep).substring(0, 8);
    return cleaned.replace(/(\d{5})(\d{3})/, '$1-$2');
  },
  set(newValue) {
    // Atualiza o valor cru no objeto cliente
    cliente.value.cep = clean(newValue);
  },
});
// =========================================================================


function onTipoPessoaChange(event: Event) {
    const target = event.target as HTMLInputElement;
    cliente.value.tipo_pessoa = target.value as 'FISICA' | 'JURIDICA';
    
    // Limpeza de campos dependentes
    if (cliente.value.tipo_pessoa === 'FISICA') {
        cliente.value.razao_social = null;
        cliente.value.inscricao_estadual = null;
    } else {
        cliente.value.data_nascimento = null;
        cliente.value.rg = null; 
        cliente.value.estado_civil = null;
        cliente.value.profissao = null;
    }
    cliente.value.nome = ''; 
    cliente.value.documento = ''; 
}


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
    if (tipoPessoaFetched === 'JURIDICA' || tipoPessoaFetched === 'PJ') {
        tipoPessoaCorreta = 'JURIDICA';
    } else if (tipoPessoaFetched === 'FISICA' || tipoPessoaFetched === 'PF') {
        tipoPessoaCorreta = 'FISICA';
    }

    if (data.data_nascimento) {
        data.data_nascimento = data.data_nascimento.split('T')[0];
    }
    
    cliente.value = { 
        ...createEmptyCliente(), 
        ...data, 
        id: data.id,
        tipo_pessoa: tipoPessoaCorreta,
    }; 
    profilePicPreview.value = cliente.value.foto_perfil || null; 
  } catch (error) {
    console.error('Erro ao carregar dados do cliente:', error);
    alert('Não foi possível carregar os dados do cliente.');
    router.push({ name: 'clientes' }); 
  } finally {
    isLoadingData.value = false;
  }
}

async function fetchAddressFromCEP() {
    const cep = clean(cliente.value.cep); // Usa o valor sem máscara
    if (cep && cep.length === 8) {
        try {
            const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            if (!response.ok) throw new Error('CEP não encontrado');
            const data = await response.json();
            if (data.erro) throw new Error('CEP inválido');

            cliente.value.logradouro = data.logradouro;
            cliente.value.bairro = data.bairro;
            cliente.value.cidade = data.localidade;
            cliente.value.estado = data.uf;
            cliente.value.cep = clean(data.cep); // Garante que o modelo armazene limpo
        } catch (error) {
            console.warn("Erro ao buscar CEP:", error);
        }
    }
}


function handleProfilePicChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    profilePicFile.value = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      profilePicPreview.value = e.target?.result as string;
    };
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
  
  // --- VALIDAÇÃO MANUAL DEFENSIVA ---
  if (!cliente.value.nome || !cliente.value.documento || !cliente.value.telefone) {
      isSubmitting.value = false;
      alert(`Atenção: Os campos Nome/Fantasia, CPF/CNPJ e Telefone são obrigatórios.`);
      return;
  }
  
  if (cliente.value.tipo_pessoa === 'JURIDICA' && !cliente.value.razao_social) {
      isSubmitting.value = false;
      alert("Atenção: A Razão Social é obrigatória para Pessoa Jurídica.");
      return;
  }
  // --- FIM VALIDAÇÃO MANUAL DEFENSIVA ---


  const formData = new FormData();
  
  // Itera sobre o objeto cliente para anexar todos os campos (incluindo os não visíveis)
  for (const key in cliente.value) {
    if (key === 'id' || key === 'foto_perfil') continue;

    const value = cliente.value[key as keyof typeof cliente.value];
    
    // CORREÇÃO: Envia string vazia para garantir que a chave vá para o Serializer.
    if (value === null || value === undefined || value === '') {
      formData.append(key, '');
    } else if (typeof value === 'boolean') {
      formData.append(key, value ? 'true' : 'false');
    } else {
      // Anexa outros valores (tipo_pessoa, nome, documento, etc.)
      formData.append(key, String(value));
    }
  }

  // Anexa a foto de perfil
  if (profilePicFile.value) {
    formData.append('foto_perfil', profilePicPicFile.value);
  } else if (cliente.value.foto_perfil === null && isEditing.value) {
    formData.append('foto_perfil', '');
  }

  try {
    if (isEditing.value && clienteId.value) {
      await apiClient.patch(`/v1/clientes/${clienteId.value}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      alert('Cliente atualizado com sucesso!');
    } else {
      await apiClient.post('/v1/clientes/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      alert('Cliente cadastrado com sucesso!');
    }

    // Redireciona para a lista de clientes
    router.push({ name: 'clientes' });
        
  } catch (error: any) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    
    let errorMessage = `Ocorreu um erro ao ${isEditing.value ? 'atualizar' : 'criar'} o cliente.`;
    
    if (error.response?.data) {
        const errors = error.response.data;
        const firstErrorKey = Object.keys(errors)[0];
        
        if (firstErrorKey && Array.isArray(errors[firstErrorKey])) {
            errorMessage = `Erro no campo '${firstErrorKey}': ${errors[firstErrorKey][0]}`;
        } else if (typeof errors === 'string') {
            errorMessage += ` Detalhe: ${errors}`;
        }
    } 
    else {
        errorMessage = "Erro de Comunicação: A requisição falhou antes de receber uma resposta válida do servidor. Verifique a conexão e as configurações CORS/API.";
    }
    
    alert(errorMessage);

  } finally {
    isSubmitting.value = false;
  }
}


function handleCancel() {
  // Redireciona para a lista de clientes ao cancelar
  router.push({ name: 'clientes' });
}

onMounted(() => {
    if (!clienteId.value || clienteId.value === 'novo') {
        cliente.value.tipo_pessoa = 'FISICA';
    }
    fetchClienteData(clienteId.value || '');
});
</script>


<style scoped>
/* A indentação foi corrigida para garantir a ausência de caracteres invisíveis */
.form-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.cliente-form {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.main-form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.grid-col-span-2 {
    grid-column: span 2;
}

.form-card {
    background-color: white;
    padding: 20px;
    border-radius: 6px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #007bff;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
}

.card-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.card-content-grid {
    display: grid;
    grid-template-columns: auto 1fr; 
    gap: 2rem;
    align-items: flex-start;
}
.fields-area {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem 1.5rem;
    grid-column: 2 / -1; 
}
@media (max-width: 768px) {
    .card-content-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    .fields-area {
        grid-column: 1 / -1;
    }
}


.form-group {
    display: flex;
    flex-direction: column;
}

.form-group.full-width {
    grid-column: 1 / -1;
}

label {
    font-weight: 500;
    margin-bottom: 0.3rem;
    color: #343a40;
}

.form-group input:not([type="radio"]):not([type="checkbox"]), .form-group select, .form-group textarea {
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.2s;
}

.form-group input:focus, .form-group textarea:focus {
    border-color: #007bff;
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-group textarea {
    resize: vertical;
    min-height: 100px;
}

.form-actions {
    margin-top: 1.5rem;
    display: flex;
    gap: 1rem;
    justify-content: flex-end; 
}

.btn-primary, .btn-secondary, .btn-action {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: background-color 0.2s ease, border-color 0.2s ease;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-primary {
    background-color: #28a745; 
    color: white;
}

.btn-primary:hover {
    background-color: #1e7e34;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #5c636a;
}

.btn-action {
    background-color: #f8f9fa;
    color: #343a40;
    border: 1px solid #ced4da;
}
.upload-btn {
    width: 100%;
}
.remove-btn {
    width: 100%;
    margin-top: 0.5rem;
}

.btn-action:hover {
    background-color: #e9ecef;
}

.btn-action i {
    margin-right: 0;
}

.loading-message {
    text-align: center;
    padding: 3rem;
    font-size: 1.2rem;
    color: #6c757d;
}

/* Estilos para Upload de Foto */
input[type="file"] {
    display: none;
}

.profile-pic-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.profile-pic-preview {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    overflow: hidden;
    margin-bottom: 0.5rem;
    background-color: #e9ecef;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 3px solid #007bff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.profile-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.profile-icon {
    font-size: 60px;
    color: #6c757d;
}


.error-message {
    padding: 1rem;
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    margin-top: 1rem;
}
.error-message-small {
    color: #dc3545;
    font-size: 0.85rem;
    margin-top: 0.2rem;
}

/* Estilos do Seletor de Tipo de Pessoa */
.tipo-pessoa-selector {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #eee;
}

.tipo-pessoa-label {
    font-size: 1.1rem;
    font-weight: 600;
    color: #495057;
    margin: 0;
}

.tipo-pessoa-options {
    display: flex;
    gap: 1.5rem;
}

.radio-option {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-weight: normal;
    color: #343a40;
    user-select: none;
}

.radio-option input[type="radio"] {
    margin-right: 0.5rem;
    accent-color: #007bff;
}

/* Media Queries para Responsividade */
@media (max-width: 900px) {
    .main-form-grid {
        grid-template-columns: 1fr;
    }

    .card-content-grid {
        grid-template-columns: 1fr;
    }

    .profile-pic-area {
        grid-column: 1; 
    }
}
</style>
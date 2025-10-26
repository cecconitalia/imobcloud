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
<input type="text" id="documento_pf" v-model="cliente.documento" required />
</div>
<div class="form-group">
<label for="data_nascimento">Data de Nascimento</label>
<input type="date" id="data_nascimento" v-model="cliente.data_nascimento" />
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
<input type="text" id="documento_pj" v-model="cliente.documento" required />
</div>
</template>

<div class="form-group">
<label for="email">Email</label>
<input type="email" id="email" v-model="cliente.email" />
</div>
<div class="form-group">
<label for="telefone">Telefone Principal</label>
<input type="text" id="telefone" v-model="cliente.telefone" required />
</div>
</div>
</div>
</div>

<div class="form-card">
<h3 class="card-title">Endereço</h3>
<div class="card-content">
<div class="form-group">
<label for="cep">CEP</label>
<input type="text" id="cep" v-model="cliente.cep" @blur="fetchAddressFromCEP" />
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
<label for="tipo">Tipo de Cliente</label>
<select id="tipo" v-model="cliente.tipo">
<option value="PROPRIETARIO">Proprietário</option>
<option value="INTERESSADO">Interessado</option>
<option value="AMBOS">Ambos</option>
</select>
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

const createEmptyCliente = () => ({
  id: null,
  tipo_pessoa: 'FISICA' as 'FISICA' | 'JURIDICA', 
  nome: '', 
  razao_social: '',
  documento: '', 
  data_nascimento: null,
  email: '',
  telefone: '',
  foto_perfil: null,
  tipo: 'INTERESSADO',
  observacoes: '',
  cep: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
  ativo: true,
});

const cliente = ref(createEmptyCliente());

function onTipoPessoaChange(event: Event) {
    const target = event.target as HTMLInputElement;
    cliente.value.tipo_pessoa = target.value as 'FISICA' | 'JURIDICA';
    
    if (cliente.value.tipo_pessoa === 'FISICA') {
        cliente.value.razao_social = '';
    } else {
        cliente.value.data_nascimento = null;
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
  isLoadingData.value = true;
  try {
    const { data } = await apiClient.get(`/v1/clientes/${id}/`);
    
    // Mapeamento de PF/PJ para FISICA/JURIDICA ao carregar para o estado local
    const tipoPessoaFetched = data.tipo_pessoa || 'FISICA';
    let tipoPessoaCorreta: 'FISICA' | 'JURIDICA' = 'FISICA';
    if (tipoPessoaFetched === 'JURIDICA' || tipoPessoaFetched === 'PJ') {
        tipoPessoaCorreta = 'JURIDICA';
    } else if (tipoPessoaFetched === 'FISICA' || tipoPessoaFetched === 'PF') {
        tipoPessoaCorreta = 'FISICA';
    }

    cliente.value = { 
        ...createEmptyCliente(), 
        ...data, 
        tipo_pessoa: tipoPessoaCorreta, // Usa o valor normalizado
        nome: data.nome || ''
    }; 
    profilePicPreview.value = cliente.value.foto_perfil || null; 
  } catch (error) {
    console.error('Erro ao carregar dados do cliente:', error);
    alert('Não foi possível carregar os dados do cliente.');
    router.push('/clientes'); 
  } finally {
    isLoadingData.value = false;
  }
}

async function fetchAddressFromCEP() {
    const cep = cliente.value.cep?.replace(/\D/g, '');
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
  
  // --- VALIDAÇÃO MANUAL DEFENSIVA (FAIL-SAFE) ---
  if (!cliente.value.nome || !cliente.value.documento || !cliente.value.telefone) {
      isSubmitting.value = false;
      let missingField = '';
      if (!cliente.value.nome) missingField = cliente.value.tipo_pessoa === 'FISICA' ? 'Nome Completo' : 'Nome Fantasia';
      else if (!cliente.value.documento) missingField = 'CPF / CNPJ';
      else if (!cliente.value.telefone) missingField = 'Telefone Principal';

      alert(`Atenção: O campo "${missingField}" é obrigatório e não pode estar vazio.`);
      return;
  }
  
  if (cliente.value.tipo_pessoa === 'JURIDICA' && !cliente.value.razao_social) {
      isSubmitting.value = false;
      alert("Atenção: A Razão Social é obrigatória para Pessoa Jurídica.");
      return;
  }
  // --- FIM VALIDAÇÃO MANUAL DEFENSIVA ---


  const formData = new FormData();

  // CORREÇÃO ESSENCIAL: Envia o valor do estado local (FISICA ou JURIDICA) diretamente.
  // O DRF deve aceitar 'FISICA' ou 'JURIDICA'. 
  // Se o modelo foi migrado para PF/PJ, esta linha deve ser alterada para mapear para PF/PJ.
  // Assumindo que o erro anterior era do serializador e este é o valor que o modelo espera:
  formData.append('tipo_pessoa', cliente.value.tipo_pessoa); 

  formData.append('nome', cliente.value.nome || '');

  if (cliente.value.tipo_pessoa === 'JURIDICA') {
      formData.append('razao_social', cliente.value.razao_social || '');
  } else {
       formData.append('razao_social', '');
  }

  formData.append('documento', cliente.value.documento || '');
  formData.append('email', cliente.value.email || '');
  formData.append('telefone', cliente.value.telefone || '');
  formData.append('tipo', cliente.value.tipo); 
  formData.append('observacoes', cliente.value.observacoes || '');
  formData.append('cep', cliente.value.cep || '');
  formData.append('logradouro', cliente.value.logradouro || '');
  formData.append('numero', cliente.value.numero || '');
  formData.append('complemento', cliente.value.complemento || '');
  formData.append('bairro', cliente.value.bairro || '');
  formData.append('cidade', cliente.value.cidade || '');
  formData.append('estado', cliente.value.estado || '');
  formData.append('ativo', cliente.value.ativo ? 'true' : 'false');


  if (profilePicFile.value) {
    formData.append('foto_perfil', profilePicFile.value);
  } else if (cliente.value.foto_perfil === null && isEditing.value) {
    formData.append('foto_perfil', '');
  }

  try {
    let response;
    if (isEditing.value && clienteId.value) {
      response = await apiClient.patch(`/v1/clientes/${clienteId.value}/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } else {
      response = await apiClient.post('/v1/clientes/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    }

    if (response.data) {
        alert(`Cliente ${isEditing.value ? 'atualizado' : 'criado'} com sucesso!`);
        router.push('/clientes');
    }

  } catch (error: any) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    let errorMessage = `Ocorreu um erro ao ${isEditing.value ? 'atualizar' : 'criar'} o cliente.`;
    
    // Tenta extrair a mensagem de erro da imobiliária
    if (error.response?.data?.imobiliaria) {
        errorMessage = `Ocorreu um erro de permissão. O servidor não recebeu o ID da imobiliária. Detalhe: ${error.response.data.imobiliaria[0]}. Verifique a configuração do seu serializador no backend.`;
    } else if (error.response?.data?.tipo_pessoa) {
        // Captura o erro específico que estava ocorrendo
        errorMessage = `Ocorreu um erro ao validar o Tipo de Pessoa. Detalhe: ${error.response.data.tipo_pessoa[0]}.`;
    }
    else if (error.response?.data) {
        const errors = error.response.data;
        const firstErrorKey = Object.keys(errors)[0];
        if (firstErrorKey && Array.isArray(errors[firstErrorKey])) {
            errorMessage += ` Detalhe: ${errors[firstErrorKey][0]}`;
        } else if (typeof errors === 'string') {
            errorMessage += ` Detalhe: ${errors}`;
        }
    }
    alert(errorMessage);
  } finally {
    isSubmitting.value = false;
  }
}


function handleCancel() {
  router.push('/clientes');
}
</script>


<style scoped>
.form-container {padding:0;max-width:1200px;margin:0 auto;}
.cliente-form{display:flex;flex-direction:column;gap:1.5rem;}
.main-form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:1.5rem;}
.form-card{background-color:#fff;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,.1);padding:1.5rem 2rem;}
.grid-col-span-2{grid-column:span 2;}
@media (max-width:1100px){.grid-col-span-2{grid-column:span 1;}}
.card-title{font-size:1.25rem;font-weight:600;color:#343a40;margin-top:0;margin-bottom:1.5rem;padding-bottom:.8rem;border-bottom:1px solid #e9ecef;}
.card-content-grid{display:grid;grid-template-columns:auto 1fr;gap:2rem;align-items:flex-start;}
@media (max-width:768px){.card-content-grid{grid-template-columns:1fr;}.profile-pic-area{margin-bottom:1.5rem;}}
.profile-pic-area{display:flex;flex-direction:column;align-items:center;gap:.8rem;}
.profile-pic-preview{width:130px;height:130px;border-radius:50%;overflow:hidden;background-color:#e9ecef;display:flex;justify-content:center;align-items:center;border:3px solid #dee2e6;margin-bottom:.5rem;}
.profile-img{width:100%;height:100%;object-fit:cover;}
.profile-icon{font-size:60px;color:#adb5bd;}
.upload-btn,.remove-btn{width:100%;}
.remove-btn{background-color:#f8d7da;color:#dc3545;border-color:#f5c6cb;}
.remove-btn:hover{background-color:#f1aeb5;}
.fields-area{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem 1.5rem;}
.form-group{display:flex;flex-direction:column;}
label{margin-bottom:.4rem;font-weight:500;font-size:.9rem;color:#495057;}
input[type="text"],input[type="email"],input[type="date"],select,textarea{padding:.75rem;border:1px solid #ced4da;border-radius:6px;font-size:.95rem;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;transition:border-color .2s ease,box-shadow .2s ease;}
input:focus,select:focus,textarea:focus{border-color:#86b7fe;outline:0;box-shadow:0 0 0 .25rem rgba(13,110,253,.25);}
textarea{resize:vertical;min-height:80px;}
.checkbox-group{display:flex;align-items:center;gap:.6rem;margin-top:.5rem;}
.checkbox-group input[type="checkbox"]{width:1.1em;height:1.1em;cursor:pointer;}
.checkbox-group label{margin-bottom:0;font-weight:normal;cursor:pointer;font-size:.95rem;}
.form-actions{display:flex;justify-content:flex-end;gap:1rem;margin-top:1rem;padding:1.5rem 2rem;background-color:#fff;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,.1);}
.btn-primary,.btn-secondary,.btn-action{padding:10px 20px;border:none;border-radius:6px;cursor:pointer;font-size:.95rem;font-weight:500;transition:background-color .2s ease,border-color .2s ease;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;display:inline-flex;align-items:center;gap:.5rem;}
.btn-primary{background-color:#0d6efd;color:white;}
.btn-primary:hover{background-color:#0b5ed7;}
.btn-secondary{background-color:#6c757d;color:white;}
.btn-secondary:hover{background-color:#5c636a;}
.btn-action{background-color:#f8f9fa;color:#343a40;border:1px solid #ced4da;}
.btn-action:hover{background-color:#e9ecef;}
.btn-action i{margin-right:0;}
.loading-message{text-align:center;padding:3rem;font-size:1.2rem;color:#6c757d;}
input[type="file"]{display:none;}
.tipo-pessoa-selector{display:flex;align-items:center;gap:1.5rem;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #eee;}
.tipo-pessoa-label{font-size:1.1rem;font-weight:600;color:#495057;margin:0;}
.tipo-pessoa-options{display:flex;gap:1rem;align-items:center;}
.radio-option{display:flex;align-items:center;cursor:pointer;font-size:.9rem;padding:.6rem 1rem;border:1px solid #ced4da;border-radius:6px;background-color:#fff;transition:background-color .2s,border-color .2s;}
.radio-option input[type="radio"]{margin-right:.5rem;accent-color:#0d6efd;}
.radio-option:hover{background-color:#f8f9fa;}
input[type="radio"]:checked+span{font-weight:600;color:#0d6efd;}
.radio-option:has(input:checked){border-color:#0d6efd;background-color:#e7f1ff;}
</style>
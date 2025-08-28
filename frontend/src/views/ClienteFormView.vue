<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Cliente' : 'Adicionar Novo Cliente' }}</h1>
      <router-link to="/clientes" class="btn-secondary">Voltar à Lista</router-link>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do cliente...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="cliente-form">
      <div class="form-section profile-pic-section">
        <h3 class="section-title">Foto de Perfil</h3>
        <div class="profile-pic-preview">
          <img v-if="profilePicPreview" :src="profilePicPreview" alt="Pré-visualização da Foto de Perfil" class="profile-img"/>
          <i v-else class="fas fa-user-circle profile-icon"></i>
        </div>
        <div class="profile-pic-controls">
          <label for="foto_perfil" class="btn-action">
            <i class="fas fa-camera"></i>
            <span>Escolher Foto</span>
            <input 
              type="file" 
              id="foto_perfil" 
              ref="profilePicInput" 
              @change="handleFileChange" 
              accept="image/*"
              hidden 
            />
          </label>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">Dados Pessoais</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="nome_completo">Nome Completo</label>
            <input type="text" id="nome_completo" v-model="cliente.nome_completo" required />
          </div>
          <div class="form-group">
            <label for="cpf_cnpj">CPF ou CNPJ</label>
            <input type="text" id="cpf_cnpj" v-model="cliente.cpf_cnpj" required />
          </div>
          <div class="form-group">
            <label for="inscricao_estadual">Inscrição Estadual</label>
            <input type="text" id="inscricao_estadual" v-model="cliente.inscricao_estadual" />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="cliente.email" required />
          </div>
          <div class="form-group">
            <label for="telefone">Telefone</label>
            <input type="tel" id="telefone" v-model="cliente.telefone" required />
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
            <label for="profissao">Profissão</label>
            <input type="text" id="profissao" v-model="cliente.profissao" />
          </div>
          <div class="form-group">
            <label for="estado_civil">Estado Civil</label>
            <input type="text" id="estado_civil" v-model="cliente.estado_civil" />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Endereço</h3>
        <div class="form-grid">
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
          <div class="form-group">
            <label for="cep">CEP</label>
            <input type="text" id="cep" v-model="cliente.cep" />
          </div>
        </div>
      </div>
      
      <div class="form-section full-width">
        <h3 class="section-title">Outras Informações</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="preferencias">Preferências do Imóvel (opcional)</label>
            <textarea id="preferencias" v-model="cliente.preferencias_imovel" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label for="observacoes">Observações (internas)</label>
            <textarea id="observacoes" v-model="cliente.observacoes" rows="4"></textarea>
          </div>
        </div>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Guardando...' : 'Guardar Cliente' }}
        </button>
      </div>
    </form>

    <ClienteAtividades v-if="isEditing && clienteId" :clienteId="clienteId" />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import ClienteAtividades from '@/components/ClienteAtividades.vue';

const route = useRoute();
const router = useRouter();

const clienteId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!clienteId.value);

const cliente = ref({
  nome_completo: '',
  cpf_cnpj: '',
  email: '',
  telefone: '',
  preferencias_imovel: '',
  data_nascimento: null,
  estado_civil: '',
  profissao: '',
  rg: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
  cep: '',
  observacoes: '',
  
  foto_perfil: null as File | null | string,
  inscricao_estadual: '',
});

const profilePicInput = ref<HTMLInputElement | null>(null);
const profilePicPreview = ref<string | null>(null);

const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchClienteData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/clientes/${clienteId.value}/`);
      cliente.value = { 
        ...cliente.value,
        ...response.data 
      };
      
      if (cliente.value.foto_perfil) {
        profilePicPreview.value = cliente.value.foto_perfil as string;
      }
    } catch (error) {
      console.error("Erro ao buscar dados do cliente:", error);
      alert("Não foi possível carregar os dados do cliente para edição.");
      router.push({ name: 'clientes' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    cliente.value.foto_perfil = file;
    profilePicPreview.value = URL.createObjectURL(file);
  } else {
    cliente.value.foto_perfil = null;
    profilePicPreview.value = null;
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  
  const payload = new FormData();
  
  // A correção está aqui: construir o FormData de forma mais segura.
  // Anexamos apenas os campos que são necessários para a API.
  
  if (cliente.value.nome_completo) payload.append('nome_completo', cliente.value.nome_completo);
  if (cliente.value.cpf_cnpj) payload.append('cpf_cnpj', cliente.value.cpf_cnpj);
  if (cliente.value.email) payload.append('email', cliente.value.email);
  if (cliente.value.telefone) payload.append('telefone', cliente.value.telefone);
  if (cliente.value.inscricao_estadual) payload.append('inscricao_estadual', cliente.value.inscricao_estadual);
  if (cliente.value.logradouro) payload.append('logradouro', cliente.value.logradouro);
  if (cliente.value.numero) payload.append('numero', cliente.value.numero);
  if (cliente.value.complemento) payload.append('complemento', cliente.value.complemento);
  if (cliente.value.bairro) payload.append('bairro', cliente.value.bairro);
  if (cliente.value.cidade) payload.append('cidade', cliente.value.cidade);
  if (cliente.value.estado) payload.append('estado', cliente.value.estado);
  if (cliente.value.cep) payload.append('cep', cliente.value.cep);
  if (cliente.value.observacoes) payload.append('observacoes', cliente.value.observacoes);
  if (cliente.value.preferencias_imovel) payload.append('preferencias_imovel', cliente.value.preferencias_imovel);
  
  // Lidamos com a foto de perfil separadamente, garantindo que seja um objeto File
  if (cliente.value.foto_perfil instanceof File) {
    payload.append('foto_perfil', cliente.value.foto_perfil, cliente.value.foto_perfil.name);
  }

  try {
    if (isEditing.value) {
      await apiClient.patch(`/v1/clientes/${clienteId.value}/`, payload);
    } else {
      await apiClient.post('/v1/clientes/', payload);
    }
    router.push({ name: 'clientes' });
  } catch (error: any) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o cliente. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'clientes' });
}

onMounted(() => {
  fetchClienteData();
});
</script>

<style scoped>
/* Os estilos existentes foram mantidos e aprimorados para o novo layout */
.form-container {
  padding: 2rem;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.cliente-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.form-section {
  width: 100%;
}
.section-title {
  font-size: 1.25rem;
  font-weight: bold;
  border-bottom: 2px solid #007bff;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
label {
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #495057;
}
input, textarea, select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  width: 100%;
  margin-top: 1rem;
}
.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.loading-message {
  text-align: center;
  padding: 2rem;
}

/* Novos estilos para a foto de perfil */
.profile-pic-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  width: 100%;
}
.profile-pic-preview {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #fff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  background-color: #e9ecef;
  display: flex;
  justify-content: center;
  align-items: center;
}
.profile-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.profile-icon {
  font-size: 80px;
  color: #adb5bd;
}
.profile-pic-controls {
  display: flex;
  gap: 1rem;
}
input[type="file"] {
  display: none;
}
</style>
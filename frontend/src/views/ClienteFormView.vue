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
      <div class="form-card">
        <h3 class="card-title">Dados Pessoais</h3>
        <div class="card-content-grid">
          <div class="profile-pic-area">
            <div class="profile-pic-preview">
              <img v-if="profilePicPreview" :src="profilePicPreview" alt="Pré-visualização da Foto de Perfil" class="profile-img"/>
              <i v-else class="fas fa-user-circle profile-icon"></i>
            </div>
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
          <div class="form-grid personal-data-grid">
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
      </div>
      <div class="form-card">
        <h3 class="card-title">Endereço</h3>
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
      <div class="form-card">
        <h3 class="card-title">Outras Informações</h3>
        <div class="form-grid">
          <div class="form-group full-width">
            <label for="preferencias">Preferências do Imóvel (opcional)</label>
            <textarea id="preferencias" v-model="cliente.preferencias_imovel" rows="4"></textarea>
          </div>
          <div class="form-group full-width">
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

// Objeto reativo para os dados do formulário
const cliente = ref({
  nome_completo: '',
  cpf_cnpj: '',
  email: '',
  telefone: '',
  preferencias_imovel: '',
  data_nascimento: null as string | null,
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
  inscricao_estadual: '',
});

const profilePicInput = ref<HTMLInputElement | null>(null);
const profilePicPreview = ref<string | null>(null);
const newProfilePicFile = ref<File | null>(null);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchClienteData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/clientes/${clienteId.value}/`);
      // Popula o ref 'cliente' apenas com os campos do formulário
      Object.keys(cliente.value).forEach(key => {
        if (response.data[key] !== undefined) {
          (cliente.value as any)[key] = response.data[key];
        }
      });
      // Define a preview da imagem separadamente
      if (response.data.foto_perfil) {
        profilePicPreview.value = response.data.foto_perfil;
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
    newProfilePicFile.value = file;
    profilePicPreview.value = URL.createObjectURL(file);
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  
  const payload = new FormData();
  
  // Adiciona apenas os campos de texto do formulário ao payload
  Object.keys(cliente.value).forEach(key => {
    const value = cliente.value[key as keyof typeof cliente.value];
    if (value !== null && value !== undefined && value !== '') {
      payload.append(key, String(value));
    }
  });
  
  // Adiciona a foto APENAS se uma NOVA foi selecionada
  if (newProfilePicFile.value) {
    payload.append('foto_perfil', newProfilePicFile.value);
  }

  try {
    const url = isEditing.value ? `/v1/clientes/${clienteId.value}/` : '/v1/clientes/';
    const method = isEditing.value ? 'patch' : 'post';
    
    // Configuração para forçar multipart/form-data
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    };
    
    await apiClient[method](url, payload, config);
    
    alert('Cliente salvo com sucesso!');
    router.push({ name: 'clientes' });
  } catch (error: any) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o cliente. Verifique os dados no console.');
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
/* SEUS ESTILOS ESTÃO MANTIDOS */
.form-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}
h1 {
  font-size: 2rem;
  color: #333;
}
.cliente-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}
.form-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  width: 100%;
  margin-bottom: 1.5rem;
}
.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
}
.card-content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
@media (min-width: 768px) {
  .card-content-grid {
    grid-template-columns: 180px 1fr;
    align-items: start;
  }
}
.profile-pic-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-right: 1px solid #f0f0f0;
}
@media (max-width: 767px) {
  .profile-pic-area {
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
  }
}
.profile-pic-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #007bff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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
  font-size: 60px;
  color: #adb5bd;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.personal-data-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
label {
  margin-bottom: 0.4rem;
  font-weight: 500;
  color: #495057;
  font-size: 0.95rem;
}
input, textarea, select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
input:focus, textarea:focus, select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  outline: none;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  width: 100%;
  margin-top: 2rem;
}
.btn-primary, .btn-secondary, .btn-action {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: background-color 0.2s, color 0.2s, box-shadow 0.2s;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0056b3;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.3);
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
  box-shadow: 0 2px 6px rgba(108, 117, 125, 0.3);
}
.btn-action {
  background-color: #e9ecef;
  color: #343a40;
  border: 1px solid #ced4da;
}
.btn-action:hover {
  background-color: #dee2e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}
.btn-action i {
  margin-right: 0.5rem;
}
.loading-message {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #6c757d;
}
input[type="file"] {
  display: none;
}
@media (max-width: 576px) {
  .form-container {
    padding: 1rem;
  }
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.8rem;
  }
  h1 {
    font-size: 1.75rem;
  }
  .card-title {
    font-size: 1.2rem;
  }
  .btn-primary, .btn-secondary, .btn-action {
    width: 100%;
    padding: 12px;
  }
  .form-actions {
    flex-direction: column;
  }
}
</style>
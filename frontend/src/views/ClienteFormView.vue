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
              <label for="foto_perfil" class="btn-action">
                <i class="fas fa-camera"></i>
                <span>Escolher Foto</span>
                <input type="file" id="foto_perfil" ref="profilePicInput" @change="handleFileChange" accept="image/*" hidden />
              </label>
            </div>
            
            <div v-if="cliente.tipo_pessoa === 'FISICA'" class="form-grid">
              <div class="form-group">
                <label for="nome">Nome Completo</label>
                <input type="text" id="nome" v-model="cliente.nome" required />
              </div>
              <div class="form-group">
                <label for="documento_cpf">CPF</label>
                <input type="text" id="documento_cpf" v-model="cliente.documento" v-mask="'###.###.###-##'" required />
              </div>
              <div class="form-group">
                <label for="rg">RG</label>
                <input type="text" id="rg" v-model="cliente.rg" />
              </div>
              <div class="form-group">
                <label for="data_nascimento">Data de Nascimento</label>
                <input type="date" id="data_nascimento" v-model="cliente.data_nascimento" />
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
            
            <div v-if="cliente.tipo_pessoa === 'JURIDICA'" class="form-grid">
              <div class="form-group">
                <label for="razao_social">Razão Social</label>
                <input type="text" id="razao_social" v-model="cliente.razao_social" required />
              </div>
              <div class="form-group">
                <label for="nome_fantasia">Nome Fantasia</label>
                <input type="text" id="nome_fantasia" v-model="cliente.nome" required />
              </div>
              <div class="form-group">
                <label for="documento_cnpj">CNPJ</label>
                <input type="text" id="documento_cnpj" v-model="cliente.documento" v-mask="'##.###.###/####-##'" required />
              </div>
              <div class="form-group">
                <label for="inscricao_estadual">Inscrição Estadual</label>
                <input type="text" id="inscricao_estadual" v-model="cliente.inscricao_estadual" />
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-card">
          <h3 class="card-title">Contato e Endereço</h3>
          <div class="form-grid">
            <div class="form-group">
              <label for="email">Email</label>
              <input type="email" id="email" v-model="cliente.email" required />
            </div>
            <div class="form-group">
              <label for="telefone">Telefone</label>
              <input type="tel" id="telefone" v-model="cliente.telefone" required />
            </div>
            <div class="form-group">
              <label for="cep">CEP</label>
              <input type="text" id="cep" v-model="cliente.cep" v-mask="'#####-###'" />
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
          <div class="form-grid-single-col">
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
      </div>

      <div class="form-actions">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A Guardar...' : 'Guardar Cliente' }}
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

const vMask = {
  beforeMount(el: HTMLInputElement, binding: { value: string }) {
    const handler = (event: Event) => {
      if ((event as CustomEvent).detail?.fromMask) return;
      let value = el.value.replace(/\D/g, '');
      const mask = binding.value;
      const maskChars = mask.split('').filter(c => c === '#').length;
      if (value.length > maskChars) {
        value = value.slice(0, maskChars);
      }
      let result = '';
      let i = 0;
      for (const char of mask) {
        if (i >= value.length) break;
        if (char === '#') {
          result += value[i];
          i++;
        } else {
          result += char;
        }
      }
      if (el.value !== result) {
        el.value = result;
        const customEvent = new CustomEvent('input', { detail: { fromMask: true } });
        el.dispatchEvent(customEvent);
      }
    };
    el.addEventListener('input', handler);
  }
};

const route = useRoute();
const router = useRouter();
const clienteId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!clienteId.value);

const cliente = ref({
  tipo_pessoa: 'FISICA',
  nome: '',
  documento: '',
  razao_social: '',
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
const tipoPessoaOriginal = ref('');

const onTipoPessoaChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const newType = target.value;

  if (newType !== cliente.value.tipo_pessoa) {
    const confirmation = window.confirm(
      "Atenção!\nAo mudar o tipo de pessoa, alguns campos específicos serão limpos.\nDeseja continuar?"
    );

    if (confirmation) {
      cliente.value.tipo_pessoa = newType;
      cliente.value.documento = '';
      if (newType === 'FISICA') {
        cliente.value.razao_social = '';
        cliente.value.inscricao_estadual = '';
      } else {
        cliente.value.rg = '';
        cliente.value.data_nascimento = null;
        cliente.value.estado_civil = '';
        cliente.value.profissao = '';
      }
    } else {
        // Força o input de rádio a voltar ao estado anterior
        const radioGroup = document.getElementsByName('tipo_pessoa_radio');
        radioGroup.forEach(radio => {
            const r = radio as HTMLInputElement;
            if (r.value === cliente.value.tipo_pessoa) {
                r.checked = true;
            }
        });
    }
  }
};

async function fetchClienteData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/clientes/${clienteId.value}/`);
      Object.keys(cliente.value).forEach(key => {
        if (response.data[key] !== undefined && response.data[key] !== null) {
          (cliente.value as any)[key] = response.data[key];
        }
      });
      tipoPessoaOriginal.value = cliente.value.tipo_pessoa;
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
  const clienteData = { ...cliente.value };
  clienteData.documento = clienteData.documento.replace(/\D/g, '');

  Object.keys(clienteData).forEach(key => {
    const value = clienteData[key as keyof typeof clienteData];
    if (value !== null && value !== undefined && value !== '') {
      payload.append(key, String(value));
    }
  });
  
  if (newProfilePicFile.value) {
    payload.append('foto_perfil', newProfilePicFile.value);
  }

  try {
    const url = isEditing.value ? `/v1/clientes/${clienteId.value}/` : '/v1/clientes/';
    const method = isEditing.value ? 'patch' : 'post';
    const config = { headers: { 'Content-Type': 'multipart/form-data' } };
    await apiClient[method](url, payload, config);
    alert('Cliente salvo com sucesso!');
    router.push({ name: 'clientes' });
  } catch (error: any) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    const errorData = error.response?.data;
    let errorMessage = 'Ocorreu um erro ao guardar o cliente.';
    if (typeof errorData === 'object' && errorData !== null) {
      errorMessage = Object.entries(errorData)
        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
        .join('\n');
    }
    alert(errorMessage);
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
/* ESTILOS COMPLETAMENTE REFATORADOS PARA UM LAYOUT MAIS COMPACTO E PROFISSIONAL */
.form-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}
h1 {
  font-size: 1.75rem;
  color: #343a40;
}
.cliente-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Grelha principal para os cartões */
.main-form-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
}
@media (min-width: 1024px) {
    .main-form-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .grid-col-span-2 {
        grid-column: span 2 / span 2;
    }
}

.form-card {
  background-color: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  width: 100%;
}
.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e9ecef;
}
.card-content-grid {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 1.5rem;
  align-items: flex-start;
}
.profile-pic-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  padding-right: 1.5rem;
  border-right: 1px solid #f1f3f5;
}
.profile-pic-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #dee2e6;
  background-color: #f8f9fa;
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
  font-size: 50px;
  color: #ced4da;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.form-grid-single-col {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
label {
  margin-bottom: 0.3rem;
  font-weight: 500;
  color: #495057;
  font-size: 0.875rem;
}
input, textarea, select {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
input:focus, textarea:focus, select:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  outline: none;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  width: 100%;
  margin-top: 1rem;
}
.btn-primary, .btn-secondary, .btn-action {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-action { background-color: #f8f9fa; color: #343a40; border: 1px solid #ced4da; }
.btn-action:hover { background-color: #e9ecef; }
.btn-action i { margin-right: 0.5rem; }
.loading-message { text-align: center; padding: 3rem; font-size: 1.2rem; color: #6c757d; }
input[type="file"] { display: none; }

.tipo-pessoa-selector {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.tipo-pessoa-label {
    font-size: 1.1rem;
    font-weight: 600;
    color: #495057;
    margin: 0;
}
.tipo-pessoa-options {
    display: flex;
    gap: 1rem;
    align-items: center;
}
.radio-option {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-size: 0.9rem;
    padding: 0.6rem 1rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    transition: all 0.2s ease-in-out;
}
.radio-option input[type="radio"] { display: none; }
.radio-option span { margin: 0; }
.radio-option:has(input:checked) {
    background-color: #e7f1ff;
    border-color: #007bff;
    color: #0056b3;
    font-weight: 500;
}
.radio-option:hover {
    border-color: #80bdff;
}

@media (max-width: 768px) {
  .card-content-grid {
    grid-template-columns: 1fr;
  }
  .profile-pic-area {
    border-right: none;
    border-bottom: 1px solid #f1f3f5;
    margin-bottom: 1.5rem;
    padding-right: 0;
    padding-bottom: 1.5rem;
  }
}
</style>
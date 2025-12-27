<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">{{ formTitle }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>A carregar...</p>
    </div>

    <div v-else class="form-card">
      <form @submit.prevent="submitForm" enctype="multipart/form-data">
        
        <div class="form-group">
          <label for="nome_banco" class="form-label">Banco:</label>
          <select id="nome_banco" v-model="config.nome_banco" class="form-input" required>
            <option value="Bradesco">Bradesco</option>
            <option value="Itau">Itaú</option>
            <option value="Santander">Santander</option>
          </select>
        </div>

        <hr>
        <h4>Dados para Remessa (CNAB)</h4>
        
        <div class="form-group">
          <label for="agencia" class="form-label">Agência (sem dígito):</label>
          <input type="text" id="agencia" v-model="config.agencia" class="form-input" required>
        </div>
        
        <div class="form-group">
          <label for="conta" class="form-label">Conta Corrente (sem dígito):</label>
          <input type="text" id="conta" v-model="config.conta" class="form-input" required>
        </div>
        
        <div class="form-group">
          <label for="convenio" class="form-label">Convênio / Código do Cedente:</label>
          <input type="text" id="convenio" v-model="config.convenio" class="form-input" required>
        </div>

        <hr>
        <h4>Credenciais da API (Opcional, para consulta direta)</h4>

        <div class="form-group">
          <label for="client_id" class="form-label">Client ID:</label>
          <input type="text" id="client_id" v-model="config.client_id" class="form-input">
        </div>
        
        <div class="form-group">
          <label for="client_secret" class="form-label">Client Secret:</label>
          <input type="text" id="client_secret" v-model="config.client_secret" class="form-input">
        </div>
        
        <hr>
        <h4>Certificados (Opcional, para API Bradesco)</h4>
        
        <div class="form-group">
            <label for="certificado_file" class="form-label">Certificado (CRT/PEM):</label>
            <input type="file" id="certificado_file" @change="handleFileChange('certificado_file', $event)" class="form-input">
            <small v-if="config.certificado_file">{{ getFileName(config.certificado_file) }}</small>
        </div>

        <div class="form-group">
            <label for="chave_privada_file" class="form-label">Chave Privada (KEY):</label>
            <input type="file" id="chave_privada_file" @change="handleFileChange('chave_privada_file', $event)" class="form-input">
            <small v-if="config.chave_privada_file">{{ getFileName(config.chave_privada_file) }}</small>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="actions">
          <button type="submit" class="submit-button" :disabled="isSubmitting">
            {{ isSubmitting ? 'A salvar...' : 'Salvar' }}
          </button>
          <router-link :to="{ name: 'integracoes' }" class="cancel-link">Cancelar</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';

interface Config {
  id?: number;
  nome_banco: string;
  client_id: string;
  client_secret: string;
  certificado_file: File | string | null;
  chave_privada_file: File | string | null;
  // NOVOS CAMPOS
  agencia: string;
  conta: string;
  convenio: string;
}

const route = useRoute();
const router = useRouter();

const config = ref<Config>({
  nome_banco: 'Bradesco',
  client_id: '',
  client_secret: '',
  certificado_file: null,
  chave_privada_file: null,
  agencia: '',
  conta: '',
  convenio: '',
});

const isLoading = ref(false);
const isSubmitting = ref(false);
const error = ref<string | null>(null);

const isEditing = computed(() => !!route.params.id);
const formTitle = computed(() => isEditing.value ? 'Editar Configuração de Banco' : 'Adicionar Nova Configuração de Banco');

const fetchConfig = async (id: number) => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get(`/v1/boletos/configuracoes-banco/${id}/`);
    config.value = { ...response.data, certificado_file: response.data.certificado_file, chave_privada_file: response.data.chave_privada_file };
  } catch (err) {
    console.error('Erro ao buscar configuração:', err);
    error.value = 'Falha ao carregar os dados da configuração.';
    router.push({ name: 'integracoes' });
  } finally {
    isLoading.value = false;
  }
};

const handleFileChange = (field: keyof Config, event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    config.value[field] = target.files[0];
  }
};

const getFileName = (file: File | string | null) => {
    if (!file) return '';
    return file instanceof File ? file.name : (file ? file.split('/').pop() : '');
};


const submitForm = async () => {
  isSubmitting.value = true;
  error.value = null;
  const formData = new FormData();
  formData.append('nome_banco', config.value.nome_banco);
  formData.append('agencia', config.value.agencia);
  formData.append('conta', config.value.conta);
  formData.append('convenio', config.value.convenio);
  formData.append('client_id', config.value.client_id);
  formData.append('client_secret', config.value.client_secret);
  
  if (config.value.certificado_file instanceof File) {
    formData.append('certificado_file', config.value.certificado_file);
  }
  if (config.value.chave_privada_file instanceof File) {
    formData.append('chave_privada_file', config.value.chave_privada_file);
  }

  try {
    if (isEditing.value) {
      await api.patch(`/v1/boletos/configuracoes-banco/${config.value.id}/`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
      });
    } else {
      await api.post('/v1/boletos/configuracoes-banco/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
      });
    }
    router.push({ name: 'integracoes' });
  } catch (err: any) {
    console.error('Erro ao salvar configuração:', err);
    if (err.response && err.response.data) {
        error.value = JSON.stringify(err.response.data);
    } else {
        error.value = 'Falha ao salvar a configuração. Verifique os dados e tente novamente.';
    }
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  if (isEditing.value) {
    fetchConfig(Number(route.params.id));
  }
});
</script>

<style scoped>
/* Estilos permanecem os mesmos */
.page-container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
.header-section { margin-bottom: 2rem; text-align: center; }
.page-title { font-size: 2rem; font-weight: bold; color: #333; }
.form-card { background-color: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
.loading-state { text-align: center; font-size: 1.2rem; color: #666; }
.form-group { margin-bottom: 1.5rem; }
.form-label { display: block; font-weight: bold; margin-bottom: 0.5rem; color: #555; }
.form-input { width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 1rem; transition: border-color 0.3s; }
.form-input:focus { outline: none; border-color: #007bff; }
.actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem; }
.submit-button, .cancel-link { padding: 12px 24px; border-radius: 6px; text-decoration: none; font-size: 1rem; font-weight: bold; cursor: pointer; transition: background-color 0.3s, color 0.3s; }
.submit-button { background-color: #007bff; color: white; border: none; }
.submit-button:hover { background-color: #0056b3; }
.cancel-link { background-color: #6c757d; color: white; border: none; }
.cancel-link:hover { background-color: #5a6268; }
.error-message { color: #d9534f; background-color: #f2dede; border: 1px solid #ebccd1; padding: 10px; border-radius: 4px; text-align: center; margin-bottom: 1rem; }
hr { margin: 2rem 0; border: 0; border-top: 1px solid #eee; }
h4 { margin-top: 0; }
</style>
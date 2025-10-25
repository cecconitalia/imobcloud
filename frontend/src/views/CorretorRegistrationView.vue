<template>
  <div class="registration-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Utilizador' : 'Registar Novo Utilizador' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do utilizador...
    </div>

    <div v-else class="form-container">
      <form @submit.prevent="handleSubmit" class="registration-form">
        <div class="form-group">
          <label for="username">Nome de Utilizador</label>
          <input type="text" id="username" v-model="user.username" required />
        </div>

        <div class="form-group">
          <label for="first_name">Nome completo</label>
          <input type="text" id="first_name" v-model="user.first_name" required />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="user.email" required />
        </div>

        <div class="form-group">
          <label for="creci">CRECI</label>
          <input type="text" id="creci" v-model="user.perfil.creci" />
        </div>

        <div class="form-group">
          <label for="telefone">Telefone</label>
          <input type="tel" id="telefone" v-model="user.perfil.telefone" />
        </div>

        <div class="form-group">
          <label for="cargo">Cargo</label>
          <select id="cargo" v-model="user.perfil.cargo" required>
            <option value="CORRETOR">Corretor</option>
            <option value="ADMIN">Administrador</option>
          </select>
        </div>

        <div class="form-group full-width">
          <h3>Endereço</h3>
        </div>

        <div class="form-group">
          <label for="logradouro">Logradouro</label>
          <input type="text" id="logradouro" v-model="user.perfil.endereco_logradouro" />
        </div>

        <div class="form-group">
          <label for="numero">Número</label>
          <input type="text" id="numero" v-model="user.perfil.endereco_numero" />
        </div>

        <div class="form-group">
          <label for="bairro">Bairro</label>
          <input type="text" id="bairro" v-model="user.perfil.endereco_bairro" />
        </div>

        <div class="form-group">
          <label for="cidade">Cidade</label>
          <input type="text" id="cidade" v-model="user.perfil.endereco_cidade" />
        </div>

        <div class="form-group">
          <label for="estado">Estado (UF)</label>
          <input type="text" id="estado" maxlength="2" v-model="user.perfil.endereco_estado" />
        </div>

        <div class="form-group">
          <label for="cep">CEP</label>
          <input type="text" id="cep" v-model="user.perfil.endereco_cep" />
        </div>

        <div class="form-group full-width">
          <label for="observacoes">Observações</label>
          <textarea id="observacoes" v-model="user.perfil.observacoes"></textarea>
        </div>

        <div class="form-group full-width">
            <label for="google_json_file">Credenciais do Google Calendar (arquivo JSON)</label>
            <input type="file" id="google_json_file" @change="handleFileUpload" accept=".json" />
        </div>

        <div class="form-group full-width" v-if="isEditing && user.perfil.google_json_file">
          <h3>Integração com o Google Calendar</h3>
          <div v-if="user.perfil.google_calendar_token">
            <p class="success-message">Conta do Google Calendar já conectada!</p>
          </div>
          <div v-else>
            <p>Conecte-se à sua conta do Google para agendar tarefas automaticamente no seu calendário.</p>
            <button type="button" @click="handleGoogleAuth" class="btn-google">
              Conectar com o Google
            </button>
          </div>
        </div>

        <div class="form-group full-width">
          <label for="password">Nova Palavra-passe (opcional)</label>
          <input type="password" id="password" v-model="user.password" :placeholder="isEditing ? 'Deixe vazio para manter a atual' : ''" :required="!isEditing" />
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="form-actions full-width">
          <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'A guardar...' : (isEditing ? 'Guardar Alterações' : 'Registar Utilizador') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();

const userId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!userId.value);

const user = ref({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  perfil: {
    cargo: 'CORRETOR',
    creci: '',
    telefone: '',
    endereco_logradouro: '',
    endereco_numero: '',
    endereco_bairro: '',
    endereco_cidade: '',
    endereco_estado: '',
    endereco_cep: '',
    observacoes: '',
    google_json_file: null as File | null,
    google_calendar_token: null as string | null,
  },
});

const isLoadingData = ref(false);
const isSubmitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

async function fetchUserData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      // CORREÇÃO: URL corrigida, o prefixo 'core/' foi removido
      const response = await apiClient.get(`/v1/corretores/${userId.value}/`);
      user.value.username = response.data.username;
      user.value.first_name = response.data.first_name;
      user.value.last_name = response.data.last_name;
      user.value.email = response.data.email;
      user.value.perfil = response.data.perfil;
    } catch (error) {
      console.error("Erro ao buscar dados do utilizador:", error);
      alert("Não foi possível carregar os dados do utilizador para edição.");
      router.push({ name: 'corretores' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

function handleFileUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
        user.value.perfil.google_json_file = target.files[0];
    }
}

function handleGoogleAuth() {
  window.location.href = `${apiClient.defaults.baseURL}/v1/clientes/google-calendar-auth/`;
}

async function handleSubmit() {
  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  const formData = new FormData();
  formData.append('username', user.value.username);
  formData.append('first_name', user.value.first_name);
  formData.append('last_name', user.value.last_name);
  formData.append('email', user.value.email);
  if (user.value.password) {
    formData.append('password', user.value.password);
  }

  if (user.value.perfil.cargo) { formData.append('perfil.cargo', user.value.perfil.cargo); }
  if (user.value.perfil.creci) { formData.append('perfil.creci', user.value.perfil.creci); }
  if (user.value.perfil.telefone) { formData.append('perfil.telefone', user.value.perfil.telefone); }
  if (user.value.perfil.endereco_logradouro) { formData.append('perfil.endereco_logradouro', user.value.perfil.endereco_logradouro); }
  if (user.value.perfil.endereco_numero) { formData.append('perfil.endereco_numero', user.value.perfil.endereco_numero); }
  if (user.value.perfil.endereco_bairro) { formData.append('perfil.endereco_bairro', user.value.perfil.endereco_bairro); }
  if (user.value.perfil.endereco_cidade) { formData.append('perfil.endereco_cidade', user.value.perfil.endereco_cidade); }
  if (user.value.perfil.endereco_estado) { formData.append('perfil.endereco_estado', user.value.perfil.endereco_estado); }
  if (user.value.perfil.endereco_cep) { formData.append('perfil.endereco_cep', user.value.perfil.endereco_cep); }
  if (user.value.perfil.observacoes) { formData.append('perfil.observacoes', user.value.perfil.observacoes); }
  if (user.value.perfil.google_json_file) {
    formData.append('perfil.google_json_file', user.value.perfil.google_json_file);
  }
  if (user.value.perfil.google_calendar_token) {
    formData.append('perfil.google_calendar_token', user.value.perfil.google_calendar_token);
  }

  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/corretores/${userId.value}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      successMessage.value = 'Utilizador atualizado com sucesso!';
    } else {
      await apiClient.post('/v1/corretores/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      successMessage.value = 'Utilizador registado com sucesso!';
      user.value = {
        username: '', first_name: '', last_name: '', email: '', password: '',
        perfil: {
          cargo: 'CORRETOR', creci: '', telefone: '', endereco_logradouro: '',
          endereco_numero: '', endereco_bairro: '', endereco_cidade: '',
          endereco_estado: '', endereco_cep: '', observacoes: '',
          google_json_file: null, google_calendar_token: null,
        }
      };
    }

    setTimeout(() => {
        router.push({ name: 'corretores' });
    }, 1500);

  } catch (err: any) {
    console.error("Erro ao guardar utilizador:", err.response?.data || err);
    if (err.response?.data?.username?.length > 0) {
        errorMessage.value = `Erro: ${err.response.data.username[0]}`;
    } else if (err.response?.data?.email?.length > 0) {
        errorMessage.value = `Erro: ${err.response.data.email[0]}`;
    } else {
        errorMessage.value = "Ocorreu um erro ao guardar o utilizador. Verifique os dados.";
    }
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'corretores' });
}

onMounted(() => {
  fetchUserData();
});
</script>

<style scoped>
.registration-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.form-container {
  max-width: 600px;
  margin: 0 auto;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}
.form-group {
  margin-bottom: 1rem;
  flex: 1 1 calc(50% - 1.5rem);
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
    flex-basis: 100%;
}
label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.5rem;
}
input, select, textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.btn-google {
  background-color: #4285F4;
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}
.btn-google:hover {
  background-color: #357ae8;
}
.form-actions {
  margin-top: 1.5rem;
  text-align: right;
  flex-basis: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.loading-message { text-align: center; padding: 2rem; }
.success-message { color: green; font-weight: bold; }
.error-message { color: red; font-weight: bold; }
</style>
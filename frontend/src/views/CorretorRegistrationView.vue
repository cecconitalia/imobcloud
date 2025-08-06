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
          <label for="first_name">Primeiro Nome</label>
          <input type="text" id="first_name" v-model="user.first_name" required />
        </div>
        
        <div class="form-group">
          <label for="last_name">Apelido</label>
          <input type="text" id="last_name" v-model="user.last_name" required />
        </div>
        
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="user.email" required />
        </div>
        
        <div class="form-group">
          <label for="password">Nova Palavra-passe (opcional)</label>
          <input type="password" id="password" v-model="user.password" :placeholder="isEditing ? 'Deixe vazio para manter a atual' : ''" :required="!isEditing" />
        </div>
        
        <div class="form-group">
          <label for="cargo">Cargo</label>
          <select id="cargo" v-model="user.perfil.cargo" required>
            <option value="CORRETOR">Corretor</option>
            <option value="ADMIN">Administrador</option>
          </select>
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="form-actions">
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
  perfil: { cargo: 'CORRETOR' },
});

const isLoadingData = ref(false);
const isSubmitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

async function fetchUserData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/core/corretores/${userId.value}/`);
      user.value.username = response.data.username;
      user.value.first_name = response.data.first_name;
      user.value.last_name = response.data.last_name;
      user.value.email = response.data.email;
      user.value.perfil.cargo = response.data.perfil.cargo;
      
    } catch (error) {
      console.error("Erro ao buscar dados do utilizador:", error);
      alert("Não foi possível carregar os dados do utilizador para edição.");
      router.push({ name: 'corretores' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const payload = {
      username: user.value.username,
      first_name: user.value.first_name,
      last_name: user.value.last_name,
      email: user.value.email,
      password: user.value.password,
      perfil: user.value.perfil,
    };
    if (isEditing.value && !payload.password) {
      delete payload.password;
    }

    if (isEditing.value) {
      await apiClient.put(`/v1/core/corretores/${userId.value}/`, payload);
      successMessage.value = 'Utilizador atualizado com sucesso!';
    } else {
      await apiClient.post('/v1/core/corretores/', payload);
      successMessage.value = 'Utilizador registado com sucesso!';
      user.value = {
        username: '',
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        perfil: { cargo: 'CORRETOR' }
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
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.5rem;
}
input, select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.form-actions {
  margin-top: 1.5rem;
  text-align: right;
}
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.loading-message { text-align: center; padding: 2rem; }
</style>
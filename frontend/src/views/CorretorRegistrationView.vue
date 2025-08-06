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
      user.value.perfil.cargo = response.data.cargo; // Atualiza o cargo no objeto aninhado
      // A password não é preenchida por segurança
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
      user.value = { username: '', password: '', perfil: { cargo: 'CORRETOR' } };
    }
    
    setTimeout(() => {
        router.push({ name: 'corretores' });
    }, 1500);

  } catch (err: any) {
    console.error("Erro ao guardar utilizador:", err.response?.data || err);
    if (err.response?.data?.username?.length > 0) {
        errorMessage.value = `Erro: ${err.response.data.username[0]}`;
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
/* Os estilos permanecem os mesmos que antes */
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
.btn-primary {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.btn-primary:disabled {
  background-color: #a0cfff;
}
.success-message {
  color: green;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}
.error-message {
  color: red;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}
</style>
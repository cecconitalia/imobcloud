<template>
  <div class="registration-container">
    <header class="view-header">
      <h1>Registar Novo Corretor</h1>
    </header>

    <div class="form-container">
      <form @submit.prevent="handleRegistration" class="registration-form">
        <div class="form-group">
          <label for="username">Nome de Utilizador</label>
          <input type="text" id="username" v-model="username" required />
        </div>

        <div class="form-group">
          <label for="password">Palavra-passe</label>
          <input type="password" id="password" v-model="password" required />
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary" :disabled="isLoading">
            {{ isLoading ? 'A registar...' : 'Registar Corretor' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import apiClient from '@/services/api';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const isLoading = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

async function handleRegistration() {
  isLoading.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const response = await apiClient.post('/v1/core/register_corretor/', {
      username: username.value,
      password: password.value,
    });
    successMessage.value = response.data.message;
    username.value = '';
    password.value = '';
  } catch (err) {
    console.error("Erro ao registar corretor:", err.response?.data || err);
    errorMessage.value = "Ocorreu um erro ao registar o corretor. Verifique os dados.";
  } finally {
    isLoading.value = false;
  }
}
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
input {
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
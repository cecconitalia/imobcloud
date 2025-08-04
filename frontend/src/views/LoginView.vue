<template>
  <div class="login-container">
    <div class="login-box">
      <h2>ImobCloud Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Utilizador</label>
          <input type="text" id="username" v-model="username" required />
        </div>
        <div class="form-group">
          <label for="password">Palavra-passe</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        <button type="submit" class="login-button" :disabled="isLoading">
          {{ isLoading ? 'A entrar...' : 'Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // 1. Importar o router novamente
import apiClient from '@/services/api';

const username = ref('');
const password = ref('');
const errorMessage = ref<string | null>(null);
const isLoading = ref(false);
const router = useRouter(); // 2. Inicializar o router

async function handleLogin() {
  isLoading.value = true;
  errorMessage.value = null;
  try {
    const response = await apiClient.post('/token/', {
      username: username.value,
      password: password.value,
    });
    
    // Guarda o token no armazenamento local
    const accessToken = response.data.access;
    localStorage.setItem('authToken', accessToken);
    
    // --- LÓGICA DE REDIRECIONAMENTO CORRIGIDA ---
    // Usa o router para navegar para a página de imóveis.
    router.push({ name: 'imoveis' });

  } catch (error) {
    console.error("Erro no login:", error);
    errorMessage.value = 'Utilizador ou palavra-passe inválidos.';
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-box {
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}
h2 {
  text-align: center;
  margin-bottom: 1.5rem;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
.login-button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}
.login-button:disabled {
  background-color: #a0cfff;
}
.error-message {
  color: red;
  text-align: center;
  margin-bottom: 1rem;
}
</style>
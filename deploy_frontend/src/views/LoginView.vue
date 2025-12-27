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
import { useRouter, useRoute } from 'vue-router';
import apiClient from '@/services/api';

const username = ref('');
const password = ref('');
const errorMessage = ref<string | null>(null);
const isLoading = ref(false);
const router = useRouter();
const route = useRoute(); 

async function handleLogin() {
  isLoading.value = true;
  errorMessage.value = null;
  try {
    // Com a baseURL definida como 'http://localhost:8000/api', 
    // esta chamada resultará em 'http://localhost:8000/api/v1/token/'
    const response = await apiClient.post('/v1/token/', {
      username: username.value,
      password: password.value,
    });
    
    const accessToken = response.data.access;
    const userCargo = response.data.cargo;
    const imobiliariaName = response.data.imobiliaria_name;
    const userName = response.data.user_name;

    // Salva no localStorage
    localStorage.setItem('authToken', accessToken);
    localStorage.setItem('userCargo', userCargo);
    localStorage.setItem('imobiliariaName', imobiliariaName);
    localStorage.setItem('userName', userName);
    
    // IMPORTANTE: Atualiza o header do axios imediatamente para requisições subsequentes
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

    // Redirecionamento inteligente
    const nextUrl = route.query.next;
    if (nextUrl && typeof nextUrl === 'string') {
      router.push(nextUrl);
    } else {
      router.push({ name: 'dashboard' });
    }

  } catch (error: any) {
    console.error("Erro no login:", error);
    if (error.response && error.response.status === 401) {
        errorMessage.value = 'Utilizador ou palavra-passe incorretos.';
    } else {
        errorMessage.value = 'Falha ao conectar com o servidor.';
    }
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
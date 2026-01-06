<template>
    <div class="login-container">
        <div class="login-card">
            <div class="brand-section">
                <div class="logo-circle">
                    <i class="fas fa-laptop-house"></i>
                </div>
                <h1>ImobHome</h1>
                <p>Gestão Imobiliária Inteligente</p>
            </div>

            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label for="username">Usuário ou E-mail</label>
                    <div class="input-wrapper">
                        <i class="fas fa-user input-icon"></i>
                        <input 
                            id="username" 
                            v-model="username" 
                            type="text" 
                            placeholder="Seu usuário de acesso"
                            required
                            :disabled="isLoading"
                        />
                    </div>
                </div>

                <div class="form-group">
                    <label for="password">Senha</label>
                    <div class="input-wrapper">
                        <i class="fas fa-lock input-icon"></i>
                        <input 
                            id="password" 
                            v-model="password" 
                            :type="showPassword ? 'text' : 'password'" 
                            placeholder="Sua senha segura"
                            required
                            :disabled="isLoading"
                        />
                        <i 
                            class="fas toggle-password"
                            :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"
                            @click="showPassword = !showPassword"
                        ></i>
                    </div>
                </div>

                <div class="form-actions">
                    <div class="remember-me">
                        <input type="checkbox" id="remember" />
                        <label for="remember">Lembrar-me</label>
                    </div>
                    <a href="#" class="forgot-password">Esqueceu a senha?</a>
                </div>

                <div v-if="errorMessage" class="error-banner">
                    <i class="fas fa-exclamation-circle"></i>
                    <span>{{ errorMessage }}</span>
                </div>

                <button type="submit" class="btn-login" :disabled="isLoading">
                    <span v-if="isLoading" class="loader"></span>
                    <span v-else>Entrar no Sistema</span>
                </button>

                <div class="register-link">
                    Ainda não tem conta? 
                    <router-link to="/cadastro">Teste 7 dias grátis</router-link>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const showPassword = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
    isLoading.value = true;
    errorMessage.value = '';

    try {
        // --- CORREÇÃO AQUI ---
        // Não fazemos axios.post aqui. Chamamos a action da store.
        await authStore.login({
            username: username.value,
            password: password.value
        });

        // Se o login der certo (não cair no catch), redireciona
        // Verifica se havia uma rota tentada antes (ex: usuário tentou ir para /dashboard direto)
        const redirectPath = (route.query.next as string) || '/dashboard';
        router.push(redirectPath);

    } catch (error: any) {
        console.error("Erro no login:", error);
        
        // Tratamento de mensagens de erro
        if (error.response) {
            if (error.response.status === 401) {
                errorMessage.value = 'Usuário ou senha incorretos.';
            } else if (error.response.status === 403) {
                // Se for bloqueio financeiro, a API já devolve a mensagem ou o interceptor pega
                errorMessage.value = error.response.data.detail || 'Acesso negado.';
            } else {
                errorMessage.value = 'Erro ao conectar ao servidor.';
            }
        } else {
            errorMessage.value = 'Verifique sua conexão com a internet.';
        }
    } finally {
        isLoading.value = false;
    }
};
</script>

<style scoped>
.login-container {
    height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
    font-family: 'Inter', sans-serif;
}

.login-card {
    background: white;
    width: 100%;
    max-width: 420px;
    padding: 2.5rem;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
}

.brand-section {
    text-align: center;
    margin-bottom: 2rem;
}

.logo-circle {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    margin: 0 auto 1rem;
    box-shadow: 0 4px 10px rgba(0, 123, 255, 0.3);
}

h1 {
    font-size: 1.5rem;
    font-weight: 800;
    color: #1f2937;
    margin: 0;
}

p {
    color: #6b7280;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

.form-group {
    margin-bottom: 1.25rem;
}

label {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-icon {
    position: absolute;
    left: 1rem;
    color: #9ca3af;
    font-size: 1rem;
}

input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.8rem;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.95rem;
    transition: all 0.2s;
    background-color: #f9fafb;
}

input:focus {
    outline: none;
    border-color: #007bff;
    background-color: white;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.toggle-password {
    position: absolute;
    right: 1rem;
    color: #9ca3af;
    cursor: pointer;
    transition: color 0.2s;
}

.toggle-password:hover {
    color: #4b5563;
}

.form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    font-size: 0.85rem;
}

.remember-me {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #6b7280;
}

.forgot-password {
    color: #007bff;
    text-decoration: none;
    font-weight: 600;
}

.btn-login {
    width: 100%;
    padding: 0.875rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    justify-content: center;
    align-items: center;
}

.btn-login:hover:not(:disabled) {
    background-color: #0056b3;
    transform: translateY(-1px);
}

.btn-login:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.error-banner {
    background-color: #fee2e2;
    color: #ef4444;
    padding: 0.75rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.register-link {
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.9rem;
    color: #6b7280;
}

.register-link a {
    color: #007bff;
    text-decoration: none;
    font-weight: 700;
}

.register-link a:hover {
    text-decoration: underline;
}

/* Spinner Simples */
.loader {
    width: 20px;
    height: 20px;
    border: 2px solid #ffffff;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    box-sizing: border-box;
    animation: rotation 1s linear infinite;
}

@keyframes rotation {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
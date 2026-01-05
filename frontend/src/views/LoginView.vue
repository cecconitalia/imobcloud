<template>
  <div class="login-wrapper">
    
    <div class="split-left">
      <div class="bg-image"></div>
      <div class="overlay"></div>
      
      <div class="brand-content">
        <div class="logo-small">
          <div class="logo-box"><i class="fas fa-laptop-house"></i></div>
          <span>ImobHome</span>
        </div>

        <div class="hero-text">
          <h2 v-if="isRegisterMode">Comece seu teste grátis de 7 dias.</h2>
          <h2 v-else>Transforme a gestão da sua imobiliária.</h2>
          
          <p>"O ImobHome centralizou todo o nosso processo, desde a captação até a assinatura do contrato."</p>
          
          <div class="avatars">
             <div class="avatar c1"></div>
             <div class="avatar c2"></div>
             <div class="avatar c3"></div>
             <span class="avatar-text">+2.000 corretores</span>
          </div>
        </div>

        <div class="left-footer">
          <span>&copy; 2026 ImobHome</span>
          <div class="links">
            <a href="#">Termos</a>
            <a href="#">Privacidade</a>
          </div>
        </div>
      </div>
    </div>

    <div class="split-right">
      <div class="login-form-container">
        
        <div class="mobile-logo">
           <i class="fas fa-laptop-house"></i> ImobHome
        </div>

        <div v-if="registerSuccess" class="text-center py-8">
            <div class="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
                <i class="fas fa-check"></i>
            </div>
            <h2 class="text-2xl font-bold text-gray-900 mb-2">Conta Criada!</h2>
            
            <div v-if="tempPassword" class="bg-yellow-50 border border-yellow-200 p-4 rounded-lg my-4 text-left">
                <p class="text-sm text-yellow-800 font-bold mb-1">Guarde suas credenciais:</p>
                <p class="text-sm text-gray-700">Usuário: <strong>{{ registerForm.email }}</strong></p>
                <p class="text-sm text-gray-700">Senha: <strong>{{ tempPassword }}</strong></p>
                <p class="text-xs text-gray-500 mt-2">(Copie a senha, ela não será mostrada novamente)</p>
            </div>
            <p v-else class="text-gray-600 mb-6">
                Enviamos sua senha para <strong>{{ registerForm.email }}</strong>.
            </p>

            <button @click="switchToLoginWithEmail" class="btn-submit">
                Ir para Login
            </button>
        </div>

        <div v-else-if="!isRegisterMode">
            <div class="form-header">
              <h2>Bem-vindo de volta</h2>
              <p>Ainda não tem conta? 
                 <a href="#" @click.prevent="isRegisterMode = true">Comece o teste grátis</a>
              </p>
            </div>

            <div v-if="errorMessage" class="alert-error">
              <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
            </div>

            <form @submit.prevent="handleLogin" class="form-box">
              <div class="form-group">
                <label>Usuário ou E-mail</label>
                <div class="input-wrapper">
                  <i class="fas fa-envelope icon"></i>
                  <input v-model="username" type="text" required placeholder="seu.usuario" />
                </div>
              </div>

              <div class="form-group">
                <label>Senha</label>
                <div class="input-wrapper">
                  <i class="fas fa-lock icon"></i>
                  <input v-model="password" :type="showPassword ? 'text' : 'password'" required placeholder="••••••••" />
                  <i class="fas toggle-eye" :class="showPassword ? 'fa-eye-slash' : 'fa-eye'" @click="showPassword = !showPassword"></i>
                </div>
              </div>

              <div class="form-extras">
                <label class="checkbox-container">
                  <input type="checkbox" /> Lembrar de mim
                </label>
                <a href="#" class="forgot-link">Esqueceu a senha?</a>
              </div>

              <button type="submit" class="btn-submit" :disabled="isLoading">
                <span v-if="isLoading"><i class="fas fa-circle-notch fa-spin"></i> Entrando...</span>
                <span v-else>Entrar no Sistema</span>
              </button>
            </form>
        </div>

        <div v-else>
            <div class="form-header">
              <h2>Crie sua conta Grátis</h2>
              <p>Já tem cadastro? 
                 <a href="#" @click.prevent="isRegisterMode = false">Fazer Login</a>
              </p>
            </div>

            <div v-if="errorMessage" class="alert-error">
              <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
            </div>

            <form @submit.prevent="handleRegister" class="form-box">
              <div class="form-group">
                  <label>Nome Completo</label>
                  <div class="input-wrapper">
                    <i class="fas fa-user icon"></i>
                    <input v-model="registerForm.nome" type="text" required placeholder="Ex: João Silva" />
                  </div>
              </div>

              <div class="form-group">
                  <label>Nome da Imobiliária</label>
                  <div class="input-wrapper">
                    <i class="fas fa-building icon"></i>
                    <input v-model="registerForm.nome_imobiliaria" type="text" required placeholder="Ex: Silva Imóveis" />
                  </div>
              </div>

              <div class="form-group">
                  <label>E-mail Corporativo</label>
                  <div class="input-wrapper">
                    <i class="fas fa-envelope icon"></i>
                    <input v-model="registerForm.email" type="email" required placeholder="joao@exemplo.com" />
                  </div>
              </div>

              <div class="form-group">
                  <label>Telefone / WhatsApp</label>
                  <div class="input-wrapper">
                    <i class="fas fa-phone icon"></i>
                    <input v-model="registerForm.telefone" type="text" required placeholder="(00) 90000-0000" />
                  </div>
              </div>

              <button type="submit" class="btn-submit" :disabled="isLoading">
                  <span v-if="isLoading"><i class="fas fa-circle-notch fa-spin"></i> Criando conta...</span>
                  <span v-else>Gerar Minha Senha</span>
              </button>
              
              <p class="terms-text">
                  Ao clicar, você concorda com nossos Termos de Uso.
              </p>
            </form>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();

// Estado Geral
const isLoading = ref(false);
const errorMessage = ref('');
const isRegisterMode = ref(false); // Controla qual form aparece

// Estado Login
const username = ref('');
const password = ref('');
const showPassword = ref(false);

// Estado Cadastro
const registerSuccess = ref(false);
const tempPassword = ref(''); // Para mostrar se o email falhar
const registerForm = ref({
    nome: '',
    nome_imobiliaria: '',
    email: '',
    telefone: ''
});

// --- LÓGICA DE LOGIN ---
const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await api.post('/v1/token/', {
      username: username.value,
      password: password.value
    });

    const { access, refresh } = response.data;
    authStore.setToken(access); 
    localStorage.setItem('refreshToken', refresh);

    const userResponse = await api.get('/v1/core/usuarios/me/');
    const userData = userResponse.data;

    authStore.setUser(userData, null, userData.imobiliaria_nome);
    router.push({ name: 'dashboard' });

  } catch (error: any) {
    console.error('Erro no login:', error);
    if (error.response && error.response.status === 401) {
        errorMessage.value = 'Usuário ou senha incorretos.';
    } else {
        errorMessage.value = 'Falha ao conectar ao servidor.';
    }
    authStore.logout();
  } finally {
    isLoading.value = false;
  }
};

// --- LÓGICA DE CADASTRO ---
const handleRegister = async () => {
    isLoading.value = true;
    errorMessage.value = '';

    try {
        const response = await api.post('/v1/public/register/', registerForm.value);
        
        // Se o backend retornar a senha (fallback por falta de email), guardamos
        if (response.data.senha_gerada) {
            tempPassword.value = response.data.senha_gerada;
        }
        registerSuccess.value = true;

    } catch (error: any) {
        if (error.response && error.response.data && error.response.data.error) {
            errorMessage.value = error.response.data.error;
        } else {
            errorMessage.value = 'Erro ao processar cadastro. Tente novamente.';
        }
    } finally {
        isLoading.value = false;
    }
};

const switchToLoginWithEmail = () => {
    username.value = registerForm.value.email;
    isRegisterMode.value = false;
    registerSuccess.value = false;
    errorMessage.value = ''; // Limpa msg de sucesso ou erro anterior
}
</script>

<style scoped>
/* --- LAYOUT GERAL --- */
.login-wrapper {
  display: flex; min-height: 100vh; font-family: 'Inter', sans-serif;
}

/* --- LADO ESQUERDO (VISUAL) --- */
.split-left {
  display: none; /* Escondido em mobile */
  width: 50%;
  position: relative;
  background-color: #1e1b4b; /* Indigo Escuro */
  overflow: hidden;
  color: white;
}
@media (min-width: 1024px) { .split-left { display: flex; flex-direction: column; } }

.bg-image {
  position: absolute; inset: 0;
  background-image: url('https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1073&q=80');
  background-size: cover; background-position: center;
  opacity: 0.4;
}
.overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, #1e1b4b, transparent);
}

.brand-content {
  position: relative; z-index: 10;
  padding: 3rem; flex: 1; display: flex; flex-direction: column; justify-content: space-between;
}

.logo-small { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; font-size: 1.1rem; }
.logo-box {
  width: 32px; height: 32px; background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center; border-radius: 8px;
}

.hero-text h2 { font-size: 2.5rem; line-height: 1.1; margin-bottom: 1.5rem; }
.hero-text p { font-size: 1.1rem; color: #c7d2fe; max-width: 400px; }

.avatars { display: flex; align-items: center; gap: 1rem; margin-top: 2rem; }
.avatar { width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1e1b4b; background-color: #ddd; }
.avatar.c1 { background-color: #ffadad; transform: translateX(0); }
.avatar.c2 { background-color: #ffd6a5; transform: translateX(-10px); }
.avatar.c3 { background-color: #fdffb6; transform: translateX(-20px); }
.avatar-text { font-size: 0.9rem; font-weight: 600; color: #c7d2fe; transform: translateX(-15px); }

.left-footer { display: flex; justify-content: space-between; font-size: 0.8rem; color: #818cf8; }
.left-footer a { color: inherit; text-decoration: none; margin-left: 1rem; }
.left-footer a:hover { color: white; }

/* --- LADO DIREITO (FORM) --- */
.split-right {
  flex: 1; display: flex; align-items: center; justify-content: center;
  background-color: white; padding: 2rem;
}

.login-form-container { width: 100%; max-width: 400px; }

.mobile-logo {
  display: block; text-align: center; font-size: 1.5rem; font-weight: 700; color: #4f46e5; margin-bottom: 2rem;
}
@media (min-width: 1024px) { .mobile-logo { display: none; } }

.form-header { margin-bottom: 2rem; }
.form-header h2 { font-size: 1.8rem; font-weight: 800; color: #111827; margin: 0 0 0.5rem 0; }
.form-header p { color: #6b7280; font-size: 0.9rem; }
.form-header a { color: #4f46e5; font-weight: 600; text-decoration: none; }

.alert-error {
  background: #fef2f2; border-left: 4px solid #ef4444; color: #b91c1c;
  padding: 1rem; border-radius: 6px; font-size: 0.9rem; margin-bottom: 1.5rem;
  display: flex; align-items: center; gap: 0.5rem;
}

.form-box { display: flex; flex-direction: column; gap: 1.25rem; }

.form-group label { display: block; font-size: 0.9rem; font-weight: 500; color: #374151; margin-bottom: 0.4rem; }
.input-wrapper { position: relative; }
.input-wrapper input {
  width: 100%; padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.95rem;
  outline: none; transition: border-color 0.2s; box-sizing: border-box;
}
.input-wrapper input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
.input-wrapper .icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9ca3af; }
.input-wrapper .toggle-eye { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #9ca3af; cursor: pointer; }

.form-extras { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; }
.checkbox-container { display: flex; align-items: center; gap: 0.5rem; color: #374151; cursor: pointer; }
.forgot-link { color: #4f46e5; font-weight: 500; text-decoration: none; }

.btn-submit {
  width: 100%; padding: 0.8rem; background: #4f46e5; color: white;
  border: none; border-radius: 8px; font-weight: 600; font-size: 1rem; cursor: pointer;
  transition: background 0.2s;
}
.btn-submit:hover { background: #4338ca; }
.btn-submit:disabled { opacity: 0.7; cursor: not-allowed; }

.terms-text { font-size: 0.75rem; color: #9ca3af; text-align: center; margin-top: 1rem; }
</style>
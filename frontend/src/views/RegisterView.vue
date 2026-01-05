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
          <h2>Comece seu teste grátis de 7 dias.</h2>
          <p>"A melhor decisão que tomei para minha carreira foi automatizar meus processos com o ImobHome."</p>
        </div>
        <div class="left-footer">
          <span>&copy; 2026 ImobHome</span>
        </div>
      </div>
    </div>

    <div class="split-right">
      <div class="login-form-container">
        
        <div v-if="successStep" class="text-center-success">
            <div class="success-icon">
                <i class="fas fa-check"></i>
            </div>
            <h2 class="success-title">Conta Criada!</h2>
            <p class="success-desc">
                Enviamos sua senha de acesso para <strong>{{ form.email }}</strong>.
                <br>Verifique sua caixa de entrada (e spam).
            </p>
            <router-link to="/login" class="btn-submit btn-link">
                Ir para Login
            </router-link>
        </div>

        <div v-else>
            <div class="form-header">
              <h2>Crie sua conta</h2>
              <p>Já tem uma conta? <router-link to="/login">Fazer Login</router-link></p>
            </div>

            <div v-if="errorMessage" class="alert-error">
              <i class="fas fa-exclamation-circle"></i> {{ errorMessage }}
            </div>

            <form @submit.prevent="handleRegister" class="form-box">
            
              <div class="form-group">
                  <label>Nome Completo</label>
                  <div class="input-wrapper">
                  <i class="fas fa-user icon"></i>
                  <input v-model="form.nome" type="text" required placeholder="Ex: João Silva" />
                  </div>
              </div>

              <div class="form-group">
                  <label>Nome da Imobiliária</label>
                  <div class="input-wrapper">
                  <i class="fas fa-building icon"></i>
                  <input v-model="form.nome_imobiliaria" type="text" required placeholder="Ex: Silva Imóveis" />
                  </div>
              </div>

              <div class="form-group">
                  <label>E-mail Corporativo</label>
                  <div class="input-wrapper">
                  <i class="fas fa-envelope icon"></i>
                  <input v-model="form.email" type="email" required placeholder="joao@exemplo.com" />
                  </div>
              </div>

              <div class="form-group">
                  <label>Telefone / WhatsApp</label>
                  <div class="input-wrapper">
                  <i class="fas fa-phone icon"></i>
                  <input v-model="form.telefone" type="text" required placeholder="(00) 90000-0000" />
                  </div>
              </div>

              <button type="submit" class="btn-submit" :disabled="isLoading">
                  <span v-if="isLoading"><i class="fas fa-circle-notch fa-spin"></i> Gerando Acesso...</span>
                  <span v-else>Gerar Minha Senha Grátis</span>
              </button>
              
              <p class="terms-text">
                  Ao clicar, você concorda com nossos Termos de Uso. A senha será enviada para o seu e-mail.
              </p>
            </form>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import api from '@/services/api';

const isLoading = ref(false);
const errorMessage = ref('');
const successStep = ref(false);

const form = ref({
    nome: '',
    nome_imobiliaria: '',
    email: '',
    telefone: ''
});

const handleRegister = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    // Chama a API Pública criada no backend
    await api.post('/v1/public/register/', form.value);
    successStep.value = true;
  } catch (error: any) {
    console.error('Erro no cadastro:', error);
    if (error.response && error.response.data && error.response.data.error) {
        errorMessage.value = error.response.data.error;
    } else {
        errorMessage.value = 'Erro ao processar cadastro. Tente novamente.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* REUTILIZANDO O ESTILO DO LOGIN PARA CONSISTÊNCIA */
.login-wrapper { display: flex; min-height: 100vh; font-family: 'Inter', sans-serif; }

/* Lado Esquerdo */
.split-left { display: none; width: 50%; position: relative; background-color: #1e1b4b; overflow: hidden; color: white; }
@media (min-width: 1024px) { .split-left { display: flex; flex-direction: column; } }
.bg-image { position: absolute; inset: 0; background-image: url('https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1073&q=80'); background-size: cover; background-position: center; opacity: 0.4; }
.overlay { position: absolute; inset: 0; background: linear-gradient(to top, #1e1b4b, transparent); }
.brand-content { position: relative; z-index: 10; padding: 3rem; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.logo-small { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; font-size: 1.1rem; }
.logo-box { width: 32px; height: 32px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; border-radius: 8px; }
.hero-text h2 { font-size: 2.5rem; line-height: 1.1; margin-bottom: 1.5rem; }
.hero-text p { font-size: 1.1rem; color: #c7d2fe; max-width: 400px; }
.left-footer { font-size: 0.8rem; color: #818cf8; }

/* Lado Direito */
.split-right { flex: 1; display: flex; align-items: center; justify-content: center; background-color: white; padding: 2rem; }
.login-form-container { width: 100%; max-width: 400px; }

.form-header { margin-bottom: 2rem; }
.form-header h2 { font-size: 1.8rem; font-weight: 800; color: #111827; margin: 0 0 0.5rem 0; }
.form-header p { color: #6b7280; font-size: 0.9rem; }
.form-header a { color: #4f46e5; font-weight: 600; text-decoration: none; }

.alert-error { background: #fef2f2; border-left: 4px solid #ef4444; color: #b91c1c; padding: 1rem; border-radius: 6px; font-size: 0.9rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem; }

.form-box { display: flex; flex-direction: column; gap: 1rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 500; color: #374151; margin-bottom: 0.3rem; }
.input-wrapper { position: relative; }
.input-wrapper input { width: 100%; padding: 0.75rem 1rem 0.75rem 2.5rem; border: 1px solid #d1d5db; border-radius: 8px; font-size: 0.95rem; outline: none; transition: border-color 0.2s; box-sizing: border-box; }
.input-wrapper input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
.input-wrapper .icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9ca3af; }

.btn-submit { width: 100%; padding: 0.9rem; background: #4f46e5; color: white; border: none; border-radius: 8px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: background 0.2s; margin-top: 1rem; }
.btn-submit:hover { background: #4338ca; }
.btn-submit:disabled { opacity: 0.7; cursor: not-allowed; }

.terms-text { font-size: 0.75rem; color: #9ca3af; text-align: center; margin-top: 1rem; }

/* Estilos de Sucesso */
.text-center-success { text-align: center; padding: 2rem 0; }
.success-icon { width: 80px; height: 80px; background: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; margin: 0 auto 1.5rem; }
.success-title { font-size: 1.8rem; font-weight: 800; color: #111827; margin-bottom: 0.5rem; }
.success-desc { color: #4b5563; margin-bottom: 2rem; line-height: 1.6; }
.btn-link { display: block; text-decoration: none; }
</style>
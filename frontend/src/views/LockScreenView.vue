<template>
    <div class="lock-screen">
        <div class="lock-content">
            <div class="icon-container">
                <i :class="isTrial ? 'fas fa-stopwatch' : 'fas fa-lock'"></i>
            </div>
            
            <h1>{{ title }}</h1>
            
            <p class="message">
                {{ mainMessage }}
            </p>
            
            <p class="sub-message">
                {{ subMessage }}
            </p>
            
            <div class="actions">
                <template v-if="isTrial">
                    <a href="https://wa.me/5500000000000?text=Ola,%20gostaria%20de%20assinar%20um%20plano" target="_blank" class="btn-primary">
                        <i class="fas fa-star"></i> Assinar Agora
                    </a>
                </template>
                <template v-else>
                    <a href="https://wa.me/5500000000000?text=Ola,%20preciso%20de%20ajuda%20com%20minha%20fatura" target="_blank" class="btn-whatsapp">
                        <i class="fab fa-whatsapp"></i> Regularizar Pagamento
                    </a>
                </template>

                <button @click="logout" class="btn-logout">
                    <i class="fas fa-sign-out-alt"></i> Sair da Conta
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Verifica se a razão do bloqueio é 'trial' (vindo da query param ?reason=trial)
const isTrial = computed(() => route.query.reason === 'trial');

// Título dinâmico
const title = computed(() => 
    isTrial.value ? 'Período de Teste Finalizado' : 'Acesso Suspenso'
);

// Mensagem principal dinâmica
const mainMessage = computed(() => 
    isTrial.value 
        ? 'Esperamos que tenha gostado dos seus 7 dias gratuitos!'
        : 'Identificamos uma pendência financeira na sua assinatura.'
);

// Sub-mensagem dinâmica
const subMessage = computed(() => 
    isTrial.value 
        ? 'Para continuar gerenciando seus imóveis e não perder seus dados cadastrados, escolha um plano e assine agora.'
        : 'Para restabelecer o acesso imediato ao sistema, por favor regularize o pagamento ou entre em contato com nosso suporte.'
);

const logout = () => {
    authStore.logout();
    router.push('/login');
};
</script>

<style scoped>
.lock-screen {
    height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: white;
    font-family: 'Inter', sans-serif;
    padding: 1rem;
}

.lock-content {
    background: white;
    padding: 3rem;
    border-radius: 16px;
    text-align: center;
    max-width: 500px;
    width: 100%;
    box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    color: #333;
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.icon-container {
    font-size: 4rem;
    color: #dc3545;
    margin-bottom: 1.5rem;
}

/* Cor amarela para o ícone de teste */
.fa-stopwatch {
    color: #ffc107; 
}

h1 {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 1rem;
    color: #2c3e50;
}

.message {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
    color: #dc3545;
}

.sub-message {
    color: #666;
    margin-bottom: 2rem;
    line-height: 1.6;
    font-size: 0.95rem;
}

.actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.btn-whatsapp {
    background-color: #25D366;
    color: white;
    padding: 14px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: none;
}

.btn-whatsapp:hover {
    background-color: #128C7E;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
}

.btn-primary {
    background-color: #007bff;
    color: white;
    padding: 14px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.btn-primary:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.btn-logout {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    color: #6c757d;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.btn-logout:hover {
    background-color: #e9ecef;
    color: #495057;
}
</style>
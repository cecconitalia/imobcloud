<template>
  <div v-if="shouldShow" class="financeiro-banner">
    <div class="banner-content">
      <div class="alert-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      
      <div class="text-content">
        <span class="title">Atenção: Mensalidade Pendente</span>
        <span class="subtitle">
          Sua fatura venceu em <strong>{{ vencimento }}</strong>. 
          Regularize para evitar o bloqueio do sistema.
        </span>
      </div>
      
      <a href="https://wa.me/5500000000000" target="_blank" class="btn-regularizar">
        Regularizar Agora <i class="fas fa-arrow-right"></i>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

const shouldShow = computed(() => {
    return authStore.isFinancialPending;
});

const vencimento = computed(() => {
    return authStore.vencimentoAtual;
});
</script>

<style scoped>
.financeiro-banner {
  background-color: #fff3cd; /* Amarelo Fundo */
  border-bottom: 1px solid #ffeeba;
  color: #856404; /* Marrom Texto */
  padding: 12px 20px;
  width: 100%;
  position: relative;
  z-index: 999;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  animation: slideDown 0.4s ease-out;
}

@keyframes slideDown {
  from { transform: translateY(-100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.banner-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center; /* Centralizado se for mobile */
  gap: 15px;
  flex-wrap: wrap;
}

/* Em telas maiores, separa os itens */
@media (min-width: 768px) {
    .banner-content {
        justify-content: space-between;
    }
}

.alert-icon {
  font-size: 1.4rem;
  color: #ffc107;
  display: flex;
  align-items: center;
}

.text-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.title {
  font-weight: 800;
  font-size: 0.9rem;
  text-transform: uppercase;
}

.subtitle {
  font-size: 0.9rem;
}

.btn-regularizar {
  background-color: #856404;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-regularizar:hover {
  background-color: #6d5203;
  transform: translateY(-1px);
}
</style>
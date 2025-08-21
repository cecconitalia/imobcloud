<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Gerar Boleto para Pagamento</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <p>
          Selecione a configuração bancária para gerar o boleto para a
          transação **#{{ pagamento.id }}** no valor de
          **{{ formatarValor(pagamento.valor) }}**.
        </p>

        <div v-if="isLoadingBancos" class="loading-state">
          <p>A carregar bancos...</p>
        </div>

        <div v-else class="form-group">
          <label for="banco">Configuração Bancária:</label>
          <select id="banco" v-model="bancoSelecionadoId" required>
            <option disabled value="">Selecione um banco</option>
            <option
              v-for="banco in bancosDisponiveis"
              :key="banco.id"
              :value="banco.id"
            >
              {{ banco.nome_banco }}
            </option>
          </select>
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>
      </div>

      <div class="modal-actions">
        <button @click="gerarBoleto" class="btn-primary" :disabled="isSubmitting || !bancoSelecionadoId">
          {{ isSubmitting ? 'A gerar...' : 'Gerar Boleto' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, defineEmits } from 'vue';
import apiClient from '@/services/api';

const props = defineProps({
  pagamento: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['close', 'boletoGerado']);

const bancosDisponiveis = ref<any[]>([]);
const bancoSelecionadoId = ref(null);
const isLoadingBancos = ref(true);
const isSubmitting = ref(false);
const error = ref<string | null>(null);

function formatarValor(valor: number) {
  return parseFloat(valor.toString()).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

async function fetchBancos() {
  isLoadingBancos.value = true;
  try {
    const response = await apiClient.get('/v1/boletos/configuracoes-banco/');
    bancosDisponiveis.value = response.data;
  } catch (err) {
    console.error('Erro ao carregar bancos:', err);
    error.value = 'Não foi possível carregar as configurações de banco.';
  } finally {
    isLoadingBancos.value = false;
  }
}

async function gerarBoleto() {
  if (!bancoSelecionadoId.value) return;

  isSubmitting.value = true;
  error.value = null;

  try {
    const payload = {
      transacao_id: props.pagamento.id,
      banco_id: bancoSelecionadoId.value,
    };
    await apiClient.post('/v1/boletos/gerar/', payload);
    emit('boletoGerado');
  } catch (err: any) {
    console.error('Erro ao gerar boleto:', err.response?.data || err);
    error.value = err.response?.data?.mensagem || 'Falha ao gerar o boleto.';
  } finally {
    isSubmitting.value = false;
  }
}

function closeModal() {
  emit('close');
}

onMounted(() => {
  fetchBancos();
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}
.modal-body {
  flex-grow: 1;
}
.form-group {
  margin-top: 1rem;
}
.form-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.5rem;
}
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.modal-actions {
  margin-top: 1.5rem;
  text-align: right;
}
.btn-primary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: #007bff;
  color: white;
}
.loading-state, .error-message {
  text-align: center;
  padding: 1rem;
}
.error-message {
  color: red;
}
</style>
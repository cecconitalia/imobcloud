<template>
  <div class="config-ia-container">
    <h2>Configurações da Inteligência Artificial</h2>
    <div v-if="loading" class="loading-message">Carregando...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!loading && !error" class="form-section">
      <h3>Tom de Voz da Marca</h3>
      <p>Selecione o estilo de comunicação que a IA deve usar ao gerar textos para as suas publicações. Esta voz representará a sua marca.</p>
      
      <div class="select-wrapper">
        <select v-model="vozSelecionadaId" @change="salvarConfiguracao">
          <option :value="null">-- Padrão do Sistema --</option>
          <option v-for="opcao in opcoesDeVoz" :key="opcao.id" :value="opcao.id">
            {{ opcao.nome }}
          </option>
        </select>
      </div>
      <div v-if="opcaoAtual" class="descricao-voz">
        <strong>Descrição:</strong> {{ opcaoAtual.descricao }}
      </div>

      <div v-if="saveStatus" :class="['save-status', { success: isSuccess, fail: !isSuccess }]">
        {{ saveStatus }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '@/services/api'; 

const loading = ref(true);
const error = ref<string | null>(null);
const opcoesDeVoz = ref<any[]>([]);
const vozSelecionadaId = ref<number | null>(null);
const saveStatus = ref<string | null>(null);
const isSuccess = ref(false);

const opcaoAtual = computed(() => {
  if (!vozSelecionadaId.value) return null;
  return opcoesDeVoz.value.find(opt => opt.id === vozSelecionadaId.value);
});

async function carregarDados() {
  loading.value = true;
  error.value = null;
  try {
    const [resOpcoes, resConfig] = await Promise.all([
      apiClient.get('/v1/configuracao-ia/opcoes-voz/'),
      apiClient.get('/v1/configuracao-ia/configuracao/')
    ]);
    
    opcoesDeVoz.value = resOpcoes.data;
    vozSelecionadaId.value = resConfig.data.voz_da_marca_preferida_id;

  } catch (err) {
    console.error("Erro ao carregar configurações:", err);
    error.value = "Não foi possível carregar as configurações. Tente novamente mais tarde.";
  } finally {
    loading.value = false;
  }
}

async function salvarConfiguracao() {
  saveStatus.value = 'Salvando...';
  isSuccess.value = false;
  try {
    await apiClient.put('/v1/configuracao-ia/configuracao/', {
      voz_da_marca_id: vozSelecionadaId.value
    });
    saveStatus.value = 'Configuração salva com sucesso!';
    isSuccess.value = true;
  } catch (err) {
    console.error("Erro ao salvar configuração:", err);
    saveStatus.value = 'Falha ao salvar. Tente novamente.';
    isSuccess.value = false;
  } finally {
    setTimeout(() => { saveStatus.value = null; }, 3000);
  }
}

onMounted(async () => {
  await carregarDados();
});
</script>

<style scoped>
.config-ia-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
h2, h3 {
  color: #333;
}
.form-section p {
  color: #666;
  margin-bottom: 1.5rem;
}
.select-wrapper select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}
.descricao-voz {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #eef;
  border-radius: 4px;
  color: #444;
}
.save-status {
  margin-top: 1rem;
  padding: 0.8rem;
  border-radius: 4px;
  text-align: center;
}
.save-status.success {
  background-color: #d4edda;
  color: #155724;
}
.save-status.fail {
  background-color: #f8d7da;
  color: #721c24;
}
.error-message {
  color: #721c24;
}
.loading-message {
  color: #004085;
}
</style>
<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">Remessa e Retorno de Boletos</h1>
      <p class="page-subtitle">Gere arquivos de remessa para o banco e processe os retornos para dar baixa nos pagamentos.</p>
    </div>

    <div class="content-card">
      <h2 class="card-title">1. Gerar Arquivo de Remessa</h2>
      <div class="form-group">
        <label for="banco">Selecione a Configuração Bancária:</label>
        <select id="banco" v-model="configBancoId" class="form-control">
          <option :value="null">-- Selecione --</option>
          <option v-for="banco in bancos" :key="banco.id" :value="banco.id">{{ banco.nome_banco }}</option>
        </select>
      </div>

      <div v-if="isLoadingPendentes" class="loading-state">Carregando contas pendentes...</div>
      <div v-else>
        <h3 class="table-title">Contas Pendentes de Remessa ({{ transacoesPendentes.length }})</h3>
        <div class="table-wrapper">
          <table class="styled-table">
            <thead>
              <tr>
                <th><input type="checkbox" @change="selecionarTodos" /></th>
                <th>Vencimento</th>
                <th>Cliente</th>
                <th>Descrição</th>
                <th class="text-right">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in transacoesPendentes" :key="t.id">
                <td><input type="checkbox" v-model="transacoesSelecionadas" :value="t.id" /></td>
                <td>{{ formatDate(t.vencimento) }}</td>
                <td>{{ t.cliente_nome }}</td>
                <td>{{ t.descricao }}</td>
                <td class="text-right">{{ formatCurrency(t.valor) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <button @click="gerarRemessa" :disabled="!configBancoId || transacoesSelecionadas.length === 0" class="btn-primary">
          Gerar Arquivo de Remessa ({{ transacoesSelecionadas.length }} selecionadas)
        </button>
      </div>
    </div>

    <div class="content-card">
      <h2 class="card-title">2. Processar Arquivo de Retorno</h2>
      <div class="form-group">
        <label for="retorno-file">Selecione o arquivo de retorno (.ret) fornecido pelo banco:</label>
        <input type="file" id="retorno-file" @change="handleFileChange" class="form-control" />
      </div>
      <button @click="processarRetorno" :disabled="!arquivoRetorno" class="btn-success">
        Processar Arquivo
      </button>
      <div v-if="logProcessamento" class="log-processamento">
        <h4>Resultado:</h4>
        <pre>{{ logProcessamento }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const bancos = ref<any[]>([]);
const configBancoId = ref(null);
const transacoesPendentes = ref<any[]>([]);
const transacoesSelecionadas = ref<number[]>([]);
const isLoadingPendentes = ref(true);

const arquivoRetorno = ref<File | null>(null);
const logProcessamento = ref('');

const fetchPendentes = async () => {
  isLoadingPendentes.value = true;
  try {
    const response = await api.get('/v1/boletos/ciclo-boletos/pendentes-remessa/');
    transacoesPendentes.value = response.data;
  } catch (error) { console.error(error); }
  finally { isLoadingPendentes.value = false; }
};

const fetchBancos = async () => {
  try {
    const response = await api.get('/v1/boletos/configuracoes-banco/');
    bancos.value = response.data;
  } catch (error) { console.error(error); }
};

const gerarRemessa = async () => {
  try {
    const response = await api.post('/v1/boletos/ciclo-boletos/gerar-remessa/', {
      transacao_ids: transacoesSelecionadas.value,
      config_banco_id: configBancoId.value
    }, { responseType: 'blob' });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `REMESSA_${new Date().toISOString()}.txt`);
    document.body.appendChild(link);
    link.click();
    link.remove();

    transacoesSelecionadas.value = [];
    fetchPendentes(); // Atualiza a lista de pendentes
  } catch (error) {
    alert('Erro ao gerar arquivo de remessa.');
    console.error(error);
  }
};

const processarRetorno = async () => {
  if (!arquivoRetorno.value) return;
  const formData = new FormData();
  formData.append('arquivo_retorno', arquivoRetorno.value);

  try {
    const response = await api.post('/v1/boletos/ciclo-boletos/processar-retorno/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    logProcessamento.value = response.data.log;
  } catch (error) {
    alert('Erro ao processar arquivo de retorno.');
    console.error(error);
  }
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    arquivoRetorno.value = target.files[0];
  }
};

const selecionarTodos = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.checked) {
    transacoesSelecionadas.value = transacoesPendentes.value.map(t => t.id);
  } else {
    transacoesSelecionadas.value = [];
  }
};

const formatDate = (date: string) => new Date(date + 'T00:00:00').toLocaleDateString('pt-BR');
const formatCurrency = (val: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val || 0);

onMounted(() => {
  fetchBancos();
  fetchPendentes();
});
</script>

<style scoped>
.page-container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; display: flex; flex-direction: column; gap: 2rem; }
.header-section { text-align: left; }
.content-card { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.card-title { margin-top: 0; }
.table-wrapper { max-height: 400px; overflow-y: auto; margin-top: 1rem; }
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th, .styled-table td { padding: 12px; border-bottom: 1px solid #ddd; }
.btn-primary, .btn-success { margin-top: 1rem; }
.log-processamento { margin-top: 1rem; background-color: #f0f0f0; padding: 1rem; border-radius: 4px; }
.log-processamento pre { white-space: pre-wrap; word-wrap: break-word; }
</style>
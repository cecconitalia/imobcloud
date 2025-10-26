<template>
  <div class="integracoes-container">
    <div v-if="isLoading" class="loading-message">
      A carregar configurações...
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <form v-if="!isLoading && !error" @submit.prevent="saveIntegrations" class="integrations-form">
      <div class="card">
        <div class="card-header">
          <h3>Facebook & Instagram</h3>
          <p>Insira as credenciais obtidas na sua conta de desenvolvedor do Facebook para permitir a publicação automática.</p>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label for="facebook_page_id">ID da Página do Facebook</label>
            <input type="text" id="facebook_page_id" v-model="credentials.facebook_page_id" placeholder="Ex: 101234567890123">
          </div>

          <div class="form-group">
            <label for="instagram_business_account_id">ID da Conta Empresarial do Instagram</label>
            <input type="text" id="instagram_business_account_id" v-model="credentials.instagram_business_account_id" placeholder="Ex: 17890123456789012">
          </div>

          <div class="form-group">
            <label for="facebook_page_access_token">Token de Acesso da Página (L longa duração)</label>
            <textarea id="facebook_page_access_token" v-model="credentials.facebook_page_access_token" rows="5" placeholder="Cole aqui o seu token de acesso de longa duração..."></textarea>
            <small>Este token é sensível. Não o partilhe com ninguém.</small>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="isSaving">
          {{ isSaving ? 'A guardar...' : 'Salvar Alterações' }}
        </button>
      </div>

      <div v-if="saveStatus" :class="['save-status', { success: saveStatus.includes('sucesso') }]">
        {{ saveStatus }}
      </div>
    </form>

    <div class="card mt-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h3>Configurações Bancárias (Boletos)</h3>
            <router-link :to="{ name: 'configuracao-banco-nova' }" class="btn-primary">
                + Adicionar Configuração
            </router-link>
        </div>
        <div class="card-body">
            <div v-if="isLoadingBancos" class="loading-message">Carregando configurações de bancos...</div>
            <div v-else-if="bancos.length === 0" class="no-data-message">Nenhuma configuração de banco encontrada.</div>
            <div v-else class="tabela-wrapper">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Banco</th>
                            <th>Client ID</th>
                            <th>Certificado</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="banco in bancos" :key="banco.id">
                            <td>{{ banco.nome_banco }}</td>
                            <td>{{ banco.client_id }}</td>
                            <td>
                                <span v-if="banco.certificado_file" class="file-status-ok">✔ Uploaded</span>
                                <span v-else class="file-status-missing">❌ Missing</span>
                            </td>
                            <td>
                                <router-link :to="{ name: 'configuracao-banco-editar', params: { id: banco.id } }" class="btn-secondary">
                                    Editar
                                </router-link>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const credentials = ref({
  facebook_page_id: '',
  facebook_page_access_token: '',
  instagram_business_account_id: '',
});

const bancos = ref<any[]>([]);

const isLoading = ref(true);
const isLoadingBancos = ref(true);
const isSaving = ref(false);
const error = ref<string | null>(null);
const saveStatus = ref<string | null>(null);

async function fetchIntegrations() {
  isLoading.value = true;
  error.value = null;
  try {
    // Endpoint original
    const response = await apiClient.get('/v1/integracoes/redes-sociais/');
    credentials.value = response.data;
  } catch (err) {
    console.error("Erro ao carregar integrações:", err);
    error.value = "Não foi possível carregar as configurações de integração.";
  } finally {
    isLoading.value = false;
  }
}

async function fetchBancos() {
    isLoadingBancos.value = true;
    try {
        // Endpoint original
        const response = await apiClient.get('/v1/boletos/configuracoes-banco/');
        bancos.value = response.data;
    } catch (err) {
        console.error("Erro ao carregar configurações de bancos:", err);
    } finally {
        isLoadingBancos.value = false;
    }
}

async function saveIntegrations() {
  isSaving.value = true;
  saveStatus.value = null;
  try {
    // Endpoint original
    const response = await apiClient.put('/v1/integracoes/redes-sociais/', credentials.value);
    saveStatus.value = response.data.success || 'Configurações guardadas.';
  } catch (err: any) {
    console.error("Erro ao guardar integrações:", err);
    saveStatus.value = err.response?.data?.error || "Ocorreu um erro ao guardar as configurações.";
  } finally {
    isSaving.value = false;
    setTimeout(() => { saveStatus.value = null; }, 4000);
  }
}

onMounted(() => {
  fetchIntegrations();
  fetchBancos();
});
</script>

<style scoped>
.integracoes-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0; /* CORREÇÃO APLICADA AQUI */
}
/* Regras .view-header e afins removidas */

.card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem; /* Ajustado para consistência */
  overflow: hidden;
}
.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}
.card-header h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.card-header p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}
.card-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}
.form-group small {
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.8rem;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  padding: 0 1.5rem 1.5rem; /* Padding inferior para ações */
}
.save-status {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
}
.save-status.success {
  background-color: #d4edda;
  color: #155724;
}

/* Bancos */
.card-header.d-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.tabela-wrapper {
    overflow-x: auto;
    padding: 0 1.5rem 1.5rem;
}
.table {
    width: 100%;
    border-collapse: collapse;
}
.table th, .table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}
.table th {
    background-color: #f8f9fa;
    font-weight: bold;
}
.btn-primary, .btn-secondary {
    padding: 8px 12px;
    border-radius: 4px;
    text-decoration: none;
    font-weight: bold;
    border: none;
    cursor: pointer;
    background-color: #007bff;
    color: white;
}
.btn-secondary {
    background-color: #6c757d;
}
.file-status-ok {
    color: #28a745;
    font-weight: bold;
}
.file-status-missing {
    color: #dc3545;
    font-weight: bold;
}
.loading-message, .no-data-message, .error-message {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
}
.error-message {
    color: #dc3545;
    background-color: #f8d7da;
}
.no-data-message {
    padding: 1.5rem;
}
</style>
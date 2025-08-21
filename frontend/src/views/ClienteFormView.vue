<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Cliente' : 'Adicionar Novo Cliente' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do cliente...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="cliente-form">
      <div class="form-section">
        <h3 class="section-title">Dados Pessoais</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="nome_completo">Nome Completo</label>
            <input type="text" id="nome_completo" v-model="cliente.nome_completo" required />
          </div>
          <div class="form-group">
            <label for="cpf_cnpj">CPF ou CNPJ</label>
            <input type="text" id="cpf_cnpj" v-model="cliente.cpf_cnpj" required />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="cliente.email" required />
          </div>
          <div class="form-group">
            <label for="telefone">Telefone</label>
            <input type="tel" id="telefone" v-model="cliente.telefone" required />
          </div>
          
          <div class="form-group">
            <label for="data_nascimento">Data de Nascimento</label>
            <input type="date" id="data_nascimento" v-model="cliente.data_nascimento" />
          </div>
          <div class="form-group">
            <label for="rg">RG</label>
            <input type="text" id="rg" v-model="cliente.rg" />
          </div>
          <div class="form-group">
            <label for="profissao">Profissão</label>
            <input type="text" id="profissao" v-model="cliente.profissao" />
          </div>
          <div class="form-group">
            <label for="estado_civil">Estado Civil</label>
            <input type="text" id="estado_civil" v-model="cliente.estado_civil" />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Endereço</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="endereco">Endereço</label>
            <input type="text" id="endereco" v-model="cliente.endereco" />
          </div>
          <div class="form-group">
            <label for="numero">Número</label>
            <input type="text" id="numero" v-model="cliente.numero" />
          </div>
          <div class="form-group">
            <label for="bairro">Bairro</label>
            <input type="text" id="bairro" v-model="cliente.bairro" />
          </div>
          <div class="form-group">
            <label for="cidade">Cidade</label>
            <input type="text" id="cidade" v-model="cliente.cidade" />
          </div>
          <div class="form-group">
            <label for="estado">Estado (UF)</label>
            <input type="text" id="estado" v-model="cliente.estado" maxlength="2" />
          </div>
          <div class="form-group">
            <label for="cep">CEP</label>
            <input type="text" id="cep" v-model="cliente.cep" />
          </div>
        </div>
      </div>
      
      <div class="form-section full-width">
        <h3 class="section-title">Outras Informações</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="preferencias">Preferências do Imóvel (opcional)</label>
            <textarea id="preferencias" v-model="cliente.preferencias_imovel" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label for="observacoes">Observações (internas)</label>
            <textarea id="observacoes" v-model="cliente.observacoes" rows="4"></textarea>
          </div>
        </div>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Guardando...' : 'Guardar Cliente' }}
        </button>
      </div>
    </form>

    <ClienteAtividades v-if="isEditing && clienteId" :clienteId="clienteId" />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import ClienteAtividades from '@/components/ClienteAtividades.vue';

const route = useRoute();
const router = useRouter();

const clienteId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!clienteId.value);

const cliente = ref({
  nome_completo: '',
  cpf_cnpj: '',
  email: '',
  telefone: '',
  preferencias_imovel: '',
  data_nascimento: null,
  estado_civil: '',
  profissao: '',
  rg: '',
  endereco: '',
  numero: '',
  bairro: '',
  cidade: '',
  estado: '',
  cep: '',
  observacoes: '',
});

const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchClienteData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/clientes/${clienteId.value}/`);
      cliente.value = { 
        ...cliente.value,
        ...response.data 
      };
    } catch (error) {
      console.error("Erro ao buscar dados do cliente:", error);
      alert("Não foi possível carregar os dados do cliente para edição.");
      router.push({ name: 'clientes' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

onMounted(() => {
  fetchClienteData();
});

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/clientes/${clienteId.value}/`, cliente.value);
    } else {
      await apiClient.post('/v1/clientes/', cliente.value);
    }
    router.push({ name: 'clientes' });
  } catch (error: any) {
    console.error("Erro ao guardar o cliente:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o cliente. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'clientes' });
}
</script>

<style scoped>
/* Os estilos existentes foram mantidos e aprimorados para o novo layout */
.form-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.cliente-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.form-section {
  width: 100%;
}
.section-title {
  font-size: 1.25rem;
  font-weight: bold;
  border-bottom: 2px solid #007bff;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
label {
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #495057;
}
input, textarea, select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  width: 100%;
  margin-top: 1rem;
}
.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.loading-message {
  text-align: center;
  padding: 2rem;
}
</style>
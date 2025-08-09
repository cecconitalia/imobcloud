<template>
  <div class="transacao-form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Transação' : 'Nova Transação' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="transacao-form">
      <div class="form-group">
        <label for="tipo">Tipo de Transação</label>
        <select id="tipo" v-model="transacao.tipo" required>
          <option value="RECEITA">Receita</option>
          <option value="DESPESA">Despesa</option>
        </select>
      </div>

      <div class="form-group">
        <label for="valor">Valor (R$)</label>
        <input type="number" step="0.01" id="valor" v-model="transacao.valor" required />
      </div>

      <div class="form-group">
        <label for="data">Data</label>
        <input type="date" id="data" v-model="transacao.data" required />
      </div>
      
      <div class="form-group">
        <label for="categoria">Categoria</label>
        <select id="categoria" v-model="transacao.categoria" required>
          <option disabled value="">Selecione uma categoria</option>
          <option v-for="cat in categoriasFiltradas" :key="cat.id" :value="cat.id">
            {{ cat.nome }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="conta_bancaria">Conta Bancária</label>
        <select id="conta_bancaria" v-model="transacao.conta_bancaria" required>
          <option disabled value="">Selecione uma conta</option>
          <option v-for="conta in contas" :key="conta.id" :value="conta.id">
            {{ conta.nome }}
          </option>
        </select>
      </div>
      
      <div class="form-group full-width">
        <label for="descricao">Descrição</label>
        <textarea id="descricao" v-model="transacao.descricao" rows="3" required></textarea>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A Guardar...' : (isEditing ? 'Guardar Alterações' : 'Adicionar Transação') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const router = useRouter();
const route = useRoute();

const transacaoId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!transacaoId.value);

const transacao = ref({
  tipo: 'RECEITA',
  valor: null as number | null,
  data: new Date().toISOString().substr(0, 10),
  descricao: '',
  categoria: null as number | null,
  conta_bancaria: null as number | null,
  oportunidade: null as number | null,
  contrato: null as number | null,
});

const categorias = ref<any[]>([]);
const contas = ref<any[]>([]);
const isLoadingData = ref(true);
const isSubmitting = ref(false);

const categoriasFiltradas = computed(() => {
  return categorias.value.filter(c => c.tipo === transacao.value.tipo);
});

async function fetchData() {
  isLoadingData.value = true;
  try {
    const [categoriasResponse, contasResponse] = await Promise.all([
      apiClient.get('/v1/financeiro/categorias/'),
      apiClient.get('/v1/financeiro/contas-bancarias/')
    ]);
    categorias.value = categoriasResponse.data;
    contas.value = contasResponse.data;

    if (isEditing.value && transacaoId.value) {
      const response = await apiClient.get(`/v1/financeiro/transacoes/${transacaoId.value}/`);
      transacao.value = response.data;
    }
  } catch (error) {
    console.error("Erro ao carregar dados:", error);
    alert('Não foi possível carregar os dados para o formulário.');
  } finally {
    isLoadingData.value = false;
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value && transacaoId.value) {
      await apiClient.put(`/v1/financeiro/transacoes/${transacaoId.value}/`, transacao.value);
    } else {
      await apiClient.post('/v1/financeiro/transacoes/', transacao.value);
    }
    router.push('/financeiro/transacoes');
  } catch (error) {
    console.error("Erro ao guardar transação:", error);
    alert('Ocorreu um erro ao guardar a transação. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push('/financeiro/transacoes');
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.transacao-form-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.transacao-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  flex: 1 1 calc(50% - 1.5rem);
}
.form-group.full-width {
  flex-basis: 100%;
}
label {
  margin-bottom: 0.5rem;
  font-weight: bold;
}
input, select, textarea {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
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
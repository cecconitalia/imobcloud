<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">{{ formTitle }}</h1>
    
    <div v-if="isLoading" class="text-center text-gray-500">
      <p>Carregando formulário...</p>
    </div>

    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <form v-if="!isLoading" @submit.prevent="submitForm" class="bg-white shadow-md rounded-lg p-6 max-w-2xl mx-auto">
      
      <div class="mb-4">
        <label for="banco" class="block text-gray-700 text-sm font-bold mb-2">Banco:</label>
        <input 
          type="text" 
          id="banco" 
          v-model="conta.banco" 
          required 
          class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        >
      </div>

      <div class="mb-4">
        <label for="numero_conta" class="block text-gray-700 text-sm font-bold mb-2">Número da Conta:</label>
        <input 
          type="text" 
          id="numero_conta" 
          v-model="conta.numero_conta" 
          required 
          class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        >
      </div>

      <div class="mb-6">
        <label for="saldo" class="block text-gray-700 text-sm font-bold mb-2">Saldo Inicial:</label>
        <input 
          type="number" 
          id="saldo" 
          v-model.number="conta.saldo" 
          step="0.01" 
          required 
          class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        >
      </div>
      
      <div class="flex items-center justify-between">
        <button 
          type="submit" 
          class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline transition-colors"
        >
          Salvar
        </button>
        <button 
          @click="router.back()" 
          type="button" 
          class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline transition-colors"
        >
          Cancelar
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api'; // Verifique se o caminho do seu serviço de API está correto

interface Conta {
  id?: number;
  banco: string;
  numero_conta: string;
  saldo: number;
}

const route = useRoute();
const router = useRouter();

const conta = ref<Conta>({
  banco: '',
  numero_conta: '',
  saldo: 0,
});

const isLoading = ref(false);
const error = ref<string | null>(null);

const isEditing = computed(() => !!route.params.id);
const formTitle = computed(() => isEditing.value ? 'Editar Conta Bancária' : 'Adicionar Nova Conta Bancária');

const fetchConta = async (id: number) => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get(`/financeiro/contas/${id}/`);
    conta.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar conta:', err);
    error.value = 'Falha ao carregar os dados da conta.';
  } finally {
    isLoading.value = false;
  }
};

const submitForm = async () => {
  try {
    if (isEditing.value) {
      // Lógica para editar uma conta existente
      await api.put(`/financeiro/contas/${conta.value.id}/`, conta.value);
    } else {
      // Lógica para criar uma nova conta
      await api.post('/financeiro/contas/', conta.value);
    }
    router.push({ name: 'lista-contas' }); // Redireciona para a lista após salvar
  } catch (err) {
    console.error('Erro ao salvar conta:', err);
    error.value = 'Falha ao salvar a conta. Verifique os dados e tente novamente.';
  }
};

onMounted(() => {
  if (isEditing.value) {
    fetchConta(Number(route.params.id));
  }
});
</script>

<style scoped>
/* Estilos específicos para o formulário */
</style>
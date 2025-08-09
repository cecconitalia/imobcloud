<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">Gerir Contas Bancárias</h1>
    
    <div v-if="isLoading" class="text-center text-gray-500">
      <p>Carregando contas...</p>
    </div>

    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <div class="bg-white shadow-md rounded-lg p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-700">Contas Cadastradas</h2>
        <button @click="adicionarConta" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">
          Nova Conta
        </button>
      </div>

      <table class="min-w-full leading-normal">
        <thead>
          <tr>
            <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              Banco
            </th>
            <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              Número da Conta
            </th>
            <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              Saldo
            </th>
            <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
              Ações
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="conta in contas" :key="conta.id">
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
              <p class="text-gray-900 whitespace-no-wrap">{{ conta.banco }}</p>
            </td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
              <p class="text-gray-900 whitespace-no-wrap">{{ conta.numero_conta }}</p>
            </td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
              <p class="text-gray-900 whitespace-no-wrap">{{ formatCurrency(conta.saldo) }}</p>
            </td>
            <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
              <button @click="editarConta(conta.id)" class="text-blue-600 hover:text-blue-900 transition-colors mr-3">
                Editar
              </button>
              <button @click="excluirConta(conta.id)" class="text-red-600 hover:text-red-900 transition-colors">
                Excluir
              </button>
            </td>
          </tr>
          <tr v-if="contas.length === 0">
            <td colspan="4" class="text-center py-4 text-gray-500">Nenhuma conta bancária cadastrada.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api'; // Certifique-se de que este import está correto

interface Conta {
  id: number;
  banco: string;
  numero_conta: string;
  saldo: number;
}

const contas = ref<Conta[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const router = useRouter();

const fetchContas = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get('/financeiro/contas/');
    contas.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar contas:', err);
    error.value = 'Falha ao carregar as contas bancárias.';
  } finally {
    isLoading.value = false;
  }
};

const adicionarConta = () => {
  router.push({ name: 'conta-nova' });
};

const editarConta = (id: number) => {
  router.push({ name: 'conta-editar', params: { id } });
};

const excluirConta = async (id: number) => {
  if (confirm('Tem certeza que deseja excluir esta conta?')) {
    try {
      await api.delete(`/financeiro/contas/${id}/`);
      fetchContas(); // Recarrega a lista após a exclusão
    } catch (err) {
      console.error('Erro ao excluir conta:', err);
      alert('Falha ao excluir a conta.');
    }
  }
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
};

onMounted(fetchContas);
</script>

<style scoped>
/* Adicione aqui quaisquer estilos adicionais, se necessário */
</style>
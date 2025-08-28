<template>
  <div v-if="loading">
    <p>Carregando contrato...</p>
  </div>
  <div v-else-if="error">
    <p class="text-danger">Ocorreu um erro ao carregar o contrato: {{ error }}</p>
  </div>
  <div v-else class="contrato-container" v-html="contratoHtml"></div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';
import { useToast } from 'vue-toast-notification';

export default defineComponent({
  name: 'ContratoReadView',
  setup() {
    const route = useRoute();
    const toast = useToast();
    const contratoHtml = ref('');
    const loading = ref(true);
    const error = ref('');

    const fetchContrato = async () => {
      try {
        const contratoId = route.params.id;
        const response = await api.get(`/contratos/${contratoId}/html/`);
        contratoHtml.value = response.data;
      } catch (err) {
        error.value = 'Não foi possível carregar o conteúdo do contrato.';
        toast.error(error.value);
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchContrato);

    return {
      contratoHtml,
      loading,
      error,
    };
  },
});
</script>

<style scoped>
.contrato-container {
  background-color: #f8f9fa;
  padding: 2rem;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  white-space: pre-wrap; /* Mantém a formatação do texto */
  font-family: Arial, sans-serif;
}
</style>
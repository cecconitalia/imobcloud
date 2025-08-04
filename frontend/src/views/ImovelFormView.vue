<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Imóvel' : 'Adicionar Novo Imóvel' }}</h1>
    </header>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do imóvel...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="imovel-form">
      <div class="form-group full-width">
        <label for="endereco">Endereço Completo</label>
        <input type="text" id="endereco" v-model="imovel.endereco" required />
      </div>

      <div class="form-group">
        <label for="cidade">Cidade</label>
        <input type="text" id="cidade" v-model="imovel.cidade" required />
      </div>
      <div class="form-group">
        <label for="estado">Estado (UF)</label>
        <input type="text" id="estado" maxlength="2" v-model="imovel.estado" required />
      </div>
       <div class="form-group">
        <label for="cep">CEP</label>
        <input type="text" id="cep" v-model="imovel.cep" required />
      </div>

      <div class="form-group">
        <label for="tipo">Tipo de Imóvel</label>
        <select id="tipo" v-model="imovel.tipo" required>
          <option value="Casa">Casa</option>
          <option value="Apartamento">Apartamento</option>
          <option value="Terreno">Terreno</option>
          <option value="Sala Comercial">Sala Comercial</option>
        </select>
      </div>
      <div class="form-group">
        <label for="finalidade">Finalidade</label>
        <select id="finalidade" v-model="imovel.finalidade" required>
          <option value="Venda">Venda</option>
          <option value="Aluguel">Aluguel</option>
        </select>
      </div>

      <div class="form-group">
        <label for="valor_venda">Valor de Venda (R$)</label>
        <input type="number" step="0.01" id="valor_venda" v-model.number="imovel.valor_venda" />
      </div>
      <div class="form-group">
        <label for="valor_aluguel">Valor de Aluguel (R$)</label>
        <input type="number" step="0.01" id="valor_aluguel" v-model.number="imovel.valor_aluguel" />
      </div>

      <div class="form-group">
        <label for="quartos">Quartos</label>
        <input type="number" id="quartos" v-model.number="imovel.quartos" />
      </div>
       <div class="form-group">
        <label for="area_total">Área Total (m²)</label>
        <input type="number" step="0.01" id="area_total" v-model.number="imovel.area_total" required />
      </div>

      <div class="form-group">
        <label for="status">Status</label>
        <select id="status" v-model="imovel.status" required>
          <option value="Disponível">Disponível</option>
          <option value="Alugado">Alugado</option>
          <option value="Vendido">Vendido</option>
        </select>
      </div>

      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Guardando...' : 'Guardar Alterações' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();

// Determina se estamos em modo de edição com base na presença do parâmetro 'id' no URL
const imovelId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!imovelId.value);

// Objeto reativo que guarda os dados do formulário
const imovel = ref({
  endereco: '',
  cidade: '',
  estado: '',
  cep: '',
  tipo: 'Casa',
  finalidade: 'Venda',
  valor_venda: null,
  valor_aluguel: null,
  area_total: null,
  quartos: null,
  status: 'Disponível',
});

// Controlo de estados da UI
const isLoadingData = ref(false);
const isSubmitting = ref(false);

// Função para buscar os dados de um imóvel existente (só é executada em modo de edição)
async function fetchImovelData() {
  if (isEditing.value) {
    isLoadingData.value = true;
    try {
      const response = await apiClient.get(`/v1/imoveis/imoveis/${imovelId.value}/`);
      imovel.value = response.data; // Preenche o formulário com os dados da API
    } catch (error) {
      console.error("Erro ao buscar dados do imóvel:", error);
      alert("Não foi possível carregar os dados do imóvel para edição.");
      router.push({ name: 'imoveis' });
    } finally {
      isLoadingData.value = false;
    }
  }
}

// Quando o componente é montado, chama a função para buscar os dados se necessário
onMounted(() => {
  fetchImovelData();
});

// Função de submissão que agora lida com criar (POST) e editar (PUT)
async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      // MODO EDIÇÃO: Usa o método PUT para atualizar o imóvel existente
      await apiClient.put(`/v1/imoveis/imoveis/${imovelId.value}/`, imovel.value);
    } else {
      // MODO CRIAÇÃO: Usa o método POST para criar um novo imóvel
      await apiClient.post('/v1/imoveis/imoveis/', imovel.value);
    }
    router.push({ name: 'imoveis' }); // Redireciona para a lista após o sucesso
  } catch (error) {
    console.error("Erro ao guardar o imóvel:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o imóvel. Verifique os dados.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'imoveis' });
}
</script>

<style scoped>
/* Os seus estilos do formulário continuam aqui */
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.imovel-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; flex: 1 1 calc(50% - 1.5rem); }
.form-group.full-width { flex-basis: 100%; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, select { padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.loading-message { text-align: center; padding: 2rem; }
</style>
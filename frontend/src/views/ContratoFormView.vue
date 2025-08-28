<template>
  <div class="page-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Contrato' : 'Novo Contrato' }}</h1>
      <router-link to="/contratos" class="btn-secondary">
        <i class="fas fa-arrow-left"></i> Voltar à Lista
      </router-link>
    </header>

    <form @submit.prevent="handleSubmit" class="form-layout">
      <div class="form-card">
        <h3 class="card-title">Detalhes do Contrato</h3>
        <div class="form-grid">
          
          <div class="form-group">
            <label for="tipo_contrato">Tipo de Contrato</label>
            <select id="tipo_contrato" v-model="contrato.tipo_contrato" required>
              <option disabled value="">Selecione o tipo</option>
              <option value="Venda">Venda</option>
              <option value="Aluguel">Aluguel</option>
            </select>
          </div>

          <div class="form-group">
            <label for="status_contrato">Status do Contrato</label>
            <select id="status_contrato" v-model="contrato.status_contrato" required>
              <option disabled value="">Selecione o status</option>
              <option value="Pendente">Pendente</option>
              <option value="Ativo">Ativo</option>
              <option value="Concluído">Concluído</option>
              <option value="Rescindido">Rescindido</option>
              <option value="Inativo">Inativo</option>
            </select>
          </div>

          <div class="form-group">
            <label for="valor_total">Valor Total do Contrato (R$)</label>
            <input type="number" id="valor_total" v-model.number="contrato.valor_total" required step="0.01" />
          </div>

          <div v-if="contrato.tipo_contrato === 'Aluguel'" class="form-group">
            <label for="duracao_meses">Duração (meses)</label>
            <input type="number" id="duracao_meses" v-model.number="contrato.duracao_meses" />
          </div>

          <div class="form-group">
            <label for="data_inicio">Data de Início</label>
            <input type="date" id="data_inicio" v-model="contrato.data_inicio" required />
          </div>

          <div class="form-group">
            <label for="data_assinatura">Data de Assinatura</label>
            <input type="date" id="data_assinatura" v-model="contrato.data_assinatura" required />
          </div>
        </div>
      </div>

      <div class="form-card">
        <h3 class="card-title">Partes Envolvidas</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="imovel">Imóvel</label>
            <select id="imovel" v-model="contrato.imovel" required>
              <option disabled :value="null">Selecione um imóvel</option>
              <option v-for="imovel in imoveis" :key="imovel.id" :value="imovel.id">
                {{ imovel.titulo_anuncio || imovel.logradouro }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="proprietario">Proprietário</label>
            <select id="proprietario" v-model="contrato.proprietario" required>
              <option disabled :value="null">Selecione o proprietário</option>
              <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                {{ cliente.nome_completo }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="inquilino">Inquilino / Comprador</label>
            <select id="inquilino" v-model="contrato.inquilino" required>
              <option disabled :value="null">Selecione o inquilino/comprador</option>
              <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                {{ cliente.nome_completo }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-card">
         <h3 class="card-title">Informações Adicionais</h3>
          <div class="form-group full-width">
            <label for="informacoes_adicionais">Cláusulas e Observações</label>
            <textarea id="informacoes_adicionais" v-model="contrato.informacoes_adicionais" rows="5"></textarea>
          </div>
      </div>
      
      <div class="form-actions">
        <button type="button" @click="$router.push('/contratos')" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm"></span>
          {{ isSubmitting ? 'Salvando...' : 'Salvar Contrato' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

const route = useRoute();
const router = useRouter();

// A estrutura do 'ref' agora armazena apenas os IDs para os campos de seleção
const contrato = ref({
  tipo_contrato: '',
  status_contrato: 'Pendente',
  valor_total: 0,
  duracao_meses: 12,
  data_inicio: '',
  data_assinatura: '',
  imovel: null as number | null,
  proprietario: null as number | null,
  inquilino: null as number | null,
  informacoes_adicionais: '',
});

const clientes = ref<any[]>([]);
const imoveis = ref<any[]>([]);

const isSubmitting = ref(false);
const contratoId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!contratoId.value);

async function fetchData() {
  try {
    const [clientesRes, imoveisRes] = await Promise.all([
      apiClient.get('/v1/clientes/'),
      apiClient.get('/v1/imoveis/')
    ]);
    clientes.value = clientesRes.data;
    imoveis.value = imoveisRes.data;

    if (isEditing.value) {
      const contratoRes = await apiClient.get(`/v1/contratos/${contratoId.value}/`);
      const data = contratoRes.data;

      // *** CORREÇÃO DE CARREGAMENTO ***
      // Mapeia os dados da API para o nosso 'ref', garantindo que apenas os IDs
      // sejam armazenados nos campos de seleção.
      contrato.value = {
        ...data,
        imovel: data.imovel?.id || null,
        proprietario: data.proprietario?.id || null,
        inquilino: data.inquilino?.id || null,
      };
    }
  } catch (error) {
    console.error("Erro ao buscar dados para o formulário:", error);
    alert("Não foi possível carregar os dados necessários.");
  }
}

onMounted(fetchData);

async function handleSubmit() {
  isSubmitting.value = true;
  
  // O 'payload' já está no formato correto que o backend espera,
  // pois o 'ref' agora armazena apenas os IDs.
  const payload = { ...contrato.value };

  if (payload.tipo_contrato === 'Venda') {
    payload.duracao_meses = 1;
  }

  try {
    if (isEditing.value) {
      await apiClient.put(`/v1/contratos/${contratoId.value}/`, payload);
      alert('Contrato atualizado com sucesso!');
    } else {
      await apiClient.post('/v1/contratos/', payload);
      alert('Contrato criado com sucesso!');
    }
    router.push('/contratos');
  } catch (error: any) {
    console.error("Erro ao salvar contrato:", error.response?.data || error);
    const errorMsg = error.response?.data ? JSON.stringify(error.response.data) : 'Verifique os dados e tente novamente.';
    alert(`Ocorreu um erro ao salvar o contrato: ${errorMsg}`);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
/* Estilos padronizados para o formulário */
.page-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}
h1 {
  font-size: 2rem;
}
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #6c757d;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #007bff;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.form-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 2rem;
}
.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
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
  font-weight: 500;
  color: #495057;
}
input, select, textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
}
input:focus, select:focus, textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
  outline: none;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
</style>
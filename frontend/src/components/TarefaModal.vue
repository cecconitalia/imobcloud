<template>
  <div class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <h3>{{ isEditing ? 'Editar Tarefa' : 'Adicionar Nova Tarefa' }}</h3>
        <button @click="emit('close')" class="close-btn">&times;</button>
      </div>

      <div v-if="tarefaLocal.oportunidade_titulo" class="info-section">
        <h4>Oportunidade: {{ tarefaLocal.oportunidade_titulo }}</h4>
        <p v-if="tarefaLocal.cliente_nome">Cliente: {{ tarefaLocal.cliente_nome }}</p>
        <p v-if="tarefaLocal.imovel_endereco">Imóvel: {{ tarefaLocal.imovel_endereco }}</p>
      </div>

      <form @submit.prevent="handleSubmit">

        <div class="form-group" v-if="!isEditing">
          <label for="cliente-select">Cliente (Opcional)</label>
          <v-select
            id="cliente-select"
            label="nome_completo"
            :options="clientes"
            v-model="clienteSelecionado"
            placeholder="Pesquisar clientes..."
          >
            <template #option="option">
              {{ option.nome_completo }}
            </template>
            <template #no-options>
              <div class="no-results-message">Nenhum cliente encontrado.</div>
            </template>
          </v-select>
        </div>

        <div class="form-group" v-if="!isEditing && clienteSelecionado">
          <label for="oportunidade-select">Oportunidade (Opcional)</label>
          <v-select
            id="oportunidade-select"
            label="titulo"
            :options="oportunidadesFiltradas"
            v-model="oportunidadeSelecionada"
            placeholder="Selecione a oportunidade..."
          >
            <template #option="option">
              {{ option.titulo }}
            </template>
            <template #no-options>
              <div class="no-results-message">Nenhuma oportunidade encontrada para este cliente.</div>
            </template>
          </v-select>
        </div>

        <div class="form-group">
          <label for="descricao">Descrição</label>
          <textarea id="descricao" v-model="tarefaLocal.descricao" required></textarea>
        </div>
        <div class="form-group">
          <label for="data_conclusao">Prazo</label>
          <input type="date" id="data_conclusao" v-model="tarefaLocal.data_conclusao" />
        </div>
        <div class="modal-actions">
          <button v-if="isEditing && !tarefaLocal.concluida" type="button" @click="handleConcluir" class="btn-success">
            Concluir Tarefa
          </button>
          <button v-if="isEditing" type="button" @click="handleDelete" class="btn-danger">
            Eliminar
          </button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'A guardar...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, onMounted, watch } from 'vue';
import apiClient from '@/services/api';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const props = defineProps({
  oportunidadeId: { type: [String, Number, null], default: null },
  tarefa: { type: Object, default: null },
  dataInicial: { type: String, default: '' },
});

const emit = defineEmits(['close', 'saved']);

const isEditing = ref(false);
const isSubmitting = ref(false);
const clientes = ref<any[]>([]);
const oportunidades = ref<any[]>([]);
const clienteSelecionado = ref(null);
const oportunidadeSelecionada = ref(null);

const oportunidadesFiltradas = ref<any[]>([]);

const tarefaLocal = ref({
  id: null,
  descricao: '',
  data_conclusao: '',
  oportunidade: props.oportunidadeId,
  oportunidade_titulo: '',
  cliente_nome: '',
  imovel_endereco: '',
  concluida: false,
});

watch(() => props.tarefa, (novaTarefa) => {
    if (novaTarefa) {
        isEditing.value = true;
        tarefaLocal.value = { ...novaTarefa };
    } else {
        isEditing.value = false;
        tarefaLocal.value = {
            id: null,
            descricao: '',
            data_conclusao: props.dataInicial,
            oportunidade: props.oportunidadeId,
            oportunidade_titulo: '',
            cliente_nome: '',
            imovel_endereco: '',
            concluida: false,
        };
        clienteSelecionado.value = null;
        oportunidadeSelecionada.value = null;
    }
}, { immediate: true });

watch(clienteSelecionado, (novoCliente) => {
    if (novoCliente) {
        oportunidadesFiltradas.value = oportunidades.value.filter(op => op.cliente?.id === novoCliente.id);
        oportunidadeSelecionada.value = null;
    } else {
        oportunidadesFiltradas.value = [];
    }
});

watch(oportunidadeSelecionada, (novaOportunidade) => {
    if (novaOportunidade) {
        tarefaLocal.value.oportunidade = novaOportunidade.id;
        tarefaLocal.value.oportunidade_titulo = novaOportunidade.titulo;
        tarefaLocal.value.cliente_nome = novaOportunidade.cliente?.nome_completo || 'N/A';
        tarefaLocal.value.imovel_endereco = novaOportunidade.imovel?.endereco || 'N/A';
    } else {
        tarefaLocal.value.oportunidade = null;
        tarefaLocal.value.oportunidade_titulo = '';
        tarefaLocal.value.cliente_nome = '';
        tarefaLocal.value.imovel_endereco = '';
    }
});

onMounted(async () => {
  if (!isEditing.value) {
    try {
      const [clientesResponse, oportunidadesResponse] = await Promise.all([
        apiClient.get('/v1/clientes/clientes/'),
        apiClient.get('/v1/clientes/oportunidades/')
      ]);
      clientes.value = clientesResponse.data;
      oportunidades.value = oportunidadesResponse.data;
    } catch (error) {
      console.error("Erro ao carregar dados:", error);
    }
  }
});

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    const payload = {
        descricao: tarefaLocal.value.descricao,
        data_conclusao: tarefaLocal.value.data_conclusao,
        oportunidade: tarefaLocal.value.oportunidade,
        concluida: tarefaLocal.value.concluida,
    };
    if (isEditing.value) {
        if (tarefaLocal.value.oportunidade) {
            await apiClient.patch(`/v1/clientes/oportunidades/${tarefaLocal.value.oportunidade}/tarefas/${tarefaLocal.value.id}/`, payload);
        } else {
            // CORREÇÃO: O URL deve incluir 'clientes/'
            await apiClient.patch(`/v1/clientes/tarefas/${tarefaLocal.value.id}/`, payload);
        }
    } else {
        if (tarefaLocal.value.oportunidade) {
            await apiClient.post(`/v1/clientes/oportunidades/${tarefaLocal.value.oportunidade}/tarefas/`, payload);
        } else {
            // CORREÇÃO: O URL deve incluir 'clientes/'
            await apiClient.post(`/v1/clientes/tarefas/`, payload);
        }
    }
    emit('saved');
  } catch (error) {
    console.error("Erro ao salvar a tarefa:", error);
    alert('Ocorreu um erro ao salvar a tarefa.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleConcluir() {
  if (!window.confirm('Tem certeza que deseja concluir esta tarefa?')) {
    return;
  }
  isSubmitting.value = true;
  try {
    const payload = { concluida: true };
    if (tarefaLocal.value.oportunidade) {
        await apiClient.patch(`/v1/clientes/oportunidades/${tarefaLocal.value.oportunidade}/tarefas/${tarefaLocal.value.id}/`, payload);
    } else {
        // CORREÇÃO: O URL deve incluir 'clientes/'
        await apiClient.patch(`/v1/clientes/tarefas/${tarefaLocal.value.id}/`, payload);
    }
    emit('saved');
  } catch (error) {
    console.error("Erro ao concluir a tarefa:", error);
    alert('Ocorreu um erro ao concluir a tarefa.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleDelete() {
  if (!window.confirm('Tem certeza que deseja eliminar esta tarefa?')) {
    return;
  }
  isSubmitting.value = true;
  try {
    if (tarefaLocal.value.oportunidade) {
        await apiClient.delete(`/v1/clientes/oportunidades/${tarefaLocal.value.oportunidade}/tarefas/${tarefaLocal.value.id}/`);
    } else {
        // CORREÇÃO: O URL deve incluir 'clientes/'
        await apiClient.delete(`/v1/clientes/tarefas/${tarefaLocal.value.id}/`);
    }
    emit('saved');
  } catch (error) {
    console.error("Erro ao eliminar a tarefa:", error);
    alert('Ocorreu um erro ao eliminar a tarefa.');
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.modal-header h3 {
  margin: 0;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}
.info-section {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
}
.info-section h4 {
    margin: 0 0 0.5rem 0;
}
.form-group {
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
}
.form-group label {
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.form-group textarea,
.form-group input,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
}
.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.btn-primary, .btn-danger, .btn-success {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-success { background-color: #28a745; color: white; }
.no-results-message { padding: 1rem; text-align: center; }
</style>
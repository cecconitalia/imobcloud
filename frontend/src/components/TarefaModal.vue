<template>
  <div class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <h3>{{ isEditing ? 'Editar Tarefa' : 'Adicionar Nova Tarefa' }}</h3>
        <button @click="emit('close')" class="close-btn">&times;</button>
      </div>

      <div v-if="isEditing && tarefaLocal.oportunidade_titulo" class="info-section">
        <p>Esta tarefa está atualmente ligada à oportunidade: <strong>{{ tarefaLocal.oportunidade_titulo }}</strong></p>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
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

        <div class="form-group" v-if="clienteSelecionado">
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
  // A tarefa recebida como prop pode ter a estrutura que vem do backend
  tarefa: { type: Object as () => any, default: null },
  dataInicial: { type: String, default: '' },
});

const emit = defineEmits(['close', 'saved']);

const isEditing = ref(false);
const isSubmitting = ref(false);
const clientes = ref<any[]>([]);
const oportunidades = ref<any[]>([]);
const clienteSelecionado = ref<any>(null);
const oportunidadeSelecionada = ref<any>(null);

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
        if (oportunidadeSelecionada.value && oportunidadeSelecionada.value.cliente?.id !== novoCliente.id) {
            oportunidadeSelecionada.value = null;
        }
    } else {
        oportunidadesFiltradas.value = [];
        oportunidadeSelecionada.value = null;
    }
});

watch(oportunidadeSelecionada, (novaOportunidade) => {
    if (novaOportunidade) {
        tarefaLocal.value.oportunidade = novaOportunidade.id;
    } else {
        tarefaLocal.value.oportunidade = null;
    }
});

onMounted(async () => {
  try {
    // Carrega as listas de clientes e oportunidades
    const [clientesResponse, oportunidadesResponse] = await Promise.all([
      apiClient.get('/v1/clientes/clientes/'), // URL corrigida
      apiClient.get('/v1/clientes/oportunidades/') // URL corrigida
    ]);
    clientes.value = clientesResponse.data;
    oportunidades.value = oportunidadesResponse.data;

    // CORREÇÃO: Lógica para pré-selecionar os campos no modo de edição
    if (isEditing.value && props.tarefa) {
      let clienteIdParaBuscar: number | null = null;

      // Se a tarefa tem uma oportunidade, o cliente vem dela
      if (props.tarefa.oportunidade) {
        // Encontra a oportunidade completa na lista
        const oportunidadeDaTarefa = oportunidades.value.find(o => o.id === props.tarefa.oportunidade);
        if (oportunidadeDaTarefa) {
          oportunidadeSelecionada.value = oportunidadeDaTarefa;
          // Pega o ID do cliente a partir da oportunidade encontrada
          if (oportunidadeDaTarefa.cliente) {
            clienteIdParaBuscar = oportunidadeDaTarefa.cliente.id;
          }
        }
      } 
      // Se não tem oportunidade, mas tem um cliente direto
      else if (props.tarefa.cliente) {
        clienteIdParaBuscar = props.tarefa.cliente.id;
      }

      // Se encontramos um ID de cliente, busca o objeto completo e seleciona
      if (clienteIdParaBuscar) {
        clienteSelecionado.value = clientes.value.find(c => c.id === clienteIdParaBuscar) || null;
      }
    }
  } catch (error) {
    console.error("Erro ao carregar dados do modal:", error);
  }
});


async function handleSubmit() {
  isSubmitting.value = true;
  try {
    const payload = {
        descricao: tarefaLocal.value.descricao,
        data_conclusao: tarefaLocal.value.data_conclusao,
        oportunidade: oportunidadeSelecionada.value ? oportunidadeSelecionada.value.id : null,
        concluida: tarefaLocal.value.concluida,
        cliente: clienteSelecionado.value ? clienteSelecionado.value.id : null,
    };
    if (isEditing.value) {
        await apiClient.patch(`/v1/clientes/tarefas/${tarefaLocal.value.id}/`, payload);
    } else {
        await apiClient.post(`/v1/clientes/tarefas/`, payload);
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
    await apiClient.patch(`/v1/clientes/tarefas/${tarefaLocal.value.id}/`, payload);
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
    await apiClient.delete(`/v1/clientes/tarefas/${tarefaLocal.value.id}/`);
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
/* Estilos permanecem os mesmos */
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
    background-color: #f0f4f8;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
    border-left: 4px solid #007bff;
}
.info-section p {
    margin: 0;
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
.form-group input {
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

/* Estilos para o v-select */
:deep(.vs__dropdown-toggle) {
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
}
:deep(.vs__search::placeholder) {
    color: #999;
}
</style>
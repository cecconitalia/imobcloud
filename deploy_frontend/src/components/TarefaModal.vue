<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h3>{{ tituloModal }}</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <form @submit.prevent="submitForm" class="modal-form">
        
        <div class="form-group">
          <label for="titulo">Título da Tarefa</label>
          <input 
            id="titulo"
            v-model="tarefa.titulo" 
            type="text" 
            placeholder="Ex: Ligar para o cliente" 
            required 
          />
        </div>

        <div class="form-group">
          <label for="descricao">Descrição</label>
          <textarea 
            id="descricao"
            v-model="tarefa.descricao" 
            placeholder="Adicionar mais detalhes..."
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="data_vencimento">Prazo Final</label>
          <input 
            id="data_vencimento"
            v-model="tarefa.data_vencimento" 
            type="datetime-local" 
            required 
          />
        </div>

        <div class="form-group">
          <label for="oportunidade">Associar à Oportunidade</label>
          <v-select
            id="oportunidade"
            label="formatted_title"
            :options="oportunidades"
            :reduce="oportunidade => oportunidade.id"
            v-model="tarefa.oportunidade"
            placeholder="Nenhuma oportunidade associada"
          >
            <template #option="option">
              <strong>{{ option.titulo }}</strong><br>
              <small>{{ option.cliente?.nome_completo || 'Cliente não informado' }}</small>
            </template>
            <template #no-options>
              Nenhuma oportunidade encontrada.
            </template>
          </v-select>
        </div>

        <div class="modal-actions">
          <button v-if="isEditing" type="button" @click="handleDelete" class="btn-danger">
            Eliminar
          </button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ submitButtonText }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, defineProps, defineEmits, watch } from 'vue';
import apiClient from '@/services/api';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

// --- PROPS E EMITS ---
const props = defineProps<{
  tarefaParaEditar?: any | null;
  oportunidadeInicial?: any | null;
}>();

const emit = defineEmits(['close', 'saved']);

// --- ESTADO DO COMPONENTE ---
const isSubmitting = ref(false);
const oportunidades = ref<any[]>([]);

const tarefa = reactive({
  id: null as number | null,
  titulo: '',
  descricao: '',
  data_vencimento: '',
  oportunidade: null as number | null,
});

// --- DADOS COMPUTADOS ---
const isEditing = computed(() => !!tarefa.id);
const tituloModal = computed(() => isEditing.value ? 'Editar Tarefa' : 'Adicionar Nova Tarefa');
const submitButtonText = computed(() => {
  if (isSubmitting.value) {
    return isEditing.value ? 'A atualizar...' : 'A criar...';
  }
  return isEditing.value ? 'Atualizar Tarefa' : 'Criar Tarefa';
});

// --- MÉTODOS ---
const closeModal = () => {
  emit('close');
};

const fetchOportunidades = async () => {
  try {
    const response = await apiClient.get('/v1/oportunidades/');
    // CORREÇÃO: Mapeia os dados para incluir uma propriedade formatada para o v-select
    oportunidades.value = response.data.map((op: any) => ({
      ...op,
      formatted_title: `${op.titulo} - ${op.cliente?.nome_completo || 'Cliente não informado'}`
    }));
  } catch (error) {
    console.error("Erro ao carregar oportunidades:", error);
  }
};

const submitForm = async () => {
  isSubmitting.value = true;
  try {
    // CORREÇÃO: Cria uma oportunidade padrão se nenhuma for selecionada
    if (!tarefa.oportunidade) {
      let clientePadraoId = null;
      try {
        const clienteResponse = await apiClient.get('/v1/clientes/', { params: { search: 'Cliente Padrão' } });
        if (clienteResponse.data.length > 0) {
          clientePadraoId = clienteResponse.data[0].id;
        } else {
          const novoClienteResponse = await apiClient.post('/v1/clientes/', { nome_completo: 'Cliente Padrão', tipo_cliente: 'PESSOA_FISICA' });
          clientePadraoId = novoClienteResponse.data.id;
        }
      } catch (error) {
        console.error("Erro ao encontrar ou criar cliente padrão:", error);
        alert('Ocorreu um erro ao preparar o cliente padrão.');
        return;
      }

      const novaOportunidadePayload = {
        titulo: `Oportunidade gerada automaticamente para a tarefa '${tarefa.titulo}'`,
        fase: 'LEAD',
        probabilidade: 10,
        valor_estimado: 0,
        cliente: clientePadraoId, // Adiciona o cliente padrão
      };
      const response = await apiClient.post('/v1/oportunidades/', novaOportunidadePayload);
      tarefa.oportunidade = response.data.id;
    }

    const payload = {
      titulo: tarefa.titulo,
      descricao: tarefa.descricao,
      data_vencimento: tarefa.data_vencimento,
      oportunidade: tarefa.oportunidade,
    };

    if (isEditing.value) {
      await apiClient.patch(`/v1/tarefas/${tarefa.id}/`, payload);
    } else {
      await apiClient.post('/v1/tarefas/', payload);
    }
    
    emit('saved');

  } catch (error) {
    console.error("Erro ao salvar a tarefa:", error);
    alert('Ocorreu um erro ao salvar a tarefa. Verifique a consola para mais detalhes.');
  } finally {
    isSubmitting.value = false;
  }
};

const handleDelete = async () => {
  if (!window.confirm('Tem a certeza de que deseja eliminar esta tarefa?')) {
    return;
  }
  isSubmitting.value = true;
  try {
    await apiClient.delete(`/v1/tarefas/${tarefa.id}/`);
    
    emit('saved');

  } catch (error) {
    console.error("Erro ao eliminar a tarefa:", error);
    alert('Ocorreu um erro ao eliminar a tarefa.');
  } finally {
    isSubmitting.value = false;
  }
};

const preencherFormularioParaEdicao = (tarefaParaEditar: any) => {
    tarefa.id = tarefaParaEditar.id;
    tarefa.titulo = tarefaParaEditar.titulo;
    tarefa.descricao = tarefaParaEditar.descricao;
    tarefa.data_vencimento = tarefaParaEditar.data_vencimento 
      ? new Date(tarefaParaEditar.data_vencimento).toISOString().slice(0, 16) 
      : '';
    tarefa.oportunidade = tarefaParaEditar.oportunidade;
};

// --- CICLO DE VIDA ---
onMounted(() => {
  fetchOportunidades();
  if (props.tarefaParaEditar) {
    preencherFormularioParaEdicao(props.tarefaParaEditar);
  }
  else if (props.oportunidadeInicial) {
    tarefa.oportunidade = props.oportunidadeInicial.id;
  }
});

watch(() => props.oportunidadeInicial, (novaOportunidade) => {
  if (novaOportunidade) {
    tarefa.oportunidade = novaOportunidade.id;
  } else {
    tarefa.oportunidade = null;
  }
});
</script>

<style scoped>
/* Estilos modernos e limpos para o modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}
.modal-container {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 550px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  transform: scale(0.95);
  animation: scaleIn 0.3s forwards;
}

@keyframes scaleIn {
  to {
    transform: scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}
.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #111827;
}
.close-btn {
  background: #f3f4f6;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: #6b7280;
  transition: background-color 0.2s, color 0.2s;
}
.close-btn:hover {
    background-color: #e5e7eb;
    color: #111827;
}

.modal-form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.form-group {
    display: flex;
    flex-direction: column;
}
.form-group label {
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #374151;
    font-size: 0.9rem;
}
.form-group input,
.form-group textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 1rem;
    box-sizing: border-box;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group input:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}
textarea {
    resize: vertical;
}

.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}
.btn-primary, .btn-danger {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  transition: background-color 0.2s, transform 0.1s;
}
.btn-primary { background-color: #2563eb; color: white; }
.btn-primary:hover { background-color: #1d4ed8; }
.btn-primary:disabled { background-color: #9ca3af; cursor: not-allowed; }

.btn-danger { background-color: #dc2626; color: white; }
.btn-danger:hover { background-color: #b91c1c; }

.btn-primary:active, .btn-danger:active {
    transform: scale(0.98);
}

/* Estilos para o v-select */
:deep(.vs__dropdown-toggle) {
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #d1d5db;
}
:deep(.vs--open .vs__dropdown-toggle) {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}
</style>
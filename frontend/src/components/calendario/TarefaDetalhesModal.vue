<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Detalhes da Tarefa</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <div v-if="tarefa" class="modal-content">
        <p><strong>Título:</strong> {{ tarefa.titulo }}</p>
        <p><strong>Prazo:</strong> {{ formatarData(tarefa.data_vencimento) }}</p>
        <p><strong>Status:</strong>
          <span :class="['status-badge', tarefa.concluida ? 'status-concluido' : 'status-pendente']">
            {{ tarefa.concluida ? 'Concluída' : 'Pendente' }}
          </span>
        </p>
        <p><strong>Responsável:</strong> {{ tarefa.responsavel_nome || 'Não atribuído' }}</p>
        <p v-if="tarefa.descricao"><strong>Descrição:</strong> {{ tarefa.descricao }}</p>
        
        <p v-if="tarefa.concluida && tarefa.observacoes_finalizacao" class="observacoes-finalizacao">
          <strong>Observações da Finalização:</strong> {{ tarefa.observacoes_finalizacao }}
        </p>
        </div>

      <div class="modal-actions">
        <button @click="closeModal" class="btn-secondary">Fechar</button>
        <button v-if="!tarefa.concluida" @click="handleEditar" class="btn-edit">Alterar Tarefa</button>
        <button v-if="!tarefa.concluida" @click="handleFinalizar" class="btn-success">Finalizar Tarefa</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import apiClient from '@/services/api';

const props = defineProps<{
  tarefa: any;
}>();

const emit = defineEmits(['close', 'edit', 'saved']);

function closeModal() {
  emit('close');
}

// --- INÍCIO DA ALTERAÇÃO: Pede observações ao finalizar ---
async function handleFinalizar() {
  const observacoes = window.prompt('Deseja adicionar alguma observação ao finalizar a tarefa? (Opcional)');

  // Se o utilizador clicar em "Cancelar", o prompt retorna null.
  if (observacoes === null) {
    return;
  }

  try {
    const payload = { 
      concluida: true,
      observacoes_finalizacao: observacoes // Envia as observações para a API
    };
    await apiClient.patch(`/v1/tarefas/${props.tarefa.id}/`, payload);
    emit('saved');
  } catch (error) {
    console.error("Erro ao finalizar a tarefa:", error);
    alert('Não foi possível finalizar a tarefa.');
  }
}
// --- FIM DA ALTERAÇÃO ---

function handleEditar() {
  emit('edit', props.tarefa);
}

function formatarData(data: string) {
  if (!data) return 'N/A';
  const dataObj = new Date(data);
  return dataObj.toLocaleString('pt-BR', {
    dateStyle: 'long',
    timeStyle: 'short',
  });
}
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-container { background: white; padding: 2rem; border-radius: 8px; width: 100%; max-width: 550px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
.modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 1rem; margin-bottom: 1rem; }
.modal-header h3 { margin: 0; font-size: 1.5rem; }
.close-btn { background: none; border: none; font-size: 2rem; cursor: pointer; }
.modal-content p { margin: 0.5rem 0; line-height: 1.6; }
.modal-actions { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem; }
.btn-secondary, .btn-success, .btn-edit { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-success { background-color: #28a745; color: white; }
.btn-edit { background-color: #ffc107; color: #212529; }
.status-badge { padding: 0.25em 0.6em; border-radius: 10px; color: white; font-size: 0.9em; }
.status-pendente { background-color: #ffc107; color: #212529; }
.status-concluido { background-color: #28a745; }
.observacoes-finalizacao {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-left: 4px solid #28a745;
  font-size: 0.9em;
  white-space: pre-wrap; /* Preserva os espaços e quebras de linha */
}
</style>
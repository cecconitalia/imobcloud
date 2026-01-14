<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="fechar">
    
    <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl overflow-hidden transform transition-all animate-fade-in-up">
      
      <div class="px-6 py-4 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
        <h2 class="text-lg font-bold text-gray-800">
          {{ isEditing ? 'Editar Nota' : 'Nova Nota' }}
        </h2>
        <button 
          class="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-full hover:bg-red-50" 
          @click="fechar"
        >
          <i class="fas fa-times text-lg"></i>
        </button>
      </div>

      <form @submit.prevent="salvarTarefa" class="p-6 space-y-5">
        
        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">
            Título <span class="text-red-500">*</span>
          </label>
          <input 
            type="text" 
            v-model="form.titulo" 
            placeholder="Ex: Ligar para cliente..." 
            required
            class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-gray-700 placeholder-gray-400 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm font-medium"
          >
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Descrição</label>
          <textarea 
            v-model="form.descricao" 
            rows="3" 
            placeholder="Detalhes da tarefa..."
            class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-gray-700 placeholder-gray-400 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm resize-none"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Vencimento</label>
            <input 
              type="date" 
              v-model="form.data_vencimento" 
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-gray-700 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm"
            >
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Prioridade</label>
            <select 
              v-model="form.prioridade" 
              class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-gray-700 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm appearance-none cursor-pointer"
            >
              <option value="BAIXA">🟢 Baixa</option>
              <option value="MEDIA">🔵 Média</option>
              <option value="ALTA">🔴 Alta</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-gray-500 uppercase tracking-wide mb-1.5">Status</label>
          <select 
            v-model="form.status" 
            class="w-full px-4 py-2.5 border rounded-xl text-gray-700 focus:ring-2 outline-none transition-all text-sm font-medium cursor-pointer"
            :class="form.status === 'concluida' 
              ? 'bg-green-50 border-green-200 text-green-700 focus:ring-green-500/20 focus:border-green-500' 
              : 'bg-gray-50 border-gray-200 focus:bg-white focus:ring-blue-500/20 focus:border-blue-500'"
          >
            <option value="pendente">📝 Pendente</option>
            <option value="concluida">✅ Concluída</option>
          </select>
        </div>

        <div v-if="form.status === 'concluida' || form.observacoes_finalizacao" class="animate-fade-in">
          <label class="block text-xs font-bold text-green-600 uppercase tracking-wide mb-1.5 flex items-center gap-1">
            <i class="fas fa-check-double"></i> Observação Final
          </label>
          <textarea 
            v-model="form.observacoes_finalizacao" 
            rows="2" 
            placeholder="Resultado da tarefa..."
            class="w-full px-4 py-2.5 bg-green-50 border border-green-200 rounded-xl text-green-800 placeholder-green-400/70 focus:bg-white focus:ring-2 focus:ring-green-500/20 focus:border-green-500 outline-none transition-all text-sm resize-none"
          ></textarea>
        </div>

      </form>

      <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
        <button 
          type="button" 
          class="px-5 py-2.5 rounded-xl text-sm font-medium text-gray-600 bg-white border border-gray-200 hover:bg-gray-100 hover:text-gray-800 transition-all active:scale-95" 
          @click="fechar"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          class="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-blue-600 shadow-md hover:bg-blue-700 hover:shadow-lg hover:-translate-y-0.5 transition-all active:scale-95 flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed" 
          @click="salvarTarefa" 
          :disabled="loading"
        >
          <i class="fas fa-save" v-if="!loading"></i>
          <i class="fas fa-circle-notch fa-spin" v-else></i>
          {{ isEditing ? 'Atualizar' : 'Salvar' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import api from '../services/api';

const props = defineProps({
  show: { type: Boolean, required: true },
  tarefa: { type: Object, default: null } 
});

const emit = defineEmits(['close', 'saved']);

const loading = ref(false);
const form = reactive({
  id: null as number | null,
  titulo: '',
  descricao: '',
  data_vencimento: '',
  prioridade: 'MEDIA',
  status: 'pendente',
  observacoes_finalizacao: ''
});

const isEditing = computed(() => !!form.id);

watch(() => props.tarefa, (novaTarefa) => {
  if (novaTarefa) {
    form.id = novaTarefa.id;
    form.titulo = novaTarefa.titulo;
    form.descricao = novaTarefa.descricao || '';
    form.data_vencimento = novaTarefa.data_vencimento ? novaTarefa.data_vencimento.split('T')[0] : '';
    form.prioridade = novaTarefa.prioridade || 'MEDIA';
    
    let statusRecebido = novaTarefa.status || 'pendente';
    if (statusRecebido === 'em_andamento') statusRecebido = 'pendente';
    
    form.status = statusRecebido;
    form.observacoes_finalizacao = novaTarefa.observacoes_finalizacao || '';
  } else {
    resetForm();
  }
}, { immediate: true });

const resetForm = () => {
  form.id = null;
  form.titulo = '';
  form.descricao = '';
  form.data_vencimento = '';
  form.prioridade = 'MEDIA';
  form.status = 'pendente';
  form.observacoes_finalizacao = '';
};

const fechar = () => {
  emit('close');
};

const salvarTarefa = async () => {
  if (!form.titulo) {
    alert('O título é obrigatório.');
    return;
  }

  loading.value = true;
  try {
    const payload: any = { ...form };
    
    if (!payload.data_vencimento) delete payload.data_vencimento;
    payload.concluida = payload.status === 'concluida';

    if (isEditing.value) {
      await api.patch(`/v1/tarefas/${form.id}/`, payload);
    } else {
      await api.post('/v1/tarefas/', payload);
    }

    emit('saved');
    fechar();
  } catch (error) {
    console.error('Erro ao salvar tarefa:', error);
    alert('Erro ao salvar tarefa.');
  } finally {
    loading.value = false;
  }
};
</script>
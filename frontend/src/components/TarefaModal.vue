<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-[9999] flex items-center justify-center bg-gray-900 bg-opacity-60 backdrop-blur-sm p-4 transition-all">
      
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg transform transition-all flex flex-col max-h-[90vh] border border-gray-100 animate-scale-in">
        
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-gray-50 rounded-t-xl">
          <div class="flex items-center gap-3">
            <div class="h-10 w-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shadow-sm">
              <i :class="tarefa?.id ? 'fas fa-edit' : 'fas fa-plus'"></i>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-800 leading-tight">
                {{ tarefa?.id ? 'Editar Tarefa' : 'Nova Tarefa' }}
              </h3>
              <p class="text-xs text-gray-500">Preencha os detalhes abaixo</p>
            </div>
          </div>
          <button @click="$emit('close')" class="text-gray-400 hover:text-red-500 transition-colors h-8 w-8 flex items-center justify-center rounded-full hover:bg-white hover:shadow-sm">
            <i class="fas fa-times text-lg"></i>
          </button>
        </div>

        <div class="p-6 space-y-6 overflow-y-auto custom-scrollbar bg-white">
          
          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1.5">Título da Tarefa <span class="text-red-500">*</span></label>
            <input 
              v-model="form.titulo" 
              type="text" 
              ref="tituloInput"
              :class="{'border-red-300 ring-red-100': errors.titulo, 'border-gray-300 focus:border-blue-500 focus:ring-blue-100': !errors.titulo}"
              class="w-full px-4 py-3 border rounded-lg focus:ring-4 outline-none transition-all text-gray-800 placeholder-gray-400 text-sm font-medium"
              placeholder="Ex: Reunião com cliente..."
              @input="errors.titulo = false"
            >
            <p v-if="errors.titulo" class="text-xs text-red-500 mt-1 font-medium">Este campo é obrigatório.</p>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-1.5">Descrição</label>
            <textarea 
              v-model="form.descricao" 
              rows="3" 
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all resize-none text-gray-700 placeholder-gray-400 text-sm"
              placeholder="Detalhes adicionais..."
            ></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Data Vencimento</label>
              <input 
                v-model="form.data_vencimento" 
                type="datetime-local" 
                class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-4 focus:ring-blue-100 focus:border-blue-500 outline-none text-sm text-gray-700 font-medium"
              >
            </div>
            
            <div>
              <label class="block text-sm font-bold text-gray-700 mb-1.5">Prioridade</label>
              <div class="flex gap-2 h-[42px]">
                <button 
                  v-for="prio in prioridadeOptions"
                  :key="prio.value"
                  type="button"
                  @click="form.prioridade = prio.value"
                  class="flex-1 rounded-lg text-xs font-bold border transition-all flex items-center justify-center gap-1.5"
                  :class="form.prioridade === prio.value ? prio.activeClass : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50 hover:border-gray-300'"
                >
                  <i :class="prio.icon"></i> {{ prio.label }}
                </button>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-bold text-gray-700 mb-2">Status</label>
            <div class="grid grid-cols-3 gap-3">
              <button 
                v-for="st in statusOptions" 
                :key="st.value"
                type="button"
                @click="form.status = st.value"
                class="py-3 px-2 text-xs font-bold rounded-lg border transition-all flex flex-col items-center justify-center gap-1 relative overflow-hidden"
                :class="form.status === st.value ? st.activeClass : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50 hover:border-gray-300'"
              >
                <div v-if="form.status === st.value" class="absolute top-0 right-0 w-3 h-3 bg-current opacity-20 rounded-bl-lg"></div>
                <i :class="st.icon" class="text-sm mb-1"></i> 
                <span>{{ st.label }}</span>
              </button>
            </div>
          </div>

          <div v-if="tarefa?.cliente_nome" class="bg-blue-50 border border-blue-100 rounded-lg p-3 flex items-center gap-3">
             <div class="bg-blue-100 text-blue-600 rounded-full h-8 w-8 flex items-center justify-center flex-shrink-0 text-sm">
               <i class="fas fa-user"></i>
             </div>
             <div class="overflow-hidden">
               <p class="text-xs text-blue-600 font-bold uppercase tracking-wide">Vinculado ao Cliente</p>
               <p class="text-sm font-medium text-gray-800 truncate">
                 {{ tarefa.cliente_nome }}
               </p>
             </div>
          </div>

        </div>

        <div class="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3 rounded-b-xl">
          <button 
            @click="$emit('close')" 
            class="px-5 py-2.5 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 font-medium text-sm transition-all shadow-sm"
          >
            Cancelar
          </button>
          <button 
            @click="salvar" 
            :disabled="loading"
            class="px-6 py-2.5 text-white bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-sm shadow-md hover:shadow-lg flex items-center gap-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed transform active:scale-95"
          >
            <i v-if="loading" class="fas fa-circle-notch fa-spin"></i>
            <span v-else><i class="fas fa-save mr-1"></i></span>
            {{ loading ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, reactive, nextTick } from 'vue';
import api from '../services/api';

// Definição de Tipos
interface Tarefa {
  id?: number;
  titulo: string;
  descricao?: string;
  data_vencimento?: string;
  prioridade?: 'BAIXA' | 'MEDIA' | 'ALTA';
  status?: 'pendente' | 'em_andamento' | 'concluida';
  oportunidade?: number | null;
  concluida?: boolean;
  cliente_nome?: string;
}

const props = defineProps<{
  show: boolean;
  tarefa?: Tarefa | null;
}>();

const emit = defineEmits(['close', 'saved']);

const loading = ref(false);
const tituloInput = ref<HTMLInputElement | null>(null);
const errors = reactive({
  titulo: false
});

const form = ref<Tarefa>({
  titulo: '',
  descricao: '',
  data_vencimento: '',
  prioridade: 'MEDIA',
  status: 'pendente',
  oportunidade: null
});

// Helper Nativo para data (YYYY-MM-DDTHH:MM)
const formatarDataInput = (isoDate?: string) => {
    if (!isoDate) return '';
    try {
        const date = new Date(isoDate);
        if (isNaN(date.getTime())) return '';
        // Ajuste fuso horário local
        const offset = date.getTimezoneOffset() * 60000;
        return (new Date(date.getTime() - offset)).toISOString().slice(0, 16);
    } catch {
        return '';
    }
};

const statusOptions = [
  { value: 'pendente', label: 'Pendente', icon: 'far fa-clock', activeClass: 'bg-orange-50 border-orange-500 text-orange-700 ring-1 ring-orange-500' },
  { value: 'em_andamento', label: 'Em Andamento', icon: 'fas fa-spinner fa-spin-pulse', activeClass: 'bg-blue-50 border-blue-500 text-blue-700 ring-1 ring-blue-500' },
  { value: 'concluida', label: 'Concluída', icon: 'fas fa-check-circle', activeClass: 'bg-green-50 border-green-500 text-green-700 ring-1 ring-green-500' }
];

const prioridadeOptions = [
  { value: 'BAIXA', label: 'Baixa', icon: 'fas fa-arrow-down', activeClass: 'bg-green-100 border-green-300 text-green-800' },
  { value: 'MEDIA', label: 'Média', icon: 'fas fa-minus', activeClass: 'bg-yellow-100 border-yellow-300 text-yellow-800' },
  { value: 'ALTA', label: 'Alta', icon: 'fas fa-exclamation', activeClass: 'bg-red-100 border-red-300 text-red-800' },
];

watch(() => props.show, (newVal) => {
    if (newVal) {
        errors.titulo = false;
        // Popula formulário
        if (props.tarefa) {
            form.value = {
                titulo: props.tarefa.titulo || '',
                descricao: props.tarefa.descricao || '',
                data_vencimento: formatarDataInput(props.tarefa.data_vencimento),
                prioridade: props.tarefa.prioridade || 'MEDIA',
                status: props.tarefa.status || (props.tarefa.concluida ? 'concluida' : 'pendente'),
                oportunidade: props.tarefa.oportunidade
            };
        } else {
            // Nova tarefa
            const now = new Date();
            form.value = {
                titulo: '',
                descricao: '',
                data_vencimento: formatarDataInput(now.toISOString()),
                prioridade: 'MEDIA',
                status: 'pendente',
                oportunidade: null
            };
        }
        
        // Foco automático no título
        nextTick(() => {
            if (tituloInput.value) tituloInput.value.focus();
        });
    }
}, { immediate: true });

const salvar = async () => {
  if (!form.value.titulo || form.value.titulo.trim() === '') {
    errors.titulo = true;
    if(tituloInput.value) tituloInput.value.focus();
    return;
  }

  loading.value = true;
  try {
    const payload = {
        ...form.value,
        concluida: form.value.status === 'concluida'
    };

    // CORREÇÃO: Usando /v1/ explicitamente
    if (props.tarefa?.id) {
      await api.patch(`/v1/tarefas/${props.tarefa.id}/`, payload);
    } else {
      await api.post('/v1/tarefas/', payload);
    }
    
    emit('saved');
    emit('close');
  } catch (error) {
    console.error('Erro ao salvar:', error);
    alert('Erro ao salvar. Verifique se o servidor está rodando.');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f9fafb; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #d1d5db; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* Animação de entrada */
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
.animate-scale-in {
  animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
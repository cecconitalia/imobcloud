<template>
  <div class="flex flex-col h-screen bg-gray-50 font-sans overflow-hidden text-gray-700">
    
    <header class="flex-none bg-white border-b border-gray-200 px-6 py-5 shadow-sm z-20">
      <div class="max-w-7xl mx-auto w-full">
        
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-6">
          <div>
            <nav class="flex items-center gap-2 text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">
              <span>Comercial</span> 
              <i class="fas fa-chevron-right text-[10px]"></i> 
              <span class="text-blue-600">Mural</span>
            </nav>
            <h1 class="text-2xl font-bold text-gray-800 tracking-tight">Minhas Anotações</h1>
            <p class="text-sm text-gray-500 mt-1 flex items-center gap-2">
              <i class="fas" :class="exibirConcluidas ? 'fa-history text-purple-500' : 'fa-sort-amount-down text-blue-500'"></i>
              {{ exibirConcluidas ? 'Visualizando histórico de tarefas finalizadas' : 'Organizado por data de vencimento' }}
            </p>
          </div>

          <div class="flex items-center gap-3">
            <button 
              class="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border active:scale-95"
              :class="exibirConcluidas 
                ? 'bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100' 
                : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300'"
              @click="exibirConcluidas = !exibirConcluidas"
            >
              <i class="fas" :class="exibirConcluidas ? 'fa-arrow-left' : 'fa-check-double'"></i>
              {{ exibirConcluidas ? 'Voltar para Pendentes' : 'Ver Concluídas' }}
            </button>

            <button 
              class="w-9 h-9 rounded-full flex items-center justify-center border border-gray-200 text-gray-500 hover:text-blue-600 hover:border-blue-200 hover:bg-blue-50 transition-all active:scale-95 bg-white" 
              @click="carregarTarefas" 
              title="Recarregar"
            >
              <i class="fas fa-sync-alt" :class="{ 'animate-spin': isLoading }"></i>
            </button>
            
            <button 
              v-if="!exibirConcluidas"
              class="flex items-center gap-2 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full text-sm font-semibold shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 active:scale-95" 
              @click="abrirModalNovaTarefa"
            >
              <i class="fas fa-plus"></i> Nova Nota
            </button>
          </div>
        </div>

        <div class="relative max-w-md">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i class="fas fa-search text-gray-400"></i>
          </div>
          <input 
            type="text" 
            v-model="termoBusca" 
            class="block w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-xl leading-5 bg-gray-50 text-gray-900 placeholder-gray-400 focus:outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors text-sm"
            placeholder="Filtrar por título, descrição ou cliente..." 
          >
        </div>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto p-6 scroll-smooth custom-scrollbar bg-[#f0f2f5]">
      <div class="max-w-7xl mx-auto h-full">
        
        <div v-if="isLoading" class="flex flex-col items-center justify-center h-64 text-gray-400 animate-pulse">
          <i class="fas fa-circle-notch fa-spin text-3xl mb-3"></i>
          <span class="text-sm font-medium">Carregando suas anotações...</span>
        </div>

        <div v-else-if="tarefasFiltradas.length === 0" class="flex flex-col items-center justify-center h-[70vh] text-center">
          <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6 text-gray-300 text-4xl">
            <i class="far" :class="exibirConcluidas ? 'fa-folder-open' : 'fa-sticky-note'"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">
            {{ exibirConcluidas ? 'Histórico limpo' : 'Tudo em dia por aqui!' }}
          </h3>
          <p class="text-gray-500 max-w-xs mx-auto mb-8 leading-relaxed">
            {{ exibirConcluidas 
              ? 'Nenhuma tarefa finalizada foi encontrada com os filtros atuais.' 
              : 'Não há pendências no momento. Aproveite para descansar ou planejar o futuro.' }}
          </p>
          <button 
            v-if="!exibirConcluidas" 
            class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-lg hover:shadow-blue-500/30 transition-all"
            @click="abrirModalNovaTarefa"
          >
            Criar Primeira Tarefa
          </button>
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12 items-start">
          <div 
            v-for="tarefa in tarefasFiltradas" 
            :key="tarefa.id"
            @click="editarTarefa(tarefa)"
            class="group relative bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col min-h-[180px] border-t-4"
            :class="[
              getPriorityBorderClass(tarefa.prioridade),
              { 'opacity-60 bg-gray-50 hover:opacity-100 grayscale-[0.5] hover:grayscale-0': tarefa.status === 'concluida' },
              { 'bg-red-50 border-red-200': isAtrasada(tarefa.data_vencimento) && tarefa.status !== 'concluida' }
            ]"
          >
            <div class="flex justify-between items-center mb-4">
              <span 
                class="px-2.5 py-1 rounded-md text-[11px] font-bold uppercase tracking-wide flex items-center gap-1.5 border"
                :class="getDataBadgeClass(tarefa.data_vencimento, tarefa.status)"
              >
                <i class="far fa-clock"></i> {{ formatarData(tarefa.data_vencimento) }}
              </span>
              
              <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  @click.stop="alternarConclusaoRapida(tarefa)"
                  class="w-7 h-7 flex items-center justify-center rounded-full border transition-all duration-200 shadow-sm hover:scale-110 focus:outline-none"
                  :class="tarefa.status === 'concluida' 
                    ? 'border-gray-300 text-gray-400 hover:text-blue-600 hover:border-blue-400 bg-white' 
                    : 'border-gray-200 text-gray-300 hover:text-green-600 hover:border-green-400 hover:bg-green-50'"
                  :title="tarefa.status === 'concluida' ? 'Reabrir' : 'Concluir'"
                >
                  <i class="fas" :class="tarefa.status === 'concluida' ? 'fa-undo text-xs' : 'fa-check'"></i>
                </button>
              </div>
            </div>

            <div class="flex-1 mb-4">
              <h4 
                class="text-base font-bold text-gray-800 mb-2 leading-snug group-hover:text-blue-700 transition-colors line-clamp-2"
                :class="{'line-through text-gray-400 decoration-2 decoration-gray-300': tarefa.status === 'concluida'}"
              >
                {{ tarefa.titulo }}
              </h4>
              <p class="text-sm text-gray-600 line-clamp-4 leading-relaxed whitespace-pre-line">
                {{ tarefa.descricao || 'Sem descrição.' }}
              </p>
              
              <div v-if="tarefa.observacoes_finalizacao && tarefa.status === 'concluida'" class="mt-3 p-2 bg-green-50 border border-green-100 rounded-lg">
                <p class="text-xs text-green-800 italic flex items-start gap-1.5">
                  <i class="fas fa-pen-fancy text-[10px] mt-0.5"></i> 
                  <span>{{ tarefa.observacoes_finalizacao }}</span>
                </p>
              </div>
            </div>

            <div class="pt-3 border-t border-gray-100 border-dashed flex items-center justify-between mt-auto">
              <div class="flex items-center gap-1.5 text-gray-500 max-w-[75%]" v-if="tarefa.cliente_nome">
                <div class="bg-gray-50 border border-gray-100 px-2 py-0.5 rounded text-[10px] font-medium truncate flex items-center gap-1">
                  <i class="fas fa-user-circle text-gray-400"></i> {{ tarefa.cliente_nome }}
                </div>
              </div>
              <div v-else></div> <div 
                class="w-7 h-7 rounded-full bg-blue-50 border border-blue-100 text-blue-600 text-[10px] font-bold flex items-center justify-center shadow-sm"
                :title="tarefa.responsavel_nome"
              >
                {{ pegarIniciais(tarefa.responsavel_nome) }}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <TarefaModal 
      v-if="mostrarModal" 
      :show="mostrarModal"
      :tarefa="tarefaSelecionada"
      @close="fecharModal"
      @saved="carregarTarefas"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import api from '../services/api';
import TarefaModal from '../components/TarefaModal.vue';

interface Tarefa {
  id: number;
  titulo: string;
  descricao?: string;
  status: string; 
  data_vencimento?: string;
  prioridade?: string;
  cliente_nome?: string;
  responsavel_nome?: string;
  observacoes_finalizacao?: string;
}

// State
const rawTarefas = ref<Tarefa[]>([]);
const isLoading = ref(false);
const mostrarModal = ref(false);
const tarefaSelecionada = ref<Tarefa | null>(null);
const termoBusca = ref('');
const exibirConcluidas = ref(false);

// --- Computed ---
const tarefasFiltradas = computed(() => {
  let lista = rawTarefas.value;

  if (exibirConcluidas.value) {
    lista = lista.filter(t => t.status === 'concluida');
  } else {
    lista = lista.filter(t => t.status !== 'concluida');
  }

  if (termoBusca.value) {
    const termo = termoBusca.value.toLowerCase();
    lista = lista.filter(t => 
      t.titulo.toLowerCase().includes(termo) ||
      (t.descricao && t.descricao.toLowerCase().includes(termo)) ||
      (t.cliente_nome && t.cliente_nome.toLowerCase().includes(termo))
    );
  }

  return lista.sort((a, b) => {
    if (exibirConcluidas.value) return b.id - a.id; 
    const dataA = a.data_vencimento ? new Date(a.data_vencimento).getTime() : Infinity;
    const dataB = b.data_vencimento ? new Date(b.data_vencimento).getTime() : Infinity;
    return dataA - dataB;
  });
});

// --- Methods ---
const carregarTarefas = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('/v1/tarefas/kanban/');
    rawTarefas.value = Array.isArray(response.data) ? response.data : (response.data.results || []);
  } catch (error) {
    console.error('Erro ao carregar:', error);
  } finally {
    isLoading.value = false;
  }
};

const alternarConclusaoRapida = async (tarefa: Tarefa) => {
  const estaConcluida = tarefa.status === 'concluida';
  let novoStatus = '';
  let observacao = '';

  if (estaConcluida) {
    if (!confirm('Reabrir esta tarefa para pendente?')) return;
    novoStatus = 'pendente';
  } else {
    const input = window.prompt('Observação ao finalizar? (Opcional)');
    if (input === null) return;
    observacao = input.trim();
    novoStatus = 'concluida';
  }

  const bkp = { ...tarefa };
  tarefa.status = novoStatus;
  tarefa.observacoes_finalizacao = observacao;

  try {
    await api.patch(`/v1/tarefas/${tarefa.id}/`, {
      status: novoStatus,
      observacoes_finalizacao: observacao,
      concluida: novoStatus === 'concluida'
    });
  } catch (error) {
    console.error("Erro API:", error);
    Object.assign(tarefa, bkp);
    alert("Erro ao sincronizar. Tente novamente.");
  }
};

const isAtrasada = (data?: string) => {
  if (!data) return false;
  const hoje = new Date();
  hoje.setHours(0,0,0,0);
  const venc = new Date(data.split('T')[0] + 'T00:00:00');
  return venc < hoje;
};

// --- Helpers de Estilo ---
const getPriorityBorderClass = (prioridade?: string) => {
  const p = prioridade?.toUpperCase() || 'MEDIA';
  if (p === 'ALTA') return 'border-t-red-500';
  if (p === 'BAIXA') return 'border-t-green-500';
  return 'border-t-blue-500'; // Média
};

const getDataBadgeClass = (data?: string, status?: string) => {
  if (!data || status === 'concluida') return 'bg-gray-100 text-gray-500 border-gray-200';
  if (isAtrasada(data)) return 'bg-red-100 text-red-700 border-red-200';
  
  const hoje = new Date();
  hoje.setHours(0,0,0,0);
  const venc = new Date(data.split('T')[0] + 'T00:00:00');
  
  if (venc.getTime() === hoje.getTime()) return 'bg-orange-100 text-orange-700 border-orange-200';
  return 'bg-blue-50 text-blue-600 border-blue-100';
};

const formatarData = (data?: string) => {
  if (!data) return 'S/ Data';
  const d = new Date(data.split('T')[0] + 'T00:00:00');
  const hoje = new Date();
  hoje.setHours(0,0,0,0);
  const amanha = new Date(hoje);
  amanha.setDate(amanha.getDate() + 1);

  if (d.getTime() === hoje.getTime()) return 'Hoje';
  if (d.getTime() === amanha.getTime()) return 'Amanhã';
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
};

const pegarIniciais = (nome?: string) => {
  if (!nome) return '?';
  const partes = nome.trim().split(' ');
  if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
  return (partes[0][0] + partes[1][0]).toUpperCase();
};

// Modal Handlers
const abrirModalNovaTarefa = () => { tarefaSelecionada.value = null; mostrarModal.value = true; };
const editarTarefa = (tarefa: Tarefa) => { tarefaSelecionada.value = { ...tarefa }; mostrarModal.value = true; };
const fecharModal = () => { mostrarModal.value = false; tarefaSelecionada.value = null; };

onMounted(() => carregarTarefas());
</script>

<style scoped>
/* Estilização minimalista da barra de rolagem */
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
  border: 3px solid transparent;
  background-clip: content-box;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}
</style>
<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <span>Comercial</span> 
              <i class="fas fa-chevron-right separator"></i> 
              <span class="active">Quadro de Tarefas</span>
           </nav>
           <h1>Gerenciar Tarefas</h1>
        </div>
        
        <div class="actions-area">
            <button class="btn-icon-thin" @click="carregarTarefas" title="Recarregar">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
            </button>
            <button class="btn-primary-thin" @click="abrirModalNovaTarefa">
              <i class="fas fa-plus"></i> Nova Tarefa
            </button>
        </div>
      </div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card blue" :class="{ active: filters.status === '' }" @click="setQuickFilter('')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.total }}</span>
          <span class="kpi-label">Total</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-tasks"></i></div>
      </div>
      
      <div class="kpi-card orange" :class="{ active: filters.status === 'pendente' }" @click="setQuickFilter('pendente')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.pendentes }}</span>
          <span class="kpi-label">Pendentes</span>
        </div>
        <div class="kpi-icon"><i class="far fa-clock"></i></div>
      </div>
      
      <div class="kpi-card purple" :class="{ active: filters.status === 'em_andamento' }" @click="setQuickFilter('em_andamento')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.emAndamento }}</span>
          <span class="kpi-label">Em Andamento</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-spinner"></i></div>
      </div>
      
      <div class="kpi-card green" :class="{ active: filters.status === 'concluida' }" @click="setQuickFilter('concluida')">
        <div class="kpi-content">
          <span class="kpi-value">{{ kpis.concluidas }}</span>
          <span class="kpi-label">Concluídas</span>
        </div>
        <div class="kpi-icon"><i class="fas fa-check-circle"></i></div>
      </div>
    </div>

    <div class="toolbar-row">
        <div class="filter-group search-group">
          <label>Buscar</label>
          <div class="input-with-icon">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="Título, cliente ou responsável..." 
              class="form-control"
              @input="distribuirTarefas"
            >
          </div>
        </div>
        <div class="filter-group small-btn">
            <label>&nbsp;</label>
            <button @click="clearFilters" class="btn-clear" title="Limpar Filtros">
                <i class="fas fa-eraser"></i>
            </button>
        </div>
    </div>

    <div class="kanban-wrapper">
      <div class="flex flex-col md:flex-row gap-6 h-full overflow-x-auto pb-4">
        
        <div class="kanban-column" v-if="shouldShowColumn('pendente')">
          <div class="column-header bg-orange-50 border-orange-200">
            <h3 class="text-orange-800 font-bold">Pendente</h3>
            <span class="counter bg-orange-200 text-orange-800">{{ colunas.pendente.length }}</span>
          </div>
          <div class="column-body custom-scrollbar">
            <draggable 
              v-model="colunas.pendente" 
              group="tarefas" 
              item-key="id"
              @change="(e) => aoMoverCard(e, 'pendente')"
              class="drag-area"
              ghost-class="ghost-card"
            >
              <template #item="{ element }">
                <div @click="editarTarefa(element)" class="task-card border-l-4 border-orange-400 bg-white hover:bg-orange-50">
                  <div class="card-meta">
                    <span>{{ formatarData(element.data_vencimento) }}</span>
                    <span v-if="element.prioridade === 'ALTA'" class="text-red-600 font-bold text-xs flex items-center gap-1">
                        <i class="fas fa-exclamation-circle"></i> Alta
                    </span>
                  </div>
                  <p class="card-title">{{ element.titulo }}</p>
                  <div class="card-footer">
                    <span class="client-badge" v-if="element.cliente_nome">
                      {{ element.cliente_nome }}
                    </span>
                    <span v-else class="client-badge opacity-50">Geral</span>
                    <div class="avatar-mini bg-gray-400 text-white" :title="element.responsavel_nome">
                      {{ pegarIniciais(element.responsavel_nome) }}
                    </div>
                  </div>
                </div>
              </template>
            </draggable>
          </div>
        </div>

        <div class="kanban-column" v-if="shouldShowColumn('em_andamento')">
          <div class="column-header bg-purple-50 border-purple-200">
            <h3 class="text-purple-800 font-bold">Em Andamento</h3>
            <span class="counter bg-purple-200 text-purple-800">{{ colunas.em_andamento.length }}</span>
          </div>
          <div class="column-body custom-scrollbar">
            <draggable 
              v-model="colunas.em_andamento" 
              group="tarefas" 
              item-key="id"
              @change="(e) => aoMoverCard(e, 'em_andamento')"
              class="drag-area"
              ghost-class="ghost-card"
            >
              <template #item="{ element }">
                <div @click="editarTarefa(element)" class="task-card border-l-4 border-purple-400 bg-white hover:bg-purple-50">
                  <div class="card-meta">
                    <span>{{ formatarData(element.data_vencimento) }}</span>
                  </div>
                  <p class="card-title">{{ element.titulo }}</p>
                  <div class="card-footer">
                    <span class="client-badge" v-if="element.cliente_nome">
                      {{ element.cliente_nome }}
                    </span>
                    <span v-else class="client-badge opacity-50">Geral</span>
                    <div class="avatar-mini bg-purple-500 text-white" :title="element.responsavel_nome">
                      {{ pegarIniciais(element.responsavel_nome) }}
                    </div>
                  </div>
                </div>
              </template>
            </draggable>
          </div>
        </div>

        <div class="kanban-column" v-if="shouldShowColumn('concluida')">
          <div class="column-header bg-green-50 border-green-200">
            <h3 class="text-green-800 font-bold">Concluída</h3>
            <span class="counter bg-green-200 text-green-800">{{ colunas.concluida.length }}</span>
          </div>
          <div class="column-body custom-scrollbar">
            <draggable 
              v-model="colunas.concluida" 
              group="tarefas" 
              item-key="id"
              @change="(e) => aoMoverCard(e, 'concluida')"
              class="drag-area"
              ghost-class="ghost-card"
            >
              <template #item="{ element }">
                <div @click="editarTarefa(element)" class="task-card border-l-4 border-green-400 bg-white hover:bg-green-50 opacity-80 hover:opacity-100">
                  <div class="card-meta text-green-600">
                    <span class="line-through">{{ formatarData(element.data_vencimento) }}</span>
                    <i class="fas fa-check"></i>
                  </div>
                  <p class="card-title line-through text-gray-500">{{ element.titulo }}</p>
                  <div class="card-footer">
                    <span class="client-badge opacity-70" v-if="element.cliente_nome">
                      {{ element.cliente_nome }}
                    </span>
                    <span v-else class="client-badge opacity-50">Geral</span>
                  </div>
                </div>
              </template>
            </draggable>
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
import { ref, onMounted, reactive, computed } from 'vue';
import draggable from 'vuedraggable';
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
}

const rawTarefas = ref<Tarefa[]>([]);
const colunas = reactive({
  pendente: [] as Tarefa[],
  em_andamento: [] as Tarefa[],
  concluida: [] as Tarefa[]
});
const isLoading = ref(false);
const mostrarModal = ref(false);
const tarefaSelecionada = ref<Tarefa | null>(null);
const filters = ref({ search: '', status: '' });

const kpis = computed(() => {
  const total = rawTarefas.value.length;
  let pendentes = 0;
  let emAndamento = 0;
  let concluidas = 0;

  rawTarefas.value.forEach(t => {
    const s = t.status?.toLowerCase() || 'pendente';
    if (s === 'concluida' || s === 'concluída') concluidas++;
    else if (s === 'em_andamento' || s === 'em andamento') emAndamento++;
    else pendentes++;
  });

  return { total, pendentes, emAndamento, concluidas };
});

const carregarTarefas = async () => {
  isLoading.value = true;
  try {
    // CORREÇÃO: /v1/
    const response = await api.get('/v1/tarefas/kanban/');
    rawTarefas.value = response.data.results || response.data;
    distribuirTarefas();
  } catch (error) {
    console.error('Erro ao carregar tarefas:', error);
  } finally {
    isLoading.value = false;
  }
};

const distribuirTarefas = () => {
  colunas.pendente = [];
  colunas.em_andamento = [];
  colunas.concluida = [];

  const termo = filters.value.search.toLowerCase();

  const tarefasFiltradas = rawTarefas.value.filter(t => {
    const matchTexto = 
      !termo || 
      t.titulo.toLowerCase().includes(termo) || 
      (t.cliente_nome && t.cliente_nome.toLowerCase().includes(termo)) ||
      (t.responsavel_nome && t.responsavel_nome.toLowerCase().includes(termo));
    return matchTexto;
  });

  tarefasFiltradas.forEach(tarefa => {
    const status = tarefa.status?.toLowerCase() || 'pendente';
    if (status === 'concluida' || status === 'concluída') {
      colunas.concluida.push(tarefa);
    } else if (status === 'em_andamento' || status === 'em andamento') {
      colunas.em_andamento.push(tarefa);
    } else {
      colunas.pendente.push(tarefa);
    }
  });
};

const setQuickFilter = (status: string) => {
  filters.value.status = filters.value.status === status ? '' : status;
};

const shouldShowColumn = (coluna: string) => {
  if (!filters.value.status) return true;
  return filters.value.status === coluna;
};

const clearFilters = () => {
  filters.value.search = '';
  filters.value.status = '';
  distribuirTarefas();
};

const aoMoverCard = async (evt: any, novoStatus: string) => {
  if (evt.added) {
    const tarefa = evt.added.element;
    const statusApi = converterStatusParaApi(novoStatus);
    try {
      // CORREÇÃO: /v1/
      await api.patch(`/v1/tarefas/${tarefa.id}/`, { status: statusApi });
      tarefa.status = statusApi;
      const index = rawTarefas.value.findIndex(t => t.id === tarefa.id);
      if (index !== -1) rawTarefas.value[index].status = statusApi;
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      alert('Erro ao mover. Revertendo...');
      carregarTarefas();
    }
  }
};

const converterStatusParaApi = (statusColuna: string) => {
  switch(statusColuna) {
    case 'pendente': return 'pendente';
    case 'em_andamento': return 'em_andamento';
    case 'concluida': return 'concluida';
    default: return 'pendente';
  }
};

const abrirModalNovaTarefa = () => {
  tarefaSelecionada.value = null;
  mostrarModal.value = true;
};

const editarTarefa = (tarefa: Tarefa) => {
  // Clona o objeto para evitar reatividade indesejada
  tarefaSelecionada.value = { ...tarefa };
  mostrarModal.value = true;
};

const fecharModal = () => {
  mostrarModal.value = false;
  tarefaSelecionada.value = null;
};

const formatarData = (data?: string) => {
  if (!data) return '';
  const d = new Date(data);
  return isNaN(d.getTime()) ? data : d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
};

const pegarIniciais = (nome?: string) => {
  if (!nome) return '?';
  const partes = nome.split(' ');
  if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase();
  return (partes[0][0] + partes[1][0]).toUpperCase();
};

onMounted(() => {
  carregarTarefas();
});
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
}

/* HEADER */
.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }
.header-main { display: flex; justify-content: space-between; align-items: flex-end; }
.actions-area { display: flex; gap: 0.75rem; }

/* Botões */
.btn-primary-thin {
  background: #2563eb; color: white; border: none; padding: 0.5rem 1.2rem;
  border-radius: 6px; font-weight: 400; font-size: 0.85rem; cursor: pointer;
  display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.15);
}
.btn-primary-thin:hover { background: #1d4ed8; transform: translateY(-1px); }

.btn-icon-thin {
  background: white; border: 1px solid #e2e8f0; color: #64748b; width: 34px; height: 34px;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; font-size: 0.8rem;
}
.btn-icon-thin:hover { border-color: #cbd5e1; color: #2563eb; background: #f8fafc; }

/* KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 2rem; }
.kpi-card {
  background: white; border-radius: 8px; padding: 1.25rem 1.5rem; border: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02); cursor: pointer; transition: all 0.2s;
  position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.kpi-card.active { border: 1px solid; }

.kpi-content { display: flex; flex-direction: column; }
.kpi-value { font-size: 1.6rem; font-weight: 300; line-height: 1.1; color: #111; }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; color: #9ca3af; margin-top: 4px; letter-spacing: 0.05em; }
.kpi-icon { font-size: 1.8rem; opacity: 0.1; position: absolute; right: 1.5rem; bottom: 1rem; }

.kpi-card.blue.active { background-color: #f8fbff; border-color: #3b82f6; }
.kpi-card.blue .kpi-value { color: #2563eb; }
.kpi-card.orange.active { background-color: #fffdf5; border-color: #f59e0b; }
.kpi-card.orange .kpi-value { color: #d97706; }
.kpi-card.purple.active { background-color: #f3e8ff; border-color: #7e22ce; }
.kpi-card.purple .kpi-value { color: #7e22ce; }
.kpi-card.green.active { background-color: #f3fdf8; border-color: #10b981; }
.kpi-card.green .kpi-value { color: #059669; }

/* Filtros */
.toolbar-row {
  background-color: #ffffff; border-radius: 8px; border: 1px solid #e5e7eb; padding: 1rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02); display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end; margin-bottom: 1.5rem;
}
.filter-group { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; min-width: 160px; }
.search-group { flex: 2; min-width: 260px; }
.small-btn { flex: 0 0 auto; min-width: auto; }
.filter-group label { font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
.input-with-icon { position: relative; width: 100%; }
.input-with-icon i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.form-control {
  width: 100%; padding: 0.5rem 0.8rem 0.5rem 2.2rem; font-size: 0.85rem;
  border: 1px solid #cbd5e1; border-radius: 6px; background-color: #fff; color: #334155;
  outline: none; height: 38px; box-sizing: border-box; transition: all 0.2s;
}
.form-control:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }
.btn-clear {
    width: 38px; height: 38px; border: 1px solid #cbd5e1; background: #f8fafc;
    border-radius: 6px; color: #64748b; cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-clear:hover { background: #fee2e2; color: #ef4444; border-color: #fca5a5; }

/* Kanban Layout */
.kanban-wrapper {
  flex: 1; 
  height: calc(100vh - 350px);
  min-height: 400px;
}

.kanban-column {
  flex: 1; min-width: 300px; max-width: 400px;
  background-color: #f8fafc; border-radius: 8px;
  border: 1px solid #e2e8f0;
  display: flex; flex-direction: column;
  height: 100%;
}

.column-header {
  padding: 1rem; border-bottom: 1px solid;
  border-top-left-radius: 8px; border-top-right-radius: 8px;
  display: flex; justify-content: space-between; align-items: center;
}
.column-header h3 { font-size: 0.9rem; font-weight: 700; margin: 0; }
.column-header .counter {
  padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;
}

.column-body { flex: 1; padding: 1rem; overflow-y: auto; }
.drag-area { min-height: 100px; display: flex; flex-direction: column; gap: 0.75rem; }

/* Cards */
.task-card {
  background: white; padding: 1rem; border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05); cursor: pointer;
  transition: all 0.2s ease; border: 1px solid #e2e8f0;
  border-left-width: 4px;
}
.task-card:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.05); }

.card-meta { display: flex; justify-content: space-between; font-size: 0.7rem; color: #64748b; margin-bottom: 0.5rem; }
.card-title { font-size: 0.9rem; font-weight: 600; color: #334155; margin-bottom: 0.75rem; line-height: 1.4; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }

.client-badge {
  font-size: 0.7rem; background: #f1f5f9; color: #475569; padding: 2px 6px; border-radius: 4px;
  max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.avatar-mini {
  width: 24px; height: 24px; border-radius: 50%; 
  display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: 600;
}

.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }
.ghost-card { opacity: 0.5; background: #e2e8f0; border: 2px dashed #94a3b8; }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .header-main { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .actions-area { width: 100%; justify-content: flex-start; }
  .toolbar-row { flex-direction: column; align-items: stretch; }
  .kanban-wrapper { height: auto; overflow-x: auto; }
}
</style>
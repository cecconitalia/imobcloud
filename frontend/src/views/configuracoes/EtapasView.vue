<template>
  <div class="etapas-container">
    <header class="view-header">
      <h2>Configuração do Funil de Vendas</h2>
      <p>Arraste as etapas para reordenar, edite os nomes ou adicione novas fases ao seu processo comercial.</p>
    </header>
    
    <div class="nova-etapa-form">
      <input 
        v-model="novaEtapaNome" 
        placeholder="Nome da nova etapa"
        @keyup.enter="adicionarEtapa"
        class="form-control"
      />
      <button @click="adicionarEtapa" :disabled="!novaEtapaNome" class="btn btn-primary">
        Adicionar Etapa
      </button>
    </div>

    <div v-if="loading" class="loading-indicator">
      <p>Carregando etapas...</p>
    </div>

    <draggable 
      v-else
      v-model="etapas" 
      tag="ul"
      item-key="id" 
      class="etapas-list"
      @end="salvarOrdenacao"
      handle=".drag-handle"
    >
      <template #item="{ element: etapa }">
        <li class="etapa-item">
          <span class="drag-handle" title="Arraste para reordenar">⠿</span>
          <input v-model="etapa.nome" class="etapa-nome-input form-control" @blur="salvarNomeEtapa(etapa)" />
          
          <div class="etapa-flags">
            <label class="form-check-label" title="Marque a etapa que representa um negócio ganho.">
              <input class="form-check-input" type="checkbox" v-model="etapa.e_de_sucesso" @change="salvarFlag(etapa, 'sucesso')"> Ganho
            </label>
            <label class="form-check-label" title="Marque a etapa que representa um negócio perdido.">
              <input class="form-check-input" type="checkbox" v-model="etapa.e_de_fracasso" @change="salvarFlag(etapa, 'fracasso')"> Perdido
            </label>
          </div>
          
          <button @click="removerEtapa(etapa)" class="remover-btn" title="Remover etapa">×</button>
        </li>
      </template>
    </draggable>
    <div v-if="!loading && etapas.length === 0" class="empty-state">
        <p>Nenhuma etapa encontrada. Comece adicionando a primeira etapa do seu funil!</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import draggable from 'vuedraggable'; // Lembre-se de instalar: yarn add vuedraggable
import apiClient from '@/services/api';

interface Etapa {
  id: number;
  nome: string;
  ordem: number;
  e_de_sucesso: boolean;
  e_de_fracasso: boolean;
}

const etapas = ref<Etapa[]>([]);
const novaEtapaNome = ref('');
const loading = ref(true);

const buscarEtapas = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get<Etapa[]>('/v1/clientes/etapas-funil/');
    etapas.value = response.data;
  } catch (error) {
    console.error("Erro ao buscar etapas:", error);
    // Adicionar um toast de erro para o usuário aqui seria ideal
  } finally {
    loading.value = false;
  }
};

const adicionarEtapa = async () => {
  if (!novaEtapaNome.value.trim()) return;
  try {
    const novaOrdem = etapas.value.length;
    const response = await apiClient.post<Etapa>('/v1/clientes/etapas-funil/', {
      nome: novaEtapaNome.value,
      ordem: novaOrdem
    });
    etapas.value.push(response.data);
    novaEtapaNome.value = '';
  } catch (error) {
    console.error("Erro ao adicionar etapa:", error);
  }
};

const removerEtapa = async (etapaParaRemover: Etapa) => {
  if (!confirm(`Tem certeza que deseja remover a etapa "${etapaParaRemover.nome}"?`)) return;
  try {
    await apiClient.delete(`/v1/clientes/etapas-funil/${etapaParaRemover.id}/`);
    etapas.value = etapas.value.filter(e => e.id !== etapaParaRemover.id);
  } catch (error) {
    alert("Não é possível remover uma etapa que já contém oportunidades. Mova as oportunidades para outra etapa antes de remover.");
    console.error("Erro ao remover etapa:", error);
  }
};

const salvarOrdenacao = async () => {
  const ordemIds = etapas.value.map(e => e.id);
  try {
    await apiClient.post('/v1/clientes/etapas-funil/ordenar/', { ordem: ordemIds });
  } catch (error) {
    console.error("Erro ao salvar ordenação:", error);
    alert("Ocorreu um erro ao salvar a nova ordem das etapas.");
    await buscarEtapas(); // Recarrega para reverter a mudança visual
  }
};

const salvarNomeEtapa = async (etapa: Etapa) => {
  try {
    await apiClient.patch(`/v1/clientes/etapas-funil/${etapa.id}/`, { nome: etapa.nome });
  } catch (error) {
    console.error("Erro ao salvar nome da etapa:", error);
  }
};

const salvarFlag = async (etapaModificada: Etapa, tipo: 'sucesso' | 'fracasso') => {
    // Desmarca a flag correspondente em todas as outras etapas
    etapas.value.forEach(e => {
        if (e.id !== etapaModificada.id) {
            if (tipo === 'sucesso' && etapaModificada.e_de_sucesso) e.e_de_sucesso = false;
            if (tipo === 'fracasso' && etapaModificada.e_de_fracasso) e.e_de_fracasso = false;
        }
    });

    // Salva todas as mudanças em lote para o backend
    try {
        await Promise.all(etapas.value.map(e => 
            apiClient.patch(`/v1/clientes/etapas-funil/${e.id}/`, { 
                e_de_sucesso: e.e_de_sucesso,
                e_de_fracasso: e.e_de_fracasso 
            })
        ));
    } catch (error) {
        console.error("Erro ao salvar flags:", error);
        await buscarEtapas(); // Reverte em caso de erro
    }
};

onMounted(buscarEtapas);
</script>

<style scoped>
/* Usando um estilo mais limpo e profissional */
.etapas-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.view-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}
.view-header h2 {
  font-size: 1.75rem;
  font-weight: 600;
}
.view-header p {
  color: #6c757d;
}
.nova-etapa-form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
}
.form-control { /* Classe genérica para inputs */
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 0.375rem;
  font-size: 1rem;
}
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  white-space: nowrap;
}
.btn-primary {
  background-color: #0d6efd;
  color: white;
}
.btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
.etapas-list {
  list-style: none;
  padding: 0;
}
.etapa-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75rem 1.25rem;
  margin-bottom: 0.5rem;
  border-radius: 0.375rem;
}
.drag-handle {
  cursor: grab;
  font-size: 1.5rem;
  color: #adb5bd;
}
.etapa-nome-input {
  flex-grow: 1;
  border: none;
  background: transparent;
  padding: 0;
}
.etapa-flags {
  display: flex;
  gap: 1.5rem;
  margin-left: auto;
  font-size: 0.9rem;
}
.form-check-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}
.remover-btn {
  background: none;
  border: none;
  color: #dc3545;
  font-size: 1.75rem;
  font-weight: bold;
  cursor: pointer;
  line-height: 1;
  padding: 0 0.5rem;
}
.empty-state, .loading-indicator {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
}
</style>
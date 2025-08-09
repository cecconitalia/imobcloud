<template>
  <div class="funil-container">
    <header class="view-header">
      <h1>Funil de Vendas</h1>
      <router-link to="/oportunidades/nova" class="btn-primary">
        + Nova Oportunidade
      </router-link>
    </header>

    <div class="filter-bar">
      <div class="filter-group">
        <label for="search-input">Pesquisar:</label>
        <input 
          id="search-input" 
          v-model="filtro.search" 
          type="text" 
          placeholder="Título, cliente ou endereço"
          class="form-control search-input"
        />
      </div>
      
      <div class="filter-group">
        <label for="responsavel-filter">Corretor:</label>
        <select 
          id="responsavel-filter" 
          v-model="filtro.responsavel"
          class="form-control"
        >
          <option value="">Todos</option>
          <option v-for="resp in corretores" :key="resp.id" :value="resp.id">
            {{ resp.first_name }}
          </option>
        </select>
      </div>

      <button @click="limparFiltros" class="btn-secondary">Limpar Filtros</button>
    </div>

    <div v-if="isLoading" class="loading-message">A carregar oportunidades...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!isLoading" class="funil-board">
      <div v-for="fase in fasesDoFunil" :key="fase.id" class="funil-coluna">
        <h3 class="coluna-titulo">
          {{ fase.titulo }} ({{ funilData[fase.id]?.length || 0 }})
          <span class="coluna-total">{{ calcularValorTotal(funilData[fase.id]) }}</span>
        </h3>
        
        <draggable
          class="coluna-content"
          :list="funilData[fase.id]"
          group="oportunidades"
          itemKey="id"
          @end="handleDragEnd"
          :data-fase-id="fase.id"
        >
          <template #item="{ element: oportunidade }">
            <router-link :to="`/oportunidades/editar/${oportunidade.id}`" class="oportunidade-card-link">
              <div class="oportunidade-card" :data-id="oportunidade.id">
                <h4 class="card-titulo">{{ oportunidade.titulo }}</h4>
                <p class="card-cliente">{{ oportunidade.cliente?.nome_completo || 'Cliente não definido' }}</p>
                <p class="card-imovel">{{ oportunidade.imovel?.endereco || 'Sem imóvel associado' }}</p>
                <div class="card-footer">
                  <span class="card-valor">{{ formatarValor(oportunidade.valor_estimado) }}</span>
                  <span class="card-responsavel">{{ oportunidade.responsavel?.username.charAt(0).toUpperCase() || '?' }}</span>
                </div>
              </div>
            </router-link>
          </template>
        </draggable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import apiClient from '@/services/api';
import draggable from 'vuedraggable';

const oportunidades = ref<any[]>([]);
const funilData = ref<{ [key: string]: any[] }>({});
const isLoading = ref(true);
const error = ref<string | null>(null);
const corretores = ref<any[]>([]);

const filtro = ref({
  search: '',
  responsavel: ''
});

const fasesDoFunil = ref([
  { id: 'LEAD', titulo: 'Novo Lead' },
  { id: 'CONTATO', titulo: 'Primeiro Contato' },
  { id: 'VISITA', titulo: 'Visita Agendada' },
  { id: 'PROPOSTA', titulo: 'Proposta Enviada' },
  { id: 'NEGOCIACAO', titulo: 'Em Negociação' },
  { id: 'GANHO', titulo: 'Negócio Ganho' },
  { id: 'PERDIDO', titulo: 'Negócio Perdido' },
]);

const oportunidadesFiltradas = computed(() => {
  let lista = oportunidades.value;

  if (filtro.value.search) {
    const termo = filtro.value.search.toLowerCase();
    lista = lista.filter(op => {
      const titulo = op.titulo?.toLowerCase().includes(termo);
      const clienteNome = op.cliente?.nome_completo?.toLowerCase().includes(termo);
      const imovelEndereco = op.imovel?.endereco?.toLowerCase().includes(termo);
      return titulo || clienteNome || imovelEndereco;
    });
  }

  if (filtro.value.responsavel) {
    lista = lista.filter(op => op.responsavel?.id === parseInt(filtro.value.responsavel));
  }

  return lista;
});

watch(oportunidadesFiltradas, (novaLista) => {
  const agrupado: { [key: string]: any[] } = {};
  fasesDoFunil.value.forEach(fase => {
    agrupado[fase.id] = [];
  });
  novaLista.forEach(oportunidade => {
    agrupado[oportunidade.fase].push(oportunidade);
  });
  funilData.value = agrupado;
}, { immediate: true });

async function fetchOportunidades() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/clientes/oportunidades/');
    oportunidades.value = response.data;
    const responsaveisUnicos = Array.from(new Set(oportunidades.value.map(op => op.responsavel?.id)))
      .filter(id => id !== undefined)
      .map(id => oportunidades.value.find(op => op.responsavel?.id === id).responsavel);
    corretores.value = responsaveisUnicos;
  } catch (err) {
    console.error("Erro ao buscar oportunidades:", err);
    error.value = "Não foi possível carregar o funil de vendas.";
  } finally {
    isLoading.value = false;
  }
}

async function handleDragEnd(event: any) {
  const { to, item } = event;
  console.log('Evento de drag-and-drop finalizado. Item:', item, 'Para:', to);
  
  // CORREÇÃO: Procura o elemento filho com o data-id
  const oportunidadeId = item.querySelector('.oportunidade-card')?.dataset.id;
  const novaFaseId = to.dataset.faseId;

  console.log('ID da Oportunidade:', oportunidadeId);
  console.log('Nova Fase ID:', novaFaseId);

  if (!oportunidadeId || !novaFaseId) {
    console.error("Não foi possível obter o ID da oportunidade ou a nova fase.");
    fetchOportunidades();
    return;
  }
  
  const oportunidadeMovida = oportunidades.value.find(op => op.id === parseInt(oportunidadeId));
  if (oportunidadeMovida && oportunidadeMovida.fase !== novaFaseId) {
    try {
      // Envia a requisição de atualização para a API
      await apiClient.patch(`/v1/clientes/oportunidades/${oportunidadeId}/`, {
        fase: novaFaseId,
      });

      // Atualiza o estado da oportunidade no array principal. O watcher irá reagir e atualizar o funilData
      oportunidadeMovida.fase = novaFaseId;

    } catch (error) {
      console.error('Erro ao atualizar a fase da oportunidade:', error);
      alert('Não foi possível mover a oportunidade. A página será recarregada para reverter a mudança.');
      // Em caso de erro, recarrega os dados para reverter a alteração visual
      fetchOportunidades();
    }
  }
}

function formatarValor(valor: number | null) {
  if (!valor) return 'R$ -';
  return parseFloat(valor.toString()).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function calcularValorTotal(oportunidadesDaFase: any[] | undefined) {
  if (!oportunidadesDaFase) return '';
  const total = oportunidadesDaFase.reduce((sum, op) => {
    const valor = op.valor_estimado ? parseFloat(op.valor_estimado) : 0;
    return sum + valor;
  }, 0);
  
  if (total === 0) return '';
  return formatarValor(total);
}

function limparFiltros() {
  filtro.value.search = '';
  filtro.value.responsavel = '';
}

onMounted(() => {
  fetchOportunidades();
});
</script>

<style scoped>
/* Estilos adicionados para a barra de filtro */
.filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
}
.filter-group label {
  font-weight: bold;
  margin-bottom: 0.5rem;
}
.form-control {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.search-input {
  width: 250px;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  height: 40px; /* Alinha com os outros campos */
}

/* Restante dos estilos CSS */
.coluna-total {
  display: block;
  font-size: 0.85em;
  font-weight: normal;
  color: #6c757d;
  margin-top: 4px;
}
.oportunidade-card-link {
  text-decoration: none;
  color: inherit;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
}
.coluna-content {
  padding: 0 0.5rem;
  max-height: 70vh;
  min-height: 100px;
  overflow-y: auto;
}
.funil-container {
  padding: 2rem;
}
.funil-board {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 1rem;
}
.funil-coluna {
  flex: 1;
  min-width: 280px;
  background-color: #e9ecef;
  border-radius: 8px;
  padding: 0.5rem;
}
.coluna-titulo {
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  font-weight: bold;
}
.oportunidade-card {
  background-color: white;
  border-radius: 5px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  cursor: grab;
}
.oportunidade-card:hover {
  box-shadow: 0 3px 6px rgba(0,0,0,0.15);
}
.card-titulo {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}
.card-cliente, .card-imovel {
  font-size: 0.85rem;
  color: #6c757d;
  margin: 0 0 0.25rem 0;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}
.card-valor {
  font-weight: bold;
  color: #28a745;
}
.card-responsavel {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.8rem;
}
</style>
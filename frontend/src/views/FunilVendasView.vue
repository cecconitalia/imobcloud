<template>
  <div class="funil-container">
    <header class="view-header">
      <h1>Funil de Vendas</h1>
      <router-link to="/oportunidades/nova" class="btn-primary">
        + Nova Oportunidade
      </router-link>
    </header>

    <div v-if="isLoading" class="loading-message">A carregar oportunidades...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!isLoading" class="funil-board">
      <div v-for="fase in fasesDoFunil" :key="fase.id" class="funil-coluna">
        <h3 class="coluna-titulo">
          {{ fase.titulo }} ({{ getOportunidadesPorFase(fase.id).length }})
          <span class="coluna-total">{{ calcularValorTotal(fase.id) }}</span>
        </h3>
        
        <draggable
          class="coluna-content"
          :list="getOportunidadesPorFase(fase.id)"
          group="oportunidades"
          itemKey="id"
          @end="handleDragEnd"
          :data-fase-id="fase.id"
        >
          <template #item="{ element: oportunidade }">
            <router-link :to="`/oportunidades/editar/${oportunidade.id}`" class="oportunidade-card-link">
              <div class="oportunidade-card">
                <h4 class="card-titulo">{{ oportunidade.titulo }}</h4>
                <p class="card-cliente">{{ oportunidade.cliente_obj?.nome_completo || 'Cliente não definido' }}</p>
                <p class="card-imovel">{{ oportunidade.imovel_obj?.endereco || 'Sem imóvel associado' }}</p>
                <div class="card-footer">
                  <span class="card-valor">{{ formatarValor(oportunidade.valor_estimado) }}</span>
                  <span class="card-responsavel">{{ oportunidade.responsavel_obj?.username.charAt(0).toUpperCase() || '?' }}</span>
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
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import draggable from 'vuedraggable';

const oportunidades = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

const fasesDoFunil = ref([
  { id: 'LEAD', titulo: 'Novo Lead' },
  { id: 'CONTATO', titulo: 'Primeiro Contato' },
  { id: 'VISITA', titulo: 'Visita Agendada' },
  { id: 'PROPOSTA', titulo: 'Proposta Enviada' },
  { id: 'NEGOCIACAO', titulo: 'Em Negociação' },
  { id: 'GANHO', titulo: 'Negócio Ganho' },
  { id: 'PERDIDO', titulo: 'Negócio Perdido' },
]);

async function fetchOportunidades() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/clientes/oportunidades/');
    oportunidades.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar oportunidades:", err);
    error.value = "Não foi possível carregar o funil de vendas.";
  } finally {
    isLoading.value = false;
  }
}

function getOportunidadesPorFase(faseId: string) {
  return oportunidades.value.filter(op => op.fase === faseId);
}

async function handleDragEnd(event: any) {
  const { to, item } = event;
  const oportunidadeId = item._underlying_vm_ ? item._underlying_vm_.id : null;
  const novaFaseId = to.dataset.faseId;

  if (!oportunidadeId) {
      console.error("Não foi possível obter o ID da oportunidade movida.");
      return;
  }

  const oportunidadeMovida = oportunidades.value.find(op => op.id === oportunidadeId);

  if (oportunidadeMovida && oportunidadeMovida.fase !== novaFaseId) {
    try {
      // Usamos PATCH para enviar apenas o campo que mudou
      await apiClient.patch(`/v1/clientes/oportunidades/${oportunidadeId}/`, {
        fase: novaFaseId,
      });
      // Atualiza o estado local para refletir a mudança
      oportunidadeMovida.fase = novaFaseId;
    } catch (error) {
      console.error('Erro ao atualizar a fase da oportunidade:', error);
      alert('Não foi possível mover a oportunidade. A página será recarregada para reverter a mudança.');
      fetchOportunidades(); // Recarrega os dados em caso de erro
    }
  }
}

function formatarValor(valor: number | null) {
  if (!valor) return 'R$ -';
  return parseFloat(valor.toString()).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// --- NOVA FUNÇÃO PARA CALCULAR O VALOR TOTAL DA COLUNA ---
function calcularValorTotal(faseId: string) {
  const total = getOportunidadesPorFase(faseId).reduce((sum, op) => {
    // Garante que o valor é um número antes de somar
    const valor = op.valor_estimado ? parseFloat(op.valor_estimado) : 0;
    return sum + valor;
  }, 0);
  
  if (total === 0) return '';
  return formatarValor(total);
}


onMounted(() => {
  fetchOportunidades();
});
</script>

<style scoped>
/* Adicionado estilo para o total da coluna */
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
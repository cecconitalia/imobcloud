<template>
  <div class="funil-container">
    <VueFlow v-if="nodes.length > 0" v-model:nodes="nodes" v-model:edges="edges" :fit-view-on-init="true">
      <Background />
      <MiniMap />
      <Controls />
    </VueFlow>
    <div v-else class="loading-container">
      <p>Carregando dados do funil...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

// Componentes e Tipos do Vue Flow
import { VueFlow } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { MiniMap } from '@vue-flow/minimap';
import { Controls } from '@vue-flow/controls';
import type { Node, Edge } from '@vue-flow/core';

// Cliente API
import apiClient from '@/services/api';

// Estilos essenciais do Vue Flow
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';

// --- Interfaces para os dados da API ---
interface OportunidadeAPI {
  id: number;
  nome: string;
  valor: number;
}

interface FunilStageAPI {
  etapa: string;
  oportunidades: OportunidadeAPI[];
}

// --- Refs do Vue para o gráfico ---
const nodes = ref<Node[]>([]);
const edges = ref<Edge[]>([]);

/**
 * Converte os dados da API para o formato de nós e arestas do Vue Flow.
 * @param data Os dados brutos do funil vindos do backend.
 */
const parseFunilData = (data: FunilStageAPI[]) => {
  const newNodes: Node[] = [];
  const newEdges: Edge[] = [];
  let previousStageNodeId: string | null = null;
  const initialX = 100;
  const stageY = 50;
  const opportunityYOffset = 120;
  const stageXOffset = 350;

  let currentX = initialX;

  data.forEach((stage) => {
    if (stage.oportunidades.length === 0) {
      return;
    }

    const stageNodeId = `stage-${stage.etapa.replace(/\s+/g, '-')}`;

    newNodes.push({
      id: stageNodeId,
      label: `${stage.etapa} (${stage.oportunidades.length})`,
      position: { x: currentX, y: stageY },
      style: {
        background: '#007bff',
        color: 'white',
        borderRadius: '8px',
        padding: '10px 15px',
        width: '280px',
        textAlign: 'center',
        fontSize: '16px',
        fontWeight: 'bold',
      },
    });

    if (previousStageNodeId) {
      newEdges.push({
        id: `e-${previousStageNodeId}-${stageNodeId}`,
        source: previousStageNodeId,
        target: stageNodeId,
        animated: true,
        style: { strokeWidth: 2, stroke: '#007bff' },
      });
    }
    previousStageNodeId = stageNodeId;

    stage.oportunidades.forEach((op, opIndex) => {
      const opportunityNodeId = `op-${op.id}`;
      newNodes.push({
        id: opportunityNodeId,
        label: `${op.nome} - R$ ${op.valor.toLocaleString('pt-BR')}`,
        position: {
          x: currentX,
          y: stageY + opportunityYOffset + opIndex * 90,
        },
        style: {
          background: '#ffffff',
          border: '1px solid #ced4da',
          borderRadius: '4px',
          padding: '10px',
          width: '280px',
        },
      });

      newEdges.push({
        id: `e-${stageNodeId}-${opportunityNodeId}`,
        source: stageNodeId,
        target: opportunityNodeId,
        style: { stroke: '#adb5bd' },
      });
    });
    
    currentX += stageXOffset;
  });

  nodes.value = newNodes;
  edges.value = newEdges;
};

// --- Ciclo de vida do componente ---
onMounted(async () => {
  try {
    // **AQUI ESTÁ A CORREÇÃO FINAL:** Usando a URL completa que o Django espera.
    // A baseURL do apiClient é '/api', então adicionamos o resto do caminho.
    const response = await apiClient.get<FunilStageAPI[]>('/v1/clientes/funil-vendas/');
    parseFunilData(response.data);
  } catch (error) {
    console.error('Erro ao buscar dados do funil de vendas:', error);
  }
});
</script>

<style>
.funil-container {
  width: 100%;
  height: 85vh;
  background-color: #f8f9fa;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 1.2rem;
  color: #6c757d;
}

.vue-flow__minimap {
  border-radius: 8px;
}
</style>
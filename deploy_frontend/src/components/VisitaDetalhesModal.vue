<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/services/api';

// Correção dos imports: Apontando para a subpasta Vistorias/ onde os arquivos residem
import FotoUploadModal from './Vistorias/FotoUploadModal.vue';
import AmbienteFormModal from './Vistorias/AmbienteFormModal.vue';
import ItemFormModal from './Vistorias/ItemFormModal.vue';

interface Foto {
  id: number;
  url: string;
}

interface Item {
  id: number;
  item: string;
  estado: string;
  estado_entrada?: string; // Captura o estado original da entrada enviado pelo Serializer
  descricao_avaria: string;
  fotos: Foto[];
}

interface Ambiente {
  id: number;
  nome: string;
  observacoes: string;
  itens: Item[];
}

interface Vistoria {
  id: number;
  tipo: 'ENTRADA' | 'SAIDA' | 'PERIODICA';
  tipo_display: string;
  imovel_display: string;
  data_vistoria: string;
  concluida: boolean;
  ambientes: Ambiente[];
  observacoes: string;
}

const props = defineProps<{ vistoriaId: number }>();
const emit = defineEmits(['close', 'update']);

const vistoria = ref<Vistoria | null>(null);
const loading = ref(true);

const showAmbienteModal = ref(false);
const showItemModal = ref(false);
const showFotoModal = ref(false);
const activeAmbienteId = ref<number | null>(null);
const activeItemId = ref<number | null>(null);

const fetchDetalhes = async () => {
  loading.value = true;
  try {
    const response = await api.get<Vistoria>(`/vistorias/vistorias/${props.vistoriaId}/`);
    vistoria.value = response.data;
  } catch (err) {
    console.error("Erro ao carregar detalhes da vistoria:", err);
  } finally {
    loading.value = false;
  }
};

const atualizarEstadoItem = async (item: Item, novoEstado: string) => {
  if (vistoria.value?.concluida) return;
  try {
    await api.patch(`/vistorias/itens/${item.id}/`, { estado: novoEstado });
    item.estado = novoEstado;
  } catch (err) {
    alert("Erro ao atualizar estado.");
  }
};

const salvarDescricao = async (item: Item) => {
  if (vistoria.value?.concluida) return;
  try {
    await api.patch(`/vistorias/itens/${item.id}/`, { descricao_avaria: item.descricao_avaria });
  } catch (err) {
    console.error("Erro ao salvar descrição.");
  }
};

const concluirVistoria = async () => {
  if (!confirm("Deseja concluir a vistoria? Isso bloqueará edições.")) return;
  try {
    await api.patch(`/vistorias/vistorias/${props.vistoriaId}/`, { concluida: true });
    fetchDetalhes();
    emit('update');
  } catch (err) {
    alert("Erro ao concluir.");
  }
};

const downloadPDF = () => {
  window.open(`${import.meta.env.VITE_API_URL}/vistorias/vistorias/${props.vistoriaId}/gerar-laudo/`, '_blank');
};

onMounted(fetchDetalhes);
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-2 sm:p-4">
    <div class="bg-white w-full max-w-5xl max-h-[95vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
      
      <div class="p-4 border-b flex justify-between items-center bg-gray-50">
        <div class="truncate mr-4">
          <h2 class="text-lg font-bold text-gray-800 truncate">{{ vistoria?.imovel_display }}</h2>
          <p class="text-[10px] text-gray-500 uppercase font-black tracking-widest">
            {{ vistoria?.tipo_display }} | {{ vistoria?.data_vistoria }}
          </p>
        </div>
        <button @click="$emit('close')" class="p-2 hover:bg-gray-200 rounded-full transition-all active:scale-90 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>

      <div v-if="loading" class="flex-1 flex items-center justify-center p-12">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>

      <div v-else class="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-100/30">
        
        <div class="flex flex-wrap gap-2 sticky top-0 z-10 bg-white/80 backdrop-blur-md p-2 rounded-xl border shadow-sm">
          <button @click="downloadPDF" class="flex-1 sm:flex-none bg-blue-600 text-white px-4 py-2 rounded-lg text-xs font-bold hover:bg-blue-700 active:scale-95 transition-all">
            IMPRIMIR LAUDO
          </button>
          <button v-if="!vistoria?.concluida" @click="showAmbienteModal = true" class="flex-1 sm:flex-none bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-xs font-bold hover:bg-gray-300 active:scale-95 transition-all">
            + AMBIENTE
          </button>
          <button v-if="!vistoria?.concluida" @click="concluirVistoria" class="flex-1 sm:flex-none bg-green-600 text-white px-4 py-2 rounded-lg text-xs font-bold hover:bg-green-700 active:scale-95 transition-all">
            CONCLUIR
          </button>
        </div>

        <div v-for="amb in vistoria?.ambientes" :key="amb.id" class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div class="p-3 bg-gray-800 text-white flex justify-between items-center">
            <h3 class="font-bold text-xs uppercase tracking-tighter">{{ amb.nome }}</h3>
            <button v-if="!vistoria?.concluida" @click="activeAmbienteId = amb.id; showItemModal = true" class="text-[9px] bg-white/20 hover:bg-white/30 px-2 py-1 rounded font-black uppercase transition-colors">
              ADICIONAR ITEM
            </button>
          </div>

          <div class="p-3 space-y-4">
            <div v-for="item in amb.itens" :key="item.id" class="p-4 rounded-xl border border-gray-100 bg-gray-50/50">
              
              <div class="flex flex-col gap-3 mb-4">
                <div class="flex justify-between items-start">
                  <h4 class="font-bold text-gray-700 text-sm flex items-center gap-2">
                    <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                    {{ item.item }}
                  </h4>
                  
                  <div v-if="item.estado_entrada" class="text-[9px] font-black bg-orange-100 text-orange-700 px-2 py-1 rounded border border-orange-200 uppercase">
                    Entrada: {{ item.estado_entrada }}
                  </div>
                </div>

                <div class="flex flex-wrap bg-gray-200/50 p-1 rounded-lg gap-1">
                  <button 
                    v-for="e in ['NOVO', 'BOM', 'REGULAR', 'RUIM', 'INOPERANTE']" 
                    :key="e"
                    @click="atualizarEstadoItem(item, e)"
                    :disabled="vistoria?.concluida"
                    :class="[
                      'flex-1 py-1.5 rounded text-[9px] font-black transition-all active:scale-90',
                      item.estado === e ? 'bg-white text-blue-600 shadow-sm border border-gray-100' : 'text-gray-400'
                    ]"
                  >
                    {{ e }}
                  </button>
                </div>
              </div>

              <textarea 
                v-model="item.descricao_avaria"
                @blur="salvarDescricao(item)"
                :disabled="vistoria?.concluida"
                placeholder="Descreva o estado atual ou avarias..."
                class="w-full text-xs border-gray-200 rounded-lg bg-white p-2 italic mb-4 focus:ring-1 focus:ring-blue-500 outline-none"
                rows="2"
              ></textarea>

              <div class="grid grid-cols-4 sm:grid-cols-6 gap-2">
                <div v-for="foto in item.fotos" :key="foto.id" class="aspect-square rounded-lg overflow-hidden border bg-gray-200">
                  <img :src="foto.url" class="w-full h-full object-cover" />
                </div>
                <button 
                  v-if="!vistoria?.concluida"
                  @click="activeItemId = item.id; showFotoModal = true"
                  class="aspect-square rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center text-gray-400 hover:border-blue-400 hover:text-blue-500 active:scale-95 transition-all bg-white"
                >
                  <span class="text-lg font-bold">+</span>
                  <span class="text-[8px] font-black uppercase">Foto</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="vistoria?.ambientes.length === 0" class="text-center py-12 border-2 border-dashed border-gray-300 rounded-2xl bg-white">
          <p class="text-gray-400 text-xs font-bold uppercase">Nenhum ambiente herdado ou cadastrado.</p>
        </div>

      </div>
    </div>

    <AmbienteFormModal v-if="showAmbienteModal" :vistoria-id="props.vistoriaId" @close="showAmbienteModal = false" @saved="fetchDetalhes" />
    <ItemFormModal v-if="showItemModal" :ambiente-id="activeAmbienteId!" @close="showItemModal = false" @saved="fetchDetalhes" />
    <FotoUploadModal v-if="showFotoModal" :item-id="activeItemId!" @close="showFotoModal = false" @saved="fetchDetalhes" />
  </div>
</template>

<style scoped>
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
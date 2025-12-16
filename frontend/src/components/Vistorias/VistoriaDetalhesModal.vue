<template>
  <div class="modal fade" :class="{ 'show': show }" style="display: block;" tabindex="-1" v-if="show">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Detalhes da Vistoria #{{ vistoria?.id }} - {{ vistoria?.tipo_display }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        
        <div class="modal-body" v-if="loading">
          <div class="text-center p-5"><i class="fas fa-spinner fa-spin fa-2x"></i> Carregando detalhes...</div>
        </div>

        <div class="modal-body" v-else>
            
            <div class="row mb-4 border-bottom pb-3">
                <div class="col-md-4"><strong>Contrato:</strong> #{{ vistoria.contrato }}</div>
                <div class="col-md-4"><strong>Data:</strong> {{ formatDate(vistoria.data_vistoria) }}</div>
                <div class="col-md-4"><strong>Realizado Por:</strong> {{ vistoria.realizado_por_nome }}</div>
                <div class="col-12 mt-2"><strong>Obs. Gerais:</strong> {{ vistoria.observacoes_gerais || 'Nenhuma' }}</div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Ambientes Vistoriados</h4>
                <button class="btn btn-sm btn-success" @click="openAmbienteModal(null)">
                    <i class="fas fa-plus me-1"></i> Novo Ambiente
                </button>
            </div>

            <div v-if="vistoria.ambientes && vistoria.ambientes.length" class="accordion" id="accordionAmbientes">
                <div class="accordion-item" v-for="(ambiente, index) in vistoria.ambientes" :key="ambiente.id">
                    <h2 class="accordion-header" :id="'heading' + ambiente.id">
                        <button 
                            class="accordion-button" 
                            type="button" 
                            data-bs-toggle="collapse" 
                            :data-bs-target="'#collapse' + ambiente.id" 
                            :aria-expanded="index === 0" 
                            :aria-controls="'collapse' + ambiente.id"
                        >
                            {{ ambiente.nome }} ({{ ambiente.itens.length }} Itens)
                        </button>
                    </h2>
                    <div :id="'collapse' + ambiente.id" class="accordion-collapse collapse" :class="{ 'show': index === 0 }" :aria-labelledby="'heading' + ambiente.id" data-bs-parent="#accordionAmbientes">
                        <div class="accordion-body">
                            
                            <p class="small text-muted">Obs. Ambiente: {{ ambiente.observacoes || 'Nenhuma' }}</p>

                            <h6 class="mt-3">Itens:</h6>
                            <ul class="list-group list-group-flush mb-3">
                                <li class="list-group-item d-flex justify-content-between align-items-start" v-for="item in ambiente.itens" :key="item.id">
                                    <div class="ms-2 me-auto">
                                        <div class="fw-bold">{{ item.item }}</div>
                                        <span :class="getStatusBadge(item.estado)">{{ item.estado_display }}</span>
                                        <p class="small mt-1 mb-0">{{ item.descricao_avaria }}</p>
                                        <div class="mt-1">
                                            <span v-for="foto in item.fotos" :key="foto.id" class="d-inline-block me-2">
                                                <a :href="foto.imagem" target="_blank">
                                                    <img :src="foto.imagem" alt="Foto" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;">
                                                </a>
                                            </span>
                                            <button class="btn btn-sm btn-outline-secondary ms-2" @click="openFotoUploadModal(item.id)">
                                                <i class="fas fa-camera"></i> ({{ item.fotos.length }})
                                            </button>
                                        </div>
                                    </div>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" @click="openItemModal(ambiente.id, item)">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-outline-danger" @click="deleteItem(item.id)">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </li>
                            </ul>
                            
                            <button class="btn btn-sm btn-outline-primary mt-2" @click="openItemModal(ambiente.id, null)">
                                <i class="fas fa-plus me-1"></i> Adicionar Item
                            </button>
                            <button class="btn btn-sm btn-outline-danger mt-2 ms-2" @click="deleteAmbiente(ambiente.id)">
                                <i class="fas fa-trash me-1"></i> Excluir Ambiente
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else class="alert alert-info text-center">
                Adicione o primeiro ambiente para começar a vistoria.
            </div>
        </div>

        <div class="modal-footer">
          <a v-if="vistoria && vistoria.arquivo_laudo_assinado" :href="vistoria.arquivo_laudo_assinado" target="_blank" class="btn btn-info">
              <i class="fas fa-file-pdf me-1"></i> Baixar Laudo Assinado
          </a>
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Fechar</button>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop fade show" v-if="show"></div>
  
  <AmbienteFormModal
    :show="showAmbienteModal"
    :vistoriaId="vistoriaId"
    :ambienteId="editAmbienteId"
    @close="closeAmbienteModal"
    @refresh="fetchVistoriaDetalhes"
  />

  <ItemFormModal
    :show="showItemModal"
    :ambienteId="selectedAmbienteId"
    :itemId="editItemId"
    @close="closeItemModal"
    @refresh="fetchVistoriaDetalhes"
  />
  
  <FotoUploadModal
    :show="showFotoModal"
    :itemId="selectedItemIdForPhoto"
    @close="closeFotoUploadModal"
    @refresh="fetchVistoriaDetalhes"
  />
</template>

<script lang="ts">
import { defineComponent, ref, watch, nextTick } from 'vue';
import api from '@/services/api';
import { formatDate } from '@/utils/formatters';

// Importar os sub-componentes (você precisará criá-los também)
import AmbienteFormModal from './AmbienteFormModal.vue';
import ItemFormModal from './ItemFormModal.vue';
import FotoUploadModal from './FotoUploadModal.vue';

interface VistoriaDetalhes {
    id: number;
    contrato: number;
    tipo_display: string;
    data_vistoria: string;
    realizado_por_nome: string;
    observacoes_gerais: string;
    arquivo_laudo_assinado: string | null;
    ambientes: any[];
}

export default defineComponent({
  name: 'VistoriaDetalhesModal',
  components: {
    AmbienteFormModal,
    ItemFormModal,
    FotoUploadModal,
  },
  props: {
    show: {
      type: Boolean,
      required: true,
    },
    vistoriaId: {
      type: Number,
      default: null,
    },
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const vistoria = ref<VistoriaDetalhes | null>(null);
    const loading = ref(false);
    
    // Controle de Modais Aninhados
    const showAmbienteModal = ref(false);
    const editAmbienteId = ref<number | null>(null);
    
    const showItemModal = ref(false);
    const selectedAmbienteId = ref<number | null>(null);
    const editItemId = ref<number | null>(null);

    const showFotoModal = ref(false);
    const selectedItemIdForPhoto = ref<number | null>(null);


    const fetchVistoriaDetalhes = async () => {
        if (!props.vistoriaId) return;
        loading.value = true;
        try {
            const response = await api.get(`/vistorias/vistorias/${props.vistoriaId}/`);
            vistoria.value = response.data;
        } catch (error) {
            console.error('Erro ao buscar detalhes da vistoria:', error);
            vistoria.value = null;
        } finally {
            loading.value = false;
        }
    };
    
    // Watch para carregar os dados quando o modal principal for aberto
    watch(() => props.show, (newVal) => {
        if (newVal && props.vistoriaId) {
            fetchVistoriaDetalhes();
        }
    });

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'NOVO': return 'badge bg-primary';
            case 'BOM': return 'badge bg-success';
            case 'REGULAR': return 'badge bg-warning text-dark';
            case 'RUIM': return 'badge bg-danger';
            default: return 'badge bg-secondary';
        }
    }
    
    // CRUD Ambiente
    const openAmbienteModal = (id: number | null) => {
        editAmbienteId.value = id;
        showAmbienteModal.value = true;
    }
    const closeAmbienteModal = () => {
        showAmbienteModal.value = false;
        editAmbienteId.value = null;
        fetchVistoriaDetalhes();
    }
    const deleteAmbiente = async (id: number) => {
        if (confirm('Tem certeza de que deseja excluir este Ambiente e todos os seus itens?')) {
            try {
                await api.delete(`/vistorias/ambientes/${id}/`);
                alert('Ambiente excluído.');
                fetchVistoriaDetalhes();
            } catch (error) {
                console.error('Erro ao excluir ambiente:', error);
                alert('Erro ao excluir ambiente.');
            }
        }
    }

    // CRUD Item
    const openItemModal = (ambienteId: number, item: any) => {
        selectedAmbienteId.value = ambienteId;
        editItemId.value = item ? item.id : null;
        showItemModal.value = true;
    }
    const closeItemModal = () => {
        showItemModal.value = false;
        selectedAmbienteId.value = null;
        editItemId.value = null;
        fetchVistoriaDetalhes();
    }
    const deleteItem = async (id: number) => {
        if (confirm('Tem certeza de que deseja excluir este Item e suas fotos?')) {
            try {
                await api.delete(`/vistorias/itens/${id}/`);
                alert('Item excluído.');
                fetchVistoriaDetalhes();
            } catch (error) {
                console.error('Erro ao excluir item:', error);
                alert('Erro ao excluir item.');
            }
        }
    }
    
    // Upload de Fotos
    const openFotoUploadModal = (itemId: number) => {
        selectedItemIdForPhoto.value = itemId;
        showFotoModal.value = true;
    }
    const closeFotoUploadModal = () => {
        showFotoModal.value = false;
        selectedItemIdForPhoto.value = null;
        fetchVistoriaDetalhes(); // Recarrega os detalhes para ver as novas fotos
    }

    return {
      vistoria,
      loading,
      formatDate,
      getStatusBadge,
      
      showAmbienteModal,
      editAmbienteId,
      openAmbienteModal,
      closeAmbienteModal,
      deleteAmbiente,

      showItemModal,
      selectedAmbienteId,
      editItemId,
      openItemModal,
      closeItemModal,
      deleteItem,
      
      showFotoModal,
      selectedItemIdForPhoto,
      openFotoUploadModal,
      closeFotoUploadModal,
      fetchVistoriaDetalhes, // Exposto para ser usado internamente
    };
  },
});
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
  overflow-y: auto;
}
.modal-dialog {
  /* Tamanho maior para gerenciar itens */
  max-width: 1100px; 
}
</style>
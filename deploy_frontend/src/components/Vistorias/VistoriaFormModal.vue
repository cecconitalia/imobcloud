<template>
  <div v-if="show">
    
    <div class="custom-backdrop" @click="closeModal"></div>

    <div class="custom-modal" role="dialog" aria-modal="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-clipboard-list me-2"></i>
              {{ isEdit ? 'Editar Vistoria' : 'Nova Vistoria' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Fechar"></button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="saveVistoria">
              
              <div class="row g-3">
                
                <div class="col-md-6">
                  <label class="form-label fw-bold">Tipo de Vistoria <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="form.tipo" required :disabled="isEdit" @change="fetchContratosAptos">
                    <option value="ENTRADA">📥 Vistoria de Entrada</option>
                    <option value="SAIDA">📤 Vistoria de Saída</option>
                    <option value="PERIODICA">🔄 Vistoria Periódica</option>
                  </select>
                  <div class="form-text text-muted" v-if="!isEdit">
                    Selecione o tipo para buscar os contratos liberados.
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-bold">Data da Realização <span class="text-danger">*</span></label>
                  <input type="date" class="form-control" v-model="form.data_vistoria" required>
                </div>

                <div class="col-md-12">
                  <label class="form-label fw-bold">Contrato Vinculado <span class="text-danger">*</span></label>
                  
                  <div v-if="loadingContratos" class="text-center py-3 bg-light rounded">
                      <span class="spinner-border spinner-border-sm text-primary me-2"></span>
                      <span>Filtrando contratos...</span>
                  </div>

                  <select v-else class="form-select" v-model="form.contrato" required :disabled="isEdit">
                    <option :value="null" disabled>
                       {{ computedPlaceholder }}
                    </option>
                    <option v-for="c in listaContratos" :key="c.id" :value="c.id">
                      {{ c.imovel_display }} (ID: {{ c.id }})
                    </option>
                  </select>

                  <div v-if="!loadingContratos && listaContratos.length === 0 && !isEdit" class="alert alert-warning mt-2 mb-0 p-2 d-flex align-items-center gap-2">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div>
                      <strong class="d-block">Nenhum contrato disponível.</strong>
                      <small v-if="form.tipo === 'ENTRADA'">
                        Não há contratos <b>ATIVOS</b> pendentes de Entrada.
                      </small>
                      <small v-else-if="form.tipo === 'SAIDA'">
                        Não há contratos Ativos (com entrada feita) pendentes de Saída.
                      </small>
                    </div>
                  </div>
                  <div class="form-text" v-if="isEdit">O contrato não pode ser alterado após a criação.</div>
                </div>

                <div class="col-12">
                  <label class="form-label fw-bold">Observações Gerais</label>
                  <textarea class="form-control" rows="4" v-model="form.observacoes" placeholder="Descreva o estado geral ou observações importantes..."></textarea>
                </div>
              </div>

              <div class="modal-footer px-0 pb-0 mt-4 border-top-0">
                <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
                <button type="submit" class="btn btn-primary" :disabled="saving || (listaContratos.length === 0 && !isEdit)">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="fas fa-save me-1"></i>
                  {{ isEdit ? 'Salvar Alterações' : 'Criar Vistoria' }}
                </button>
              </div>

            </form>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed, PropType } from 'vue';
import api from '@/services/api';

export default defineComponent({
  name: 'VistoriaFormModal',
  props: {
    show: { type: Boolean, required: true },
    vistoriaId: { type: Number as PropType<number | null>, default: null },
    // Mantemos a prop para não quebrar o pai, mas não a usamos na lógica
    contratos: { type: Array, default: () => [] } 
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const saving = ref(false);
    
    // Novas variáveis para controle da lista filtrada
    const loadingContratos = ref(false);
    const listaContratos = ref<any[]>([]); 
    
    const today = new Date().toISOString().split('T')[0];

    const initialForm = {
      contrato: null as number | null,
      tipo: 'ENTRADA',
      data_vistoria: today,
      observacoes: ''
    };

    const form = ref({ ...initialForm });
    const isEdit = computed(() => !!props.vistoriaId);

    const computedPlaceholder = computed(() => {
        if (loadingContratos.value) return "Carregando...";
        if (listaContratos.value.length === 0) return "Nenhum contrato encontrado para este tipo";
        return "Selecione um contrato...";
    });

    // --- LÓGICA DE FILTRO (NOVO) ---
    const fetchContratosAptos = async () => {
        if (isEdit.value) return; // Não recarrega na edição

        loadingContratos.value = true;
        listaContratos.value = [];
        form.value.contrato = null; 

        try {
            const tipo = form.value.tipo;
            // Chama o endpoint que criamos no backend
            const response = await api.get('/v1/contratos/pendentes_vistoria/', { 
                params: { tipo: tipo } 
            });
            
            // Trata se vier paginado ou lista direta
            listaContratos.value = response.data.results || response.data;
            
            console.log(`Contratos filtrados (${tipo}):`, listaContratos.value.length);

        } catch (error) {
            console.error("Erro ao buscar contratos:", error);
            // Fallback: se a API falhar, mostra a lista completa (comportamento antigo) só para não travar
            // listaContratos.value = props.contratos; 
        } finally {
            loadingContratos.value = false;
        }
    };

    // --- CARREGA DADOS NA EDIÇÃO ---
    const fetchVistoria = async () => {
      if (!props.vistoriaId) return;
      try {
        const response = await api.get(`/v1/vistorias/vistorias/${props.vistoriaId}/`);
        form.value = {
            ...response.data,
            data_vistoria: response.data.data_vistoria ? response.data.data_vistoria.split('T')[0] : today
        };
        
        // Na edição, precisamos buscar o contrato específico para ele aparecer no select
        if (response.data.contrato) {
            const contratoRes = await api.get(`/v1/contratos/${response.data.contrato}/`);
            listaContratos.value = [contratoRes.data];
        }
      } catch (error) {
        console.error("Erro ao carregar vistoria", error);
        alert("Erro ao carregar dados.");
        closeModal();
      }
    };

    // --- WATCHERS ---
    watch(() => props.show, (newVal) => {
      if (newVal) {
        if (props.vistoriaId) {
          fetchVistoria();
        } else {
          form.value = { ...initialForm };
          // Ao abrir, já busca os contratos de ENTRADA (padrão)
          fetchContratosAptos();
        }
      }
    });

    const closeModal = () => {
      emit('close');
    };

    const saveVistoria = async () => {
      if (!form.value.contrato) {
        alert("Por favor, selecione um contrato vinculado.");
        return;
      }

      saving.value = true;
      try {
        if (isEdit.value) {
          await api.patch(`/v1/vistorias/vistorias/${props.vistoriaId}/`, form.value);
          alert("Vistoria atualizada!");
        } else {
          await api.post('/v1/vistorias/vistorias/', form.value);
          alert("Vistoria criada com sucesso!");
        }
        emit('refresh');
        closeModal();
      } catch (error: any) {
        console.error("Erro ao salvar:", error);
        const msg = error.response?.data?.detail || "Erro ao salvar vistoria.";
        alert(msg);
      } finally {
        saving.value = false;
      }
    };

    return {
      form,
      isEdit,
      saving,
      loadingContratos,
      listaContratos, // Usamos esta lista agora
      computedPlaceholder,
      closeModal,
      saveVistoria,
      fetchContratosAptos
    };
  }
});
</script>

<style scoped>
.custom-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050;
  backdrop-filter: blur(2px);
}

.custom-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1060;
  overflow-x: hidden;
  overflow-y: auto;
  outline: 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 30px;
}

.modal-dialog {
  width: 100%;
  max-width: 600px;
  margin: 1.75rem auto;
  pointer-events: none;
}

.modal-content {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  pointer-events: auto;
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
  outline: 0;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  border-top-left-radius: calc(0.3rem - 1px);
  border-top-right-radius: calc(0.3rem - 1px);
  background-color: #f8f9fa;
}

.modal-title {
  margin-bottom: 0;
  line-height: 1.5;
  font-weight: 600;
  color: #343a40;
}

.modal-body {
  position: relative;
  flex: 1 1 auto;
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  flex-wrap: wrap;
  flex-shrink: 0;
  align-items: center;
  justify-content: flex-end;
  padding: 0.75rem;
  border-top: 1px solid #dee2e6;
  border-bottom-right-radius: calc(0.3rem - 1px);
  border-bottom-left-radius: calc(0.3rem - 1px);
  gap: 10px;
}

.btn-close {
  box-sizing: content-box;
  width: 1em;
  height: 1em;
  padding: 0.25em 0.25em;
  color: #000;
  background: transparent url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23000'%3e%3cpath d='M.293.293a1 1 0 0 1 1.414 0L8 6.586 14.293.293a1 1 0 1 1 1.414 1.414L9.414 8l6.293 6.293a1 1 0 0 1-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 0 1-1.414-1.414L6.586 8 .293 1.707a1 1 0 0 1 0-1.414z'/%3e%3c/svg%3e") center/1em auto no-repeat;
  border: 0;
  border-radius: 0.25rem;
  opacity: .5;
  cursor: pointer;
}
.btn-close:hover { opacity: .75; }

.form-label {
  margin-bottom: 0.5rem;
  color: #495057;
}
</style>
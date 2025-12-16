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
                
                <div class="col-md-12">
                  <label class="form-label fw-bold">Contrato Vinculado <span class="text-danger">*</span></label>
                  
                  <select class="form-select" v-model="form.contrato" required :disabled="isEdit">
                    <option :value="null" disabled>Selecione um contrato...</option>
                    <option v-for="c in contratos" :key="c.id" :value="c.id">
                      {{ c.imovel_display }} (ID: {{ c.id }})
                    </option>
                  </select>

                  <div v-if="contratos.length === 0" class="alert alert-warning mt-2 mb-0 p-2">
                    <small><i class="fas fa-exclamation-triangle"></i> Nenhum contrato encontrado. Verifique se existem contratos cadastrados.</small>
                  </div>
                  <div class="form-text" v-if="isEdit">O contrato não pode ser alterado após a criação.</div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-bold">Tipo de Vistoria <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="form.tipo" required>
                    <option value="ENTRADA">📥 Vistoria de Entrada</option>
                    <option value="SAIDA">📤 Vistoria de Saída</option>
                    <option value="PERIODICA">🔄 Vistoria Periódica</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-bold">Data da Realização <span class="text-danger">*</span></label>
                  <input type="date" class="form-control" v-model="form.data_vistoria" required>
                </div>

                <div class="col-12">
                  <label class="form-label fw-bold">Observações Gerais</label>
                  <textarea class="form-control" rows="4" v-model="form.observacoes" placeholder="Descreva o estado geral ou observações importantes..."></textarea>
                </div>
              </div>

              <div class="modal-footer px-0 pb-0 mt-4 border-top-0">
                <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
                <button type="submit" class="btn btn-primary" :disabled="saving || contratos.length === 0">
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
    contratos: { type: Array as PropType<any[]>, default: () => [] }
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const saving = ref(false);
    
    // Pega a data de hoje formatada YYYY-MM-DD para o input date
    const today = new Date().toISOString().split('T')[0];

    const initialForm = {
      contrato: null as number | null,
      tipo: 'ENTRADA',
      data_vistoria: today,
      observacoes: ''
    };

    const form = ref({ ...initialForm });
    const isEdit = computed(() => !!props.vistoriaId);

    const fetchVistoria = async () => {
      if (!props.vistoriaId) return;
      try {
        const response = await api.get(`/v1/vistorias/vistorias/${props.vistoriaId}/`);
        form.value = {
            ...response.data,
            data_vistoria: response.data.data_vistoria ? response.data.data_vistoria.split('T')[0] : today
        };
      } catch (error) {
        console.error("Erro ao carregar vistoria", error);
        alert("Erro ao carregar dados da vistoria.");
        closeModal();
      }
    };

    // Monitora a abertura do modal
    watch(() => props.show, (newVal) => {
      if (newVal) {
        console.log("Modal de Vistoria Aberto. ID:", props.vistoriaId);
        console.log("Contratos disponíveis:", props.contratos.length);
        
        if (props.vistoriaId) {
          fetchVistoria();
        } else {
          // Reseta o formulário para criação
          form.value = { 
            contrato: null, 
            tipo: 'ENTRADA', 
            data_vistoria: new Date().toISOString().split('T')[0], 
            observacoes: '' 
          }; 
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
          alert("Vistoria atualizada com sucesso!");
        } else {
          await api.post('/v1/vistorias/vistorias/', form.value);
          // Mensagem de sucesso simples
          alert("Vistoria criada com sucesso!");
        }
        emit('refresh'); // Avisa o pai para atualizar a lista
        closeModal();
      } catch (error: any) {
        console.error("Erro ao salvar:", error);
        const msg = error.response?.data?.detail || "Ocorreu um erro ao salvar. Verifique os dados.";
        alert(msg);
      } finally {
        saving.value = false;
      }
    };

    return {
      form,
      isEdit,
      saving,
      closeModal,
      saveVistoria
    };
  }
});
</script>

<style scoped>
/* ESTILOS CRÍTICOS PARA GARANTIR VISIBILIDADE DO MODAL */

/* Fundo Escuro (Backdrop) */
.custom-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050; /* Alto z-index para cobrir menu lateral */
  backdrop-filter: blur(2px);
}

/* Container do Modal */
.custom-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1060; /* Maior que o backdrop */
  overflow-x: hidden;
  overflow-y: auto;
  outline: 0;
  display: flex;
  align-items: flex-start; /* Alinha no topo */
  justify-content: center;
  padding-top: 30px; /* Espaço do topo */
}

.modal-dialog {
  width: 100%;
  max-width: 600px;
  margin: 1.75rem auto;
  pointer-events: none; /* Permite clicar no fundo se necessário, mas content recupera */
}

.modal-content {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  pointer-events: auto; /* Recupera cliques */
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

/* Botões */
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

/* Labels */
.form-label {
  margin-bottom: 0.5rem;
  color: #495057;
}
</style>
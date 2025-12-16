<template>
  <div class="modal fade" :class="{ 'show': show }" style="display: block;" tabindex="-1" v-if="show">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEdit ? 'Editar Ambiente' : 'Novo Ambiente' }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveAmbiente">
            
            <div class="mb-3">
              <label for="nome" class="form-label">Nome do Ambiente</label>
              <input type="text" id="nome" class="form-control" v-model="form.nome" required maxlength="100">
            </div>

            <div class="mb-3">
              <label for="observacoes" class="form-label">Observações sobre o Ambiente</label>
              <textarea id="observacoes" class="form-control" rows="3" v-model="form.observacoes"></textarea>
            </div>
            
            <div class="d-flex justify-content-end">
              <button type="button" class="btn btn-secondary me-2" @click="$emit('close')">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <i class="fas fa-spinner fa-spin me-1" v-if="saving"></i>
                Salvar Ambiente
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop fade show" v-if="show"></div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed } from 'vue';
import api from '@/services/api';

export default defineComponent({
  name: 'AmbienteFormModal',
  props: {
    show: { type: Boolean, required: true },
    vistoriaId: { type: Number, default: null }, // ID da Vistoria Mãe
    ambienteId: { type: Number, default: null }, // ID do Ambiente para Edição
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const isEdit = computed(() => !!props.ambienteId);
    const saving = ref(false);
    
    const initialForm = {
      nome: '',
      observacoes: null as string | null,
      vistoria: props.vistoriaId // Inicializado, mas atualizado no watch
    };

    const form = ref({...initialForm});

    const fetchAmbiente = async (id: number) => {
      try {
        const response = await api.get(`/vistorias/ambientes/${id}/`);
        form.value = {
            ...response.data,
            vistoria: response.data.vistoria // Garante que o ID da Vistoria esteja correto
        }
      } catch (error) {
        console.error('Erro ao buscar ambiente:', error);
      }
    };
    
    watch(() => props.show, (newVal) => {
        if (newVal) {
            if (props.ambienteId) {
                fetchAmbiente(props.ambienteId);
            } else {
                // Criação: Reseta e associa a nova Vistoria ID
                form.value = {...initialForm, vistoria: props.vistoriaId}; 
            }
        }
    });

    const saveAmbiente = async () => {
      saving.value = true;
      // Garante que o ID da Vistoria está no payload
      if (!form.value.vistoria) {
          alert("Erro: Vistoria não identificada.");
          saving.value = false;
          return;
      }

      try {
        if (isEdit.value) {
          await api.patch(`/vistorias/ambientes/${props.ambienteId}/`, form.value);
        } else {
          await api.post('/vistorias/ambientes/', form.value);
        }
        
        alert(`Ambiente ${isEdit.value ? 'atualizado' : 'criado'} com sucesso!`);
        emit('refresh');
        emit('close');
      } catch (error) {
        console.error('Erro ao salvar ambiente:', error);
        alert('Erro ao salvar ambiente.');
      } finally {
        saving.value = false;
      }
    };

    return {
      form,
      isEdit,
      saving,
      saveAmbiente,
    };
  },
});
</script>

<style scoped>
/* Estilos modais (pode ser compartilhado via CSS global) */
.modal { background-color: rgba(0, 0, 0, 0.5); }
</style>
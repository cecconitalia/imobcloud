<template>
  <div class="modal fade" :class="{ 'show': show }" style="display: block;" tabindex="-1" v-if="show">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEdit ? 'Editar Item de Vistoria' : 'Adicionar Novo Item' }}</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveItem">
            
            <div class="mb-3">
              <label for="item" class="form-label">Nome do Item / Elemento</label>
              <input type="text" id="item" class="form-control" v-model="form.item" required maxlength="150" placeholder="Ex: Pintura da Parede, Ar Condicionado, Tomada">
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="estado" class="form-label">Estado de Conservação</label>
                    <select id="estado" class="form-select" v-model="form.estado" required>
                        <option value="NOVO">Novo</option>
                        <option value="BOM">Bom</option>
                        <option value="REGULAR">Regular</option>
                        <option value="RUIM">Ruim</option>
                        <option value="INOPERANTE">Inoperante</option>
                    </select>
                </div>
            </div>

            <div class="mb-3">
              <label for="descricao_avaria" class="form-label">Descrição de Avaria/Detalhes</label>
              <textarea id="descricao_avaria" class="form-control" rows="3" v-model="form.descricao_avaria" placeholder="Descreva qualquer dano ou observação importante."></textarea>
            </div>
            
            <div class="d-flex justify-content-end">
              <button type="button" class="btn btn-secondary me-2" @click="$emit('close')">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <i class="fas fa-spinner fa-spin me-1" v-if="saving"></i>
                Salvar Item
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
  name: 'ItemFormModal',
  props: {
    show: { type: Boolean, required: true },
    ambienteId: { type: Number, default: null }, // ID do Ambiente Pai
    itemId: { type: Number, default: null }, // ID do Item para Edição
  },
  emits: ['close', 'refresh'],
  setup(props, { emit }) {
    const isEdit = computed(() => !!props.itemId);
    const saving = ref(false);
    
    const initialForm = {
      item: '',
      estado: 'BOM',
      descricao_avaria: null as string | null,
      ambiente: props.ambienteId
    };

    const form = ref({...initialForm});

    const fetchItem = async (id: number) => {
      try {
        const response = await api.get(`/vistorias/itens/${id}/`);
        form.value = {
            ...response.data,
            ambiente: response.data.ambiente // Garante que o ID do Ambiente esteja correto
        }
      } catch (error) {
        console.error('Erro ao buscar item:', error);
      }
    };
    
    watch(() => props.show, (newVal) => {
        if (newVal) {
            if (props.itemId) {
                fetchItem(props.itemId);
            } else {
                // Criação: Reseta e associa o novo Ambiente ID
                form.value = {...initialForm, ambiente: props.ambienteId};
            }
        }
    });

    const saveItem = async () => {
      saving.value = true;
      if (!form.value.ambiente) {
          alert("Erro: Ambiente não identificado.");
          saving.value = false;
          return;
      }

      try {
        if (isEdit.value) {
          await api.patch(`/vistorias/itens/${props.itemId}/`, form.value);
        } else {
          await api.post('/vistorias/itens/', form.value);
        }
        
        alert(`Item ${isEdit.value ? 'atualizado' : 'adicionado'} com sucesso!`);
        emit('refresh');
        emit('close');
      } catch (error) {
        console.error('Erro ao salvar item:', error);
        alert('Erro ao salvar item.');
      } finally {
        saving.value = false;
      }
    };

    return {
      form,
      isEdit,
      saving,
      saveItem,
    };
  },
});
</script>
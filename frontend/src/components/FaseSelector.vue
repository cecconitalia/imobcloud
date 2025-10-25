<template>
  <div class="fase-selector-container">
    <label class="label-fase">Fase do Funil:</label>
    <div class="fase-dropdown" :class="{ 'is-open': isOpen }" @click="toggleDropdown">
      <div class="fase-current" :style="{ backgroundColor: currentFaseColor }">
        {{ currentFaseTitle }}
        <i class="fas fa-chevron-down dropdown-icon"></i>
      </div>
      <div v-if="isOpen" class="fase-options">
        <div
          v-for="fase in fasesDisponiveis"
          :key="fase.id"
          class="fase-option"
          @click.stop="selectFase(fase.id)"
        >
          <div class="option-color" :style="{ backgroundColor: fasesDeFunilCores[fase.id] }"></div>
          {{ fase.titulo }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  currentFaseId: string;
}>();

const emit = defineEmits(['update:fase']);

const isOpen = ref(false);

const fasesDoFunil = [
  { id: 'LEAD', titulo: 'Novo Lead' },
  { id: 'CONTATO', titulo: 'Primeiro Contato' },
  { id: 'VISITA', titulo: 'Visita Agendada' },
  { id: 'PROPOSTA', titulo: 'Proposta Enviada' },
  { id: 'NEGOCIACAO', titulo: 'Em Negociação' },
  { id: 'GANHO', titulo: 'Negócio Ganho' },
  { id: 'PERDIDO', titulo: 'Negócio Perdido' },
];

const fasesDeFunilCores: { [key: string]: string } = {
  'LEAD': '#42A5F5',
  'CONTATO': '#29B6F6',
  'VISITA': '#26C6DA',
  'PROPOSTA': '#66BB6A',
  'NEGOCIACAO': '#FFCA28',
  'GANHO': '#4CAF50',
  'PERDIDO': '#FF5252',
};

const currentFase = computed(() => {
  return fasesDoFunil.find(f => f.id === props.currentFaseId);
});

const currentFaseTitle = computed(() => {
  return currentFase.value?.titulo || 'Fase não definida';
});

const currentFaseColor = computed(() => {
  return fasesDeFunilCores[props.currentFaseId] || '#ccc';
});

const fasesDisponiveis = computed(() => {
  return fasesDoFunil.filter(f => f.id !== props.currentFaseId);
});

function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

function selectFase(faseId: string) {
  emit('update:fase', faseId);
  isOpen.value = false;
}
</script>

<style scoped>
.fase-selector-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.label-fase {
  font-weight: bold;
  color: #495057;
  font-size: 0.9rem;
}
.fase-dropdown {
  position: relative;
  cursor: pointer;
  width: 200px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: all 0.2s ease-in-out;
}
.fase-dropdown.is-open {
  box-shadow: 0 3px 6px rgba(0,0,0,0.15);
}
.fase-current {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  color: white;
  font-weight: bold;
  border-radius: 6px;
  transition: border-radius 0.2s ease-in-out;
}
.fase-dropdown.is-open .fase-current {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}
.dropdown-icon {
  transition: transform 0.2s ease-in-out;
}
.fase-dropdown.is-open .dropdown-icon {
  transform: rotate(180deg);
}
.fase-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: white;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
  z-index: 100;
  overflow: hidden;
}
.fase-option {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  color: #495057;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}
.fase-option:hover {
  background-color: #f1f1f1;
}
.option-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 10px;
}
</style>
<template>
  <input
    ref="inputRef"
    type="text"
    :value="displayValue"
    @input="handleInput"
    class="form-control"
    placeholder="00000-000"
    maxlength="9"
    inputmode="numeric"
  />
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';

const props = defineProps<{
  modelValue: string | null | undefined
}>();

const emit = defineEmits(['update:modelValue']);
const inputRef = ref<HTMLInputElement | null>(null);
const displayValue = ref('');

// Função que aplica a máscara visualmente: 12345678 -> 12345-678
const formatCep = (value: string) => {
  if (!value) return '';
  
  // Remove tudo que não é número
  value = value.replace(/\D/g, '');
  
  // Limita a 8 dígitos
  value = value.slice(0, 8);

  // Aplica o hífen após o 5º dígito
  if (value.length > 5) {
    value = value.replace(/^(\d{5})(\d)/, '$1-$2');
  }
  
  return value;
};

// Monitora alterações vindas do Pai (API carregou dados)
watch(() => props.modelValue, (newValue) => {
  displayValue.value = formatCep(newValue || '');
});

// Manipula a digitação do usuário
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const rawValue = target.value;
  
  // 1. Formata o valor para mostrar no input
  const formatted = formatCep(rawValue);
  displayValue.value = formatted;
  
  // 2. Atualiza o valor visual do campo imediatamente (evita delay)
  target.value = formatted;

  // 3. Emite APENAS OS NÚMEROS para o formulário pai
  // Ex: Input mostra "12345-678", mas o v-model recebe "12345678"
  const cleanValue = formatted.replace(/\D/g, '');
  emit('update:modelValue', cleanValue);
};

// Formata ao carregar o componente
onMounted(() => {
  displayValue.value = formatCep(props.modelValue || '');
});
</script>

<style scoped>
/* Herda o estilo global .form-control definido no App.vue
   Garante fundo branco, borda cinza e mesma altura dos outros. */
.form-control {
  width: 100%;
  padding: 0.65rem 0.8rem;
  font-size: 0.9rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  color: #1e293b;
  transition: border-color 0.2s;
  box-sizing: border-box;
  height: 40px;
}

.form-control:focus {
  border-color: #2563eb; /* Azul padrão do sistema */
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}
</style>
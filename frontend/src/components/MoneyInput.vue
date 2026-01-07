<template>
  <input
    ref="inputRef"
    type="text"
    :value="formattedValue"
    @input="handleInput"
    @blur="handleBlur"
    class="form-control"
    style="text-align: right;"
    inputmode="numeric"
  />
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue';

// --- Props ---
const props = defineProps({
  modelValue: {
    type: Number as () => number | null,
    default: null,
  },
  prefix: {
    type: String,
    default: 'R$ ',
  },
  suffix: {
    type: String,
    default: '',
  },
  precision: {
    type: Number,
    default: 2,
  },
});

// --- Emits ---
const emit = defineEmits(['update:modelValue']);

// --- Refs ---
const inputRef = ref<HTMLInputElement | null>(null);

// --- Formatter ---
const formatter = computed(() => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'decimal',
    minimumFractionDigits: props.precision,
    maximumFractionDigits: props.precision,
  });
});

/**
 * Formata número para string (10.00 -> "R$ 10,00")
 */
const formatValue = (value: number | null): string => {
  if (value === null || value === undefined) return '';
  return `${props.prefix}${formatter.value.format(value)}${props.suffix}`;
};

/**
 * Converte string para número ("R$ 10,00" -> 10.00)
 * Lógica "ATM": divide pelos centavos
 */
const parseValue = (value: string): number | null => {
  const digitsOnly = value.replace(/\D/g, '');
  if (!digitsOnly) return null;
  return Number(digitsOnly) / Math.pow(10, props.precision);
};

// Valor exibido no input
const formattedValue = ref(formatValue(props.modelValue));

// --- Watchers ---
// Atualiza se o valor vier de fora (ex: API carrega dados)
watch(() => props.modelValue, (newValue) => {
  const currentInternal = parseValue(formattedValue.value);
  // Só atualiza se o valor externo for realmente diferente do atual para evitar loops
  if (newValue !== currentInternal) {
    formattedValue.value = formatValue(newValue);
  }
});

/**
 * Manipula a digitação (CORRIGIDO)
 */
const handleInput = (event: Event) => {
  const input = event.target as HTMLInputElement;
  
  // 1. Calcula o novo número
  const numericValue = parseValue(input.value);
  
  // 2. Calcula a nova string formatada imediatamente
  const newFormatted = formatValue(numericValue);
  
  // 3. Atualiza o estado visual local AGORA (não espera o ciclo do pai)
  formattedValue.value = newFormatted;
  
  // 4. Emite o número para o pai
  emit('update:modelValue', numericValue);

  // 5. Truque CRÍTICO: Se o valor formatado for igual ao anterior (ex: digitar 0 em 0,00),
  // o Vue não atualiza o DOM. Forçamos a limpeza de caracteres "sujos" aqui.
  nextTick(() => {
    if (inputRef.value && inputRef.value.value !== newFormatted) {
      inputRef.value.value = newFormatted;
    }
  });
};

/**
 * Ao sair do campo, garante a formatação final
 */
const handleBlur = () => {
  formattedValue.value = formatValue(props.modelValue);
};

onMounted(() => {
  formattedValue.value = formatValue(props.modelValue);
});
</script>

<style scoped>
/* Adicionado form-control para pegar o estilo padrão do seu sistema */
.form-control {
  width: 100%;
  padding: 0.65rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #1e293b;
  transition: all 0.2s;
  box-sizing: border-box;
  background-color: #ffffff;
  height: 40px;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
}

.form-control:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  outline: none;
}
</style>
<template>
  <input
    ref="inputRef"
    type="text"
    :value="formattedValue"
    @input="handleInput"
    @blur="handleBlur"
    style="text-align: right;"
  />
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

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

// --- Formatação Nativa (CORRIGIDO) ---
// Alterado de 'currency' para 'decimal' para não forçar o símbolo R$.
// O símbolo agora é controlado totalmente pela prop 'prefix'.
const formatter = computed(() => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'decimal', // Usamos decimal para ter controle total do prefixo
    minimumFractionDigits: props.precision,
    maximumFractionDigits: props.precision,
  });
});

/**
 * Pega o valor numérico (ex: 600000.00) e formata para exibição (ex: "R$ 600.000,00")
 * Se o valor for nulo ou inválido, retorna uma string vazia.
 */
const formatValue = (value: number | null): string => {
  if (value === null || value === undefined) {
    return '';
  }
  
  // Formata apenas o número (ex: "5,00" ou "1.000,00")
  const formatted = formatter.value.format(value);
  
  // Monta a string final com prefixo e sufixo customizáveis
  return `${props.prefix}${formatted}${props.suffix}`;
};

/**
 * Pega o valor do input (ex: "R$ 600.000,00a") e limpa para um número (ex: 600000.00)
 */
const parseValue = (value: string): number | null => {
  // 1. Remove tudo que não for dígito
  const digitsOnly = value.replace(/\D/g, '');
  
  if (digitsOnly === '') {
    return null;
  }
  
  // 2. Converte para número e divide pela precisão
  const numberValue = Number(digitsOnly) / Math.pow(10, props.precision);
  
  return numberValue;
};

// --- Valor Computado para Exibição ---
// Este é o valor que o <input> realmente mostra
const formattedValue = ref(formatValue(props.modelValue));

/**
 * O v-model (props.modelValue) é a fonte da verdade.
 * Se ele mudar (ex: ao carregar dados da API), atualizamos o input.
 */
watch(() => props.modelValue, (newValue) => {
  formattedValue.value = formatValue(newValue);
});

/**
 * Quando o utilizador digita, limpamos o valor, emitimos o número puro,
 * e reformatamos o input.
 */
const handleInput = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const cursorPosition = input.selectionStart; // Salva a posição do cursor
  
  const numericValue = parseValue(input.value);
  
  // Emite o valor numérico puro para o v-model
  emit('update:modelValue', numericValue);

  // O 'watch' acima irá reformatar o 'formattedValue.value'
  
  // Truque para reposicionar o cursor corretamente após a reformatação
  // (Necessário porque o Vue atualiza o DOM)
  if (inputRef.value && cursorPosition !== null) {
      const originalLength = input.value.length;
      
      // Espera o Vue atualizar o DOM com o novo 'formattedValue'
      requestAnimationFrame(() => {
          const newLength = formattedValue.value.length;
          const newCursorPosition = cursorPosition + (newLength - originalLength);
          
          // Define a posição do cursor, ajustada para o final se necessário
          inputRef.value?.setSelectionRange(newCursorPosition, newCursorPosition);
      });
  }
};

/**
 * Quando o utilizador sai do campo, reformatamos para garantir
 * que esteja limpo (ex: se ele deixar "R$ 123", o blur formata para "R$ 123,00")
 */
const handleBlur = () => {
  formattedValue.value = formatValue(props.modelValue);
};

/**
 * Garante que, ao montar, o valor inicial seja formatado.
 */
onMounted(() => {
    formattedValue.value = formatValue(props.modelValue);
});

</script>
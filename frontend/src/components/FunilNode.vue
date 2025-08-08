<template>
  <div
    :style="{
      border: '2px solid ' + cor,
      borderRadius: '8px',
      padding: '8px',
      background: 'white',
      minWidth: '180px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    }"
  >
    <h4 :style="{ color: cor, fontWeight: 'bold', margin: 0 }">{{ titulo }}</h4>
    <ul style="margin-top: 8px; padding: 0; list-style: none; max-height: 200px; overflow-y: auto;">
      <li
        v-for="op in oportunidades"
        :key="op.id"
        style="padding: 4px; border-bottom: 1px solid #eee; font-size: 0.9em;"
      >
        {{ op.titulo }}
        <span style="float: right; color: green; font-weight: bold;">
          {{ formatarValor(op.valor_estimado) }}
        </span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps<{
  titulo: string
  cor: string
  oportunidades: any[]
}>()

function formatarValor(valor: number | null) {
  if (!valor) return 'R$ -'
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
</script>

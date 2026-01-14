<template>
  <div 
    class="relative flex items-center justify-between p-5 bg-white border border-gray-100 rounded-xl shadow-sm transition-all duration-300 hover:shadow-md hover:-translate-y-1 cursor-pointer group"
    @click="$emit('click')"
  >
    <div class="flex flex-col z-10">
      <span class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">
        {{ title }}
      </span>
      <div class="flex items-baseline gap-2">
        <h3 class="text-2xl font-bold text-gray-800 leading-none">
          {{ value }}
        </h3>
        <span 
          v-if="trend !== undefined" 
          class="text-xs font-bold px-1.5 py-0.5 rounded-full"
          :class="trend >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
        >
          <i :class="trend >= 0 ? 'fas fa-arrow-up text-[10px]' : 'fas fa-arrow-down text-[10px]'"></i>
          {{ Math.abs(trend) }}%
        </span>
      </div>
    </div>

    <div 
      class="flex items-center justify-center w-12 h-12 rounded-lg transition-colors duration-300"
      :class="colorClasses[color || 'primary']"
    >
      <slot name="icon">
        <i class="fas fa-chart-line text-xl"></i>
      </slot>
    </div>

    <div class="absolute -right-4 -bottom-4 opacity-5 pointer-events-none transform rotate-12 transition-transform group-hover:scale-110">
      <slot name="bg-icon"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string;
  value: string | number;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'purple' | 'info';
  trend?: number;
}>();

defineEmits(['click']);

const colorClasses = {
  primary: 'bg-blue-50 text-blue-600 group-hover:bg-blue-100',
  success: 'bg-emerald-50 text-emerald-600 group-hover:bg-emerald-100',
  warning: 'bg-amber-50 text-amber-600 group-hover:bg-amber-100',
  danger: 'bg-rose-50 text-rose-600 group-hover:bg-rose-100',
  purple: 'bg-purple-50 text-purple-600 group-hover:bg-purple-100',
  info: 'bg-cyan-50 text-cyan-600 group-hover:bg-cyan-100'
};
</script>
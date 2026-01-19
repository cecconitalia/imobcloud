<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  title: string;
  value: number | string;
  icon: string;
  color: 'blue' | 'emerald' | 'purple' | 'amber' | 'rose';
  loading?: boolean;
  isMoney?: boolean;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
}>();

const formatValue = (val: number | string) => {
  if (props.isMoney) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(val));
  }
  return val;
};

const colorClasses = computed(() => {
  const map = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
    emerald: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
    amber: 'bg-amber-50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400',
    rose: 'bg-rose-50 text-rose-600 dark:bg-rose-900/20 dark:text-rose-400',
  };
  return map[props.color] || map.blue;
});
</script>

<template>
  <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 transition-all hover:shadow-md">
    <div class="flex justify-between items-start">
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ title }}</p>
        
        <div v-if="loading" class="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded mt-2 animate-pulse"></div>
        
        <h3 v-else class="text-2xl font-bold text-gray-800 dark:text-white mt-1">
          {{ formatValue(value) }}
        </h3>
      </div>
      
      <div :class="['p-3 rounded-xl', colorClasses]">
        <div :class="[icon, 'text-xl']"></div>
      </div>
    </div>

    <div v-if="trend && !loading" class="mt-4 flex items-center text-xs font-medium">
      <span 
        :class="{
          'text-emerald-500': trendDirection === 'up',
          'text-rose-500': trendDirection === 'down',
          'text-gray-400': trendDirection === 'neutral'
        }"
        class="flex items-center gap-1"
      >
        <div v-if="trendDirection === 'up'" class="i-mdi-arrow-up"></div>
        <div v-if="trendDirection === 'down'" class="i-mdi-arrow-down"></div>
        {{ trend }}
      </span>
      <span class="text-gray-400 ml-1">vs. período anterior</span>
    </div>
  </div>
</template>
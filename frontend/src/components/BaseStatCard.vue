<template>
  <div
    class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition-all duration-150 hover:border-blue-500"
  >
    <div class="flex items-center justify-between">
      <dt class="text-sm font-medium text-slate-500">
        {{ title }}
      </dt>
      
      <dd class_name="text-slate-400">
        <slot name="icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </slot>
      </dd>
    </div>
    
    <div class="mt-1">
      <p class="text-3xl font-bold text-slate-900">
        {{ value }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  value: string | number
}>()
</script>
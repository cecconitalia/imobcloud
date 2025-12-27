<template>
  <div class="stat-card" :class="color || 'primary'">
    <div class="stat-icon">
      <slot name="icon"><i class="fas fa-chart-line"></i></slot>
    </div>
    <div class="stat-details">
      <p class="stat-label">{{ title }}</p>
      <h3 class="stat-value">{{ value }}</h3>
    </div>
    <div v-if="trend !== undefined" class="stat-trend" :class="trend >= 0 ? 'up' : 'down'">
      <i :class="trend >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
      {{ Math.abs(trend) }}%
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  value: string | number;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  trend?: number;
}>();
</script>

<style scoped>
.stat-card {
  background: #ffffff;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.stat-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  margin: 0;
  letter-spacing: 0.025em;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.stat-trend {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-trend.up { background: #f0fdf4; color: #16a34a; }
.stat-trend.down { background: #fef2f2; color: #ef4444; }

/* Colors */
.primary .stat-icon { background: #eef2ff; color: #4f46e5; }
.success .stat-icon { background: #ecfdf5; color: #10b981; }
.warning .stat-icon { background: #fffbeb; color: #f59e0b; }
.danger .stat-icon  { background: #fef2f2; color: #ef4444; }
.info .stat-icon    { background: #ecfeff; color: #06b6d4; }
</style>
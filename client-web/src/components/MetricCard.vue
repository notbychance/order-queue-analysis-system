<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    value: string
    unit?: string
    description?: string
    accent?: 'default' | 'success' | 'warning' | 'error'
  }>(),
  {
    unit: '',
    description: '',
    accent: 'default',
  },
)
</script>

<template>
  <n-card size="small" embedded class="metric-card" :class="`metric-card--${accent}`">
    <div class="metric-card__label">{{ label }}</div>
    <div class="metric-card__value">
      <span>{{ value }}</span>
      <small v-if="unit">{{ unit }}</small>
    </div>
    <div v-if="description" class="metric-card__description">
      {{ description }}
    </div>
  </n-card>
</template>

<style scoped>
.metric-card {
  height: 100%;
  border-radius: 18px;
}

.metric-card__label {
  color: var(--color-text-muted);
  font-size: 0.86rem;
  font-weight: 600;
}

.metric-card__value {
  display: flex;
  gap: 6px;
  align-items: baseline;
  margin-top: 8px;
  color: var(--color-heading);
}

.metric-card__value span {
  font-size: 1.55rem;
  font-weight: 800;
  line-height: 1.1;
}

.metric-card__value small {
  color: var(--color-text-muted);
  font-size: 0.82rem;
}

.metric-card__description {
  margin-top: 8px;
  color: var(--color-text-muted);
  font-size: 0.82rem;
  line-height: 1.4;
}

.metric-card--success {
  border-color: rgba(24, 160, 88, 0.35);
}

.metric-card--warning {
  border-color: rgba(240, 160, 32, 0.4);
}

.metric-card--error {
  border-color: rgba(208, 48, 80, 0.35);
}
</style>

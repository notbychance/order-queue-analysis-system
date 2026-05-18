<script setup lang="ts">
import type { QueueFormulasResponse } from '@/types/queue'

defineProps<{
  formulas: QueueFormulasResponse | null
  loading?: boolean
}>()

const formulaTitles: Record<string, string> = {
  utilization: 'Коэффициент загрузки',
  average_orders_in_system: 'Среднее число заказов в системе',
  average_waiting_time: 'Среднее время ожидания',
  average_time_in_system: 'Среднее время в системе',
}
</script>

<template>
  <n-card title="Формулы модели" class="formula-card">
    <n-spin :show="loading">
      <n-empty v-if="!formulas" description="Формулы еще не загружены" />

      <template v-else>
        <n-alert type="info" :show-icon="true" class="formula-card__intro">
          <strong>{{ formulas.model_name }}</strong> — {{ formulas.description }}
          Условие устойчивости: <strong>{{ formulas.stability_condition }}</strong>.
        </n-alert>

        <div class="formula-grid">
          <n-card
            v-for="(formula, key) in formulas.formulas"
            :key="key"
            size="small"
            embedded
            class="formula-item"
          >
            <div class="formula-item__title">
              {{ formulaTitles[key] ?? key }}
            </div>
            <code>{{ formula }}</code>
          </n-card>
        </div>
      </template>
    </n-spin>
  </n-card>
</template>

<style scoped>
.formula-card,
.formula-item {
  border-radius: var(--app-radius-card);
}

.formula-card__intro {
  margin-bottom: 16px;
}

.formula-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.formula-item__title {
  margin-bottom: 8px;
  color: var(--color-text-muted);
  font-size: 0.88rem;
  font-weight: 700;
}

.formula-item code {
  display: block;
  max-width: 100%;
  padding: 12px;
  overflow-x: auto;
  color: var(--color-heading);
  font-size: 1.05rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  white-space: nowrap;
}

@media (max-width: 760px) {
  .formula-grid {
    grid-template-columns: 1fr;
  }
}
</style>

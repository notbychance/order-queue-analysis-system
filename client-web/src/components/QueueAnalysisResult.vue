<script setup lang="ts">
import { computed } from 'vue'

import QueueAnalysisChart from '@/components/QueueAnalysisChart.vue'
import type { QueueAnalysisResponse } from '@/types/queue'

const props = defineProps<{
  result: QueueAnalysisResponse
}>()

const stabilityType = computed(() => (props.result.is_stable ? 'success' : 'error'))
const stabilityText = computed(() => (props.result.is_stable ? 'Система устойчива' : 'Система неустойчива'))

function formatNumber(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '—'
  }

  return new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: digits,
  }).format(value)
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '—'
  }

  return `${formatNumber(value, 2)} %`
}
</script>

<template>
  <section class="queue-result">
    <n-card class="queue-result__summary" :bordered="false">
      <template #header>
        <div class="queue-result__header">
          <div>
            <div class="queue-result__title">Результаты анализа</div>
            <div class="queue-result__subtitle">
              λ = {{ formatNumber(result.lambda_rate) }} {{ result.arrival_rate_unit }},
              μ = {{ formatNumber(result.mu_rate) }} {{ result.service_rate_unit }}
            </div>
          </div>

          <n-tag :type="stabilityType" round>
            {{ stabilityText }}
          </n-tag>
        </div>
      </template>

      <n-grid :cols="4" :x-gap="12" :y-gap="12" responsive="screen">
        <n-gi>
          <div class="queue-result__metric">
            <span class="queue-result__metric-label">Загрузка клерка</span>
            <strong>{{ formatPercent(result.utilization_percent) }}</strong>
            <small>ρ = {{ formatNumber(result.utilization) }}</small>
          </div>
        </n-gi>

        <n-gi>
          <div class="queue-result__metric">
            <span class="queue-result__metric-label">Среднее число заказов</span>
            <strong>{{ formatNumber(result.average_orders_in_system) }}</strong>
            <small>L, заказов в системе</small>
          </div>
        </n-gi>

        <n-gi>
          <div class="queue-result__metric">
            <span class="queue-result__metric-label">Ожидание обработки</span>
            <strong>{{ formatNumber(result.average_waiting_time_hours) }} ч</strong>
            <small>Wq = {{ formatNumber(result.average_waiting_time) }} {{ result.time_unit }}</small>
          </div>
        </n-gi>

        <n-gi>
          <div class="queue-result__metric">
            <span class="queue-result__metric-label">Время в системе</span>
            <strong>{{ formatNumber(result.average_time_in_system_hours) }} ч</strong>
            <small>W = {{ formatNumber(result.average_time_in_system) }} {{ result.time_unit }}</small>
          </div>
        </n-gi>
      </n-grid>

      <n-alert class="queue-result__conclusion" :type="stabilityType" :bordered="false">
        {{ result.conclusion }}
      </n-alert>
    </n-card>

    <QueueAnalysisChart :result="result" />
  </section>
</template>

<style scoped>
.queue-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.queue-result__summary {
  border: 1px solid var(--app-border-color);
  background: var(--app-card-bg);
}

.queue-result__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.queue-result__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text-color);
}

.queue-result__subtitle {
  margin-top: 4px;
  color: var(--app-text-muted-color);
  font-size: 14px;
}

.queue-result__metric {
  min-height: 118px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 8px;
  padding: 16px;
  border: 1px solid var(--app-border-color);
  border-radius: 16px;
  background: var(--app-soft-bg);
}

.queue-result__metric-label {
  color: var(--app-text-muted-color);
  font-size: 13px;
}

.queue-result__metric strong {
  color: var(--app-text-color);
  font-size: 24px;
  line-height: 1.15;
}

.queue-result__metric small {
  color: var(--app-text-muted-color);
  font-size: 12px;
}

.queue-result__conclusion {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .queue-result__header {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>

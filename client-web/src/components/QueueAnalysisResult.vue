<script setup lang="ts">
import MetricCard from './MetricCard.vue'
import { formatHours, formatNumber, formatPercent } from '@/utils/formatters'
import type { QueueAnalysisResponse } from '@/types/queue'

defineProps<{
  result: QueueAnalysisResponse | null
}>()
</script>

<template>
  <n-card title="Результаты анализа" class="result-card">
    <n-empty v-if="!result" description="Введите параметры и выполните расчет" />

    <template v-else>
      <n-result
        :status="result.is_stable ? 'success' : 'warning'"
        :title="result.is_stable ? 'Система устойчива' : 'Система неустойчива'"
        :description="result.conclusion"
        class="result-summary"
      />

      <n-grid :cols="3" :x-gap="14" :y-gap="14" item-responsive responsive="screen">
        <n-grid-item>
          <MetricCard
            label="Коэффициент загрузки"
            :value="formatPercent(result.utilization_percent, 2)"
            description="Доля времени, когда клерк занят обработкой заказов"
            :accent="result.is_stable ? 'success' : 'warning'"
          />
        </n-grid-item>

        <n-grid-item>
          <MetricCard
            label="Среднее число заказов в системе"
            :value="formatNumber(result.average_orders_in_system, 3)"
            unit="заказов"
            description="Очередь вместе с заказом, который уже обслуживается"
          />
        </n-grid-item>

        <n-grid-item>
          <MetricCard
            label="Среднее время ожидания"
            :value="formatHours(result.average_waiting_time_hours, 2)"
            description="Время до начала обработки заказа клерком"
          />
        </n-grid-item>

        <n-grid-item>
          <MetricCard
            label="Среднее время в системе"
            :value="formatHours(result.average_time_in_system_hours, 2)"
            description="Ожидание в очереди плюс время обработки"
          />
        </n-grid-item>

        <n-grid-item>
          <MetricCard
            label="Wq в днях"
            :value="formatNumber(result.average_waiting_time, 6)"
            :unit="result.time_unit"
            description="Значение для пояснительной записки"
          />
        </n-grid-item>

        <n-grid-item>
          <MetricCard
            label="W в днях"
            :value="formatNumber(result.average_time_in_system, 6)"
            :unit="result.time_unit"
            description="Полное время пребывания заказа в системе"
          />
        </n-grid-item>
      </n-grid>
    </template>
  </n-card>
</template>

<style scoped>
.result-card {
  border-radius: 20px;
}

.result-summary {
  padding-top: 0;
}
</style>

<script setup lang="ts">
import { formatDateTime, formatNumber, formatPercent } from '@/utils/formatters'
import type { QueueHistoryItem } from '@/types/history'

withDefaults(
  defineProps<{
    items: QueueHistoryItem[]
    compact?: boolean
    showClear?: boolean
  }>(),
  {
    compact: false,
    showClear: true,
  },
)

const emit = defineEmits<{
  repeat: [id: string]
  remove: [id: string]
  clear: []
}>()
</script>

<template>
  <n-card class="history-list-card" :title="compact ? 'История' : 'История расчетов'">
    <template #header-extra>
      <n-button v-if="showClear && items.length > 0" size="small" tertiary type="error" @click="emit('clear')">
        Очистить
      </n-button>
    </template>

    <n-empty v-if="items.length === 0" description="История расчетов пока пуста" />

    <n-space v-else vertical :size="compact ? 10 : 14">
      <n-card v-for="item in items" :key="item.id" size="small" embedded class="history-row">
        <div class="history-row__header">
          <div class="history-row__main">
            <div class="history-row__params">
              λ = {{ formatNumber(item.request.lambda_rate) }}, μ = {{ formatNumber(item.request.mu_rate) }}
            </div>
            <div class="history-row__date">{{ formatDateTime(item.createdAt) }}</div>
          </div>

          <n-tag :type="item.response.is_stable ? 'success' : 'warning'" round>
            {{ item.response.is_stable ? 'устойчива' : 'неустойчива' }}
          </n-tag>
        </div>

        <div v-if="!compact" class="history-row__metrics">
          <div>
            <span>Загрузка</span>
            <strong>{{ formatPercent(item.response.utilization_percent, 2) }}</strong>
          </div>
          <div>
            <span>L</span>
            <strong>{{ formatNumber(item.response.average_orders_in_system, 3) }}</strong>
          </div>
          <div>
            <span>Wq</span>
            <strong>{{ formatNumber(item.response.average_waiting_time_hours, 2) }} ч</strong>
          </div>
          <div>
            <span>W</span>
            <strong>{{ formatNumber(item.response.average_time_in_system_hours, 2) }} ч</strong>
          </div>
        </div>

        <p v-if="!compact" class="history-row__conclusion">
          {{ item.response.conclusion }}
        </p>

        <div class="history-row__actions">
          <n-button size="small" type="primary" secondary @click="emit('repeat', item.id)">
            Повторить расчет
          </n-button>
          <n-button size="small" tertiary type="error" @click="emit('remove', item.id)">
            Удалить
          </n-button>
        </div>
      </n-card>
    </n-space>
  </n-card>
</template>

<style scoped>
.history-list-card,
.history-row {
  border-radius: var(--app-radius-card);
}

.history-row__header {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: space-between;
}

.history-row__main {
  min-width: 0;
}

.history-row__params {
  color: var(--color-heading);
  font-weight: 800;
  overflow-wrap: anywhere;
}

.history-row__date {
  margin-top: 4px;
  color: var(--color-text-muted);
  font-size: 0.84rem;
}

.history-row__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.history-row__metrics div {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--color-surface);
}

.history-row__metrics span {
  display: block;
  color: var(--color-text-muted);
  font-size: 0.78rem;
}

.history-row__metrics strong {
  display: block;
  margin-top: 4px;
  color: var(--color-heading);
  font-size: 1rem;
  overflow-wrap: anywhere;
}

.history-row__conclusion {
  margin: 14px 0 0;
  color: var(--color-text);
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.history-row__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

@media (max-width: 820px) {
  .history-row__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .history-row__header {
    align-items: stretch;
    flex-direction: column;
  }

  .history-row__metrics {
    grid-template-columns: 1fr;
  }

  .history-row__actions {
    align-items: stretch;
    flex-direction: column;
  }

  .history-row__actions :deep(.n-button) {
    width: 100%;
  }
}
</style>

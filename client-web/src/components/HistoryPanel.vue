<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import HistoryFileActions from '@/components/HistoryFileActions.vue'
import { useQueueAnalysisStore } from '@/stores/queueAnalysisStore'

withDefaults(
  defineProps<{
    drawerMode?: boolean
  }>(),
  {
    drawerMode: false,
  },
)

const emit = defineEmits<{
  repeat: []
}>()

const router = useRouter()
const queueStore = useQueueAnalysisStore()

const lastHistoryItems = computed(() => queueStore.history.slice(0, 5))

function formatNumber(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—'
  }

  return new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: digits,
  }).format(value)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

async function repeatHistoryItem(id: string): Promise<void> {
  await queueStore.repeatHistoryItem(id)
  await router.push({ name: 'analysis' })
  emit('repeat')
}
</script>

<template>
  <n-card
    title="Локальная история"
    size="small"
    :bordered="false"
    class="history-card"
    :class="{ 'history-card--drawer': drawerMode }"
  >
    <template #header-extra>
      <HistoryFileActions />
    </template>

    <n-empty
      v-if="lastHistoryItems.length === 0"
      description="История расчетов пока пуста"
      size="small"
    />

    <n-space v-else vertical :size="12">
      <n-card
        v-for="item in lastHistoryItems"
        :key="item.id"
        size="small"
        embedded
        class="history-item"
      >
        <div class="history-item__top">
          <div class="history-item__main">
            <div class="history-item__params">
              λ = {{ formatNumber(item.request.lambda_rate) }},
              μ = {{ formatNumber(item.request.mu_rate) }}
            </div>
            <div class="history-item__date">{{ formatDate(item.createdAt) }}</div>
          </div>

          <n-tag size="small" :type="item.response.is_stable ? 'success' : 'error'" round>
            {{ item.response.is_stable ? 'устойчива' : 'неустойчива' }}
          </n-tag>
        </div>

        <div class="history-item__metrics">
          <span>Загрузка:</span>
          <strong>{{ formatNumber(item.response.utilization_percent, 2) }}%</strong>
        </div>

        <div class="history-item__actions">
          <n-button size="tiny" type="primary" secondary @click="repeatHistoryItem(item.id)">
            Повторить
          </n-button>
          <n-button
            size="tiny"
            tertiary
            type="error"
            @click="queueStore.removeHistoryItem(item.id)"
          >
            Удалить
          </n-button>
        </div>
      </n-card>
    </n-space>
  </n-card>
</template>

<style scoped>
.history-card {
  height: 100%;
  border-radius: 0;
}

.history-card--drawer {
  height: auto;
}

.history-item {
  border-radius: 16px;
}

.history-item__top {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: space-between;
}

.history-item__main {
  min-width: 0;
}

.history-item__params {
  color: var(--color-heading);
  font-weight: 700;
  overflow-wrap: anywhere;
}

.history-item__date {
  margin-top: 4px;
  color: var(--color-text-muted);
  font-size: 0.82rem;
}

.history-item__metrics {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
  color: var(--color-text);
}

.history-item__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

@media (max-width: 420px) {
  .history-item__top {
    align-items: stretch;
    flex-direction: column;
  }

  .history-item__actions :deep(.n-button) {
    flex: 1 1 120px;
  }
}
</style>

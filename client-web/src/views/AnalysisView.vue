<script setup lang="ts">
import { computed } from 'vue'
import { useMessage } from 'naive-ui'

import PageHeader from '@/components/PageHeader.vue'
import QueueAnalysisForm from '@/components/QueueAnalysisForm.vue'
import QueueAnalysisResult from '@/components/QueueAnalysisResult.vue'
import { useQueueAnalysisStore } from '@/stores/queueAnalysisStore'
import type { QueueAnalysisRequest } from '@/types/queue'

const message = useMessage()
const queueStore = useQueueAnalysisStore()

const result = computed(() => queueStore.lastResult)

async function analyze(request: QueueAnalysisRequest): Promise<void> {
  try {
    await queueStore.analyzeQueue(request)
    message.success('Анализ выполнен. Результат добавлен в локальную историю.')
  } catch {
    message.error(queueStore.errorMessage ?? 'Не удалось выполнить анализ системы')
  }
}

function resetResult(): void {
  queueStore.clearError()
}
</script>

<template>
  <section class="analysis-view responsive-page">
    <PageHeader
      title="Анализ одноканальной системы обслуживания"
      subtitle="Введите интенсивность поступления заказов λ и интенсивность обслуживания μ. Сервер FastAPI выполнит расчет модели M/M/1, а результат сохранится в локальную историю браузера."
    />

    <div class="analysis-view__grid">
      <QueueAnalysisForm :loading="queueStore.isLoading" @submit="analyze" @reset="resetResult" />

      <QueueAnalysisResult v-if="result" :result="result" />
      <n-card v-else title="Результат анализа" class="analysis-view__empty-result">
        <n-empty description="Введите параметры системы и выполните расчет" />
      </n-card>
    </div>
  </section>
</template>

<style scoped>
.analysis-view {
  --page-max-width: 1280px;
}

.analysis-view__grid {
  display: grid;
  grid-template-columns: minmax(320px, 0.85fr) minmax(0, 1.15fr);
  gap: 20px;
  align-items: start;
}

.analysis-view__empty-result {
  border-radius: var(--app-radius-card);
}

@media (max-width: 1180px) {
  .analysis-view__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .analysis-view__grid {
    gap: 14px;
  }
}
</style>

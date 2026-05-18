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
  <section class="analysis-view">
    <PageHeader
      title="Анализ одноканальной системы обслуживания"
      subtitle="Введите интенсивность поступления заказов λ и интенсивность обслуживания μ. Сервер FastAPI выполнит расчет модели M/M/1, а результат сохранится в локальную историю браузера."
    />

    <n-grid :cols="2" :x-gap="20" :y-gap="20" item-responsive responsive="screen">
      <n-grid-item>
        <QueueAnalysisForm :loading="queueStore.isLoading" @submit="analyze" @reset="resetResult" />
      </n-grid-item>

      <n-grid-item>
        <QueueAnalysisResult v-if="result" :result="result" />
        <n-card v-else title="Результат анализа">
          <n-empty description="Введите параметры системы и выполните расчет" />
        </n-card>
      </n-grid-item>
    </n-grid>
  </section>
</template>

<style scoped>
.analysis-view {
  max-width: 1280px;
  margin: 0 auto;
}
</style>

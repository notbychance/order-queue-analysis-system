<script setup lang="ts">
import { computed } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'

import HistoryFileActions from '@/components/HistoryFileActions.vue'
import HistoryList from '@/components/HistoryList.vue'
import PageHeader from '@/components/PageHeader.vue'
import { useQueueAnalysisStore } from '@/stores/queueAnalysisStore'

const router = useRouter()
const dialog = useDialog()
const message = useMessage()
const queueStore = useQueueAnalysisStore()

const history = computed(() => queueStore.history)

async function repeatItem(id: string): Promise<void> {
  try {
    await queueStore.repeatHistoryItem(id)
    await router.push({ name: 'analysis' })
    message.success('Расчет повторен')
  } catch {
    message.error(queueStore.errorMessage ?? 'Не удалось повторить расчет')
  }
}

function removeItem(id: string): void {
  queueStore.removeHistoryItem(id)
  message.success('Запись удалена')
}

function confirmClearHistory(): void {
  dialog.warning({
    title: 'Очистить историю?',
    content: 'Все локальные записи расчетов будут удалены из браузера.',
    positiveText: 'Очистить',
    negativeText: 'Отмена',
    onPositiveClick: () => {
      queueStore.clearHistory()
      message.success('История очищена')
    },
  })
}
</script>

<template>
  <section class="history-view">
    <PageHeader
      title="Локальная история расчетов"
      subtitle="История хранится только в браузере через Pinia и localStorage. Сервер FastAPI не сохраняет расчеты."
    >
      <template #extra>
        <HistoryFileActions />
      </template>
    </PageHeader>

    <HistoryList
      :items="history"
      @repeat="repeatItem"
      @remove="removeItem"
      @clear="confirmClearHistory"
    />
  </section>
</template>

<style scoped>
.history-view {
  max-width: 1120px;
  margin: 0 auto;
}
</style>

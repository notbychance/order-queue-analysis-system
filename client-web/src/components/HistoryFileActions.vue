<script setup lang="ts">
import { ref } from 'vue'
import { useMessage } from 'naive-ui'

import { useQueueAnalysisStore } from '@/stores/queueAnalysisStore'

const queueStore = useQueueAnalysisStore()
const message = useMessage()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isImporting = ref(false)

function openImportDialog(): void {
  fileInputRef.value?.click()
}

function exportHistory(): void {
  try {
    queueStore.exportHistoryToFile()
    message.success('Файл истории сформирован')
  } catch (error) {
    message.warning(error instanceof Error ? error.message : 'Не удалось экспортировать историю')
  }
}

async function handleFileChange(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) {
    return
  }

  isImporting.value = true

  try {
    const result = await queueStore.importHistoryFromFile(file, 'append')

    message.success(
      `Импортировано записей: ${result.importedCount}. Пропущено дублей: ${result.skippedCount}.`,
    )
  } catch (error) {
    message.error(error instanceof Error ? error.message : 'Не удалось импортировать историю')
  } finally {
    isImporting.value = false
    input.value = ''
  }
}
</script>

<template>
  <n-space :size="6" wrap>
    <n-button size="tiny" secondary :disabled="!queueStore.hasHistory" @click="exportHistory">
      Экспорт
    </n-button>

    <n-button size="tiny" secondary :loading="isImporting" @click="openImportDialog">
      Импорт
    </n-button>

    <n-button
      size="tiny"
      tertiary
      type="error"
      :disabled="!queueStore.hasHistory"
      @click="queueStore.clearHistory"
    >
      Очистить
    </n-button>

    <input
      ref="fileInputRef"
      class="history-file-input"
      type="file"
      accept="application/json,.json"
      @change="handleFileChange"
    />
  </n-space>
</template>

<style scoped>
.history-file-input {
  display: none;
}
</style>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'

import FormulaList from '@/components/FormulaList.vue'
import PageHeader from '@/components/PageHeader.vue'
import { useQueueAnalysisStore } from '@/stores/queueAnalysisStore'

const message = useMessage()
const queueStore = useQueueAnalysisStore()

const formulas = computed(() => queueStore.formulas)

async function loadFormulas(): Promise<void> {
  try {
    await queueStore.loadFormulas()
  } catch {
    message.error(queueStore.errorMessage ?? 'Не удалось загрузить формулы')
  }
}

onMounted(async () => {
  if (!queueStore.formulas) {
    await loadFormulas()
  }
})
</script>

<template>
  <section class="formulas-view">
    <PageHeader
      title="Математическая модель"
      subtitle="Сервер возвращает формулы модели M/M/1, которые используются при анализе работы конторы с одним клерком."
    >
      <template #extra>
        <n-button :loading="queueStore.isLoadingFormulas" secondary @click="loadFormulas">
          Обновить формулы
        </n-button>
      </template>
    </PageHeader>

    <FormulaList :formulas="formulas" :loading="queueStore.isLoadingFormulas" />
  </section>
</template>

<style scoped>
.formulas-view {
  max-width: 1040px;
  margin: 0 auto;
}
</style>

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { QueueAnalysisRequest } from '@/types/queue'

const props = withDefaults(
  defineProps<{
    loading?: boolean
    initialLambda?: number | null
    initialMu?: number | null
  }>(),
  {
    loading: false,
    initialLambda: null,
    initialMu: null,
  },
)

const emit = defineEmits<{
  submit: [request: QueueAnalysisRequest]
  reset: []
}>()

const lambdaRate = ref<number | null>(props.initialLambda)
const muRate = ref<number | null>(props.initialMu)

const validationMessage = computed(() => {
  if (lambdaRate.value === null || muRate.value === null) {
    return 'Заполните оба параметра системы.'
  }

  if (lambdaRate.value < 0) {
    return 'Интенсивность поступления λ не может быть отрицательной.'
  }

  if (muRate.value <= 0) {
    return 'Интенсивность обслуживания μ должна быть больше нуля.'
  }

  return null
})

const stabilityWarning = computed(() => {
  if (lambdaRate.value === null || muRate.value === null || muRate.value <= 0) {
    return null
  }

  if (lambdaRate.value >= muRate.value) {
    return 'При λ ≥ μ система неустойчива: очередь будет расти неограниченно.'
  }

  return null
})

const canSubmit = computed(() => validationMessage.value === null && !props.loading)

function clearForm(): void {
  lambdaRate.value = null
  muRate.value = null
  emit('reset')
}

function submitForm(): void {
  if (!canSubmit.value || lambdaRate.value === null || muRate.value === null) {
    return
  }

  emit('submit', {
    lambda_rate: lambdaRate.value,
    mu_rate: muRate.value,
  })
}
</script>

<template>
  <n-card title="Параметры системы" class="analysis-form-card">
    <template #header-extra>
      <n-tag type="info" round>M/M/1</n-tag>
    </template>

    <n-form label-placement="top" @submit.prevent="submitForm">
      <div class="analysis-form-card__grid">
        <n-form-item label="Интенсивность поступления λ" path="lambdaRate">
          <n-input-number
            v-model:value="lambdaRate"
            class="full-width"
            :min="0"
            :precision="3"
            :show-button="true"
            placeholder="Введите λ"
          >
            <template #suffix>заказов/день</template>
          </n-input-number>
        </n-form-item>

        <n-form-item label="Интенсивность обслуживания μ" path="muRate">
          <n-input-number
            v-model:value="muRate"
            class="full-width"
            :min="0.001"
            :precision="3"
            :show-button="true"
            placeholder="Введите μ"
          >
            <template #suffix>заказов/день</template>
          </n-input-number>
        </n-form-item>
      </div>

      <n-alert v-if="validationMessage" type="error" :show-icon="true" class="form-alert">
        {{ validationMessage }}
      </n-alert>

      <n-alert v-else-if="stabilityWarning" type="warning" :show-icon="true" class="form-alert">
        {{ stabilityWarning }} Сервер все равно выполнит анализ и вернет заключение.
      </n-alert>

      <div class="form-actions">
        <n-button type="primary" attr-type="submit" :loading="loading" :disabled="!canSubmit">
          Рассчитать
        </n-button>
        <n-button tertiary @click="clearForm">Очистить</n-button>
      </div>
    </n-form>
  </n-card>
</template>

<style scoped>
.analysis-form-card {
  border-radius: var(--app-radius-card);
}

.analysis-form-card__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 18px;
}

.full-width {
  width: 100%;
}

.form-alert {
  margin-top: 4px;
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

@media (max-width: 640px) {
  .analysis-form-card__grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .form-actions :deep(.n-button) {
    width: 100%;
  }
}
</style>

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { QueueAnalysisResponse } from '@/types/queue'

type ChartMetric = 'orders' | 'waitingTime' | 'systemTime'

type ChartPoint = {
  lambdaRate: number
  value: number
  label: string
}

const props = defineProps<{
  result: QueueAnalysisResponse
}>()

const selectedMetric = ref<ChartMetric>('orders')

const chartWidth = 720
const chartHeight = 300
const paddingLeft = 56
const paddingRight = 24
const paddingTop = 24
const paddingBottom = 44
const plotWidth = chartWidth - paddingLeft - paddingRight
const plotHeight = chartHeight - paddingTop - paddingBottom

const metricConfig = computed(() => {
  switch (selectedMetric.value) {
    case 'waitingTime':
      return {
        title: 'Среднее время ожидания начала обработки',
        shortTitle: 'Wq',
        unit: 'ч',
        getValue: (lambdaRate: number, muRate: number) =>
          (lambdaRate / (muRate * (muRate - lambdaRate))) * 24,
      }
    case 'systemTime':
      return {
        title: 'Среднее время пребывания заказа в системе',
        shortTitle: 'W',
        unit: 'ч',
        getValue: (lambdaRate: number, muRate: number) => (1 / (muRate - lambdaRate)) * 24,
      }
    case 'orders':
    default:
      return {
        title: 'Среднее число заказов в системе',
        shortTitle: 'L',
        unit: 'заказов',
        getValue: (lambdaRate: number, muRate: number) => lambdaRate / (muRate - lambdaRate),
      }
  }
})

const canBuildChart = computed(() => props.result.mu_rate > 0)

const points = computed<ChartPoint[]>(() => {
  if (!canBuildChart.value) {
    return []
  }

  const muRate = props.result.mu_rate
  const maxLambdaRate = muRate * 0.95
  const pointCount = 40

  return Array.from({ length: pointCount + 1 }, (_, index) => {
    const lambdaRate = (maxLambdaRate / pointCount) * index
    const value = metricConfig.value.getValue(lambdaRate, muRate)

    return {
      lambdaRate,
      value,
      label: `λ = ${formatNumber(lambdaRate)}`,
    }
  })
})

const maxValue = computed(() => {
  const values = points.value.map((point) => point.value).filter(Number.isFinite)
  const max = Math.max(...values, 1)

  return max <= 0 ? 1 : max
})

const linePoints = computed(() => {
  if (points.value.length === 0) {
    return ''
  }

  const maxLambdaRate = props.result.mu_rate * 0.95

  return points.value
    .map((point) => {
      const x = paddingLeft + (point.lambdaRate / maxLambdaRate) * plotWidth
      const y = paddingTop + plotHeight - (point.value / maxValue.value) * plotHeight

      return `${roundSvg(x)},${roundSvg(y)}`
    })
    .join(' ')
})

const currentMarker = computed(() => {
  if (!canBuildChart.value || props.result.lambda_rate < 0) {
    return null
  }

  const maxLambdaRate = props.result.mu_rate * 0.95
  const markerLambda = Math.min(props.result.lambda_rate, maxLambdaRate)
  const x = paddingLeft + (markerLambda / maxLambdaRate) * plotWidth

  return {
    x: roundSvg(x),
    label: props.result.lambda_rate >= props.result.mu_rate ? 'λ ≥ μ' : `λ = ${formatNumber(props.result.lambda_rate)}`,
  }
})

const yAxisTicks = computed(() => {
  const tickCount = 4

  return Array.from({ length: tickCount + 1 }, (_, index) => {
    const value = (maxValue.value / tickCount) * index
    const y = paddingTop + plotHeight - (value / maxValue.value) * plotHeight

    return {
      value,
      y: roundSvg(y),
      label: formatNumber(value),
    }
  })
})

const xAxisTicks = computed(() => {
  const tickCount = 4
  const maxLambdaRate = props.result.mu_rate * 0.95

  return Array.from({ length: tickCount + 1 }, (_, index) => {
    const lambdaRate = (maxLambdaRate / tickCount) * index
    const x = paddingLeft + (lambdaRate / maxLambdaRate) * plotWidth

    return {
      lambdaRate,
      x: roundSvg(x),
      label: formatNumber(lambdaRate),
    }
  })
})

const samplePoints = computed(() => {
  if (points.value.length === 0) {
    return []
  }

  const indexes = [0, 10, 20, 30, 38]

  return indexes
    .map((index) => points.value[index])
    .filter(Boolean)
    .map((point) => ({
      lambdaRate: formatNumber(point.lambdaRate),
      value: formatNumber(point.value),
    }))
})

function formatNumber(value: number): string {
  if (!Number.isFinite(value)) {
    return '—'
  }

  return new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: 3,
  }).format(value)
}

function roundSvg(value: number): number {
  return Math.round(value * 100) / 100
}
</script>

<template>
  <n-card class="queue-chart-card" :bordered="false">
    <template #header>
      <div class="queue-chart-card__header">
        <div>
          <div class="queue-chart-card__title">График чувствительности системы</div>
          <div class="queue-chart-card__subtitle">
            Анализ изменения показателя при росте интенсивности поступления λ
          </div>
        </div>

        <n-tag type="info" round>M/M/1</n-tag>
      </div>
    </template>

    <n-alert v-if="!canBuildChart" type="warning" :bordered="false">
      Для построения графика интенсивность обслуживания μ должна быть больше 0.
    </n-alert>

    <template v-else>
      <div class="queue-chart-card__controls">
        <n-radio-group v-model:value="selectedMetric" name="chartMetric" size="small">
          <n-radio-button value="orders">L — заказы</n-radio-button>
          <n-radio-button value="waitingTime">Wq — ожидание</n-radio-button>
          <n-radio-button value="systemTime">W — в системе</n-radio-button>
        </n-radio-group>
      </div>

      <div class="queue-chart-card__caption">
        {{ metricConfig.title }}, {{ metricConfig.unit }}
      </div>

      <div class="queue-chart-card__svg-wrapper">
        <svg
          class="queue-chart"
          :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
          role="img"
          :aria-label="metricConfig.title"
        >
          <line
            class="queue-chart__axis"
            :x1="paddingLeft"
            :y1="paddingTop + plotHeight"
            :x2="paddingLeft + plotWidth"
            :y2="paddingTop + plotHeight"
          />
          <line
            class="queue-chart__axis"
            :x1="paddingLeft"
            :y1="paddingTop"
            :x2="paddingLeft"
            :y2="paddingTop + plotHeight"
          />

          <g v-for="tick in yAxisTicks" :key="`y-${tick.label}`">
            <line
              class="queue-chart__grid"
              :x1="paddingLeft"
              :y1="tick.y"
              :x2="paddingLeft + plotWidth"
              :y2="tick.y"
            />
            <text class="queue-chart__tick" :x="paddingLeft - 10" :y="tick.y + 4" text-anchor="end">
              {{ tick.label }}
            </text>
          </g>

          <g v-for="tick in xAxisTicks" :key="`x-${tick.label}`">
            <line
              class="queue-chart__grid queue-chart__grid--vertical"
              :x1="tick.x"
              :y1="paddingTop"
              :x2="tick.x"
              :y2="paddingTop + plotHeight"
            />
            <text
              class="queue-chart__tick"
              :x="tick.x"
              :y="paddingTop + plotHeight + 24"
              text-anchor="middle"
            >
              {{ tick.label }}
            </text>
          </g>

          <polyline class="queue-chart__line" fill="none" :points="linePoints" />

          <g v-if="currentMarker">
            <line
              class="queue-chart__marker-line"
              :x1="currentMarker.x"
              :y1="paddingTop"
              :x2="currentMarker.x"
              :y2="paddingTop + plotHeight"
            />
            <text
              class="queue-chart__marker-label"
              :x="currentMarker.x"
              :y="paddingTop + 14"
              text-anchor="middle"
            >
              {{ currentMarker.label }}
            </text>
          </g>

          <text
            class="queue-chart__axis-label"
            :x="paddingLeft + plotWidth / 2"
            :y="chartHeight - 6"
            text-anchor="middle"
          >
            Интенсивность поступления λ, заказов/день
          </text>
          <text
            class="queue-chart__axis-label"
            :x="14"
            :y="paddingTop + plotHeight / 2"
            text-anchor="middle"
            transform="rotate(-90 14 150)"
          >
            {{ metricConfig.shortTitle }}, {{ metricConfig.unit }}
          </text>
        </svg>
      </div>

      <div class="queue-chart-card__notes">
        <n-alert type="info" :bordered="false">
          График строится для диапазона 0 ≤ λ &lt; μ. При приближении λ к μ показатель
          резко возрастает, поэтому система становится чувствительной к нагрузке.
        </n-alert>
      </div>

      <div class="queue-chart-card__table" aria-label="Контрольные точки графика">
        <div class="queue-chart-card__table-row queue-chart-card__table-row--head">
          <span>λ</span>
          <span>{{ metricConfig.shortTitle }}</span>
        </div>
        <div v-for="point in samplePoints" :key="point.lambdaRate" class="queue-chart-card__table-row">
          <span>{{ point.lambdaRate }}</span>
          <span>{{ point.value }} {{ metricConfig.unit }}</span>
        </div>
      </div>
    </template>
  </n-card>
</template>

<style scoped>
.queue-chart-card {
  margin-top: 16px;
  border: 1px solid var(--app-border-color);
  background: var(--app-card-bg);
}

.queue-chart-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.queue-chart-card__title {
  font-size: 18px;
  font-weight: 700;
  color: var(--app-text-color);
}

.queue-chart-card__subtitle,
.queue-chart-card__caption {
  margin-top: 4px;
  color: var(--app-text-muted-color);
  font-size: 14px;
}

.queue-chart-card__controls {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 12px;
}

.queue-chart-card__svg-wrapper {
  width: 100%;
  overflow-x: auto;
  padding: 8px 0;
}

.queue-chart {
  width: 100%;
  min-width: 560px;
  height: auto;
}

.queue-chart__axis {
  stroke: var(--app-text-muted-color);
  stroke-width: 1.5;
}

.queue-chart__grid {
  stroke: var(--app-border-color);
  stroke-width: 1;
}

.queue-chart__grid--vertical {
  opacity: 0.55;
}

.queue-chart__line {
  stroke: var(--app-primary-color);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.queue-chart__marker-line {
  stroke: var(--app-warning-color);
  stroke-width: 2;
  stroke-dasharray: 6 6;
}

.queue-chart__marker-label {
  fill: var(--app-warning-color);
  font-size: 12px;
  font-weight: 700;
}

.queue-chart__tick,
.queue-chart__axis-label {
  fill: var(--app-text-muted-color);
  font-size: 12px;
}

.queue-chart-card__notes {
  margin-top: 12px;
}

.queue-chart-card__table {
  display: grid;
  grid-template-columns: repeat(5, minmax(90px, 1fr));
  gap: 8px;
  margin-top: 14px;
}

.queue-chart-card__table-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  border: 1px solid var(--app-border-color);
  border-radius: 12px;
  background: var(--app-soft-bg);
  font-size: 13px;
}

.queue-chart-card__table-row--head {
  font-weight: 700;
  color: var(--app-text-color);
}

@media (max-width: 768px) {
  .queue-chart-card__header,
  .queue-chart-card__controls {
    align-items: stretch;
    flex-direction: column;
  }

  .queue-chart-card__table {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>

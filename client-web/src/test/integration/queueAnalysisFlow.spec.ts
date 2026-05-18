import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { queueApi } from '@/api/queueApi'
import { useQueueAnalysisStore } from '@/stores/queueAnalysisStore'
import type {
  QueueAnalysisRequest,
  QueueAnalysisResponse,
  QueueFormulasResponse,
} from '@/types/queue'

vi.mock('@/api/queueApi', () => ({
  queueApi: {
    analyzeQueue: vi.fn(),
    getQueueFormulas: vi.fn(),
  },
}))

const stableServerResponse: QueueAnalysisResponse = {
  lambda_rate: 6,
  mu_rate: 8,
  arrival_rate_unit: 'заказов/день',
  service_rate_unit: 'заказов/день',
  time_unit: 'дней',
  is_stable: true,
  utilization: 0.75,
  utilization_percent: 75,
  average_orders_in_system: 3,
  average_waiting_time: 0.375,
  average_waiting_time_hours: 9,
  average_time_in_system: 0.5,
  average_time_in_system_hours: 12,
  conclusion: 'Система устойчива. Клерк загружен на 75.0%. Очередь не растет неограниченно.',
}

const formulasServerResponse: QueueFormulasResponse = {
  model_name: 'M/M/1',
  description: 'Одноканальная система массового обслуживания.',
  stability_condition: 'λ < μ',
  formulas: {
    utilization: 'ρ = λ / μ',
    average_orders_in_system: 'L = λ / (μ - λ)',
    average_waiting_time: 'Wq = λ / (μ * (μ - λ))',
    average_time_in_system: 'W = 1 / (μ - λ)',
  },
}

describe('integration: queue analysis web flow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('accepts current FastAPI analysis contract and stores it in local history', async () => {
    const request: QueueAnalysisRequest = {
      lambda_rate: 6,
      mu_rate: 8,
    }

    vi.mocked(queueApi.analyzeQueue).mockResolvedValue(stableServerResponse)

    const store = useQueueAnalysisStore()
    const result = await store.analyzeQueue(request)

    expect(queueApi.analyzeQueue).toHaveBeenCalledWith(request)
    expect(result).toEqual(stableServerResponse)

    expect(result).toHaveProperty('utilization', 0.75)
    expect(result).not.toHaveProperty('rho')
    expect(result).not.toHaveProperty('rate_unit')
    expect(result).not.toHaveProperty('rate_unit_label')
    expect(result).not.toHaveProperty('time_unit_label')
    expect(result).not.toHaveProperty('message')

    expect(store.lastRequest).toEqual(request)
    expect(store.lastResult).toEqual(stableServerResponse)
    expect(store.history).toHaveLength(1)
    expect(store.history[0]!.request).toEqual(request)
    expect(store.history[0]!.response).toEqual(stableServerResponse)
    expect(store.hasHistory).toBe(true)
  })

  it('loads formulas using current FastAPI formulas contract', async () => {
    vi.mocked(queueApi.getQueueFormulas).mockResolvedValue(formulasServerResponse)

    const store = useQueueAnalysisStore()
    const formulas = await store.loadFormulas()

    expect(formulas.model_name).toBe('M/M/1')
    expect(formulas.formulas).toHaveProperty('utilization')
    expect(formulas.formulas).not.toHaveProperty('rho')
    expect(store.formulas).toEqual(formulasServerResponse)
  })

  it('can repeat locally stored calculation through API and update latest result', async () => {
    vi.mocked(queueApi.analyzeQueue).mockResolvedValueOnce(stableServerResponse)

    const store = useQueueAnalysisStore()
    const firstResult = await store.analyzeQueue({
      lambda_rate: 6,
      mu_rate: 8,
    })

    const firstHistoryItem = store.history[0]!

    const repeatedResponse: QueueAnalysisResponse = {
      ...firstResult,
      utilization_percent: 70,
      conclusion: 'Повторный расчет выполнен.',
    }

    vi.mocked(queueApi.analyzeQueue).mockResolvedValueOnce(repeatedResponse)

    const repeatedResult = await store.repeatHistoryItem(firstHistoryItem.id)

    expect(repeatedResult).toEqual(repeatedResponse)
    expect(store.lastResult).toEqual(repeatedResponse)
    expect(store.history[0]!.response).toEqual(repeatedResponse)
    expect(store.history[1]!.response).toEqual(stableServerResponse)
  })
})

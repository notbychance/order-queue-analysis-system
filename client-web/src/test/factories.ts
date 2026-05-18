import type { QueueHistoryItem } from '@/types/history'
import type {
  QueueAnalysisRequest,
  QueueAnalysisResponse,
  QueueFormulasResponse,
} from '@/types/queue'

export function createQueueAnalysisRequest(
  overrides: Partial<QueueAnalysisRequest> = {},
): QueueAnalysisRequest {
  return {
    lambda_rate: 6,
    mu_rate: 8,
    ...overrides,
  }
}

export function createStableQueueAnalysisResponse(
  overrides: Partial<QueueAnalysisResponse> = {},
): QueueAnalysisResponse {
  return {
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
    conclusion: 'Система устойчива. Клерк загружен на 75%. Очередь не растет неограниченно.',
    ...overrides,
  }
}

export function createUnstableQueueAnalysisResponse(
  overrides: Partial<QueueAnalysisResponse> = {},
): QueueAnalysisResponse {
  return createStableQueueAnalysisResponse({
    lambda_rate: 8,
    mu_rate: 8,
    is_stable: false,
    utilization: 1,
    utilization_percent: 100,
    average_orders_in_system: null,
    average_waiting_time: null,
    average_waiting_time_hours: null,
    average_time_in_system: null,
    average_time_in_system_hours: null,
    conclusion: 'Система неустойчива: очередь будет расти неограниченно.',
    ...overrides,
  })
}

export function createQueueHistoryItem(
  overrides: Partial<QueueHistoryItem> = {},
): QueueHistoryItem {
  const request = createQueueAnalysisRequest()
  const response = createStableQueueAnalysisResponse()

  return {
    id: 'history-item-1',
    createdAt: '2026-05-18T12:00:00.000Z',
    request,
    response,
    ...overrides,
  }
}

export function createQueueFormulasResponse(
  overrides: Partial<QueueFormulasResponse> = {},
): QueueFormulasResponse {
  return {
    model_name: 'M/M/1',
    description: 'Одноканальная система массового обслуживания.',
    stability_condition: 'λ < μ',
    formulas: {
      utilization: 'ρ = λ / μ',
      average_orders_in_system: 'L = λ / (μ - λ)',
      average_waiting_time: 'Wq = λ / (μ * (μ - λ))',
      average_time_in_system: 'W = 1 / (μ - λ)',
    },
    ...overrides,
  }
}

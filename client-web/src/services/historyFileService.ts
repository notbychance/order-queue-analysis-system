import type {
  QueueHistoryExportFile,
  QueueHistoryItem,
} from '@/types/history'
import type { QueueAnalysisRequest, QueueAnalysisResponse } from '@/types/queue'

const HISTORY_FILE_SOURCE = 'queue-analysis-web'
const HISTORY_FILE_SCHEMA_VERSION = 1

type UnknownRecord = Record<string, unknown>

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function isNullableFiniteNumber(value: unknown): value is number | null {
  return value === null || isFiniteNumber(value)
}

function isQueueAnalysisRequest(value: unknown): value is QueueAnalysisRequest {
  if (!isRecord(value)) {
    return false
  }

  return isFiniteNumber(value.lambda_rate) && isFiniteNumber(value.mu_rate)
}

function isQueueAnalysisResponse(value: unknown): value is QueueAnalysisResponse {
  if (!isRecord(value)) {
    return false
  }

  return (
    isFiniteNumber(value.lambda_rate) &&
    isFiniteNumber(value.mu_rate) &&
    typeof value.arrival_rate_unit === 'string' &&
    typeof value.service_rate_unit === 'string' &&
    typeof value.time_unit === 'string' &&
    typeof value.is_stable === 'boolean' &&
    isFiniteNumber(value.utilization) &&
    isFiniteNumber(value.utilization_percent) &&
    isNullableFiniteNumber(value.average_orders_in_system) &&
    isNullableFiniteNumber(value.average_waiting_time) &&
    isNullableFiniteNumber(value.average_waiting_time_hours) &&
    isNullableFiniteNumber(value.average_time_in_system) &&
    isNullableFiniteNumber(value.average_time_in_system_hours) &&
    typeof value.conclusion === 'string'
  )
}

function isQueueHistoryItem(value: unknown): value is QueueHistoryItem {
  if (!isRecord(value)) {
    return false
  }

  return (
    typeof value.id === 'string' &&
    value.id.trim().length > 0 &&
    typeof value.createdAt === 'string' &&
    !Number.isNaN(Date.parse(value.createdAt)) &&
    isQueueAnalysisRequest(value.request) &&
    isQueueAnalysisResponse(value.response)
  )
}

function normalizePayloadToItems(payload: unknown): QueueHistoryItem[] {
  if (Array.isArray(payload)) {
    return payload.filter(isQueueHistoryItem)
  }

  if (!isRecord(payload)) {
    return []
  }

  if (Array.isArray(payload.items)) {
    return payload.items.filter(isQueueHistoryItem)
  }

  return []
}

function createHistoryFileName(date = new Date()): string {
  const timestamp = date
    .toISOString()
    .replace(/:/g, '-')
    .replace(/\./g, '-')

  return `queue-analysis-history-${timestamp}.json`
}

function downloadJsonFile(fileName: string, content: string): void {
  const blob = new Blob([content], {
    type: 'application/json;charset=utf-8',
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = fileName
  link.style.display = 'none'

  document.body.appendChild(link)
  link.click()
  link.remove()

  URL.revokeObjectURL(url)
}

export const historyFileService = {
  buildExportFile(items: QueueHistoryItem[]): QueueHistoryExportFile {
    return {
      schemaVersion: HISTORY_FILE_SCHEMA_VERSION,
      source: HISTORY_FILE_SOURCE,
      exportedAt: new Date().toISOString(),
      items,
    }
  },

  exportToJsonFile(items: QueueHistoryItem[]): void {
    if (typeof document === 'undefined') {
      throw new Error('Экспорт истории доступен только в браузере')
    }

    const file = this.buildExportFile(items)
    const content = JSON.stringify(file, null, 2)
    const fileName = createHistoryFileName()

    downloadJsonFile(fileName, content)
  },

  async readJsonFile(file: File): Promise<QueueHistoryItem[]> {
    if (!file.name.toLowerCase().endsWith('.json')) {
      throw new Error('Можно импортировать только JSON-файл истории')
    }

    const text = await file.text()

    if (text.trim().length === 0) {
      throw new Error('Файл истории пуст')
    }

    let payload: unknown

    try {
      payload = JSON.parse(text)
    } catch {
      throw new Error('Файл истории содержит некорректный JSON')
    }

    const items = normalizePayloadToItems(payload)

    if (items.length === 0) {
      throw new Error('В файле не найдено корректных записей истории')
    }

    return items
  },
}

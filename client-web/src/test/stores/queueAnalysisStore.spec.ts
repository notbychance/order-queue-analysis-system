import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { queueApi } from '@/api/queueApi'
import { historyFileService } from '@/services/historyFileService'
import { useQueueAnalysisStore } from '@/stores//queueAnalysisStore'
import {
  createQueueAnalysisRequest,
  createQueueFormulasResponse,
  createQueueHistoryItem,
  createStableQueueAnalysisResponse,
} from '@/test/factories'

vi.mock('@/api/queueApi', () => ({
  queueApi: {
    analyzeQueue: vi.fn(),
    getQueueFormulas: vi.fn(),
  },
}))

vi.mock('@/services/historyFileService', () => ({
  historyFileService: {
    exportToJsonFile: vi.fn(),
    readJsonFile: vi.fn(),
  },
}))

describe('useQueueAnalysisStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('analyzes queue and saves result to local history', async () => {
    const request = createQueueAnalysisRequest()
    const response = createStableQueueAnalysisResponse()
    vi.mocked(queueApi.analyzeQueue).mockResolvedValue(response)

    const store = useQueueAnalysisStore()
    const result = await store.analyzeQueue(request)

    expect(result).toEqual(response)
    expect(queueApi.analyzeQueue).toHaveBeenCalledWith(request)
    expect(store.lastRequest).toEqual(request)
    expect(store.lastResult).toEqual(response)
    expect(store.history).toHaveLength(1)
    expect(store.history[0]!.request).toEqual(request)
    expect(store.history[0]!.response).toEqual(response)
    expect(store.isLoading).toBe(false)
    expect(store.errorMessage).toBeNull()
  })

  it('stores API error message when analyze request fails', async () => {
    vi.mocked(queueApi.analyzeQueue).mockRejectedValue(new Error('FastAPI недоступен'))

    const store = useQueueAnalysisStore()

    await expect(store.analyzeQueue(createQueueAnalysisRequest())).rejects.toThrow(
      'FastAPI недоступен',
    )
    expect(store.errorMessage).toBe('FastAPI недоступен')
    expect(store.isLoading).toBe(false)
    expect(store.history).toHaveLength(0)
  })

  it('loads formulas from API', async () => {
    const formulas = createQueueFormulasResponse()
    vi.mocked(queueApi.getQueueFormulas).mockResolvedValue(formulas)

    const store = useQueueAnalysisStore()
    const result = await store.loadFormulas()

    expect(result).toEqual(formulas)
    expect(store.formulas).toEqual(formulas)
    expect(store.isLoadingFormulas).toBe(false)
  })

  it('repeats history item by id', async () => {
    const historyItem = createQueueHistoryItem({ id: 'repeat-id' })
    const response = createStableQueueAnalysisResponse({ utilization_percent: 50 })
    vi.mocked(queueApi.analyzeQueue).mockResolvedValue(response)

    const store = useQueueAnalysisStore()
    store.history = [historyItem]

    await store.repeatHistoryItem('repeat-id')

    expect(queueApi.analyzeQueue).toHaveBeenCalledWith(historyItem.request)
    expect(store.history[0]!.response).toEqual(response)
  })

  it('throws readable error when repeating unknown history item', async () => {
    const store = useQueueAnalysisStore()

    await expect(store.repeatHistoryItem('missing-id')).rejects.toThrow('Запись истории не найдена')
  })

  it('imports history in append mode and skips duplicate ids', () => {
    const existingItem = createQueueHistoryItem({ id: 'same-id' })
    const importedDuplicate = createQueueHistoryItem({ id: 'same-id' })
    const importedUnique = createQueueHistoryItem({ id: 'unique-id' })

    const store = useQueueAnalysisStore()
    store.history = [existingItem]

    const result = store.importHistoryItems([importedDuplicate, importedUnique], 'append')

    expect(result).toEqual({
      totalCount: 2,
      importedCount: 1,
      skippedCount: 1,
    })
    expect(store.history.map((item) => item.id)).toContain('same-id')
    expect(store.history.map((item) => item.id)).toContain('unique-id')
  })

  it('imports history in replace mode', () => {
    const oldItem = createQueueHistoryItem({ id: 'old-id' })
    const newItem = createQueueHistoryItem({ id: 'new-id' })

    const store = useQueueAnalysisStore()
    store.history = [oldItem]

    const result = store.importHistoryItems([newItem], 'replace')

    expect(result).toEqual({
      totalCount: 1,
      importedCount: 1,
      skippedCount: 0,
    })
    expect(store.history).toHaveLength(1)
    expect(store.history[0]!.id).toBe('new-id')
    expect(store.lastRequest).toEqual(newItem.request)
    expect(store.lastResult).toEqual(newItem.response)
  })

  it('removes history item and resets last result when history becomes empty', () => {
    const item = createQueueHistoryItem({ id: 'remove-id' })

    const store = useQueueAnalysisStore()
    store.history = [item]
    store.lastRequest = item.request
    store.lastResult = item.response

    store.removeHistoryItem('remove-id')

    expect(store.history).toHaveLength(0)
    expect(store.lastRequest).toBeNull()
    expect(store.lastResult).toBeNull()
  })

  it('clears history and last result', () => {
    const item = createQueueHistoryItem()

    const store = useQueueAnalysisStore()
    store.history = [item]
    store.lastRequest = item.request
    store.lastResult = item.response

    store.clearHistory()

    expect(store.history).toEqual([])
    expect(store.lastRequest).toBeNull()
    expect(store.lastResult).toBeNull()
  })

  it('exports non-empty history to JSON file', () => {
    const item = createQueueHistoryItem()
    const store = useQueueAnalysisStore()
    store.history = [item]

    store.exportHistoryToFile()

    expect(historyFileService.exportToJsonFile).toHaveBeenCalledWith([item])
  })

  it('does not export empty history', () => {
    const store = useQueueAnalysisStore()

    expect(() => store.exportHistoryToFile()).toThrow('История расчетов пуста')
  })
})

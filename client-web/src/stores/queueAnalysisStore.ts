import { defineStore } from 'pinia'

import { queueApi } from '@/api/queueApi'
import { historyFileService } from '@/services/historyFileService'
import type {
  QueueHistoryImportMode,
  QueueHistoryImportResult,
  QueueHistoryItem,
} from '@/types/history'
import type {
  QueueAnalysisRequest,
  QueueAnalysisResponse,
  QueueFormulasResponse,
} from '@/types/queue'

interface QueueAnalysisState {
  history: QueueHistoryItem[]
  lastRequest: QueueAnalysisRequest | null
  lastResult: QueueAnalysisResponse | null
  formulas: QueueFormulasResponse | null
  isLoading: boolean
  isLoadingFormulas: boolean
  errorMessage: string | null
}

const MAX_HISTORY_ITEMS = 50

function createHistoryId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }

  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message
  }

  return 'Не удалось выполнить анализ системы'
}

function normalizeHistoryItems(items: QueueHistoryItem[]): QueueHistoryItem[] {
  return [...items]
    .sort((left, right) => Date.parse(right.createdAt) - Date.parse(left.createdAt))
    .slice(0, MAX_HISTORY_ITEMS)
}

export const useQueueAnalysisStore = defineStore('queue-analysis', {
  state: (): QueueAnalysisState => ({
    history: [],
    lastRequest: null,
    lastResult: null,
    formulas: null,
    isLoading: false,
    isLoadingFormulas: false,
    errorMessage: null,
  }),

  getters: {
    hasHistory: (state): boolean => state.history.length > 0,

    latestHistoryItem: (state): QueueHistoryItem | null => state.history[0] ?? null,

    stableHistoryCount: (state): number =>
      state.history.filter((item) => item.response.is_stable).length,

    unstableHistoryCount: (state): number =>
      state.history.filter((item) => !item.response.is_stable).length,
  },

  actions: {
    async analyzeQueue(request: QueueAnalysisRequest): Promise<QueueAnalysisResponse> {
      this.isLoading = true
      this.errorMessage = null

      try {
        const response = await queueApi.analyzeQueue(request)

        this.lastRequest = { ...request }
        this.lastResult = response
        this.addHistoryItem(request, response)

        return response
      } catch (error) {
        this.errorMessage = getErrorMessage(error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async loadFormulas(): Promise<QueueFormulasResponse> {
      this.isLoadingFormulas = true
      this.errorMessage = null

      try {
        this.formulas = await queueApi.getQueueFormulas()
        return this.formulas
      } catch (error) {
        this.errorMessage = getErrorMessage(error)
        throw error
      } finally {
        this.isLoadingFormulas = false
      }
    },

    async repeatHistoryItem(id: string): Promise<QueueAnalysisResponse> {
      const item = this.history.find((historyItem) => historyItem.id === id)

      if (!item) {
        throw new Error('Запись истории не найдена')
      }

      return this.analyzeQueue(item.request)
    },

    addHistoryItem(
      request: QueueAnalysisRequest,
      response: QueueAnalysisResponse,
    ): QueueHistoryItem {
      const item: QueueHistoryItem = {
        id: createHistoryId(),
        createdAt: new Date().toISOString(),
        request: { ...request },
        response,
      }

      this.history = normalizeHistoryItems([item, ...this.history])

      return item
    },

    exportHistoryToFile(): void {
      if (this.history.length === 0) {
        throw new Error('История расчетов пуста')
      }

      historyFileService.exportToJsonFile(this.history)
    },

    async importHistoryFromFile(
      file: File,
      mode: QueueHistoryImportMode = 'append',
    ): Promise<QueueHistoryImportResult> {
      const importedItems = await historyFileService.readJsonFile(file)
      return this.importHistoryItems(importedItems, mode)
    },

    importHistoryItems(
      items: QueueHistoryItem[],
      mode: QueueHistoryImportMode = 'append',
    ): QueueHistoryImportResult {
      const existingIds = new Set(mode === 'append' ? this.history.map((item) => item.id) : [])
      const uniqueItems = items.filter((item) => !existingIds.has(item.id))
      const nextHistory = mode === 'replace' ? uniqueItems : [...uniqueItems, ...this.history]

      this.history = normalizeHistoryItems(nextHistory)

      const latestItem = this.history[0] ?? null

      if (latestItem) {
        this.lastRequest = latestItem.request
        this.lastResult = latestItem.response
      } else {
        this.lastRequest = null
        this.lastResult = null
      }

      return {
        totalCount: items.length,
        importedCount: uniqueItems.length,
        skippedCount: items.length - uniqueItems.length,
      }
    },

    removeHistoryItem(id: string): void {
      this.history = this.history.filter((item) => item.id !== id)

      if (this.latestHistoryItem) {
        this.lastRequest = this.latestHistoryItem.request
        this.lastResult = this.latestHistoryItem.response
      } else {
        this.lastRequest = null
        this.lastResult = null
      }
    },

    clearHistory(): void {
      this.history = []
      this.lastRequest = null
      this.lastResult = null
    },

    clearError(): void {
      this.errorMessage = null
    },
  },

  persist: {
    key: 'queue-analysis-store',
    pick: ['history', 'lastRequest', 'lastResult'],
  },
})

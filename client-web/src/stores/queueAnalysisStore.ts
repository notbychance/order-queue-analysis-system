import { defineStore } from 'pinia'

import { queueApi } from '@/api/queueApi'
import type { QueueHistoryItem } from '@/types/history'
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

      this.history = [item, ...this.history].slice(0, MAX_HISTORY_ITEMS)

      return item
    },

    removeHistoryItem(id: string): void {
      this.history = this.history.filter((item) => item.id !== id)
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

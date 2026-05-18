import type { QueueAnalysisRequest, QueueAnalysisResponse } from './queue'

export interface QueueHistoryItem {
  id: string
  createdAt: string
  request: QueueAnalysisRequest
  response: QueueAnalysisResponse
}

export interface QueueHistoryExportFile {
  schemaVersion: 1
  source: 'queue-analysis-web'
  exportedAt: string
  items: QueueHistoryItem[]
}

export type QueueHistoryImportMode = 'append' | 'replace'

export interface QueueHistoryImportResult {
  totalCount: number
  importedCount: number
  skippedCount: number
}

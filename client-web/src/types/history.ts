import type { QueueAnalysisRequest, QueueAnalysisResponse } from './queue'

export interface QueueHistoryItem {
  id: string
  createdAt: string
  request: QueueAnalysisRequest
  response: QueueAnalysisResponse
}

import { httpClient } from './httpClient'
import type {
  QueueAnalysisRequest,
  QueueAnalysisResponse,
  QueueFormulasResponse,
} from '@/types/queue'

export const queueApi = {
  async analyzeQueue(request: QueueAnalysisRequest): Promise<QueueAnalysisResponse> {
    const response = await httpClient.post<QueueAnalysisResponse>('/queue/analyze', request)
    return response.data
  },

  async getQueueFormulas(): Promise<QueueFormulasResponse> {
    const response = await httpClient.get<QueueFormulasResponse>('/queue/formulas')
    return response.data
  },
}

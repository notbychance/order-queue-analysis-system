export interface QueueAnalysisRequest {
  lambda_rate: number
  mu_rate: number
}

export interface QueueAnalysisResponse {
  lambda_rate: number
  mu_rate: number

  arrival_rate_unit: string
  service_rate_unit: string
  time_unit: string

  is_stable: boolean

  utilization: number
  utilization_percent: number

  average_orders_in_system: number | null
  average_waiting_time: number | null
  average_waiting_time_hours: number | null
  average_time_in_system: number | null
  average_time_in_system_hours: number | null

  conclusion: string
}

export interface QueueFormulasResponse {
  model_name: string
  description: string
  stability_condition: string
  formulas: Record<string, string>
}

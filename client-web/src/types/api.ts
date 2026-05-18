export interface FastApiValidationErrorItem {
  loc: Array<string | number>
  msg: string
  type: string
  input?: unknown
  ctx?: Record<string, unknown>
}

export interface ApiErrorResponse {
  detail?: string | FastApiValidationErrorItem[]
}

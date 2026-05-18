import axios from 'axios'
import type { AxiosError } from 'axios'

import { env } from '../config/env'
import type { ApiErrorResponse, FastApiValidationErrorItem } from '../types/api'

export const httpClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: env.requestTimeoutMs,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

function formatValidationErrorItem(errorItem: FastApiValidationErrorItem): string {
  const fieldPath = errorItem.loc.join('.')
  return fieldPath ? `${fieldPath}: ${errorItem.msg}` : errorItem.msg
}

function formatFastApiDetail(detail: ApiErrorResponse['detail']): string | null {
  if (!detail) {
    return null
  }

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail.map(formatValidationErrorItem).join('; ')
  }

  return null
}

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError<ApiErrorResponse>(error)) {
    return 'Произошла неизвестная ошибка при обращении к серверу.'
  }

  const axiosError = error as AxiosError<ApiErrorResponse>

  if (axiosError.code === 'ECONNABORTED') {
    return 'Сервер не ответил за отведенное время. Повторите запрос позже.'
  }

  if (!axiosError.response) {
    return 'Не удалось подключиться к серверу. Проверьте, что FastAPI запущен.'
  }

  const detailMessage = formatFastApiDetail(axiosError.response.data?.detail)

  if (detailMessage) {
    return detailMessage
  }

  return `Ошибка сервера: ${axiosError.response.status}`
}

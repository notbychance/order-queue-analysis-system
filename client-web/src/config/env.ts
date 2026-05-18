const DEFAULT_DEV_API_BASE_URL = 'http://localhost:8000/api/v1'
const DEFAULT_PROD_API_BASE_URL = '/api/v1'
const DEFAULT_REQUEST_TIMEOUT_MS = 10_000
const DEFAULT_APP_NAME = 'Queue Analysis Web'

function normalizeApiBaseUrl(value: string): string {
  const trimmedValue = value.trim()

  if (!trimmedValue) {
    return import.meta.env.DEV ? DEFAULT_DEV_API_BASE_URL : DEFAULT_PROD_API_BASE_URL
  }

  return trimmedValue.replace(/\/+$/, '')
}

function parsePositiveInteger(value: string | undefined, fallback: number): number {
  if (!value) {
    return fallback
  }

  const parsedValue = Number.parseInt(value, 10)

  if (Number.isNaN(parsedValue) || parsedValue <= 0) {
    return fallback
  }

  return parsedValue
}

export const env = {
  appName: import.meta.env.VITE_APP_NAME?.trim() || DEFAULT_APP_NAME,
  apiBaseUrl: normalizeApiBaseUrl(
    import.meta.env.VITE_API_BASE_URL ||
      (import.meta.env.DEV ? DEFAULT_DEV_API_BASE_URL : DEFAULT_PROD_API_BASE_URL),
  ),
  requestTimeoutMs: parsePositiveInteger(
    import.meta.env.VITE_REQUEST_TIMEOUT_MS,
    DEFAULT_REQUEST_TIMEOUT_MS,
  ),
} as const

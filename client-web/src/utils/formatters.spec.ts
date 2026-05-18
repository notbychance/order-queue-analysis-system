import { describe, expect, it } from 'vitest'

import { formatDateTime, formatHours, formatNumber, formatPercent } from './formatters'

describe('formatters', () => {
  it('formats finite numbers with Russian locale', () => {
    expect(formatNumber(3.14159, 2)).toBe('3,14')
  })

  it('returns dash for empty number values', () => {
    expect(formatNumber(null)).toBe('—')
    expect(formatNumber(undefined)).toBe('—')
    expect(formatNumber(Number.NaN)).toBe('—')
  })

  it('formats percent values', () => {
    expect(formatPercent(75, 2)).toBe('75%')
    expect(formatPercent(null)).toBe('—')
  })

  it('formats hours values', () => {
    expect(formatHours(9, 2)).toBe('9 ч')
    expect(formatHours(null)).toBe('—')
  })

  it('formats invalid dates as dash', () => {
    expect(formatDateTime('invalid-date')).toBe('—')
  })
})

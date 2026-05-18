import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useThemeStore } from '@/stores/themeStore'

function mockMatchMedia(matches: boolean): void {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}

function removeMatchMedia(): void {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: undefined,
  })
}

describe('themeStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.restoreAllMocks()
    removeMatchMedia()
  })

  it('uses light theme by default when saved theme and matchMedia are unavailable', () => {
    const themeStore = useThemeStore()

    expect(themeStore.mode).toBe('light')
    expect(themeStore.isLight).toBe(true)
    expect(themeStore.isDark).toBe(false)
  })

  it('uses saved theme from localStorage', () => {
    localStorage.setItem('queue-analysis-theme', 'dark')

    const themeStore = useThemeStore()

    expect(themeStore.mode).toBe('dark')
    expect(themeStore.isDark).toBe(true)
  })

  it('ignores invalid saved theme and falls back to light when matchMedia is unavailable', () => {
    localStorage.setItem('queue-analysis-theme', 'invalid-theme')

    const themeStore = useThemeStore()

    expect(themeStore.mode).toBe('light')
  })

  it('uses system dark theme when matchMedia returns dark preference', () => {
    mockMatchMedia(true)

    const themeStore = useThemeStore()

    expect(themeStore.mode).toBe('dark')
  })

  it('uses system light theme when matchMedia returns light preference', () => {
    mockMatchMedia(false)

    const themeStore = useThemeStore()

    expect(themeStore.mode).toBe('light')
  })

  it('applies current theme to document on initTheme', () => {
    localStorage.setItem('queue-analysis-theme', 'dark')

    const themeStore = useThemeStore()
    themeStore.initTheme()

    expect(document.documentElement.dataset.theme).toBe('dark')
  })

  it('sets dark theme', () => {
    const themeStore = useThemeStore()

    themeStore.setDarkTheme()

    expect(themeStore.mode).toBe('dark')
    expect(themeStore.isDark).toBe(true)
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(localStorage.getItem('queue-analysis-theme')).toBe('dark')
  })

  it('sets light theme', () => {
    const themeStore = useThemeStore()

    themeStore.setDarkTheme()
    themeStore.setLightTheme()

    expect(themeStore.mode).toBe('light')
    expect(themeStore.isLight).toBe(true)
    expect(document.documentElement.dataset.theme).toBe('light')
    expect(localStorage.getItem('queue-analysis-theme')).toBe('light')
  })

  it('toggles theme from light to dark', () => {
    const themeStore = useThemeStore()

    themeStore.toggleTheme()

    expect(themeStore.mode).toBe('dark')
    expect(document.documentElement.dataset.theme).toBe('dark')
  })

  it('toggles theme from dark to light', () => {
    localStorage.setItem('queue-analysis-theme', 'dark')

    const themeStore = useThemeStore()

    themeStore.toggleTheme()

    expect(themeStore.mode).toBe('light')
    expect(document.documentElement.dataset.theme).toBe('light')
  })
})

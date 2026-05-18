import { defineStore } from 'pinia'

import type { ThemeMode } from '@/types/theme'

const DEFAULT_THEME: ThemeMode = 'light'

function isValidThemeMode(value: unknown): value is ThemeMode {
  return value === 'light' || value === 'dark'
}

function getInitialTheme(): ThemeMode {
  if (typeof window === 'undefined') {
    return DEFAULT_THEME
  }

  const savedTheme = window.localStorage.getItem('queue-analysis-theme')

  if (isValidThemeMode(savedTheme)) {
    return savedTheme
  }

  if (typeof window.matchMedia === 'function') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  return DEFAULT_THEME
}

function applyTheme(mode: ThemeMode): void {
  if (typeof document === 'undefined') {
    return
  }

  document.documentElement.dataset.theme = mode
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: getInitialTheme(),
  }),

  getters: {
    isDark: (state) => state.mode === 'dark',
    isLight: (state) => state.mode === 'light',
  },

  actions: {
    initTheme(): void {
      applyTheme(this.mode)
    },

    setTheme(mode: ThemeMode): void {
      this.mode = mode
      applyTheme(mode)

      if (typeof window !== 'undefined') {
        window.localStorage.setItem('queue-analysis-theme', mode)
      }
    },

    setLightTheme(): void {
      this.setTheme('light')
    },

    setDarkTheme(): void {
      this.setTheme('dark')
    },

    toggleTheme(): void {
      this.setTheme(this.isDark ? 'light' : 'dark')
    },
  },

  persist: {
    key: 'queue-analysis-theme-store',
    pick: ['mode'],
  },
})

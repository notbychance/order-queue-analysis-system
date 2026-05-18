import { defineStore } from 'pinia'

import type { ThemeMode, ThemeState } from '@/types/theme'

const THEME_ATTRIBUTE = 'data-theme'

function getInitialTheme(): ThemeMode {
  if (typeof window === 'undefined') {
    return 'light'
  }

  const savedTheme = window.localStorage.getItem('theme')

  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({
    mode: getInitialTheme(),
  }),

  getters: {
    isDark: (state) => state.mode === 'dark',
    isLight: (state) => state.mode === 'light',
    themeTitle: (state) => (state.mode === 'dark' ? 'Темная тема' : 'Светлая тема'),
  },

  actions: {
    initTheme(): void {
      this.applyTheme()
    },

    setTheme(mode: ThemeMode): void {
      this.mode = mode
      this.applyTheme()
    },

    setLightTheme(): void {
      this.setTheme('light')
    },

    setDarkTheme(): void {
      this.setTheme('dark')
    },

    toggleTheme(): void {
      this.setTheme(this.mode === 'dark' ? 'light' : 'dark')
    },

    applyTheme(): void {
      if (typeof document === 'undefined') {
        return
      }

      document.documentElement.setAttribute(THEME_ATTRIBUTE, this.mode)
      document.documentElement.style.colorScheme = this.mode
    },
  },

  persist: {
    key: 'queue-analysis-theme',
    pick: ['mode'],
  },
})

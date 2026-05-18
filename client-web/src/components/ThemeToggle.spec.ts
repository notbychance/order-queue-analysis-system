import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ThemeToggle from './ThemeToggle.vue'
import { useThemeStore } from '@/stores/themeStore'
import { naiveStubs } from '@/test/naiveStubs'

function mockMatchMedia(matches: boolean): void {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
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

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear()
    mockMatchMedia(false)
    setActivePinia(createPinia())
  })

  it('toggles theme after click', async () => {
    const wrapper = mount(ThemeToggle, {
      global: {
        stubs: naiveStubs,
      },
    })
    const themeStore = useThemeStore()

    expect(wrapper.text()).toContain('Темная тема')

    await wrapper.find('button').trigger('click')

    expect(themeStore.mode).toBe('dark')
    expect(wrapper.text()).toContain('Светлая тема')
  })
})

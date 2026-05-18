import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '@/App.vue'
import { useQueueAnalysisStore } from '@/stores/queueAnalysisStore'
import { createQueueHistoryItem } from '@/test/factories'
import { naiveStubs } from '@/test/naiveStubs'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/',
        name: 'analysis',
        component: {
          template: '<div>Страница анализа</div>',
        },
      },
      {
        path: '/history',
        name: 'history',
        component: {
          template: '<div>История расчетов</div>',
        },
      },
      {
        path: '/formulas',
        name: 'formulas',
        component: {
          template: '<div>Формулы</div>',
        },
      },
    ],
  })
}

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

async function mountApp() {
  const pinia = createPinia()
  const router = createTestRouter()

  setActivePinia(pinia)
  router.push('/')
  await router.isReady()

  const wrapper = mount(App, {
    global: {
      plugins: [pinia, router],
      stubs: {
        ...naiveStubs,
        HistoryFileActions: {
          template: '<div data-test="history-file-actions"></div>',
        },
        ThemeToggle: {
          template: '<button data-test="theme-toggle">Темная тема</button>',
        },
      },
    },
  })

  return { wrapper, router, pinia }
}

describe('App', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    mockMatchMedia(false)
  })

  it('renders application layout and navigation', async () => {
    const { wrapper } = await mountApp()

    expect(wrapper.text()).toContain('Анализ очереди заказов')
    expect(wrapper.text()).toContain('Анализ')
    expect(wrapper.text()).toContain('История')
    expect(wrapper.text()).toContain('Формулы')
    expect(wrapper.text()).toContain('Страница анализа')
  })

  it('shows empty local history state', async () => {
    const { wrapper } = await mountApp()

    expect(wrapper.text()).toContain('Локальная история')
    expect(wrapper.text()).toContain('История расчетов пока пуста')
  })

  it('renders recent local history item in sidebar', async () => {
    const pinia = createPinia()
    const router = createTestRouter()
    setActivePinia(pinia)

    const queueStore = useQueueAnalysisStore(pinia)
    queueStore.history = [createQueueHistoryItem({ id: 'history-1' })]

    router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
        stubs: {
          ...naiveStubs,
          HistoryFileActions: {
            template: '<div data-test="history-file-actions"></div>',
          },
          ThemeToggle: {
            template: '<button data-test="theme-toggle">Темная тема</button>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('λ = 6')
    expect(wrapper.text()).toContain('μ = 8')
    expect(wrapper.text()).toContain('устойчива')
    expect(wrapper.text()).toContain('75%')
  })
})

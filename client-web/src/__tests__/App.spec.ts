import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

import App from '@/App.vue'

const createTestRouter = () =>
  createRouter({
    history: createWebHistory(),
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

describe('App', () => {
  it('mounts renders properly', async () => {
    const pinia = createPinia()
    const router = createTestRouter()

    router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
        stubs: {
          NConfigProvider: {
            template: '<div><slot /></div>',
          },
          NMessageProvider: {
            template: '<div><slot /></div>',
          },
          NDialogProvider: {
            template: '<div><slot /></div>',
          },
          NLayout: {
            template: '<div><slot /></div>',
          },
          NLayoutHeader: {
            template: '<header><slot /></header>',
          },
          NLayoutContent: {
            template: '<main><slot /></main>',
          },
          NLayoutSider: {
            template: '<aside><slot /></aside>',
          },
          NCard: {
            template: '<section><slot /></section>',
          },
          NButton: {
            template: '<button><slot /></button>',
          },
          NTag: {
            template: '<span><slot /></span>',
          },
          NEmpty: {
            template: '<div></div>',
          },
          NScrollbar: {
            template: '<div><slot /></div>',
          },
        },
      },
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Анализ')
  })
})

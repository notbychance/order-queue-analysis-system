import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import QueueAnalysisResult from './QueueAnalysisResult.vue'
import { createStableQueueAnalysisResponse, createUnstableQueueAnalysisResponse } from '@/test/factories'
import { naiveStubs } from '@/test/naiveStubs'

describe('QueueAnalysisResult', () => {
  it('shows empty state when result is not provided', () => {
    const wrapper = mount(QueueAnalysisResult, {
      props: {
        result: null,
      },
      global: {
        stubs: naiveStubs,
      },
    })

    expect(wrapper.text()).toContain('Введите параметры и выполните расчет')
  })

  it('renders stable queue analysis result', () => {
    const wrapper = mount(QueueAnalysisResult, {
      props: {
        result: createStableQueueAnalysisResponse(),
      },
      global: {
        stubs: naiveStubs,
      },
    })

    expect(wrapper.text()).toContain('Система устойчива')
    expect(wrapper.text()).toContain('Коэффициент загрузки')
    expect(wrapper.text()).toContain('75%')
    expect(wrapper.text()).toContain('Среднее число заказов в системе')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('9 ч')
    expect(wrapper.text()).toContain('12 ч')
  })

  it('renders unstable queue analysis result with empty calculated metrics', () => {
    const wrapper = mount(QueueAnalysisResult, {
      props: {
        result: createUnstableQueueAnalysisResponse(),
      },
      global: {
        stubs: naiveStubs,
      },
    })

    expect(wrapper.text()).toContain('Система неустойчива')
    expect(wrapper.text()).toContain('100%')
    expect(wrapper.text()).toContain('—')
  })
})

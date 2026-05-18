import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import QueueAnalysisResult from '@/components/QueueAnalysisResult.vue'
import { createStableQueueAnalysisResponse, createUnstableQueueAnalysisResponse } from '@/test/factories'
import { naiveStubs } from '@/test/naiveStubs'

function mountResult(result = createStableQueueAnalysisResponse()) {
  return mount(QueueAnalysisResult, {
    props: { result },
    global: {
      stubs: {
        ...naiveStubs,
        QueueAnalysisChart: {
          props: ['result'],
          template: '<div data-test="queue-chart">График</div>',
        },
      },
    },
  })
}

describe('QueueAnalysisResult', () => {
  it('renders stable analysis metrics and conclusion', () => {
    const wrapper = mountResult()

    expect(wrapper.text()).toContain('Результаты анализа')
    expect(wrapper.text()).toContain('Система устойчива')
    expect(wrapper.text()).toContain('75 %')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('9 ч')
    expect(wrapper.text()).toContain('12 ч')
    expect(wrapper.find('[data-test="queue-chart"]').exists()).toBe(true)
  })

  it('renders unstable result with empty calculated metrics', () => {
    const wrapper = mountResult(createUnstableQueueAnalysisResponse())

    expect(wrapper.text()).toContain('Система неустойчива')
    expect(wrapper.text()).toContain('100 %')
    expect(wrapper.text()).toContain('—')
    expect(wrapper.text()).toContain('очередь будет расти')
  })
})

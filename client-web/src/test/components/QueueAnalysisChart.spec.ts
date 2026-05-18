import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import QueueAnalysisChart from '@/components/QueueAnalysisChart.vue'
import { createStableQueueAnalysisResponse } from '@/test/factories'
import { naiveStubs } from '@/test/naiveStubs'

function mountChart(result = createStableQueueAnalysisResponse()) {
  return mount(QueueAnalysisChart, {
    props: { result },
    global: {
      stubs: naiveStubs,
    },
  })
}

describe('QueueAnalysisChart', () => {
  it('renders SVG chart for valid service rate', () => {
    const wrapper = mountChart()

    expect(wrapper.text()).toContain('График чувствительности системы')
    expect(wrapper.text()).toContain('Среднее число заказов в системе')
    expect(wrapper.find('svg.queue-chart').exists()).toBe(true)
    expect(wrapper.find('polyline.queue-chart__line').attributes('points')).toBeTruthy()
    expect(wrapper.text()).toContain('λ = 6')
  })

  it('shows warning when chart cannot be built', () => {
    const wrapper = mountChart(
      createStableQueueAnalysisResponse({
        lambda_rate: 0,
        mu_rate: 0,
      }),
    )

    expect(wrapper.find('svg.queue-chart').exists()).toBe(false)
    expect(wrapper.text()).toContain('интенсивность обслуживания μ должна быть больше 0')
  })
})

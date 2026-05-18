import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import QueueAnalysisForm from './QueueAnalysisForm.vue'
import { naiveStubs } from '@/test/naiveStubs'

function mountForm(props = {}) {
  return mount(QueueAnalysisForm, {
    props,
    global: {
      stubs: naiveStubs,
    },
  })
}

describe('QueueAnalysisForm', () => {
  it('shows validation message for empty fields', () => {
    const wrapper = mountForm()

    expect(wrapper.text()).toContain('Заполните оба параметра системы')
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
  })

  it('emits submit with lambda and mu values', async () => {
    const wrapper = mountForm({
      initialLambda: 6,
      initialMu: 8,
    })

    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toEqual([
      [
        {
          lambda_rate: 6,
          mu_rate: 8,
        },
      ],
    ])
  })

  it('updates input values and emits submit payload', async () => {
    const wrapper = mountForm()
    const inputs = wrapper.findAll('input')

    await inputs[0].setValue('5')
    await inputs[1].setValue('10')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toEqual([
      [
        {
          lambda_rate: 5,
          mu_rate: 10,
        },
      ],
    ])
  })

  it('shows warning for unstable system but still allows request', async () => {
    const wrapper = mountForm({
      initialLambda: 8,
      initialMu: 8,
    })

    expect(wrapper.text()).toContain('При λ ≥ μ система неустойчива')

    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toHaveLength(1)
  })

  it('clears form and emits reset event', async () => {
    const wrapper = mountForm({
      initialLambda: 6,
      initialMu: 8,
    })
    const buttons = wrapper.findAll('button')

    await buttons[1].trigger('click')

    expect(wrapper.emitted('reset')).toHaveLength(1)
    expect(wrapper.text()).toContain('Заполните оба параметра системы')
  })
})

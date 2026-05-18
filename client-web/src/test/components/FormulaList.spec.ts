import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import FormulaList from '@/components/FormulaList.vue'
import { createQueueFormulasResponse } from '@/test/factories'
import { naiveStubs } from '@/test/naiveStubs'

function mountFormulaList(props = {}) {
  return mount(FormulaList, {
    props: {
      formulas: null,
      loading: false,
      ...props,
    },
    global: {
      stubs: naiveStubs,
    },
  })
}

describe('FormulaList', () => {
  it('renders empty state before formulas are loaded', () => {
    const wrapper = mountFormulaList()

    expect(wrapper.text()).toContain('Формулы еще не загружены')
  })

  it('renders model description and formulas', () => {
    const wrapper = mountFormulaList({ formulas: createQueueFormulasResponse() })

    expect(wrapper.text()).toContain('M/M/1')
    expect(wrapper.text()).toContain('λ < μ')
    expect(wrapper.text()).toContain('Коэффициент загрузки')
    expect(wrapper.text()).toContain('ρ = λ / μ')
    expect(wrapper.text()).toContain('L = λ / (μ - λ)')
  })
})

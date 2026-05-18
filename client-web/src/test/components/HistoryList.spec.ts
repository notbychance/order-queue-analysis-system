import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import HistoryList from '@/components/HistoryList.vue'
import { createQueueHistoryItem } from '@/test/factories'
import { naiveStubs } from '@/test/naiveStubs'

function mountHistoryList(props = {}) {
  return mount(HistoryList, {
    props: {
      items: [],
      ...props,
    },
    global: {
      stubs: naiveStubs,
    },
  })
}

describe('HistoryList', () => {
  it('renders empty state', () => {
    const wrapper = mountHistoryList()

    expect(wrapper.text()).toContain('История расчетов пока пуста')
    expect(wrapper.findAll('button')).toHaveLength(0)
  })

  it('renders history item and emits actions', async () => {
    const item = createQueueHistoryItem({ id: 'item-1' })
    const wrapper = mountHistoryList({ items: [item] })

    expect(wrapper.text()).toContain('λ = 6')
    expect(wrapper.text()).toContain('μ = 8')
    expect(wrapper.text()).toContain('устойчива')
    expect(wrapper.text()).toContain('75%')

    const buttons = wrapper.findAll('button')
    await buttons.find((button) => button.text().includes('Повторить'))!.trigger('click')
    await buttons.find((button) => button.text().includes('Удалить'))!.trigger('click')
    await buttons.find((button) => button.text().includes('Очистить'))!.trigger('click')

    expect(wrapper.emitted('repeat')).toEqual([['item-1']])
    expect(wrapper.emitted('remove')).toEqual([['item-1']])
    expect(wrapper.emitted('clear')).toEqual([[]])
  })
})

import { defineComponent, type PropType } from 'vue'

const NButtonStub = defineComponent({
  name: 'NButton',
  props: {
    disabled: Boolean,
    loading: Boolean,
    attrType: {
      type: String,
      default: 'button',
    },
  },
  emits: ['click'],
  template: `
    <button
      :type="attrType"
      :disabled="disabled || loading"
      @click="$emit('click')"
    >
      <slot />
    </button>
  `,
})

const NInputNumberStub = defineComponent({
  name: 'NInputNumber',
  props: {
    value: {
      type: Number as PropType<number | null>,
      default: null,
    },
    placeholder: {
      type: String,
      default: '',
    },
  },
  emits: ['update:value'],
  setup(_, { emit }) {
    function onInput(event: Event): void {
      const input = event.target as HTMLInputElement
      const nextValue = input.value.trim() === '' ? null : Number(input.value)
      emit('update:value', nextValue)
    }

    return { onInput }
  },
  template: `
    <label>
      <input
        type="number"
        :placeholder="placeholder"
        :value="value ?? ''"
        @input="onInput"
      />
      <span><slot name="suffix" /></span>
    </label>
  `,
})

const NFormStub = defineComponent({
  name: 'NForm',
  template: '<form><slot /></form>',
})

const NCardStub = defineComponent({
  name: 'NCard',
  props: {
    title: {
      type: String,
      default: '',
    },
  },
  template: `
    <section>
      <h3 v-if="title">{{ title }}</h3>
      <slot name="header-extra" />
      <slot />
    </section>
  `,
})

const NAlertStub = defineComponent({
  name: 'NAlert',
  template: '<div role="alert"><slot /></div>',
})

const NEmptyStub = defineComponent({
  name: 'NEmpty',
  props: {
    description: {
      type: String,
      default: '',
    },
  },
  template: '<div>{{ description }}<slot /></div>',
})

const NResultStub = defineComponent({
  name: 'NResult',
  props: {
    title: {
      type: String,
      default: '',
    },
    description: {
      type: String,
      default: '',
    },
  },
  template: '<section><h2>{{ title }}</h2><p>{{ description }}</p><slot /></section>',
})

const NTagStub = defineComponent({
  name: 'NTag',
  template: '<span><slot /></span>',
})

const PassthroughStub = defineComponent({
  name: 'PassthroughStub',
  template: '<div><slot /></div>',
})

export const naiveStubs = {
  NAlert: NAlertStub,
  'n-alert': NAlertStub,
  NButton: NButtonStub,
  'n-button': NButtonStub,
  NCard: NCardStub,
  'n-card': NCardStub,
  NEmpty: NEmptyStub,
  'n-empty': NEmptyStub,
  NForm: NFormStub,
  'n-form': NFormStub,
  NFormItem: PassthroughStub,
  'n-form-item': PassthroughStub,
  NGrid: PassthroughStub,
  'n-grid': PassthroughStub,
  NGridItem: PassthroughStub,
  'n-grid-item': PassthroughStub,
  NInputNumber: NInputNumberStub,
  'n-input-number': NInputNumberStub,
  NResult: NResultStub,
  'n-result': NResultStub,
  NTag: NTagStub,
  'n-tag': NTagStub,
}

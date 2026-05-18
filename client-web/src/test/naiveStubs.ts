export const naiveStubs = {
  NAlert: {
    props: ['type', 'showIcon', 'bordered'],
    template: '<div class="n-alert"><slot /></div>',
  },

  NButton: {
    props: ['type', 'attrType', 'loading', 'disabled', 'secondary', 'tertiary', 'strong', 'round', 'size'],
    template: `
      <button
        class="n-button"
        :type="attrType || 'button'"
        :disabled="disabled || loading"
      >
        <slot />
      </button>
    `,
  },

  NCard: {
    props: ['title', 'bordered', 'size', 'embedded'],
    template: `
      <section class="n-card">
        <header v-if="title || $slots.header || $slots['header-extra']" class="n-card__header">
          <slot name="header"><span>{{ title }}</span></slot>
          <slot name="header-extra" />
        </header>
        <slot />
      </section>
    `,
  },

  NConfigProvider: {
    props: ['theme'],
    template: '<div class="n-config-provider"><slot /></div>',
  },

  NDialogProvider: {
    template: '<div class="n-dialog-provider"><slot /></div>',
  },

  NEmpty: {
    props: ['description', 'size'],
    template: '<div class="n-empty">{{ description }}<slot /></div>',
  },

  NForm: {
    template: '<form class="n-form"><slot /></form>',
  },

  NFormItem: {
    props: ['label', 'path'],
    template: '<label class="n-form-item"><span>{{ label }}</span><slot /></label>',
  },

  NGi: {
    template: '<div class="n-gi"><slot /></div>',
  },

  NGrid: {
    props: ['cols', 'xGap', 'yGap', 'itemResponsive', 'responsive'],
    template: '<div class="n-grid"><slot /></div>',
  },

  NGridItem: {
    template: '<div class="n-grid-item"><slot /></div>',
  },

  NInputNumber: {
    props: ['value', 'min', 'precision', 'showButton', 'placeholder'],
    emits: ['update:value'],
    template: `
      <label class="n-input-number-wrapper">
        <input
          class="n-input-number"
          type="number"
          :value="value ?? ''"
          :placeholder="placeholder"
          @input="$emit('update:value', $event.target.value === '' ? null : Number($event.target.value))"
        />
        <span class="n-input-number-suffix"><slot name="suffix" /></span>
      </label>
    `,
  },

  NLayout: {
    props: ['position', 'hasSider'],
    template: '<div class="n-layout"><slot /></div>',
  },

  NLayoutContent: {
    template: '<main class="n-layout-content"><slot /></main>',
  },

  NLayoutHeader: {
    props: ['bordered'],
    template: '<header class="n-layout-header"><slot /></header>',
  },

  NLayoutSider: {
    props: ['bordered', 'collapseMode', 'collapsedWidth', 'width', 'showTrigger'],
    template: '<aside class="n-layout-sider"><slot /></aside>',
  },

  NMessageProvider: {
    template: '<div class="n-message-provider"><slot /></div>',
  },

  NRadioButton: {
    props: ['value'],
    template: '<label class="n-radio-button"><slot /></label>',
  },

  NRadioGroup: {
    props: ['value', 'name', 'size'],
    emits: ['update:value'],
    template: '<div class="n-radio-group"><slot /></div>',
  },

  NScrollbar: {
    template: '<div class="n-scrollbar"><slot /></div>',
  },

  NSpace: {
    props: ['vertical', 'size', 'wrap'],
    template: '<div class="n-space"><slot /></div>',
  },

  NSpin: {
    props: ['show'],
    template: '<div class="n-spin"><slot /></div>',
  },

  NTag: {
    props: ['type', 'round', 'size'],
    template: '<span class="n-tag"><slot /></span>',
  },
}

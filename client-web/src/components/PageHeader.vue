<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <section class="page-header">
    <div class="page-header__main">
      <h2>{{ title }}</h2>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>

    <div v-if="$slots.extra" class="page-header__extra">
      <slot name="extra" />
    </div>
  </section>
</template>

<style scoped>
.page-header {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 22px;
}

.page-header__main {
  min-width: 0;
}

.page-header h2 {
  margin: 0;
  color: var(--color-heading);
  font-size: clamp(1.35rem, 2.2vw, 2rem);
  line-height: 1.2;
  overflow-wrap: anywhere;
}

.page-header p {
  max-width: 760px;
  margin: 8px 0 0;
  color: var(--color-text-muted);
  font-size: 0.98rem;
  line-height: 1.55;
}

.page-header__extra {
  display: flex;
  flex: 0 0 auto;
  justify-content: flex-end;
}

@media (max-width: 720px) {
  .page-header {
    display: block;
    margin-bottom: 16px;
  }

  .page-header p {
    font-size: 0.92rem;
  }

  .page-header__extra {
    justify-content: stretch;
    margin-top: 14px;
  }

  .page-header__extra :deep(.n-button),
  .page-header__extra :deep(.n-space) {
    width: 100%;
  }
}
</style>

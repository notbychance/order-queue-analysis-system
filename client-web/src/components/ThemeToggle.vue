<script setup lang="ts">
import { computed } from 'vue'

import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()

const buttonText = computed(() => {
  return themeStore.isDark ? 'Светлая тема' : 'Темная тема'
})
</script>

<template>
  <n-button class="theme-toggle" secondary strong round @click="themeStore.toggleTheme">
    {{ buttonText }}
  </n-button>
</template>

<style scoped>
.theme-toggle {
  white-space: nowrap;
}

@media (max-width: 420px) {
  .theme-toggle {
    width: 100%;
  }
}
</style>

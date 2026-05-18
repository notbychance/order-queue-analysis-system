<script setup lang="ts">
import { computed } from 'vue'

import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()

const buttonText = computed(() => {
  return themeStore.isDark ? 'Светлая тема' : 'Темная тема'
})
</script>

<template>
  <n-button secondary strong round @click="themeStore.toggleTheme">
    {{ buttonText }}
  </n-button>
</template>

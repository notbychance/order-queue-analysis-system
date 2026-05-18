<script setup lang="ts">
import { computed } from 'vue'

import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()

const buttonTitle = computed(() =>
  themeStore.isDark ? 'Переключить на светлую тему' : 'Переключить на темную тему',
)
</script>

<template>
  <button class="theme-toggle" type="button" :title="buttonTitle" @click="themeStore.toggleTheme">
    <span class="theme-toggle__icon" aria-hidden="true">
      {{ themeStore.isDark ? '🌙' : '☀️' }}
    </span>
    <span>{{ themeStore.themeTitle }}</span>
  </button>
</template>

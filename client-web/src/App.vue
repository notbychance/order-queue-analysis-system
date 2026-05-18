<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { darkTheme, type GlobalTheme } from 'naive-ui'

import HistoryPanel from './components/HistoryPanel.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import { useThemeStore } from './stores/themeStore'

const themeStore = useThemeStore()

const isHistoryDrawerOpen = ref(false)
const isMobileLayout = ref(false)

const naiveTheme = computed<GlobalTheme | null>(() => {
  return themeStore.isDark ? darkTheme : null
})

function updateLayoutMode(): void {
  if (typeof window === 'undefined') {
    return
  }

  isMobileLayout.value = window.matchMedia('(max-width: 1100px)').matches

  if (!isMobileLayout.value) {
    isHistoryDrawerOpen.value = false
  }
}

function closeHistoryDrawer(): void {
  isHistoryDrawerOpen.value = false
}

onMounted(() => {
  updateLayoutMode()
  window.addEventListener('resize', updateLayoutMode)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateLayoutMode)
})
</script>

<template>
  <n-config-provider :theme="naiveTheme">
    <n-message-provider>
      <n-dialog-provider>
        <n-layout class="app-shell" position="absolute">
          <n-layout-header bordered class="app-header">
            <RouterLink to="/" class="brand" aria-label="Перейти к анализу">
              <div class="brand__mark">M/M/1</div>
              <div class="brand__text">
                <h1 class="brand__title">Анализ очереди заказов</h1>
                <p class="brand__subtitle">Курсовая работа · методы оптимизации</p>
              </div>
            </RouterLink>

            <nav class="nav" aria-label="Основная навигация">
              <RouterLink to="/" class="nav__link">Анализ</RouterLink>
              <RouterLink to="/history" class="nav__link">История</RouterLink>
              <RouterLink to="/formulas" class="nav__link">Формулы</RouterLink>
            </nav>

            <div class="app-header__actions">
              <n-button
                class="history-drawer-button"
                secondary
                size="small"
                @click="isHistoryDrawerOpen = true"
              >
                Локальная история
              </n-button>

              <ThemeToggle />
            </div>
          </n-layout-header>

          <n-layout has-sider class="app-body">
            <n-layout-content class="app-content">
              <RouterView />
            </n-layout-content>

            <n-layout-sider
              v-if="!isMobileLayout"
              bordered
              class="history-sider"
              collapse-mode="width"
              :collapsed-width="0"
              :width="360"
              show-trigger="bar"
            >
              <HistoryPanel />
            </n-layout-sider>
          </n-layout>

          <n-drawer
            v-model:show="isHistoryDrawerOpen"
            placement="right"
            :width="360"
            :max-width="'92vw'"
            display-directive="show"
          >
            <n-drawer-content title="Локальная история" closable>
              <HistoryPanel drawer-mode @repeat="closeHistoryDrawer" />
            </n-drawer-content>
          </n-drawer>
        </n-layout>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--color-background);
}

.app-header {
  display: grid;
  grid-template-columns: minmax(230px, 1fr) auto auto;
  gap: 24px;
  align-items: center;
  min-height: var(--app-header-height);
  padding: 12px 28px;
  background: var(--color-surface);
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  min-width: 0;
}

.brand__mark {
  display: grid;
  width: 52px;
  height: 52px;
  place-items: center;
  border-radius: 16px;
  color: #ffffff;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  background: linear-gradient(135deg, #18a058, #2080f0);
  box-shadow: 0 10px 28px rgba(32, 128, 240, 0.22);
  flex: 0 0 auto;
}

.brand__text {
  min-width: 0;
}

.brand__title {
  margin: 0;
  overflow: hidden;
  color: var(--color-heading);
  font-size: 1.08rem;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand__subtitle {
  margin: 4px 0 0;
  overflow: hidden;
  color: var(--color-text-muted);
  font-size: 0.84rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  min-width: 0;
}

.nav__link {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  color: var(--color-text);
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition:
    color 0.2s ease,
    background-color 0.2s ease;
}

.nav__link:hover {
  color: var(--color-primary);
  background: var(--color-surface-soft);
}

.nav__link.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-soft);
}

.app-header__actions {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: flex-end;
}

.history-drawer-button {
  display: none;
}

.app-body {
  top: var(--app-header-height);
}

.app-content {
  min-width: 0;
  min-height: calc(100vh - var(--app-header-height));
  padding: var(--app-content-padding);
  background: var(--color-background);
}

.history-sider {
  background: var(--color-surface);
}

@media (max-width: 1100px) {
  .app-header {
    grid-template-columns: minmax(210px, 1fr) auto;
  }

  .nav {
    grid-column: 1 / -1;
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 2px;
    scrollbar-width: none;
  }

  .nav::-webkit-scrollbar {
    display: none;
  }

  .history-drawer-button {
    display: inline-flex;
  }

  .app-body {
    top: 116px;
  }

  .app-content {
    min-height: calc(100vh - 116px);
  }
}

@media (max-width: 720px) {
  .app-header {
    grid-template-columns: 1fr;
    gap: 12px;
    min-height: 150px;
    padding: 12px 16px;
  }

  .brand__mark {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    font-size: 0.72rem;
  }

  .brand__title {
    white-space: normal;
    font-size: 0.98rem;
  }

  .brand__subtitle {
    display: none;
  }

  .nav {
    width: 100%;
  }

  .app-header__actions {
    justify-content: space-between;
  }

  .app-body {
    top: 150px;
  }

  .app-content {
    min-height: calc(100vh - 150px);
  }
}

@media (max-width: 420px) {
  .app-header__actions {
    align-items: stretch;
    flex-direction: column;
  }

  .history-drawer-button {
    justify-content: center;
  }

  .app-body {
    top: 192px;
  }

  .app-content {
    min-height: calc(100vh - 192px);
  }
}
</style>

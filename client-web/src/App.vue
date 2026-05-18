<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { darkTheme, type GlobalTheme } from 'naive-ui'

import ThemeToggle from './components/ThemeToggle.vue'
import { useQueueAnalysisStore } from './stores/queueAnalysisStore'
import { useThemeStore } from './stores/themeStore'

const router = useRouter()
const queueStore = useQueueAnalysisStore()
const themeStore = useThemeStore()

const naiveTheme = computed<GlobalTheme | null>(() => {
  return themeStore.theme === 'dark' ? darkTheme : null
})

const lastHistoryItems = computed(() => queueStore.history.slice(0, 5))

function formatNumber(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—'
  }

  return new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: digits,
  }).format(value)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

async function repeatHistoryItem(id: string): Promise<void> {
  await queueStore.repeatHistoryItem(id)
  await router.push({ name: 'analysis' })
}
</script>

<template>
  <n-config-provider :theme="naiveTheme">
    <n-message-provider>
      <n-dialog-provider>
        <n-layout class="app-shell" position="absolute">
          <n-layout-header bordered class="app-header">
            <div class="brand">
              <div class="brand__mark">M/M/1</div>
              <div>
                <h1 class="brand__title">Анализ очереди заказов</h1>
                <p class="brand__subtitle">Курсовая работа · методы оптимизации</p>
              </div>
            </div>

            <nav class="nav">
              <RouterLink to="/" class="nav__link">Анализ</RouterLink>
              <RouterLink to="/history" class="nav__link">История</RouterLink>
              <RouterLink to="/formulas" class="nav__link">Формулы</RouterLink>
            </nav>

            <ThemeToggle />
          </n-layout-header>

          <n-layout has-sider class="app-body">
            <n-layout-content class="app-content">
              <RouterView />
            </n-layout-content>

            <n-layout-sider
              bordered
              class="history-sider"
              collapse-mode="width"
              :collapsed-width="0"
              :width="360"
              show-trigger="bar"
            >
              <n-card title="Локальная история" size="small" :bordered="false" class="history-card">
                <template #header-extra>
                  <n-button
                    v-if="queueStore.history.length > 0"
                    size="tiny"
                    tertiary
                    type="error"
                    @click="queueStore.clearHistory"
                  >
                    Очистить
                  </n-button>
                </template>

                <n-empty
                  v-if="lastHistoryItems.length === 0"
                  description="История расчетов пока пуста"
                  size="small"
                />

                <n-space v-else vertical :size="12">
                  <n-card
                    v-for="item in lastHistoryItems"
                    :key="item.id"
                    size="small"
                    embedded
                    class="history-item"
                  >
                    <div class="history-item__top">
                      <div>
                        <div class="history-item__params">
                          λ = {{ formatNumber(item.request.lambda_rate) }},
                          μ = {{ formatNumber(item.request.mu_rate) }}
                        </div>
                        <div class="history-item__date">{{ formatDate(item.createdAt) }}</div>
                      </div>

                      <n-tag
                        size="small"
                        :type="item.response.is_stable ? 'success' : 'error'"
                        round
                      >
                        {{ item.response.is_stable ? 'устойчива' : 'неустойчива' }}
                      </n-tag>
                    </div>

                    <div class="history-item__metrics">
                      <span>Загрузка:</span>
                      <strong>{{ formatNumber(item.response.utilization_percent, 2) }}%</strong>
                    </div>

                    <div class="history-item__actions">
                      <n-button size="tiny" type="primary" secondary @click="repeatHistoryItem(item.id)">
                        Повторить
                      </n-button>
                      <n-button
                        size="tiny"
                        tertiary
                        type="error"
                        @click="queueStore.removeHistoryItem(item.id)"
                      >
                        Удалить
                      </n-button>
                    </div>
                  </n-card>
                </n-space>
              </n-card>
            </n-layout-sider>
          </n-layout>
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
  grid-template-columns: minmax(240px, 1fr) auto auto;
  gap: 24px;
  align-items: center;
  min-height: 76px;
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

.brand__title {
  margin: 0;
  color: var(--color-heading);
  font-size: 1.08rem;
  line-height: 1.2;
}

.brand__subtitle {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.84rem;
}

.nav {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
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

.app-body {
  top: 76px;
}

.app-content {
  min-height: calc(100vh - 76px);
  padding: 28px;
  background: var(--color-background);
}

.history-sider {
  background: var(--color-surface);
}

.history-card {
  height: 100%;
  border-radius: 0;
}

.history-item {
  border-radius: 16px;
}

.history-item__top {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: space-between;
}

.history-item__params {
  color: var(--color-heading);
  font-weight: 700;
}

.history-item__date {
  margin-top: 4px;
  color: var(--color-text-muted);
  font-size: 0.82rem;
}

.history-item__metrics {
  display: flex;
  justify-content: space-between;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
  color: var(--color-text);
}

.history-item__actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

@media (max-width: 980px) {
  .app-header {
    grid-template-columns: 1fr auto;
  }

  .nav {
    grid-column: 1 / -1;
    justify-content: flex-start;
    overflow-x: auto;
  }

  .app-body {
    top: 112px;
  }

  .app-content {
    min-height: calc(100vh - 112px);
    padding: 18px;
  }
}

@media (max-width: 720px) {
  .app-header {
    padding: 12px 16px;
  }

  .brand__mark {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    font-size: 0.72rem;
  }

  .brand__title {
    font-size: 0.98rem;
  }

  .brand__subtitle {
    display: none;
  }

  .app-content {
    padding: 14px;
  }
}
</style>

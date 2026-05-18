import './assets/main.css'
import './assets/theme.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/themeStore'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)

const themeStore = useThemeStore(pinia)
themeStore.initTheme()

app.use(router)
app.mount('#app')

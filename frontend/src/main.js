import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
// ИМПОРТИРУЕМ ГЛОБАЛЬНЫЕ СТИЛИ
import './assets/main.css'

// --- ДОБАВИТЬ ИМПОРТ ---
import { useAuthStore } from './store/auth'

const app = createApp(App)
const pinia = createPinia() // <-- Создаем экземпляр Pinia

app.use(pinia) // <-- Используем Pinia

// --- НАЧАЛО НОВОГО БЛОКА ---
// Получаем доступ к authStore после того, как Pinia была установлена
const authStore = useAuthStore()

// Проверяем наличие токена и пытаемся загрузить данные пользователя
// ДО монтирования приложения.
async function initializeApp() {
  if (authStore.token) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error("Failed to fetch user on startup, logging out.", error)
      // Если токен есть, но он невалидный, очищаем состояние
      authStore.logout()
    }
  }

  // Только после этого монтируем приложение
  app.use(router)
  app.mount('#app')
}

initializeApp()
// --- КОНЕЦ НОВОГО БЛОКА ---
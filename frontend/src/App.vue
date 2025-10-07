<template>
  <div id="app-wrapper">
    <header class="app-header" v-if="authStore.token">
      <nav class="nav-container">
        <router-link to="/" class="nav-logo">Plotix</router-link>
        <!-- (Задача 9.1) Новая ссылка -->
        <router-link to="/friends" class="nav-link">Друзья</router-link>
        <router-link to="/feed" class="nav-link">Лента</router-link> <!-- Ссылка на страницу ленты -->
        <div class="nav-user-info">
          <span v-if="authStore.user">{{ authStore.user.email }}</span>
          <NotificationBell /> <!-- Наш новый компонент -->
          <button @click="authStore.logout()" class="btn btn-secondary">Выйти</button>
        </div>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { useRouter } from 'vue-router'; // ИЗМЕНЕНИЕ: Импортируем useRouter
import { useAuthStore } from './store/auth';
import { useListsStore } from './store/lists';
import { themes } from './themes.js';
// Импортируем NotificationBell и useNotificationStore
import NotificationBell from './components/NotificationBell.vue';
import { useNotificationStore } from './store/notifications';
// --- ИМПОРТИРУЕМ СЕРВИС ---
import { websocketService } from '@/services/websocket.js';

const authStore = useAuthStore();
const listsStore = useListsStore();
const notificationStore = useNotificationStore(); // Получаем экземпляр
const router = useRouter(); // ИЗМЕНЕНИЕ: Получаем доступ к роутеру

// Функция для применения стилей темы
const applyTheme = (themeName) => {
  const theme = themes[themeName] || themes.default;
  for (const [key, value] of Object.entries(theme.styles)) {
    document.documentElement.style.setProperty(key, value);
  }
};

// Этот наблюдатель отвечает за применение темы, КОГДА МЫ НАХОДИМСЯ НА СТРАНИЦЕ СПИСКА.
// Он срабатывает, когда данные о списке загружаются в хранилище.
watch(() => listsStore.currentList, (newList) => {
  if (newList && newList.theme_name) {
    applyTheme(newList.theme_name);
  } else {
    // Если данные списка сброшены или не удалось загрузить, применяем тему по умолчанию.
    applyTheme('default');
  }
}, { deep: true });


// ИЗМЕНЕНИЕ: Добавлен новый наблюдатель за сменой маршрута.
// Этот наблюдатель отвечает за СБРОС темы, КОГДА МЫ УХОДИМ со страницы списка.
watch(() => router.currentRoute.value.name, (routeName) => {
  // Если мы перешли на любую страницу, которая НЕ является страницей просмотра списка,
  // то принудительно сбрасываем тему на стандартную.
  if (routeName !== 'ListView' && routeName !== 'PublicListView') {
    applyTheme('default');
  }
});

// (Новое) Следим за изменением токена (логин/логаут)
watch(() => authStore.token, (newToken) => {
  if (newToken) {
    // Если пользователь вошел, запускаем опрос
    notificationStore.fetchNotifications(); // Загружаем начальные уведомления
    websocketService.connect(); // Устанавливаем WebSocket соединение
  } else {
    // Если вышел - останавливаем
    websocketService.disconnect(); // Закрываем соединение
  }
});


onMounted(() => {
  if (authStore.token && !authStore.user) {
    authStore.fetchUser();
  }
  // Применяем тему по умолчанию при самой первой загрузке приложения
  applyTheme('default');
  
  // (Новое) При монтировании App.vue, если пользователь авторизован,
  // запускаем опрос уведомлений
  if (authStore.token) {
    notificationStore.fetchNotifications();
    websocketService.connect();
  }
});

</script>

<style scoped>
.app-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 2rem;
  border-bottom: 1px solid var(--border-color, #dee2e6);
  position: sticky;
  top: 0;
  z-index: 100;
  /* ИЗМЕНЕНИЕ: Делаем шапку полупрозрачной для лучшего вида с цветными фонами */
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(5px);
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: bold;
  /* ИЗМЕНЕНИЕ: Цвет логотипа теперь берется из CSS переменной */
  color: var(--text-color, #333);
}

.nav-user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-user-info span {
  font-weight: 500;
  /* ИЗМЕНЕНИЕ: Цвет текста email теперь берется из CSS переменной */
  color: var(--text-color, #333);
}

.nav-user-info .btn {
  padding: 0.5rem 1rem;
}
</style>
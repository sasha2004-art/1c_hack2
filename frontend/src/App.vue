<template>
  <div id="app-wrapper">
    <header class="app-header" v-if="authStore.token">
      <nav class="nav-container">
        <div class="nav-left">
          <router-link to="/" class="nav-logo">Plotix</router-link>
          <router-link to="/public/feed" class="btn btn-primary nav-feed-btn">Лента</router-link>
        </div>
        <div class="nav-user-info">
          <router-link v-if="authStore.user" to="/profile" class="user-email-link">
            {{ authStore.user.nickname || authStore.user.email }}
          </router-link>
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

const authStore = useAuthStore();
const listsStore = useListsStore();
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


onMounted(() => {
  if (authStore.token && !authStore.user) {
    authStore.fetchUser();
  }
  // Применяем тему по умолчанию при самой первой загрузке приложения
  applyTheme('default');
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

.nav-left {
  display: flex;
  align-items: center;
  gap: 1.5rem; /* Отступ между логотипом и кнопкой "Лента" */
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--text-color, #333);
  margin-right: 1.5rem; /* Добавляем отступ справа от логотипа */
}

.nav-feed-btn {
  margin-right: auto; /* Сдвигает кнопку "Лента" влево */
  margin-left: 0.5rem; /* Небольшой отступ от логотипа */
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

.user-email-link {
  font-weight: 600; /* Делаем шрифт чуть жирнее */
  color: var(--text-color, #333);
  text-decoration: none;
  transition: color 0.3s ease, text-decoration 0.3s ease; /* Добавляем плавный переход */
}

.user-email-link:hover {
  color: var(--primary-color, #007bff); /* Изменяем цвет при наведении на основной */
  text-decoration: underline;
}

.nav-container .btn {
  padding: 0.7rem 1.5rem; /* Применяем общий padding для всех кнопок в nav-container */
  font-size: 1rem;
}
</style>
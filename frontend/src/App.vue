<template>
  <div id="app-wrapper">
    <header class="app-header" v-if="authStore.token">
      <nav class="nav-container">
        <router-link to="/" class="nav-logo">Plotix</router-link>
        <div class="nav-user-info">
          <span v-if="authStore.user">{{ authStore.user.email }}</span>
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
import { useAuthStore } from './store/auth';
import { useListsStore } from './store/lists';
import { themes } from './themes.js';

const authStore = useAuthStore();
const listsStore = useListsStore();

// --- ЛОГИКА ПРИМЕНЕНИЯ ТЕМЫ ---
// Эта функция применяет стили из объекта темы к корневому элементу <html>
const applyTheme = (themeName) => {
  const theme = themes[themeName] || themes.default; // Если темы нет, ставим по умолчанию
  if (theme) {
    for (const [key, value] of Object.entries(theme.styles)) {
      document.documentElement.style.setProperty(key, value);
    }
  }
};

// Следим за изменением текущего списка в хранилище (Pinia).
// Когда пользователь переходит на страницу списка, эта функция применит его тему.
watch(() => listsStore.currentList, (newList) => {
  if (newList && newList.theme_name) {
    applyTheme(newList.theme_name);
  } else {
    // Если мы не на странице списка (например, на главной), применяем тему по умолчанию.
    applyTheme('default');
  }
}, { deep: true });

onMounted(() => {
  // При первоначальной загрузке приложения, если есть токен, получаем данные пользователя
  if (authStore.token && !authStore.user) {
    authStore.fetchUser();
  }
  // Применяем тему по умолчанию при старте
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
  color: var(--text-color, #333);
}

.nav-user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-user-info span {
  font-weight: 500;
}

.nav-user-info .btn {
  padding: 0.5rem 1rem;
}
</style>
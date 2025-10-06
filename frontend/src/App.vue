<template>
  <div id="app-container">
    <header v-if="authStore.token">
      <nav>
        <router-link to="/">Главная</router-link>
        <div class="user-info">
          <span>{{ authStore.user?.email }}</span>
          <button @click="handleLogout">Выйти</button>
        </div>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from './store/auth';

const authStore = useAuthStore();

onMounted(() => {
  // При загрузке приложения проверяем, есть ли токен, и загружаем данные пользователя
  if (authStore.token) {
    authStore.fetchUser();
  }
});

const handleLogout = () => {
  authStore.logout();
};
</script>

<style>
/* Стили для всего приложения */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  margin: 0;
  background-color: #f0f2f5;
  color: #333;
}

#app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

header {
  background-color: #fff;
  padding: 1rem 2rem;
  border-bottom: 1px solid #ddd;
  margin-bottom: 2rem;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

button {
    background-color: #42b983;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
}

button:hover {
    background-color: #36a46e;
}

button.secondary {
    background-color: #f0f0f0;
    color: #333;
    border: 1px solid #ccc;
}
button.secondary:hover {
    background-color: #e0e0e0;
}

button.danger {
    background-color: #e74c3c;
}
button.danger:hover {
    background-color: #c0392b;
}

</style>
<template>
  <div id="app-wrapper">
    <header class="app-header" v-if="authStore.token">
      <nav class="nav-container">
        <div class="nav-left">
          <router-link to="/" class="nav-logo">Plotix Blog</router-link>
          <router-link to="/" class="nav-link" active-class="nav-link-active">Мои списки</router-link>
          <router-link to="/feed" class="nav-link" active-class="nav-link-active">Лента друзей</router-link>
          <router-link to="/friends" class="nav-link" active-class="nav-link-active">Друзья</router-link>
        </div>
        <div class="nav-right">
          <span v-if="authStore.user" class="user-email">{{ authStore.user.email }}</span>
          <NotificationBell />
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
import { useRouter } from 'vue-router';
import { useAuthStore } from './store/auth';
import { useListsStore } from './store/lists';
import { themes } from './themes.js';
import NotificationBell from './components/NotificationBell.vue';
import { useNotificationStore } from './store/notifications';
import { websocketService } from '@/services/websocket.js';

const authStore = useAuthStore();
const listsStore = useListsStore();
const notificationStore = useNotificationStore();
const router = useRouter();

const applyTheme = (themeName) => {
  const theme = themes[themeName] || themes.default;
  for (const [key, value] of Object.entries(theme.styles)) {
    document.documentElement.style.setProperty(key, value);
  }
};

watch(() => listsStore.currentList, (newList) => {
  if (newList && newList.theme_name) {
    applyTheme(newList.theme_name);
  } else {
    applyTheme('default');
  }
}, { deep: true });

watch(() => router.currentRoute.value.name, (routeName) => {
  if (routeName !== 'ListView' && routeName !== 'PublicListView') {
    applyTheme('default');
  }
});

watch(() => authStore.token, (newToken) => {
  if (newToken) {
    notificationStore.fetchNotifications();
    websocketService.connect();
  } else {
    websocketService.disconnect();
  }
});

onMounted(() => {
  if (authStore.token && !authStore.user) {
    authStore.fetchUser();
  }
  applyTheme('default');
  
  if (authStore.token) {
    notificationStore.fetchNotifications();
    websocketService.connect();
  }
});
</script>

<style scoped>
.app-header {
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  height: 64px;
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.nav-logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
}
.nav-logo:hover {
  text-decoration: none;
}

.nav-link {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-color);
  opacity: 0.7;
  padding: var(--space-sm) 0;
  border-bottom: 3px solid transparent;
  transition: opacity 0.2s, border-color 0.2s;
}

.nav-link:hover {
  opacity: 1;
  text-decoration: none;
}

.nav-link-active {
  opacity: 1;
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.user-email {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-color);
  opacity: 0.6;
}
</style>
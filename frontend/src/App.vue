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
          <!-- Блок пользователя с выпадающим меню -->
          <div class="user-menu-container" v-if="authStore.user" v-click-outside="closeUserMenu">
            <button @click="toggleUserMenu" class="user-menu-button">
              {{ authStore.user.email }}
              <span class="arrow" :class="{ 'up': isUserMenuOpen }">▼</span>
            </button>
            <transition name="fade">
              <div v-if="isUserMenuOpen" class="user-menu-dropdown">
                <router-link :to="{ name: 'UserProfile', params: { userId: authStore.user.id } }" class="dropdown-item">Мой профиль</router-link>
                <router-link to="/settings" class="dropdown-item">Настройки</router-link>
                <div class="dropdown-divider"></div>
                <button @click="authStore.logout()" class="dropdown-item dropdown-item-button">Выйти</button>
              </div>
            </transition>
          </div>
          <!-- Конец блока пользователя -->
          <NotificationBell />
        </div>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
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

// --- Логика для выпадающего меню ---
const isUserMenuOpen = ref(false);
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value;
};
const closeUserMenu = () => {
  isUserMenuOpen.value = false;
};
const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event, el);
      }
    };
    document.body.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.body.removeEventListener('click', el.clickOutsideEvent);
  },
};
// --- Конец логики меню ---

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
  closeUserMenu(); // Закрываем меню при смене роута
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
/* Анимация для выпадающего меню */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
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
.user-menu-container {
  position: relative;
}
.user-menu-button {
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  color: var(--text-color);
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 4px;
}
.user-menu-button:hover {
  opacity: 1;
}
.arrow {
  display: inline-block;
  transition: transform 0.2s;
}
.arrow.up {
  transform: rotate(180deg);
}
.user-menu-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background-color: #fff;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--shadow-2);
  z-index: 1001;
  width: 200px;
  padding: 0.5rem 0;
}
.dropdown-item {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  color: var(--text-color);
  text-decoration: none;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
}
.dropdown-item:hover {
  background-color: #f5f5f5;
  text-decoration: none;
}
.dropdown-item-button {
  color: var(--destructive-color);
}
.dropdown-divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 0.5rem 0;
}
</style>
<template>
  <div class="list-view-container" v-if="!listsStore.isLoading && currentList">
    <header class="list-header">
      <h1>{{ currentList.title }}</h1>
      <p v-if="currentList.description">{{ currentList.description }}</p>
    </header>

    <div v-if="currentList.list_type !== 'wishlist' && authStore.token" class="info-banner">
      Это не вишлист, поэтому функционал бронирования недоступен.
    </div>
    
    <div class="items-grid">
      <div class="item-card" v-for="item in currentList.items" :key="item.id">
        <h3>{{ item.title }}</h3>
        <div class="item-description" v-if="item.description" v-html="item.description"></div>
        
        <!-- Блок с кнопками бронирования -->
        <div class="item-actions" v-if="currentList.list_type === 'wishlist'">
          <button 
            v-if="!item.is_reserved" 
            @click="handleReserve(item.id)" 
            class="btn btn-primary">
            🎁 Забронировать
          </button>
          <button 
            v-else-if="isReservedByCurrentUser(item.id)" 
            @click="handleUnreserve(item.id)" 
            class="btn btn-secondary">
            ❌ Снять бронь
          </button>
          <button v-else class="btn btn-disabled" disabled>
            ✅ Забронировано
          </button>
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="listsStore.isLoading" class="loading-indicator">
    Загрузка...
  </div>
  <div v-else class="error-message">
    <h2>Ошибка</h2>
    <p>{{ listsStore.error || 'Не удалось найти этот список.' }}</p>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth';
import { themes } from '@/themes.js';

const route = useRoute();
const router = useRouter();
const listsStore = useListsStore();
const authStore = useAuthStore();

const currentList = computed(() => listsStore.currentList);
const userReservations = computed(() => listsStore.userReservations);

// Проверяет, забронирован ли элемент ТЕКУЩИМ пользователем
const isReservedByCurrentUser = (itemId) => {
  return userReservations.value.some(res => res.item_id === itemId);
};

const handleReserve = (itemId) => {
  if (!authStore.token) {
    // Если пользователь не авторизован, перенаправляем на страницу входа
    router.push({ name: 'Login' });
    return;
  }
  // ИЗМЕНЕНИЕ: Передаем publicKey из URL
  listsStore.reserveItem(itemId, route.params.publicKey).catch(err => {
    alert(`Ошибка: ${listsStore.error}`);
  });
};

const handleUnreserve = (itemId) => {
  // ИЗМЕНЕНИЕ: Передаем publicKey из URL
  listsStore.unreserveItem(itemId, route.params.publicKey).catch(err => {
    alert(`Ошибка: ${listsStore.error}`);
  });
};


const applyTheme = (themeName) => {
  const theme = themes[themeName] || themes.default;
  for (const [key, value] of Object.entries(theme.styles)) {
    document.documentElement.style.setProperty(key, value);
  }
};

onMounted(async () => {
  const publicKey = route.params.publicKey;
  await listsStore.fetchPublicListByKey(publicKey);

  if (currentList.value) {
    applyTheme(currentList.value.theme_name);
    // Если пользователь авторизован, загружаем его бронирования
    if (authStore.token) {
      await listsStore.fetchUserReservations();
    }
  }
});
</script>

<style scoped>
/* Стили можно взять из ListView.vue или адаптировать */
.list-view-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  color: var(--text-color);
}

.list-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.list-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.item-card {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.item-card h3 {
  margin-top: 0;
  color: var(--primary-color);
}

.item-description {
  flex-grow: 1;
  margin-bottom: 1rem;
  word-wrap: break-word;
}

/* Стили для изображений внутри описания */
.item-description :deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.item-actions {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}
.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background-color: var(--secondary-color);
  color: var(--secondary-text-color);
}
.btn-secondary:hover {
  opacity: 0.9;
}

.btn-disabled {
  background-color: #ccc;
  color: #666;
  cursor: not-allowed;
}

.info-banner {
  background-color: var(--edit-color);
  color: var(--edit-text-color);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 2rem;
}
</style>
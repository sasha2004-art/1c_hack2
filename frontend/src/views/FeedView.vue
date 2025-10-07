<template>
  <div class="feed-view container">
    <h1>Лента друзей</h1>
    
    <p v-if="!isAuthenticated" class="info-message">
      Войдите, чтобы увидеть списки ваших друзей.
    </p>

    <div v-else-if="loading" class="loading-message">
      Загрузка списков...
    </div>

    <div v-else-if="error" class="error-message">
      Ошибка при загрузке списков: {{ error }}
    </div>

    <div v-else-if="lists.length === 0" class="info-message">
      Пока нет списков от ваших друзей. Добавьте друзей или попросите их создать публичные списки!
    </div>

    <div v-else class="lists-grid">
      <ListCard 
        v-for="list in lists" 
        :key="list.id" 
        :list="list" 
        :isOwner="list.owner_id === user?.id"
      />
    </div>

    <Pagination
      v-if="lists.length > 0"
      :currentPage="currentPage"
      :totalItems="totalItems"
      :itemsPerPage="itemsPerPage"
      @page-change="handlePageChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { apiClient } from '../store/auth';
import { useAuthStore } from '../store/auth';
import { storeToRefs } from 'pinia';
import ListCard from '../components/ListCard.vue';
import Pagination from '../components/Pagination.vue';

const authStore = useAuthStore();
const { user, token } = storeToRefs(authStore);

const lists = ref([]);
const currentPage = ref(1);
const totalItems = ref(0);
const itemsPerPage = 10; // Должно соответствовать лимиту бэкенда
const loading = ref(false);
const error = ref(null);

const isAuthenticated = computed(() => !!token.value);

const fetchFriendsLists = async () => {
  if (!isAuthenticated.value) {
    lists.value = [];
    totalItems.value = 0;
    return;
  }

  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get('/feed/friends-lists', {
      params: {
        skip: (currentPage.value - 1) * itemsPerPage,
        limit: itemsPerPage
      }
    });
    lists.value = response.data;
    // Так как бэкенд не возвращает общее количество, 
    // нам нужно будет предположить его на основе полученных данных.
    // В реальном приложении бэкенд должен возвращать total_count.
    // Для простоты пока предположим, что если элементов меньше лимита, это последняя страница.
    if (response.data.length < itemsPerPage) {
      totalItems.value = (currentPage.value - 1) * itemsPerPage + response.data.length;
    } else {
      // Если мы получили полную страницу, это может быть не последняя. Увеличиваем totalItems
      // на 1, чтобы позволить перейти на следующую страницу (если там есть данные).
      // Это упрощение, в идеале бэкенд должен возвращать общее количество.
      totalItems.value = currentPage.value * itemsPerPage + 1; 
    }

  } catch (e) {
    error.value = e.message || 'Неизвестная ошибка';
    console.error('Ошибка при загрузке ленты друзей:', e);
  } finally {
    loading.value = false;
  }
};

const handlePageChange = (page) => {
  currentPage.value = page;
};

onMounted(() => {
  fetchFriendsLists();
});

watch(currentPage, () => {
  fetchFriendsLists();
});

// Добавим вотчер для token.value, чтобы обновлять ленту при входе/выходе
watch(token, (newToken) => {
  if (newToken) {
    fetchFriendsLists();
  } else {
    lists.value = [];
    totalItems.value = 0;
  }
});
</script>

<style scoped>
.feed-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: var(--text-color);
  text-align: center;
  margin-bottom: 30px;
}

.info-message, .loading-message, .error-message {
  text-align: center;
  color: var(--text-color-light);
  font-size: 1.1em;
  margin-top: 30px;
}

.error-message {
  color: var(--error-color);
}

.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}
</style>

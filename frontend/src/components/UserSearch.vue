<template>
  <div class="user-search">
    <!-- ИЗМЕНЕНИЕ ЗДЕСЬ: убран слэш в конце тега input -->
    <input 
      type="text" 
      v-model="searchQuery" 
      @input="handleSearch"
      placeholder="Поиск по email или имени..." 
    >
    <div v-if="friendsStore.isLoading">Загрузка...</div>
    <ul v-if="searchResults.length > 0" class="search-results">
      <li v-for="user in searchResults" :key="user.id">
        <router-link :to="{ name: 'UserProfile', params: { userId: user.id } }">
          {{ user.name }} ({{ user.email }})
        </router-link>
      </li>
    </ul>
    <div v-if="!friendsStore.isLoading && searchQuery && searchResults.length === 0">
      Пользователи не найдены.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useFriendsStore } from '@/store/friends';

const friendsStore = useFriendsStore();
const searchQuery = ref('');

// Компьютед свойство для удобного доступа к результатам
const searchResults = computed(() => friendsStore.searchResults);

let searchTimeout = null;

const handleSearch = () => {
  clearTimeout(searchTimeout);
  // Добавляем задержку, чтобы не отправлять запрос на каждое нажатие клавиши
  searchTimeout = setTimeout(() => {
    friendsStore.searchUsers(searchQuery.value);
  }, 300);
};
</script>

<style scoped>
/* Стили для компонента поиска */
.user-search input {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}
.search-results {
  list-style: none;
  padding: 0;
  margin-top: 10px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}
.search-results li {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color);
}
.search-results li:last-child {
  border-bottom: none;
}
</style>
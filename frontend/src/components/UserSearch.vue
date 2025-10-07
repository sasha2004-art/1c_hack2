<template>
  <div class="search-container">
    <h4>Найти пользователей</h4>
    <input 
      type="text" 
      v-model="searchQuery" 
      @input="onSearch" 
      placeholder="Введите email..."
      class="search-input"
    />
    <div v-if="store.isLoading">Поиск...</div>
    <ul v-if="store.searchResults.length" class="search-results">
      <li v-for="user in store.searchResults" :key="user.id">
        <router-link :to="{ name: 'UserProfile', params: { userId: user.id } }">
          {{ user.email }}
        </router-link>
      </li>
    </ul>
    <p v-if="searchQuery && !store.searchResults.length && !store.isLoading">
      Пользователи не найдены.
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useFriendsStore } from '@/store/friends';

const store = useFriendsStore();
const searchQuery = ref('');
let searchTimeout = null;

const onSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    store.searchUsers(searchQuery.value);
  }, 300); // Задержка для предотвращения слишком частых запросов
};
</script>

<style scoped>
.search-container {
  padding: 1rem;
  background-color: rgba(0,0,0,0.05);
  border-radius: 8px;
  margin-bottom: 2rem;
}
.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 5px;
}
.search-results {
  list-style-type: none;
  padding: 0;
  margin-top: 0.5rem;
}
.search-results li a {
  display: block;
  padding: 0.5rem;
  text-decoration: none;
  color: var(--primary-color);
  border-radius: 5px;
}
.search-results li a:hover {
  background-color: rgba(0,0,0,0.05);
}
</style>
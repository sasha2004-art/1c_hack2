<template>
  <div class="public-list-container" :style="containerStyle">
    <div v-if="isLoading" class="status-message">Загрузка списка...</div>
    <div v-else-if="error" class="status-message error">{{ error }}</div>
    <div v-else-if="list" class="list-content">
      <h1>{{ list.title }}</h1>
      <p v-if="list.description">{{ list.description }}</p>
      
      <hr>

      <h2>Элементы списка:</h2>
      <ul v-if="list.items.length > 0" class="items-list">
        <li v-for="item in list.items" :key="item.id">
          <ItemCard :item="item" :is-public-view="true" :is-owner="isOwner" /> 
        </li>
      </ul>
      <p v-else>В этом списке пока нет элементов.</p>
    </div>
    <div v-else class="status-message">Список не найден.</div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useListsStore } from '../store/lists';
import { useAuthStore } from '../store/auth'; // Импортируем useAuthStore
import { storeToRefs } from 'pinia';
import { themes } from '../themes.js'; // Импортируем наши темы
import ItemCard from '../components/ItemCard.vue'; // Импортируем ItemCard

const props = defineProps({
  publicKey: {
    type: String,
    required: true
  }
});

const listsStore = useListsStore();
// Используем currentList, так как он будет заполнен данными публичного списка
const { currentList: list, isLoading, error } = storeToRefs(listsStore);

const authStore = useAuthStore(); // Инициализируем authStore
const { currentUser } = storeToRefs(authStore); // Получаем текущего пользователя

const isOwner = computed(() => {
  return currentList.value && currentUser.value && currentList.value.owner_id === currentUser.value.id;
});

onMounted(() => {
  // Вызываем новую функцию из стора
  listsStore.fetchPublicListByKey(props.publicKey);
});

// (Задача 1.5) Обновленное вычисляемое свойство для стилей
const containerStyle = computed(() => {
  if (!list.value || !list.value.theme_name) {
    return themes.default.styles; // Тема по умолчанию
  }
  const theme = themes[list.value.theme_name] || themes.default;
  return theme.styles;
});
</script>

<style scoped>
.public-list-container {
  min-height: 100vh;
  padding: 2rem;
  /* Применяем переменные из themes.js */
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: var(--font-family);
  background-image: var(--bg-image);
  
  transition: all 0.5s ease;
}
.list-content {
  /* Фон контента делаем полупрозрачным, чтобы тема была видна */
  background-color: rgba(255, 255, 255, 0.85);
  /* Цвет текста для контента берем из темы, но делаем его непрозрачным */
  color: var(--text-color);
  padding: 2rem;
  border-radius: 8px;
  max-width: 800px;
  margin: auto;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}
.status-message {
  text-align: center;
  font-size: 1.5rem;
  padding: 3rem;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
}
.status-message.error {
  color: #d9534f;
}
.items-list {
  list-style-type: none;
  padding: 0;
}
.items-list li {
  background-color: #f9f9f9;
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 5px;
}
</style>
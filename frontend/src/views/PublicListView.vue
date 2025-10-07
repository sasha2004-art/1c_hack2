<template>
  <div class="public-list-view" v-if="list" :style="themeStyles">
    <div class="container">
      <header class="list-header">
        <h1>{{ list.title }}</h1>
        <p v-if="list.description">{{ list.description }}</p>
      </header>

      <div v-if="isLoading" class="loader">Загрузка...</div>
      <div v-if="error" class="error-message">{{ error }}</div>

      <div class="items-grid" v-if="list.items && list.items.length > 0">
        <div class="item-card" v-for="item in list.items" :key="item.id">
          <img v-if="item.thumbnail_url" :src="`http://localhost:8000${item.thumbnail_url}`" alt="Item image" class="item-image"/>
          <h3>{{ item.title }}</h3>
          <p v-if="item.description" class="item-description" v-html="item.description"></p>
          
          <div class="card-footer">
            <div class="interactions">
              <span>❤️ {{ item.likes_count }}</span>
              <span>💬 {{ item.comments.length }}</span>
            </div>
            
            <!-- ====== БЛОК С ЛОГИКОЙ КНОПОК БРОНИРОВАНИЯ ====== -->
            <div class="actions">
              <!-- Кнопка "Забронировать" -->
              <button 
                v-if="canReserve(item)" 
                @click="handleReserve(item.id)" 
                class="btn btn-primary"
              >
                Забронировать
              </button>

              <!-- Индикатор, если забронировано кем-то другим -->
              <span v-if="item.is_reserved && !isReservedByMe(item.id)" class="reserved-badge">
                Уже забронировано
              </span>

              <!-- Кнопка "Снять бронь" -->
              <button 
                v-if="isReservedByMe(item.id)" 
                @click="handleUnreserve(item.id)" 
                class="btn btn-secondary"
              >
                Снять бронь
              </button>
            </div>
            <!-- ====================================================== -->
          </div>
        </div>
      </div>
       <div v-else class="empty-list-message">
        В этом списке пока нет элементов.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth';
import { themes } from '@/themes.js';

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore();

const publicKey = ref(route.params.publicKey);

// --- Жизненный цикл ---
onMounted(async () => {
  // Убеждаемся, что данные пользователя загружены, если он авторизован
  if (authStore.token) {
    await authStore.fetchUser();
    // Загружаем бронирования текущего пользователя
    await listsStore.fetchUserReservations();
  }
  // Загружаем данные публичного списка
  await listsStore.fetchPublicListByKey(publicKey.value);
});

// --- Вычисляемые свойства ---
const list = computed(() => listsStore.currentList);
const isLoading = computed(() => listsStore.isLoading);
const error = computed(() => listsStore.error);
const currentUser = computed(() => authStore.user);
const userReservations = computed(() => listsStore.userReservations);

// Ключевая проверка: является ли текущий пользователь владельцем списка
const isOwner = computed(() => {
  if (!currentUser.value || !list.value || !list.value.owner) {
    return false;
  }
  return currentUser.value.id === list.value.owner.id;
});

// Стили для темы
const themeStyles = computed(() => {
    if (list.value && themes[list.value.theme_name]) {
        return themes[list.value.theme_name].styles;
    }
    return themes.default.styles;
});

// --- Методы ---

// Проверяем, забронирован ли элемент текущим пользователем
const isReservedByMe = (itemId) => {
  return userReservations.value.some(res => res.item_id === itemId);
};

// Определяем, можно ли показать кнопку "Забронировать"
const canReserve = (item) => {
  return currentUser.value &&         // 1. Пользователь авторизован
         !isOwner.value &&            // 2. Он НЕ владелец
         list.value?.list_type === 'wishlist' && // 3. Это вишлист
         !item.is_reserved;           // 4. Элемент еще не забронирован
};

// Обработчик бронирования
const handleReserve = async (itemId) => {
  try {
    await listsStore.reserveItem(itemId, publicKey.value);
  } catch (e) {
    alert(e.message || 'Произошла ошибка при бронировании');
  }
};

// Обработчик снятия брони
const handleUnreserve = async (itemId) => {
  try {
    await listsStore.unreserveItem(itemId, publicKey.value);
  } catch (e) {
    alert(e.message || 'Произошла ошибка при снятии брони');
  }
};

</script>

<style scoped>
.public-list-view {
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: var(--font-family);
  min-height: 100vh;
  padding: 2rem 1rem;
}
.container {
  max-width: 960px;
  margin: 0 auto;
}
.list-header {
  text-align: center;
  margin-bottom: 2rem;
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
  padding: 1rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.item-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 1rem;
}
.item-card h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}
.card-footer {
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.interactions span {
  margin-right: 1rem;
}
.reserved-badge {
  font-size: 0.9rem;
  color: #6c757d;
  font-style: italic;
}
.empty-list-message {
    text-align: center;
    padding: 2rem;
    background-color: var(--card-bg-color);
    border: 1px dashed var(--border-color);
    border-radius: 8px;
}
/* Стили для кнопок (можно вынести в main.css) */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.btn-primary {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}
.btn-secondary {
  background-color: var(--secondary-color);
  color: var(--secondary-text-color);
}
.item-description[data-v-879009ba] img {
  display: block;
  max-width: 100%;
  height: auto;
  max-height: 250px;
  object-fit: cover;
  border-radius: 8px;
  margin-top: 10px;
}
</style>

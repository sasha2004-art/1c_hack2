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
        <ItemCard
          v-for="item in list.items"
          :key="item.id"
          :item="item"
          :list-owner-id="list.owner.id"
          :is-public="true"
          @copy-item="openCopyModal"
        />
      </div>
       <div v-else class="empty-list-message">
        В этом списке пока нет элементов.
      </div>
    </div>
  </div>

  <!-- Этап 10: Модалка выбора списка для копирования -->
  <div v-if="isCopyModalVisible" class="modal-overlay" @click.self="closeCopyModal">
    <div class="modal-content">
      <h3>Скопировать желание в...</h3>
      <p v-if="copyError" class="error-message">{{ copyError }}</p>

      <div v-if="userLists.length > 0">
        <select v-model="selectedListId" class="form-select">
          <option disabled value="">Выберите ваш список</option>
          <option v-for="l in userLists" :key="l.id" :value="l.id">{{ l.title }}</option>
        </select>
        <div class="modal-actions">
          <button @click="closeCopyModal" class="btn btn-secondary">Отмена</button>
          <button @click="handleCopyConfirm" class="btn btn-primary" :disabled="!selectedListId">Подтвердить</button>
        </div>
      </div>
      <div v-else>
        <p>У вас нет списков. Создайте список на главной странице.</p>
        <div class="modal-actions">
          <button @click="closeCopyModal" class="btn btn-secondary">Закрыть</button>
        </div>
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
import ItemCard from '@/components/ItemCard.vue';

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
    // Загружаем свои списки для модального окна копирования
    await listsStore.fetchLists();
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
const userLists = computed(() => listsStore.lists);

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

// --- Этап 10: состояние и методы модалки копирования ---
const isCopyModalVisible = ref(false);
const itemToCopyId = ref(null);
const selectedListId = ref('');
const copyError = ref('');

const openCopyModal = (itemId) => {
  itemToCopyId.value = itemId;
  selectedListId.value = '';
  copyError.value = '';
  isCopyModalVisible.value = true;
};

const closeCopyModal = () => {
  isCopyModalVisible.value = false;
  itemToCopyId.value = null;
  selectedListId.value = '';
};

const handleCopyConfirm = async () => {
  if (!selectedListId.value) return;
  try {
    await listsStore.copyItem(itemToCopyId.value, Number(selectedListId.value));
    alert('Желание успешно скопировано!');
    closeCopyModal();
  } catch (e) {
    copyError.value = listsStore.error || 'Не удалось скопировать элемент';
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

/* Этап 10: стили модалки копирования */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: var(--card-bg-color);
  color: var(--text-color);
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}
.form-select {
  width: 100%;
  padding: 0.5rem;
  margin-top: 1rem;
  margin-bottom: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--bg-color);
  color: var(--text-color);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>

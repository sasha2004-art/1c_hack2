<template>
  <div class="public-list-view" :style="themeStyles">
    <div class="container">
      <!-- --- ИЗМЕНЕНИЕ: Вся логика обернута в v-if/v-else-if --- -->
      
      <!-- 1. Состояние успешной загрузки -->
      <div v-if="list">
        <header class="list-header">
          <h1>{{ list.title }}</h1>
          <p v-if="list.description">{{ list.description }}</p>
        </header>

        <div class="items-grid" v-if="list.items && list.items.length > 0">
          <div
            v-for="item in list.items"
            :key="item.id"
            class="item-wrapper"
          >
            <ItemCard
              :item="item"
              :is-owner="isOwner"
            />
            <!-- Блок с кнопками "Забронировать" и "Копировать" -->
            <div class="public-actions">
              <!-- Кнопки бронирования показываются только для вишлистов и для гостей -->
              <div v-if="list.list_type === 'wishlist' && !isOwner" class="reserve-action">
                <!-- Если элемент забронирован -->
                <button v-if="item.is_reserved"
                        :disabled="!isReservedByMe(item.id)"
                        @click="isReservedByMe(item.id) ? handleUnreserve(item.id) : null"
                        class="btn"
                        :class="isReservedByMe(item.id) ? 'btn-secondary' : 'btn-reserved'">
                  {{ isReservedByMe(item.id) ? 'Снять бронь' : 'Забронировано' }}
                </button>
                <!-- Если элемент можно забронировать -->
                <button v-else-if="canReserve(item)" @click="handleReserve(item.id)" class="btn btn-primary">
                  Забронировать
                </button>
              </div>
              <!-- Кнопка копирования, как и раньше -->
              <button
                v-if="authStore.token && !isOwner"
                class="btn btn-primary copy-button"
                title="Копировать к себе"
                @click="openCopyModal(item.id)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-list-message">
          В этом списке пока нет элементов.
        </div>
      </div>

      <!-- 2. Состояние ошибки (включая ошибку доступа) -->
      <div v-else-if="!isLoading && (error || listAccessErrorDetails)" class="access-denied-container">
        <!-- 2.1 Частный случай: Ошибка доступа к списку друзей -->
        <div v-if="listAccessErrorDetails && listAccessErrorDetails.owner">
          <h2 class="access-denied-title">Доступ ограничен 🔒</h2>
          <p>Этот список доступен только друзьям пользователя <strong>{{ listAccessErrorDetails.owner.name }}</strong>.</p>
          
          <div v-if="authStore.token" class="friend-request-actions">
            <button v-if="!requestSent" @click="handleSendFriendRequest" class="btn btn-primary">
              Отправить заявку в друзья
            </button>
            <div v-else class="request-sent-message">
              ✅ Запрос отправлен!
            </div>
          </div>
          <p v-else>
            <router-link to="/login">Войдите в свой аккаунт</router-link>, чтобы добавить пользователя в друзья.
          </p>
        </div>
        <!-- 2.2 Общий случай: любая другая ошибка -->
        <div v-else>
          <h2 class="access-denied-title">Произошла ошибка</h2>
          <p>{{ error }}</p>
          <router-link to="/" class="btn btn-secondary">Вернуться на главную</router-link>
        </div>
      </div>

      <!-- 3. Состояние загрузки -->
      <div v-else-if="isLoading" class="loader">Загрузка...</div>

    </div>
  </div>

  <!-- Модальное окно копирования (без изменений) -->
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
import { useFriendsStore } from '@/store/friends'; // <-- Импортируем friends store
import { themes } from '@/themes.js';
import ItemCard from '@/components/ItemCard.vue';

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore();
const friendsStore = useFriendsStore(); // <-- Получаем экземпляр

const publicKey = ref(route.params.publicKey);
const requestSent = ref(false); // <-- Новое состояние для кнопки "Добавить в друзья"

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
const listAccessErrorDetails = computed(() => listsStore.listAccessErrorDetails);
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

// --- НОВАЯ ФУНКЦИЯ ДЛЯ ОТПРАВКИ ЗАЯВКИ В ДРУЗЬЯ ---
const handleSendFriendRequest = async () => {
  if (!listAccessErrorDetails.value?.owner?.id) return;
  
  const ownerId = listAccessErrorDetails.value.owner.id;
  try {
    await friendsStore.sendFriendRequest(ownerId);
    requestSent.value = true; // Меняем состояние кнопки на "Запрос отправлен"
  } catch (err) {
    alert(friendsStore.error || 'Не удалось отправить запрос.');
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
  } catch (e)
  {
    copyError.value = listsStore.error || 'Не удалось скопировать элемент';
  }
};

// --- НОВЫЕ ФУНКЦИИ И ЛОГИКА ДЛЯ БРОНИРОВАНИЯ ---

// Проверяем, забронирован ли элемент ТЕКУЩИМ пользователем
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

// Обработчик клика на "Забронировать"
const handleReserve = async (itemId) => {
  try {
    await listsStore.reserveItem(itemId, publicKey.value);
  } catch (e) {
    alert(e.message || 'Произошла ошибка при бронировании');
  }
};

// Обработчик клика на "Снять бронь"
const handleUnreserve = async (itemId) => {
  if (!confirm('Вы уверены, что хотите снять бронь с этого желания?')) return;
  try {
    await listsStore.unreserveItem(itemId, publicKey.value);
  } catch (e) {
    alert(e.message || 'Произошла ошибка при снятии брони');
  }
};

// --- КОНЕЦ НОВОЙ ЛОГИКИ ДЛЯ БРОНИРОВАНИЯ ---

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

.item-wrapper {
  display: flex;
  flex-direction: column;
}

.item-card {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  /* --- ИЗМЕНЕНИЕ: Убираем скругление нижних углов --- */
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  border-radius: 8px 8px 0 0;
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

/* --- ИЗМЕНЕННЫЕ СТИЛИ ДЛЯ НИЖНЕЙ ПАНЕЛИ КАРТОЧКИ --- */
.public-actions {
  display: flex;
  align-items: center;
  justify-content: space-between; /* Размещает элементы по краям */
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 8px 8px;
  background-color: rgba(0,0,0,0.02);
}

.reserve-action {
  flex-grow: 1; /* Занимает все доступное место */
  margin-right: 0.5rem; /* Отступ от кнопки копирования */
}

.reserve-action .btn {
  width: 100%;
}

.btn-reserved {
  background-color: #6c757d;
  color: #fff;
  opacity: 0.7;
  cursor: not-allowed;
}

.btn.copy-button {
  padding: 0.6rem;
  flex-shrink: 0; /* Предотвращает сжатие кнопки */
}

.copy-button svg {
  width: 22px;
  height: 22px;
}
/* --- КОНЕЦ ИЗМЕНЕННЫХ СТИЛЕЙ --- */

/* --- НОВЫЕ СТИЛИ ДЛЯ СТРАНИЦЫ ОШИБКИ --- */
.access-denied-container {
  background-color: var(--card-bg-color);
  color: var(--text-color);
  padding: 3rem 2rem;
  border-radius: 12px;
  text-align: center;
  margin-top: 2rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.access-denied-title {
  font-size: 2rem;
  margin-bottom: 1rem;
}
.access-denied-container p {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}
.friend-request-actions {
  margin-top: 1rem;
}
.request-sent-message {
  font-weight: bold;
  color: #28a745; /* Зеленый цвет для успеха */
  font-size: 1.2rem;
}
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
}
.btn-primary {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}
.btn-secondary {
  background-color: #6c757d;
  color: #fff;
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
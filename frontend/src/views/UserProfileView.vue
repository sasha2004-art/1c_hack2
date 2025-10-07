<template>
  <div class="container">
    <div v-if="friendsStore.isLoading" class="loading-spinner">Загрузка...</div>
    <div v-else-if="friendsStore.error" class="error-message">
      {{ friendsStore.error }}
    </div>
    <div v-else-if="profile" class="profile-card">
      <!-- ИЗМЕНЕНИЕ: Отображаем имя пользователя вместо email -->
      <h2>Профиль пользователя: {{ profile.user_info.name }}</h2>
      <p class="user-email">{{ profile.user_info.email }}</p>

      <!-- Блок с кнопками управления дружбой -->
      <div class="friend-actions">
        <!-- 1. Кнопка "Добавить в друзья" -->
        <button v-if="profile.friendship_status === 'none'" @click="handleAddFriend" class="btn-primary">
          Добавить в друзья
        </button>

        <!-- 2. Кнопка "Отменить запрос" -->
        <button v-if="profile.friendship_status === 'request_sent'" @click="handleCancelRequest" class="btn-secondary">
          Отменить запрос
        </button>
        
        <!-- 3. Кнопка "Удалить из друзей" -->
        <button v-if="profile.friendship_status === 'friends'" @click="handleRemoveFriend" class="btn-danger">
          Удалить из друзей
        </button>

        <!-- 4. Кнопки для входящего запроса -->
        <div v-if="profile.friendship_status === 'request_received'" class="incoming-request-actions">
          <button @click="handleAcceptRequest" class="btn-primary">Принять</button>
          <button @click="handleDeclineRequest" class="btn-secondary">Отклонить</button>
        </div>
      </div>

      <hr>

      <h3>Списки пользователя</h3>
      <div v-if="profile.public_lists && profile.public_lists.length > 0" class="lists-grid">
         <div v-for="list in profile.public_lists" :key="list.id" class="list-card-item">
            <router-link :to="getListLink(list)">
              {{ list.title }} ({{ list.privacy_level }})
            </router-link>
         </div>
      </div>
      <p v-else>У пользователя нет видимых вам списков.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useFriendsStore } from '@/store/friends';

const route = useRoute();
const friendsStore = useFriendsStore();

// Получаем ID пользователя из URL
const userId = computed(() => parseInt(route.params.userId, 10));

// Создаем реактивную ссылку на данные профиля из стора
const profile = computed(() => friendsStore.currentUserProfile);

// --- НОВЫЙ МЕТОД ДЛЯ ГЕНЕРАЦИИ ССЫЛОК ---
const getListLink = (list) => {
  // Если список публичный, всегда используем публичный маршрут
  if (list.privacy_level === 'public') {
    return {
      name: 'PublicListView',
      params: { publicKey: list.public_url_key }
    };
  }
  
  // Для всех остальных видимых списков (например, 'friends_only')
  // используем "личный" маршрут, который требует аутентификации.
  return {
    name: 'ListView',
    params: { id: list.id }
  };
};

// --- ОСНОВНАЯ ЛОГИКА ---

// Функция для обработки клика "Добавить в друзья"
const handleAddFriend = async () => {
  try {
    await friendsStore.sendFriendRequest(userId.value);
    // После успешной отправки стор сам обновит профиль
  } catch (error) {
    // Можно показать уведомление об ошибке
    console.error("Ошибка при отправке запроса:", error);
  }
};

// Функции для отмены/удаления дружбы
const handleCancelRequest = async () => {
  await friendsStore.removeFriend(profile.value.friendship_id);
};
const handleRemoveFriend = async () => {
  await friendsStore.removeFriend(profile.value.friendship_id);
};

// Функции для принятия/отклонения запроса
const handleAcceptRequest = async () => {
  await friendsStore.acceptFriendRequest(profile.value.friendship_id);
};
const handleDeclineRequest = async () => {
  await friendsStore.declineFriendRequest(profile.value.friendship_id);
};

// Загружаем данные профиля при монтировании компонента
onMounted(() => {
  friendsStore.fetchUserProfile(userId.value);
});

// Следим за изменением userId в URL (если пользователь переходит с одного профиля на другой)
watch(userId, (newId) => {
  if (newId) {
    friendsStore.fetchUserProfile(newId);
  }
});
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}
.profile-card {
  background-color: var(--card-bg-color);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}
.user-email {
  color: #6c757d;
  margin-bottom: 1.5rem;
}
.friend-actions {
  margin-bottom: 1.5rem;
}
.incoming-request-actions {
  display: flex;
  gap: 10px;
}
hr {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 1.5rem 0;
}
.lists-grid {
  display: grid;
  gap: 1rem;
}
.list-card-item a {
  display: block;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 5px;
  text-decoration: none;
  color: var(--text-color);
  transition: background-color 0.2s;
}
.list-card-item a:hover {
  background-color: #e9ecef;
}

/* Стили для кнопок */
.btn-primary, .btn-secondary, .btn-danger {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: opacity 0.2s;
}
.btn-primary:hover, .btn-secondary:hover, .btn-danger:hover {
  opacity: 0.85;
}
.btn-primary {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-danger {
  background-color: var(--secondary-color);
  color: var(--secondary-text-color);
}
</style>
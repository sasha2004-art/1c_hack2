<template>
  <div class="friends-container">
    <h2>Управление друзьями</h2>
    
    <!-- (Задача 6.1) Вставляем компонент поиска -->
    <UserSearch />
    
    <div v-if="store.isLoading" class="loading">Загрузка...</div>
    <div v-if="store.error" class="error-message">{{ store.error }}</div>
    
    <div v-if="!store.isLoading" class="friends-sections">
      <!-- Секция: Входящие заявки -->
      <section class="friends-section">
        <h3>Входящие заявки ({{ store.incomingRequests.length }})</h3>
        <ul v-if="store.incomingRequests.length > 0" class="friends-list">
          <li v-for="request in store.incomingRequests" :key="request.id" class="friend-item">
             <!-- (Задача 6.2) Добавляем ссылку -->
            <router-link :to="{ name: 'UserProfile', params: { userId: request.requester.id } }">
              {{ request.requester.email }}
            </router-link>
            <div class="actions">
              <button @click="handleAccept(request.id)" class="btn btn-primary">Принять</button>
              <button @click="handleDecline(request.id)" class="btn btn-secondary">Отклонить</button>
            </div>
          </li>
        </ul>
        <p v-else>Нет входящих заявок.</p>
      </section>
      
      <!-- Секция: Ваши друзья -->
      <section class="friends-section">
        <h3>Ваши друзья ({{ store.friends.length }})</h3>
        <ul v-if="store.friends.length > 0" class="friends-list">
          <li v-for="friend in store.friends" :key="friend.friendship_id" class="friend-item">
             <!-- (Задача 6.2) Добавляем ссылку -->
            <router-link :to="{ name: 'UserProfile', params: { userId: friend.friend_details.id } }">
              {{ friend.friend_details.email }}
            </router-link>
            <div class="actions">
              <button @click="handleRemove(friend.friendship_id)" class="btn btn-danger">Удалить</button>
            </div>
          </li>
        </ul>
        <p v-else>У вас пока нет друзей.</p>
      </section>

      <!-- Секция: Исходящие заявки -->
      <section class="friends-section">
        <h3>Исходящие заявки ({{ store.outgoingRequests.length }})</h3>
        <ul v-if="store.outgoingRequests.length > 0" class="friends-list">
          <li v-for="request in store.outgoingRequests" :key="request.id" class="friend-item">
             <!-- (Задача 6.2) Добавляем ссылку -->
            <router-link :to="{ name: 'UserProfile', params: { userId: request.addressee.id } }">
              {{ request.addressee.email }}
            </router-link>
            <div class="actions">
              <button @click="handleCancel(request.id)" class="btn btn-secondary">Отменить</button>
            </div>
          </li>
        </ul>
        <p v-else>Нет исходящих заявок.</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useFriendsStore } from '@/store/friends';
import UserSearch from '@/components/UserSearch.vue'; // (Задача 6.3) Импортируем компонент

const store = useFriendsStore();

onMounted(() => {
  store.fetchFriendsAndRequests();
});

const handleAccept = async (requestId) => {
  try {
    await store.acceptFriendRequest(requestId);
  } catch (e) {
    // Ошибки уже обрабатываются в сторе, можно добавить доп. логику
    alert('Не удалось выполнить действие.');
  }
};

const handleDecline = async (requestId) => {
  try {
    await store.declineFriendRequest(requestId);
  } catch (e) {
    alert('Не удалось выполнить действие.');
  }
};

const handleRemove = async (friendshipId) => {
    if (confirm('Вы уверены, что хотите удалить этого пользователя из друзей?')) {
        try {
            await store.removeFriend(friendshipId);
        } catch (e) {
            alert('Не удалось выполнить действие.');
        }
    }
};

const handleCancel = async (requestId) => {
    // Отмена исходящей заявки = удаление записи о дружбе
    if (confirm('Вы уверены, что хотите отменить заявку?')) {
        try {
            await store.removeFriend(requestId);
        } catch (e) {
            alert('Не удалось выполнить действие.');
        }
    }
};
</script>

<style scoped>
.friends-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--card-bg-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--text-color);
}

.friends-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.friends-section h3 {
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.friends-list {
  list-style-type: none;
  padding: 0;
}

.friend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 5px;
  transition: background-color 0.2s;
}

.friend-item:nth-child(odd) {
  background-color: rgba(0, 0, 0, 0.03);
}

.friend-item:hover {
    background-color: rgba(0, 0, 0, 0.06);
}

.friend-item span {
    font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
    padding: 0.4rem 0.8rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
    transition: opacity 0.2s;
}
.btn:hover {
    opacity: 0.85;
}
.btn-primary {
    background-color: var(--primary-color);
    color: var(--primary-text-color);
}
.btn-secondary {
    background-color: #6c757d;
    color: #fff;
}
.btn-danger {
    background-color: var(--secondary-color);
    color: var(--secondary-text-color);
}

.friend-item a {
  text-decoration: none;
  color: var(--text-color);
  font-weight: 500;
}
.friend-item a:hover {
  text-decoration: underline;
}

.error-message {
  color: var(--secondary-color);
  text-align: center;
  font-weight: bold;
}
</style>
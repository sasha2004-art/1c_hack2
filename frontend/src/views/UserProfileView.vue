<template>
  <div class="profile-container" v-if="profile">
    <h2>Профиль пользователя: {{ profile.user_info.email }}</h2>
    
    <div class="actions">
      <button 
        v-if="profile.friendship_status === 'none'" 
        @click="handleAddFriend" 
        class="btn btn-primary"
      >
        Добавить в друзья
      </button>
      <button 
        v-if="profile.friendship_status === 'request_sent'" 
        @click="handleCancelRequest" 
        class="btn btn-secondary"
      >
        Отменить заявку
      </button>
      <div v-if="profile.friendship_status === 'request_received'" class="request-received">
        <span>Этот пользователь отправил вам заявку.</span>
        <router-link to="/friends">Перейти к заявкам</router-link>
      </div>
      <button 
        v-if="profile.friendship_status === 'friends'" 
        @click="handleRemoveFriend" 
        class="btn btn-danger"
      >
        Удалить из друзей
      </button>
    </div>

    <section class="public-lists">
      <h3>Публичные списки</h3>
      <ul v-if="profile.public_lists.length">
        <li v-for="list in profile.public_lists" :key="list.id">
          <router-link :to="{ name: 'ListView', params: { id: list.id } }">
            {{ list.title }} ({{ list.list_type }})
          </router-link>
        </li>
      </ul>
      <p v-else>У пользователя нет публичных списков.</p>
    </section>

  </div>
  <div v-else-if="store.isLoading" class="loading">Загрузка профиля...</div>
  <div v-else class="error-message">{{ store.error || 'Профиль не найден.' }}</div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useFriendsStore } from '@/store/friends';

const route = useRoute();
const store = useFriendsStore();

const profile = computed(() => store.currentUserProfile);
const userId = computed(() => route.params.userId);

onMounted(() => {
  store.fetchUserProfile(userId.value);
});

// Перезагрузка данных при смене ID в URL (например, при поиске нового юзера)
watch(userId, (newId) => {
  if (newId) {
    store.fetchUserProfile(newId);
  }
});

const handleAddFriend = () => {
  store.sendFriendRequest(userId.value);
};

const handleCancelRequest = () => {
  if (confirm('Вы уверены, что хотите отменить заявку?')) {
    store.removeFriend(profile.value.friendship_id);
  }
};

const handleRemoveFriend = () => {
  if (confirm('Вы уверены, что хотите удалить этого пользователя из друзей?')) {
    store.removeFriend(profile.value.friendship_id);
  }
};

</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--card-bg-color);
  border-radius: 8px;
}
.actions {
  margin-bottom: 2rem;
}
.public-lists h3 {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
.public-lists ul {
  list-style: none;
  padding: 0;
}
.public-lists a {
  display: block;
  padding: 0.5rem;
  text-decoration: none;
  color: var(--primary-color);
  border-radius: 5px;
}
.public-lists a:hover {
  background-color: rgba(0,0,0,0.05);
}
.btn {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
}
.btn-primary { background-color: var(--primary-color); color: var(--primary-text-color); }
.btn-secondary { background-color: #6c757d; color: #fff; }
.btn-danger { background-color: var(--secondary-color); color: var(--secondary-text-color); }
</style>
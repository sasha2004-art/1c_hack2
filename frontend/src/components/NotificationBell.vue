<!-- frontend/src/components/NotificationBell.vue -->
<template>
  <div class="notification-bell" ref="bellRef">
    <button @click="toggleDropdown" class="bell-button">
      <span class="icon">🔔</span>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>
    <div v-if="isOpen" class="dropdown-menu">
      <div class="dropdown-header">Уведомления</div>
      <div v-if="notifications.length === 0" class="no-notifications">
        Нет новых уведомлений
      </div>
      <ul v-else class="notification-list">
        <li
          v-for="notification in notifications"
          :key="notification.id"
          :class="{ 'is-unread': !notification.is_read }"
          @click="handleNotificationClick(notification)"
        >
          <p>{{ getNotificationText(notification) }}</p>
          <small>{{ new Date(notification.created_at).toLocaleString() }}</small>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useNotificationStore } from '@/store/notifications';
import { useRouter } from 'vue-router';

const store = useNotificationStore();
const { notifications, unreadCount } = storeToRefs(store);
const router = useRouter();

const isOpen = ref(false);
const bellRef = ref(null);

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const getNotificationText = (notification) => {
  const sender = notification.sender.email.split('@')[0];
  switch (notification.type) {
    case 'friend_request':
      return `${sender} отправил вам заявку в друзья.`;
    case 'like':
      return `${sender} понравился ваш элемент.`;
    case 'comment':
      return `${sender} оставил комментарий.`;
    default:
      return 'Новое уведомление.';
  }
};

const handleNotificationClick = async (notification) => {
    // Сначала помечаем как прочитанное, если нужно
    if (!notification.is_read) {
        await store.markAsRead(notification.id);
    }
    
    // --- НАЧАЛО ИЗМЕНЕНИЙ ---
    // Затем выполняем переход в зависимости от типа
    if (notification.type === 'friend_request') {
        router.push({ name: 'Friends' });
    } 
    // Если это лайк или коммент и есть вся нужная информация
    else if ((notification.type === 'like' || notification.type === 'comment') && notification.related_list_id && notification.related_item_id) {
        // Переходим на страницу списка и добавляем хеш для прокрутки к элементу
        router.push({ 
            name: 'ListView', 
            params: { id: notification.related_list_id },
            // Добавляем хеш, чтобы страница знала, к какому элементу прокрутить
            hash: `#item-${notification.related_item_id}` 
        });
    }
    // --- КОНЕЦ ИЗМЕНЕНИЙ ---

    isOpen.value = false; // Закрываем выпадающее меню в любом случае
};

const handleClickOutside = (event) => {
    if (bellRef.value && !bellRef.value.contains(event.target)) {
        isOpen.value = false;
    }
};

onMounted(() => {
    document.addEventListener('click', handleClickOutside);
});
onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
});

</script>

<style scoped>
.notification-bell {
  position: relative;
  display: inline-block;
}
.bell-button {
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
  font-size: 1.5rem;
}
.badge {
  position: absolute;
  top: -5px;
  right: -10px;
  background-color: red;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 0.75rem;
  font-weight: bold;
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--card-bg-color, white);
  border: 1px solid var(--border-color, #ccc);
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 300px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 1000;
}
.dropdown-header {
  padding: 10px;
  font-weight: bold;
  border-bottom: 1px solid var(--border-color, #ccc);
}
.notification-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.notification-list li {
  padding: 10px;
  border-bottom: 1px solid var(--border-color, #eee);
  cursor: pointer;
}
.notification-list li:last-child {
  border-bottom: none;
}
.notification-list li:hover {
  background-color: var(--bg-color, #f9f9f9);
}
.notification-list li.is-unread {
  background-color: var(--edit-color, #f0f8ff);
}
.notification-list li p {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: var(--text-color);
}
.notification-list li small {
  color: #888;
}
.no-notifications {
    padding: 20px;
    text-align: center;
    color: #888;
}
</style>
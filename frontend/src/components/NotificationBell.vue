<template>
  <div class="notification-bell-container" v-click-outside="closeDropdown">
    <div class="bell-icon-wrapper" @click="toggleDropdown">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-bell"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
    </div>

    <div v-if="isDropdownOpen" class="notification-dropdown">
      <div class="dropdown-header">Уведомления</div>
      <div v-if="notifications.length > 0" class="notifications-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="['notification-item', { 'is-read': notification.is_read }]"
          @click="handleNotificationClick(notification)"
        >
          <p class="notification-text">{{ notificationText(notification) }}</p>
          <span class="notification-date">{{ formatDate(notification.created_at) }}</span>
        </div>
      </div>
      <div v-else class="no-notifications">
        У вас нет новых уведомлений.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import { useNotificationStore } from '@/store/notifications';

const notificationStore = useNotificationStore();
const router = useRouter();

const isDropdownOpen = ref(false);

const unreadCount = computed(() => notificationStore.unreadCount);
const notifications = computed(() => notificationStore.notifications);

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

const closeDropdown = () => {
  isDropdownOpen.value = false;
};

// --- ГЛАВНОЕ ИЗМЕНЕНИЕ ЗДЕСЬ ---
// Функция для генерации текста уведомления
const notificationText = (notification) => {
  const senderName = notification.sender.name; // Используем .name вместо .email
  switch (notification.type) {
    case 'friend_request':
      return `${senderName} отправил(а) вам заявку в друзья.`;
    case 'like':
      return `${senderName} понравился ваш элемент.`;
    case 'comment':
      return `${senderName} оставил(а) комментарий.`;
    default:
      return 'Новое уведомление.';
  }
};

const handleNotificationClick = (notification) => {
  // 1. Отмечаем как прочитанное
  if (!notification.is_read) {
    notificationStore.markAsRead(notification.id);
  }

  // 2. Перенаправляем пользователя
  if (notification.type === 'friend_request') {
    router.push({ name: 'Friends' });
  } else if (notification.type === 'like' || notification.type === 'comment') {
    if (notification.related_list_id) {
        // Переходим к списку, в котором находится элемент
        router.push({ name: 'ListView', params: { id: notification.related_list_id } });
    }
  }

  // 3. Закрываем выпадающий список
  closeDropdown();
};


const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('ru-RU', options);
};

// Директива для закрытия dropdown по клику вне элемента
const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event);
      }
    };
    document.body.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.body.removeEventListener('click', el.clickOutsideEvent);
  },
};

onMounted(() => {
  notificationStore.startPolling();
});

onUnmounted(() => {
  notificationStore.stopPolling();
});
</script>

<style scoped>
.notification-bell-container {
  position: relative;
}

.bell-icon-wrapper {
  position: relative;
  cursor: pointer;
  color: #555;
}

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #dc3545;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 10px;
  font-weight: bold;
  line-height: 1;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  width: 320px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  z-index: 1000;
  overflow: hidden;
}

.dropdown-header {
  padding: 12px 16px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
}

.notifications-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item:not(.is-read) {
  background-color: #fffbeb; /* Легкий желтый фон для непрочитанных */
}

.notification-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
}

.notification-date {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  display: block;
}

.no-notifications {
  padding: 20px;
  text-align: center;
  color: #888;
}
</style>
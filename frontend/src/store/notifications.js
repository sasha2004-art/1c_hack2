// frontend/src/store/notifications.js

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth';

export const useNotificationStore = defineStore('notifications', () => {
    const notifications = ref([]);
    const unreadCount = ref(0);
    const error = ref(null);
    let pollInterval = null;

    async function fetchNotifications() {
        try {
            const response = await apiClient.get('/notifications/');
            notifications.value = response.data.notifications;
            unreadCount.value = response.data.unread_count;
            error.value = null;
        } catch (e) {
            error.value = 'Не удалось загрузить уведомления.';
            console.error(e);
        }
    }

    async function markAsRead(notificationId) {
        try {
            const response = await apiClient.post(`/notifications/${notificationId}/read`);
            const index = notifications.value.findIndex(n => n.id === notificationId);
            if (index !== -1 && notifications.value[index].is_read === false) {
                notifications.value[index].is_read = true;
                unreadCount.value = Math.max(0, unreadCount.value - 1);
            }
        } catch (e) {
            console.error('Не удалось отметить уведомление как прочитанное:', e);
        }
    }

    function startPolling() {
        // Предотвращаем запуск нескольких интервалов
        if (pollInterval) clearInterval(pollInterval);
        
        // Запускаем немедленно, а затем каждые 30 секунд
        fetchNotifications();
        pollInterval = setInterval(fetchNotifications, 30000); 
    }

    function stopPolling() {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }

    return {
        notifications,
        unreadCount,
        error,
        fetchNotifications,
        markAsRead,
        startPolling,
        stopPolling
    };
});
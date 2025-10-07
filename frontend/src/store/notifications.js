// frontend/src/store/notifications.js

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth';

// --- ИМПОРТИРУЕМ АУДИОФАЙЛ ---
import notificationSound from '@/assets/audio/notification.mp3';

// --- СОЗДАЕМ АУДИО ОБЪЕКТ ЗАРАНЕЕ ---
const audio = new Audio(notificationSound);
// Настраиваем громкость, чтобы звук был ненавязчивым (0.5 = 50% громкости)
audio.volume = 0.5;

export const useNotificationStore = defineStore('notifications', () => {
    const notifications = ref([]);
    const unreadCount = ref(0);
    const error = ref(null);

    // --- НОВАЯ ФУНКЦИЯ ДЛЯ "РАЗБЛОКИРОВКИ" ---
    function unlockAudioContext() {
      // Проверяем, нужно ли это делать
      if (audio.paused) {
        // Устанавливаем громкость в 0, чтобы пользователь ничего не услышал
        const originalVolume = audio.volume;
        audio.volume = 0;
        
        // Пытаемся воспроизвести
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
          playPromise.then(_ => {
            // Если получилось, сразу ставим на паузу и возвращаем громкость
            audio.pause();
            audio.currentTime = 0;
            audio.volume = originalVolume;
            console.log("Audio context successfully unlocked by user interaction.");
          }).catch(error => {
            // Если даже так не получилось, ничего страшного
            console.warn("Could not unlock audio context on interaction:", error);
            audio.volume = originalVolume; // Возвращаем громкость в любом случае
          });
        }
      }
    }
    // УДАЛЯЕМ: let pollInterval = null;

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
    
    // --- НОВЫЙ ЭКШЕН ---
    function handleNewNotification(notification) {
      // Добавляем новое уведомление в начало списка
      notifications.value.unshift(notification);
      // Увеличиваем счетчик непрочитанных
      unreadCount.value += 1;

      // --- ДОБАВЛЯЕМ ВОСПРОИЗВЕДЕНИЕ ЗВУКА ---
      // Сбрасываем текущее время звука, чтобы он мог проигрываться снова, даже если еще не закончился
      audio.currentTime = 0; 
      audio.play().catch(error => {
        // Современные браузеры могут блокировать авто-воспроизведение звука до первого взаимодействия пользователя со страницей.
        // Эта обработка ошибки предотвратит падение приложения, если звук заблокирован.
        console.warn("Не удалось воспроизвести звук уведомления:", error);
      });
    }

    // УДАЛЯЕМ ФУНКЦИИ startPolling и stopPolling

    return {
        notifications,
        unreadCount,
        error,
        fetchNotifications,
        markAsRead,
        handleNewNotification, // <-- Экспортируем новый экшен
        unlockAudioContext
    };
});
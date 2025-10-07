// frontend/src/services/websocket.js

import { useNotificationStore } from '@/store/notifications';

let ws = null;

export const websocketService = {
  connect() {
    // Предотвращаем создание нескольких соединений
    if (ws && ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket is already connected.');
      return;
    }
    
    // Получаем токен из localStorage
    const token = localStorage.getItem('user-token');
    if (!token) {
      console.error('No token found for WebSocket connection.');
      return;
    }

    // Устанавливаем соединение
    // Используем wss:// для HTTPS и ws:// для HTTP
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = 'localhost:8000'; // Убедитесь, что хост и порт верные
    ws = new WebSocket(`${protocol}://${host}/notifications/ws?token=${token}`);

    ws.onopen = () => {
      console.log('WebSocket connected successfully.');
    };

    ws.onmessage = (event) => {
      const notificationStore = useNotificationStore();
      const newNotification = JSON.parse(event.data);
      // Вызываем экшен в сторе, чтобы обновить состояние
      notificationStore.handleNewNotification(newNotification);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected.');
      ws = null;
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws = null;
    };
  },

  disconnect() {
    if (ws) {
      ws.close();
      ws = null;
    }
  }
};
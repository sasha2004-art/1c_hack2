import { defineStore } from 'pinia';
import { ref } from 'vue';
import router from '../router';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Создаем и экспортируем экземпляр axios здесь
export const apiClient = axios.create({
  baseURL: API_URL,
});

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('user-token') || null);
  const user = ref(null);
  const error = ref(null);
  const successMessage = ref(null); // Для сообщений об успехе

  // Interceptor по-прежнему настраивается здесь, но использует экспортированный apiClient
  apiClient.interceptors.request.use(config => {
    // Важно! Получаем токен из ref'а этого стора
    const currentToken = token.value; 
    if (currentToken) {
      config.headers.Authorization = `Bearer ${currentToken}`;
    }
    return config;
  });

  function setToken(newToken) {
    token.value = newToken;
    if (newToken) {
      localStorage.setItem('user-token', newToken);
    } else {
      localStorage.removeItem('user-token');
    }
  }

  function clearMessages() {
    error.value = null;
    successMessage.value = null;
  }

  async function register(credentials) {
    clearMessages();
    try {
      await apiClient.post('/auth/register', credentials);
      router.push({ name: 'Login' });
    } catch (e) {
      error.value = e.response?.data?.detail || 'Registration failed';
    }
  }

  async function login(credentials) {
    clearMessages();
    try {
      const params = new URLSearchParams();
      params.append('username', credentials.email);
      params.append('password', credentials.password);

      const response = await apiClient.post('/auth/token', params);
      
      setToken(response.data.access_token);
      await fetchUser();
      router.push({ name: 'Home' });
    } catch (e) {
      error.value = e.response?.data?.detail || 'Login failed';
    }
  }

  async function fetchUser() {
    if (!token.value) return;
    try {
      const response = await apiClient.get('/users/me');
      user.value = response.data;
    } catch (e) {
      console.error(e);
      logout();
    }
  }

  function logout() {
    setToken(null);
    user.value = null;
    router.push({ name: 'Login' });
  }

  // --- НОВЫЕ ЭКШЕНЫ ---
  async function updatePassword(passwordData) {
    clearMessages();
    try {
      await apiClient.put('/settings/password', passwordData);
      successMessage.value = 'Пароль успешно обновлен!';
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось обновить пароль.';
      throw e;
    }
  }

  async function updateEmail(emailData) {
    clearMessages();
    try {
      const response = await apiClient.put('/settings/email', emailData);
      user.value = response.data; // Обновляем данные пользователя в сторе
      successMessage.value = 'Email успешно обновлен!';
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось обновить email.';
      throw e;
    }
  }

  async function deleteAccount(password) {
    clearMessages();
    try {
      await apiClient.delete('/settings/account', {
        data: { password: password }
      });
      // После успешного удаления разлогиниваем пользователя
      logout();
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось удалить аккаунт.';
      throw e;
    }
  }

  return { 
    token, user, error, successMessage,
    register, login, logout, fetchUser, 
    updatePassword, updateEmail, deleteAccount,
    clearMessages,
    setToken // <--- ВОТ ИСПРАВЛЕНИЕ
  };
});
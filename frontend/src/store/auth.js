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

  async function register(credentials) {
    try {
      error.value = null;
      await apiClient.post('/auth/register', credentials);
      router.push({ name: 'Login' });
    } catch (e) {
      error.value = e.response?.data?.detail || 'Registration failed';
    }
  }

  async function login(credentials) {
    try {
      error.value = null;
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

  async function updateUser(userData) {
    try {
      error.value = null;
      const response = await apiClient.put('/users/me', userData);
      user.value = response.data; // Обновляем данные пользователя в сторе
      return true; // Успешно обновлено
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to update profile';
      console.error('Error updating user:', e);
      return false; // Ошибка обновления
    }
  }

  function logout() {
    setToken(null);
    user.value = null;
    router.push({ name: 'Login' });
  }

  // Убираем apiClient из возвращаемого объекта
  return { token, user, error, register, login, logout, fetchUser, setToken, updateUser };
});
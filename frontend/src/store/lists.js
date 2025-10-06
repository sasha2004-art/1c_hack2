import { defineStore } from 'pinia';
import { ref } from 'vue';
// Импортируем apiClient напрямую, а не через useAuthStore
import { apiClient } from './auth';

export const useListsStore = defineStore('lists', () => {
  const lists = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  
  // useAuthStore больше не нужен здесь
  // const authStore = useAuthStore(); 

  async function fetchLists() {
    isLoading.value = true;
    error.value = null;
    try {
      // Используем импортированный apiClient
      const response = await apiClient.get('/lists/');
      lists.value = response.data;
    } catch (e) {
      error.value = 'Не удалось загрузить списки.';
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  async function addList(listData) {
    error.value = null;
    try {
      const response = await apiClient.post('/lists/', listData);
      lists.value.push(response.data);
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось создать список.';
      console.error(e);
    }
  }

  async function updateList(listId, listData) {
    error.value = null;
    try {
      const response = await apiClient.put(`/lists/${listId}`, listData);
      const index = lists.value.findIndex(l => l.id === listId);
      if (index !== -1) {
        lists.value[index] = response.data;
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось обновить список.';
      console.error(e);
    }
  }

  async function deleteList(listId) {
    error.value = null;
    try {
      await apiClient.delete(`/lists/${listId}`);
      lists.value = lists.value.filter(l => l.id !== listId);
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось удалить список.';
      console.error(e);
    }
  }

  return { lists, isLoading, error, fetchLists, addList, updateList, deleteList };
});
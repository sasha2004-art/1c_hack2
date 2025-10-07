import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth'; // Импортируем настроенный axios

export const useListsStore = defineStore('lists', () => {
  const lists = ref([]);
  const currentList = ref(null); // Новое состояние для текущего открытого списка
  const publicLists = ref([]); // Новое состояние для публичных списков
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchLists() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/lists/');
      lists.value = response.data;
    } catch (e) {
      error.value = 'Не удалось загрузить списки.';
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  // Новая функция для загрузки одного списка
  async function fetchListById(listId) {
    isLoading.value = true;
    error.value = null;
    currentList.value = null;
    try {
      const response = await apiClient.get(`/lists/${listId}`);
      currentList.value = response.data;
    } catch (e) {
      error.value = 'Не удалось загрузить список.';
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  // Новая функция для получения публичного списка
  async function fetchPublicListByKey(publicKey) {
    isLoading.value = true;
    error.value = null;
    currentList.value = null; // Сбрасываем текущий список
    try {
      // Используем новый публичный эндпоинт без заголовков аутентификации
      const response = await apiClient.get(`/public/lists/${publicKey}`);
      currentList.value = response.data;
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось загрузить публичный список.';
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchPublicLists() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/public/feed');
      console.log('API Response for /public/feed:', response.data);
      if (Array.isArray(response.data)) {
        publicLists.value = response.data;
      } else {
        console.error('API response data is not an array:', response.data);
        publicLists.value = []; // Убедимся, что это всегда массив
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось загрузить публичные списки.';
      console.error('Error fetching public lists:', e);
      publicLists.value = []; // Убедимся, что это всегда массив при ошибке
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
      throw e; // Пробрасываем ошибку дальше для обработки в компоненте
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
      throw e;
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
      throw e;
    }
  }

  // --- Новые функции для работы с элементами ---

  async function addItem(listId, itemData) {
    error.value = null;
    try {
      const response = await apiClient.post(`/lists/${listId}/items`, itemData);
      if (currentList.value && currentList.value.id === listId) {
        currentList.value.items.push(response.data);
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось создать элемент.';
      console.error(e);
      throw e; // Пробрасываем ошибку дальше для обработки в компоненте
    }
  }

  async function updateItem(itemId, itemData) {
    error.value = null;
    try {
      const response = await apiClient.put(`/items/${itemId}`, itemData);
      if (currentList.value) {
        const index = currentList.value.items.findIndex(i => i.id === itemId);
        if (index !== -1) {
          currentList.value.items[index] = response.data;
        }
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось обновить элемент.';
      console.error(e);
      throw e;
    }
  }

  async function deleteItem(itemId) {
    error.value = null;
    try {
      await apiClient.delete(`/items/${itemId}`);
      if (currentList.value) {
        currentList.value.items = currentList.value.items.filter(i => i.id !== itemId);
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось удалить элемент.';
      console.error(e);
      throw e;
    }
  }

  // --- Новые функции для бронирования элементов ---

  async function reserveItem(itemId) {
    error.value = null;
    try {
      const response = await apiClient.post(`/items/${itemId}/reserve`);
      if (currentList.value) {
        const itemIndex = currentList.value.items.findIndex(item => item.id === itemId);
        if (itemIndex !== -1) {
          currentList.value.items[itemIndex].is_reserved = true;
        }
      }
      return response.data; // Возвращаем данные о бронировании, если нужно
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось забронировать элемент.';
      console.error(e);
      throw e;
    }
  }

  async function unreserveItem(itemId) {
    error.value = null;
    try {
      const response = await apiClient.delete(`/items/${itemId}/reserve`);
      if (currentList.value) {
        const itemIndex = currentList.value.items.findIndex(item => item.id === itemId);
        if (itemIndex !== -1) {
          currentList.value.items[itemIndex].is_reserved = false;
        }
      }
      return response.data; // Возвращаем данные об отмене бронирования, если нужно
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось отменить бронирование.';
      console.error(e);
      throw e;
    }
  }

  return { 
    lists, 
    currentList,
    isLoading, 
    error, 
    fetchLists, 
    fetchListById,
    fetchPublicListByKey, // Экспортируем новую функцию
    addList, 
    updateList, 
    deleteList,
    addItem,
    updateItem,
    deleteItem,
    reserveItem, // Экспортируем функцию бронирования
    unreserveItem, // Экспортируем функцию отмены бронирования
    fetchPublicLists, // Экспортируем функцию для получения всех публичных списков
    publicLists // Добавляем publicLists сюда
  };
});
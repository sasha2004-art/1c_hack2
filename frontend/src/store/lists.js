import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth'; // Импортируем настроенный axios

export const useListsStore = defineStore('lists', () => {
  const lists = ref([]);
  const currentList = ref(null);
  const userReservations = ref([]); // Новое состояние для бронирований
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
  
  // Функция обновлена для сброса userReservations
  async function fetchPublicListByKey(publicKey) {
    isLoading.value = true;
    error.value = null;
    currentList.value = null; 
    userReservations.value = []; // Сбрасываем бронирования при загрузке нового списка
    try {
      const response = await apiClient.get(`/public/lists/${publicKey}`);
      currentList.value = response.data;
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось загрузить публичный список.';
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

  // --- Новые функции для работы с бронированием ---

  async function fetchUserReservations() {
    error.value = null;
    try {
      const response = await apiClient.get('/users/me/reservations');
      userReservations.value = response.data;
    } catch(e) {
      error.value = 'Не удалось загрузить ваши бронирования.';
      console.error(e);
    }
  }

  // ИЗМЕНЕНИЕ: Добавляем publicKey как аргумент
  async function reserveItem(itemId, publicKey) {
    error.value = null;
    try {
      await apiClient.post(`/items/${itemId}/reserve`);
      if (publicKey) {
        // ИЗМЕНЕНИЕ: Используем переданный publicKey
        await fetchPublicListByKey(publicKey); 
        await fetchUserReservations();
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось забронировать элемент.';
      console.error(e);
      throw e;
    }
  }

  // ИЗМЕНЕНИЕ: Добавляем publicKey как аргумент
  async function unreserveItem(itemId, publicKey) {
    error.value = null;
    try {
      await apiClient.delete(`/items/${itemId}/unreserve`);
      if (publicKey) {
        // ИЗМЕНЕНИЕ: Используем переданный publicKey
        await fetchPublicListByKey(publicKey);
        await fetchUserReservations();
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось снять бронь.';
      console.error(e);
      throw e;
    }
  }


  return { 
    lists, 
    currentList,
    userReservations, // Экспортируем
    isLoading, 
    error, 
    fetchLists, 
    fetchListById,
    fetchPublicListByKey,
    addList, 
    updateList, 
    deleteList,
    addItem,
    updateItem,
    deleteItem,
    fetchUserReservations, // Экспортируем
    reserveItem,           // Экспортируем
    unreserveItem          // Экспортируем
  };
});
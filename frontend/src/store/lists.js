import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth'; // Импортируем настроенный axios

export const useListsStore = defineStore('lists', () => {
  const lists = ref([]);
  const currentList = ref(null);
  const userReservations = ref([]); // Новое состояние для бронирований
  const isLoading = ref(false);
  const error = ref(null);
  // --- НОВОЕ СОСТОЯНИЕ ДЛЯ ХРАНЕНИЯ ДЕТАЛЕЙ ОШИБКИ ДОСТУПА ---
  const listAccessErrorDetails = ref(null);

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
  
  // --- ИЗМЕНЕНИЕ ЗДЕСЬ: обработка новой структуры ошибки ---
  async function fetchPublicListByKey(publicKey) {
    isLoading.value = true;
    error.value = null;
    currentList.value = null; 
    listAccessErrorDetails.value = null; // Сбрасываем детали ошибки
    try {
      const response = await apiClient.get(`/public/lists/${publicKey}`);
      currentList.value = response.data;
    } catch (e) {
      const errorData = e.response?.data?.detail;
      // Проверяем, пришел ли объект с 'owner'
      if (typeof errorData === 'object' && errorData.owner) {
        listAccessErrorDetails.value = errorData;
        error.value = errorData.message;
      } else if (typeof errorData === 'object' && errorData.message) {
        error.value = errorData.message;
      }
      else {
        error.value = errorData || 'Не удалось загрузить публичный список.';
      }
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
        // Перезагружаем список, чтобы получить актуальные данные по лайкам/комментам
        await fetchListById(listId);
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось создать элемент.';
      console.error(e);
      throw e; // Пробрасываем ошибку дальше для обработки в компоненте
    }
  }

  async function uploadItemImage(itemId, file) {
    error.value = null;
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiClient.post(`/items/${itemId}/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      // Обновляем элемент в текущем списке
      if (currentList.value) {
        const index = currentList.value.items.findIndex(i => i.id === itemId);
        if (index !== -1) {
          currentList.value.items[index] = response.data;
        }
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось загрузить изображение.';
      console.error(e);
      throw e;
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

  // --- Новые функции для лайков и комментариев ---

  async function toggleLike(itemId) {
    error.value = null;
    // Находим элемент в текущем списке
    const item = currentList.value?.items.find(i => i.id === itemId);
    if (!item) return;

    try {
      if (item.is_liked_by_current_user) {
        // Убираем лайк
        await apiClient.delete(`/items/${itemId}/like`);
        item.likes_count--;
        item.is_liked_by_current_user = false;
      } else {
        // Ставим лайк
        await apiClient.post(`/items/${itemId}/like`);
        item.likes_count++;
        item.is_liked_by_current_user = true;
      }
    } catch (e) {
        error.value = e.response?.data?.detail || 'Не удалось обработать лайк.';
        // Откатываем изменения в UI в случае ошибки
        await fetchListById(currentList.value.id);
    }
  }
  
  async function addComment(itemId, commentText) {
    error.value = null;
    try {
      const response = await apiClient.post(`/items/${itemId}/comments`, { text: commentText });
      const item = currentList.value?.items.find(i => i.id === itemId);
      if(item) {
        item.comments.push(response.data);
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось добавить комментарий.';
      throw e;
    }
  }

  async function deleteComment(commentId, itemId) {
    error.value = null;
    try {
      await apiClient.delete(`/comments/${commentId}`);
      const item = currentList.value?.items.find(i => i.id === itemId);
      if(item) {
        item.comments = item.comments.filter(c => c.id !== commentId);
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось удалить комментарий.';
      throw e;
    }
  }

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

  // (Этап 10) Копирование элемента из чужого списка в свой
  async function copyItem(itemId, targetListId) {
    error.value = null;
    try {
      await apiClient.post(`/items/${itemId}/copy`, { target_list_id: targetListId });
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось скопировать элемент.';
      console.error(e);
      throw e;
    }
  }

  // (НОВЫЙ ЭКШЕН)
  async function updateGoalSettings(trackerId, goalData) {
    error.value = null;
    try {
      const response = await apiClient.put(`/goals/${trackerId}`, goalData);
      // Обновляем данные в локальном состоянии для мгновенной реакции
      if (currentList.value) {
        const itemIndex = currentList.value.items.findIndex(
          item => item.goal_tracker?.id === trackerId
        );
        if (itemIndex !== -1) {
          currentList.value.items[itemIndex].goal_tracker = response.data;
        }
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось обновить настройки цели.';
      console.error(e);
      throw e;
    }
  }

  // (Этап 14) Новый экшен для записи прогресса цели
  async function logGoalProgress(trackerId, value) {
    error.value = null;
    try {
      const response = await apiClient.post(`/goals/${trackerId}/log`, { value });
      // Обновляем данные трекера в текущем списке для мгновенной реакции UI
      if (currentList.value) {
        const itemIndex = currentList.value.items.findIndex(
          item => item.goal_tracker?.id === trackerId
        );
        if (itemIndex !== -1) {
          // Обновляем сам трекер
          currentList.value.items[itemIndex].goal_tracker = response.data;

          // Проверяем, не завершилась ли цель, и обновляем статус элемента
          const tracker = response.data;
          const target = tracker.target_value || tracker.target_count;
          if (target && tracker.current_value >= target) {
            currentList.value.items[itemIndex].is_completed = true;
          }
        }
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось записать прогресс.';
      console.error(e);
      throw e; // Пробрасываем ошибку для обработки в компоненте
    }
  }

  return { 
    lists, 
    currentList,
    userReservations, // Экспортируем
    isLoading, 
    error,
    listAccessErrorDetails, // <-- Экспортируем новое состояние
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
    unreserveItem,         // Экспортируем
    // Экспортируем новые функции
    toggleLike,
    addComment,
    deleteComment
    ,
    copyItem,
    logGoalProgress, // <-- Экспортируем новый экшен
    updateGoalSettings // <-- Экспортируем новый экшен
  };
});
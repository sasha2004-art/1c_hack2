import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth';

export const useFriendsStore = defineStore('friends', () => {
    const friends = ref([]);
    const incomingRequests = ref([]);
    const outgoingRequests = ref([]);
    // (Задача 4.1) Новое состояние для поиска
    const searchResults = ref([]);
    // (Задача 4.2) Новое состояние для профиля
    const currentUserProfile = ref(null);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchFriendsAndRequests() {
        isLoading.value = true;
        error.value = null;
        try {
            const response = await apiClient.get('/friends/');
            friends.value = response.data.friends;
            incomingRequests.value = response.data.incoming_requests;
            outgoingRequests.value = response.data.outgoing_requests;
        } catch (e) {
            error.value = 'Не удалось загрузить данные о друзьях.';
            console.error(e);
        } finally {
            isLoading.value = false;
        }
    }

    // --- ИЗМЕНИТЬ ЭТУ ФУНКЦИЮ ---
    async function searchUsers(query) { // Переименовываем параметр
        if (!query) {
            searchResults.value = [];
            return;
        }
        isLoading.value = true;
        error.value = null;
        try {
            // Используем новый параметр 'query' в запросе
            const response = await apiClient.get(`/users/search?query=${query}`);
            searchResults.value = response.data;
        } catch (e) {
            error.value = 'Ошибка поиска пользователей.';
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchUserProfile(userId) {
        isLoading.value = true;
        currentUserProfile.value = null;
        error.value = null;
        try {
            const response = await apiClient.get(`/users/${userId}/profile`);
            currentUserProfile.value = response.data;
        } catch (e) {
            error.value = 'Не удалось загрузить профиль.';
        } finally {
            isLoading.value = false;
        }
    }

    async function acceptFriendRequest(requestId) {
        error.value = null;
        try {
            await apiClient.post(`/friends/accept/${requestId}`);
            await fetchFriendsAndRequests(); // Обновляем все списки
        } catch (e) {
            error.value = 'Не удалось принять заявку.';
            console.error(e);
            throw e;
        }
    }
    
    async function declineFriendRequest(requestId) {
        error.value = null;
        try {
            await apiClient.post(`/friends/decline/${requestId}`);
            await fetchFriendsAndRequests(); // Обновляем все списки
        } catch (e) {
            error.value = 'Не удалось отклонить заявку.';
            console.error(e);
            throw e;
        }
    }

    async function removeFriend(friendshipId) {
        error.value = null;
        try {
            await apiClient.delete(`/friends/${friendshipId}`);
            await fetchFriendsAndRequests(); // Обновляем все списки
        } catch (e) {
            error.value = 'Не удалось удалить друга.';
            console.error(e);
            throw e;
        }
    }

    // В будущем, для страницы пользователя
    async function sendFriendRequest(userId) {
        error.value = null;
        try {
            await apiClient.post(`/friends/request/${userId}`);
            // Обновляем данные на странице профиля
            if (currentUserProfile.value && currentUserProfile.value.user_info.id === userId) {
                await fetchUserProfile(userId);
            }
        } catch (e) {
            error.value = e.response?.data?.detail || 'Не удалось отправить заявку.';
            console.error(e);
            throw e;
        }
    }

    return {
        friends,
        incomingRequests,
        outgoingRequests,
        searchResults, // Экспортируем
        currentUserProfile, // Экспортируем
        isLoading,
        error,
        fetchFriendsAndRequests,
        searchUsers, // Экспортируем
        fetchUserProfile, // Экспортируем
        acceptFriendRequest,
        declineFriendRequest,
        removeFriend,
        sendFriendRequest
    };
});
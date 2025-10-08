import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth';

const FEED_PAGE_SIZE = 10;

export const useFeedStore = defineStore('feed', () => {
    const friendsFeed = ref([]);
    const currentPage = ref(0);
    const isLoading = ref(false);
    const hasMore = ref(true); // Предполагаем, что данные есть
    const error = ref(null);

    async function fetchFriendsFeed() {
        if (isLoading.value || !hasMore.value) {
            return; // Предотвращаем повторные запросы
        }

        isLoading.value = true;
        error.value = null;

        try {
            const skip = currentPage.value * FEED_PAGE_SIZE;
            const response = await apiClient.get(`/feed/friends-lists?skip=${skip}&limit=${FEED_PAGE_SIZE}`);

            if (response.data.length > 0) {
                friendsFeed.value.push(...response.data);
                currentPage.value++;
            }

            // Если пришел пустой массив или массив меньше страницы, значит, это конец
            if (response.data.length < FEED_PAGE_SIZE) {
                hasMore.value = false;
            }

        } catch (e) {
            error.value = 'Не удалось загрузить ленту.';
            console.error(e);
        } finally {
            isLoading.value = false;
        }
    }
    
    // Функция для сброса состояния ленты, например, при обновлении страницы
    function resetFeed() {
        friendsFeed.value = [];
        currentPage.value = 0;
        hasMore.value = true;
        error.value = null;
    }


    return {
        friendsFeed,
        isLoading,
        hasMore,
        error,
        fetchFriendsFeed,
        resetFeed
    };
});
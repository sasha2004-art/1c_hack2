import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient } from './auth';

export const useFeedStore = defineStore('feed', () => {
    const feedLists = ref([]);
    const isLoading = ref(false);
    const error = ref(null);
    const currentPage = ref(0);
    const hasMore = ref(true);
    const pageSize = 10;

    async function loadMoreFeedItems() {
        if (isLoading.value || !hasMore.value) return;
        isLoading.value = true;
        error.value = null;
        try {
            const skip = currentPage.value * pageSize;
            const response = await apiClient.get(`/feed/friends-lists?skip=${skip}&limit=${pageSize}`);
            if (response.data.length > 0) {
                feedLists.value.push(...response.data);
                currentPage.value++;
            }
            if (response.data.length < pageSize) {
                hasMore.value = false;
            }
        } catch (e) {
            error.value = "Не удалось загрузить ленту.";
            console.error(e);
        } finally {
            isLoading.value = false;
        }
    }
    function fetchInitialFeed() {
        feedLists.value = [];
        currentPage.value = 0;
        hasMore.value = true;
        loadMoreFeedItems();
    }
    return {
        feedLists,
        isLoading,
        error,
        hasMore,
        fetchInitialFeed,
        loadMoreFeedItems
    };
});

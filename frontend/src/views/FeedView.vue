<template>
  <div class="feed-container">
    <h1>Лента друзей</h1>
    <div v-if="isLoading && feedLists.length === 0" class="status-message">
      Загрузка ленты...
    </div>
    <div v-if="error" class="status-message error">
      {{ error }}
    </div>
    <div v-if="!isLoading && feedLists.length === 0 && !error" class="status-message">
      В ленте пока пусто. Добавьте друзей или подождите, пока они создадут новые списки.
    </div>
    <div class="lists-grid" v-if="feedLists.length > 0">
      <ListCard 
        v-for="list in feedLists" 
        :key="list.id" 
        :list="list" 
      />
    </div>
    <div class="load-more-container">
      <button 
        v-if="hasMore && !isLoading" 
        @click="feedStore.loadMoreFeedItems" 
        class="btn-load-more"
      >
        Загрузить еще
      </button>
      <div v-if="isLoading && feedLists.length > 0" class="status-message">
        Загрузка...
      </div>
      <div v-if="!hasMore" class="status-message">
        Больше ничего нет :)
      </div>
    </div>
  </div>
</template>
<script setup>
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useFeedStore } from '@/store/feed';
import ListCard from '@/components/ListCard.vue';
const feedStore = useFeedStore();
const { feedLists, isLoading, error, hasMore } = storeToRefs(feedStore);
onMounted(() => {
  if (feedLists.value.length === 0) {
    feedStore.fetchInitialFeed();
  }
});
</script>
<style scoped>
.feed-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
}
h1 {
  color: var(--text-color);
  text-align: center;
  margin-bottom: 2rem;
}
.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.status-message {
  text-align: center;
  margin: 2rem 0;
  color: var(--text-color);
  opacity: 0.8;
}
.error {
  color: var(--secondary-color);
  font-weight: bold;
}
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}
.btn-load-more {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}
.btn-load-more:hover {
  opacity: 0.9;
}
</style>

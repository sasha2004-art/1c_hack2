<template>
  <div class="public-lists-feed-page">
    <h1>Публичные списки</h1>

    <div v-if="isLoading" class="status-message">Загрузка публичных списков...</div>
    <div v-else-if="error" class="status-message error">{{ error }}</div>
    <div v-else-if="publicLists.length > 0" class="lists-grid">
      <ListCard 
        v-for="list in publicLists" 
        :key="list.id" 
        :list="list" 
        :is-public-feed="true"
      />
    </div>
    <div v-else class="status-message">Публичных списков пока нет.</div>
  </div>
</template>

<script setup>
import { onMounted, watchEffect } from 'vue'; // Импортируем watchEffect
import { useListsStore } from '../store/lists';
import { storeToRefs } from 'pinia';
import ListCard from '../components/ListCard.vue'; // Импортируем ListCard

const listsStore = useListsStore();
const { publicLists, isLoading, error } = storeToRefs(listsStore);

onMounted(() => {
  listsStore.fetchPublicLists();
});
</script>

<style scoped>
.public-lists-feed-page {
  padding: 20px;
}

.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.status-message {
  text-align: center;
  font-size: 1.2rem;
  margin-top: 20px;
  color: var(--text-color);
}

.status-message.error {
  color: var(--delete-color);
}
</style>

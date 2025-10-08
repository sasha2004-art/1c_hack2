<template>
  <div class="feed-container">
    <h1>Лента друзей</h1>
    <p class="feed-description">Здесь отображаются последние публичные списки и списки для друзей от ваших друзей.</p>

    <div v-if="feedStore.friendsFeed.length > 0" class="feed-list">
      <div v-for="list in feedStore.friendsFeed" :key="list.id" class="feed-item-card">
        <div class="card-header">
          <span class="author-name">
            От: <router-link :to="{ name: 'UserProfile', params: { userId: list.owner.id } }">{{ list.owner.name }}</router-link>
          </span>
          <span class="post-date">{{ new Date(list.created_at).toLocaleDateString() }}</span>
        </div>
        <div class="card-body" @click="goToList(list.public_url_key)">
          <h3 class="list-title">{{ list.title }}</h3>
          <p v-if="list.description" class="list-description">{{ list.description }}</p>
        </div>
        <div class="card-footer">
          <span>{{ list.items_count }} {{ pluralize(list.items_count, ['элемент', 'элемента', 'элементов']) }}</span>
          <span class="privacy-tag">{{ privacyTranslations[list.privacy_level] || list.privacy_level }}</span>
        </div>
      </div>
    </div>

    <div v-else-if="!feedStore.isLoading && !feedStore.hasMore" class="empty-feed">
      <p>Лента ваших друзей пока пуста.</p>
      <p>Добавьте друзей, чтобы видеть их обновления!</p>
    </div>

    <div class="feed-controls">
      <button v-if="feedStore.hasMore && !feedStore.isLoading" @click="loadMore" class="btn btn-primary">
        Загрузить еще
      </button>
      <div v-if="feedStore.isLoading" class="loading-spinner">Загрузка...</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useFeedStore } from '@/store/feed';

const feedStore = useFeedStore();
const router = useRouter();

const privacyTranslations = {
  public: 'Публичный',
  friends_only: 'Для друзей'
};

function pluralize(count, words) {
  const cases = [2, 0, 1, 1, 1, 2];
  return words[(count % 100 > 4 && count % 100 < 20) ? 2 : cases[(count % 10 < 5) ? count % 10 : 5]];
}

// --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
const goToList = (publicKey) => {
  router.push({ name: 'PublicListView', params: { publicKey: publicKey } });
};

const loadMore = () => {
  feedStore.fetchFriendsFeed();
};

onMounted(() => {
  feedStore.resetFeed();
  feedStore.fetchFriendsFeed();
});

onUnmounted(() => {
    // Не сбрасываем состояние, чтобы при возврате на страницу лента сохранялась
});
</script>

<style scoped>
.feed-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
h1 {
  text-align: center;
  color: var(--text-color);
}
.feed-description {
  text-align: center;
  color: #6c757d;
  margin-bottom: 2rem;
}
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.feed-item-card {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
}
.card-header {
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #6c757d;
  border-bottom: 1px solid var(--border-color);
}
.author-name a {
  font-weight: bold;
  color: var(--primary-color);
  text-decoration: none;
}
.author-name a:hover {
  text-decoration: underline;
}
.card-body {
  padding: 1.5rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}
.card-body:hover {
  background-color: rgba(0,0,0,0.03);
}
.list-title {
  margin: 0 0 0.5rem;
  font-size: 1.4rem;
  color: var(--text-color);
}
.list-description {
  margin: 0;
  color: var(--text-color);
  opacity: 0.9;
}
.card-footer {
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #6c757d;
  border-top: 1px solid var(--border-color);
  background-color: rgba(0,0,0,0.02);
}
.privacy-tag {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-weight: 500;
}
.feed-controls {
  margin-top: 2rem;
  text-align: center;
}
.loading-spinner {
  padding: 2rem;
  color: #6c757d;
}
.empty-feed {
  text-align: center;
  padding: 3rem;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  background-color: rgba(0,0,0,0.02);
  color: #6c757d;
}
</style>
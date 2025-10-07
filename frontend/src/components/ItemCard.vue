<!-- frontend/src/components/ItemCard.vue -->
<template>
  <div class="item-card">
    <div class="card-content">
      <div class="card-header">
        <h3 class="item-title">{{ item.title }}</h3>
        <div class="item-actions" v-if="isOwner">
          <button @click.stop="$emit('edit', item)" class="icon-button edit-button">✏️</button>
          <button @click.stop="$emit('delete', item.id)" class="icon-button delete-button">🗑️</button>
        </div>
      </div>
      <!-- Используем v-html для безопасной отрисовки HTML из редактора -->
      <div class="item-description" v-html="item.description"></div>
    </div>
    
    <div class="card-footer">
      <div class="interactions">
        <LikeButton :item="item" />
        <div class="comments-info icon-button" @click="toggleComments">
          <span>💬</span>
          <span>{{ item.comments.length }}</span>
        </div>
      </div>
      <div class="reservation-status" v-if="isPublic && item.is_reserved">
        <span>Забронировано</span>
      </div>
    </div>

    <!-- Секция комментариев, которая появляется по клику -->
    <CommentsSection 
      v-if="showComments"
      :item-id="item.id" 
      :comments="item.comments"
      :is-public-view="isPublic"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import LikeButton from './LikeButton.vue'; // Импортируем новый компонент
import CommentsSection from './CommentsSection.vue';

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  listOwnerId: {
    type: Number,
    required: true
  },
  isPublic: {
    type: Boolean,
    default: false
  }
});

defineEmits(['edit', 'delete']);

const authStore = useAuthStore();
const showComments = ref(false);

const isOwner = computed(() => authStore.user && authStore.user.id === props.listOwnerId);

const toggleComments = () => {
  showComments.value = !showComments.value;
};
</script>

<style scoped>
.item-card {
  background-color: var(--card-bg-color, white);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* Главное свойство для прижатия футера */
  transition: box-shadow 0.3s;
  min-height: 150px; /* Минимальная высота, чтобы карточки выглядели ровно */
}
.item-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.item-title {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  word-break: break-word;
}

.item-description {
  margin-top: 0.5rem;
  color: var(--text-color);
  opacity: 0.9;
  font-size: 0.9rem;
  word-wrap: break-word;
}
/* Стили для контента из Quill редактора */
.item-description :deep(p) {
  margin: 0;
}
.item-description :deep(ul), .item-description :deep(ol) {
  padding-left: 20px;
  margin-bottom: 0;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
}
.edit-button { color: var(--edit-color); }
.delete-button { color: var(--secondary-color); }


.card-footer {
  margin-top: 1rem; /* Отступ от контента */
  padding-top: 0.75rem; /* Отступ внутри футера */
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.interactions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.comments-info {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--text-color);
}

.reservation-status span {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}
</style>

<template>
  <button @click.stop="handleLike" class="like-button" :class="{ 'liked': isLiked, 'disabled': isDisabled }">
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-heart">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
    </svg>
    <span>{{ likesCount }}</span>
  </button>
</template>

<script setup>
import { useListsStore } from '@/store/lists';

const props = defineProps({
  itemId: {
    type: Number,
    required: true,
  },
  likesCount: {
    type: Number,
    required: true,
  },
  isLiked: {
    type: Boolean,
    required: true,
  },
  isDisabled: { // Пропс, чтобы заблокировать кнопку для гостей
    type: Boolean,
    default: false,
  }
});

const listsStore = useListsStore();

const handleLike = () => {
  if (props.isDisabled) return;
  listsStore.toggleLike(props.itemId);
};
</script>

<style scoped>
.like-button {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: #f0f2f5;
  border: 1px solid #ccd0d5;
  border-radius: 20px;
  padding: 6px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
  color: #606770;
}
.like-button:hover:not(.disabled) {
  background-color: #e4e6e9;
}
.like-button.disabled {
  cursor: not-allowed;
  opacity: 0.7;
}
.like-button .feather-heart {
  transition: all 0.2s ease;
  fill: none;
  stroke: #606770;
}
.like-button.liked .feather-heart {
  fill: #e0245e;
  stroke: #e0245e;
}
.like-button.liked {
  color: #e0245e;
}
</style>
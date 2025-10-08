<!-- frontend/src/components/LikeButton.vue -->
<template>
    <div class="like-button icon-button" @click="handleLike">
        <span :class="{ 'is-liked': item.is_liked_by_current_user }">
            ❤️
        </span>
        <span>{{ item.likes_count }}</span>
    </div>
</template>

<script setup>
import { useListsStore } from '@/store/lists';

const props = defineProps({
    item: {
        type: Object,
        required: true
    }
});

const listsStore = useListsStore();

const handleLike = () => {
    listsStore.toggleLike(props.item.id);
};
</script>

<style scoped>
.like-button {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    color: var(--text-color);
}
.like-button span:first-child {
    font-size: 1.2rem;
    transition: transform 0.2s, color 0.2s; /* Изменение: Добавили transition для color */
}
.like-button .is-liked {
    color: var(--color-soft-red); /* Изменение: Красный цвет для лайка */
    transform: scale(1.1);
}
</style>
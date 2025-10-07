<template>
  <div class="item-card" :class="{ 'is-reserved': isReserved }">
    <!-- ЗАГОЛОВОК КАРТОЧКИ -->
    <div class="card-header">
      <h3 class="item-title">{{ item.title }}</h3>
      <div v-if="!isGuest" class="item-actions">
        <button @click="onEdit" class="action-btn edit-btn">✏️</button>
        <button @click="onDelete" class="action-btn delete-btn">🗑️</button>
      </div>
    </div>

    <!-- ОПИСАНИЕ (ИЗ QUILL) -->
    <div v-if="item.description" class="item-description ql-editor" v-html="item.description"></div>

    <!-- ФУТЕР С КНОПКАМИ -->
    <div class="card-footer">
      <div class="interactions">
        <LikeButton
          :item-id="item.id"
          :likes-count="item.likes_count"
          :is-liked="item.is_liked_by_current_user || false"
          :is-disabled="isGuest"
        />
        <button @click="showComments = !showComments" class="comments-toggle">
          💬 {{ item.comments.length }}
        </button>
      </div>

      <div class="reservation-status">
        <button v-if="isGuest && isReservable && !isReserved && !isMyReservation" @click="onReserve">
          Забронировать
        </button>
        <button v-if="isGuest && isMyReservation" @click="onUnreserve" class="unreserve-btn">
          Снять бронь
        </button>
        <span v-if="isReserved" class="reserved-badge">
          🎁 Забронировано
        </span>
      </div>
    </div>

    <!-- СЕКЦИЯ КОММЕНТАРИЕВ (ПОКАЗЫВАЕТСЯ ПО КЛИКУ) -->
    <CommentsSection
      v-if="showComments"
      :item-id="item.id"
      :comments="item.comments"
      :is-guest="isGuest"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import LikeButton from './LikeButton.vue';
import CommentsSection from './CommentsSection.vue';

// Подключаем стили Quill для корректного отображения
import '@vueup/vue-quill/dist/vue-quill.snow.css';

// defineProps и defineEmits доступны автоматически в <script setup>
const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  isGuest: {
    type: Boolean,
    default: false
  },
  isReservable: Boolean,
  isReserved: Boolean,
  isMyReservation: Boolean,
});

const emit = defineEmits(['edit', 'delete', 'reserve', 'unreserve']);

const showComments = ref(false);

const onEdit = () => emit('edit', props.item);
const onDelete = () => emit('delete', props.item.id);
const onReserve = () => emit('reserve', props.item.id);
const onUnreserve = () => emit('unreserve', props.item.id);
</script>

<style scoped>
/* Стили остаются такими же, как в прошлый раз */
.ql-editor {
    padding: 1rem 0;
    border: none;
    line-height: 1.6;
    background: transparent;
    color: var(--text-color);
}
.ql-editor :deep(a) {
  color: var(--primary-color);
}
.item-card {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s ease-in-out;
}
.item-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}
.item-title {
  margin: 0;
  font-size: 1.5em;
  color: var(--text-color);
  word-break: break-word;
}
.item-actions {
  display: flex;
  gap: 0.5rem;
}
.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}
.action-btn:hover {
    background-color: rgba(0,0,0,0.1);
}
.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}
.interactions {
    display: flex;
    gap: 1rem;
    align-items: center;
}
.comments-toggle {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-color);
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 6px 12px;
    border-radius: 20px;
    transition: background-color 0.2s;
}
.comments-toggle:hover {
    background-color: #e4e6e9;
}
.reserved-badge {
    font-weight: bold;
    color: #28a745;
}
.is-reserved {
    opacity: 0.7;
    background-color: #f8f9fa;
}
.reservation-status button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    background-color: var(--primary-color);
    color: var(--primary-text-color);
    font-weight: bold;
}
.unreserve-btn {
    background-color: var(--secondary-color);
    color: var(--secondary-text-color);
}
</style>

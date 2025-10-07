<template>
  <div class="item-card">
    <div class="card-content">
      <h3 class="item-title">{{ item.title }}</h3>
      <div v-if="item.description" class="item-description" v-html="item.description"></div>
      
      <!-- Статус бронирования -->
      <div v-if="isWishlist && item.is_reserved" class="reservation-status reserved">
        Забронировано
      </div>
    </div>
    <div class="card-footer">
        <!-- Кнопки для публичного просмотра -->
        <template v-if="isPublicView">
          <button 
            v-if="showReserveButton" 
            @click="$emit('reserve', item.id)"
            class="btn btn-reserve">
            Забронировать
          </button>
          <button 
            v-if="showUnreserveButton"
            @click="$emit('unreserve', item.id)"
            class="btn btn-unreserve">
            Снять бронь
          </button>
          <!-- Новая кнопка "Добавить к себе" -->
          <button
            v-if="showCopyButton"
            @click="copyItem"
            class="btn btn-copy"
          >
            Добавить к себе
          </button>
        </template>
        
        <!-- Здесь можно будет добавить кнопки для владельца (редактировать/удалить) -->

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import { storeToRefs } from 'pinia';
import { apiClient } from '../store/auth'; // Импортируем apiClient

const props = defineProps({
  item: { type: Object, required: true },
  listType: { type: String, required: true },
  isOwner: { type: Boolean, default: false },
  isPublicView: { type: Boolean, default: false },
  isLoggedIn: { type: Boolean, default: false },
});

const emit = defineEmits(['reserve', 'unreserve', 'itemCopied']); // Добавляем 'itemCopied'

const authStore = useAuthStore();
const { user } = storeToRefs(authStore);

const isWishlist = computed(() => props.listType === 'wishlist');

// Условие для показа кнопки "Забронировать"
const showReserveButton = computed(() => {
  return props.isLoggedIn && 
         isWishlist.value && 
         !props.isOwner && 
         !props.item.is_reserved;
});

// Условие для показа кнопки "Снять бронь"
const showUnreserveButton = computed(() => {
  // Эта логика требует, чтобы бэкенд отдавал ID того, кто зарезервировал, 
  // но для простоты пока сделаем на основе данных, которые уже есть.
  // В идеале, нужно добавить reserver_id в ItemPublicRead
  return false; // Пока скрываем, т.к. нет данных, кто забронировал
});

// Новая вычисляемая пропертя для кнопки "Добавить к себе"
const showCopyButton = computed(() => {
  return props.isLoggedIn && !props.isOwner;
});

const copyItem = async () => {
  try {
    await apiClient.post(`/items/${props.item.id}/copy`);
    emit('itemCopied'); // Отправляем событие о том, что элемент скопирован
    alert('Элемент успешно скопирован в ваш список!');
  } catch (error) {
    console.error('Ошибка при копировании элемента:', error);
    alert('Не удалось скопировать элемент.');
  }
};

</script>

<style scoped>
.item-card {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.card-content {
  padding: 1rem 1.2rem;
}

.item-title {
  font-size: 1.2rem;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.item-description {
  font-size: 0.95rem;
  opacity: 0.8;
  line-height: 1.5;
}
/* Стили для v-html */
.item-description :deep(p) {
  margin: 0.5em 0;
}
.item-description :deep(ul), .item-description :deep(ol) {
  padding-left: 1.2em;
}

.card-footer {
  padding: 0.8rem 1.2rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 0.5rem;
}

.reservation-status {
  margin-top: 1rem;
  padding: 0.4rem 0.8rem;
  border-radius: 5px;
  font-weight: bold;
  text-align: center;
}
.reserved {
  background-color: #e9ecef;
  color: #495057;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: opacity 0.2s;
}
.btn:hover {
  opacity: 0.85;
}

.btn-reserve {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}

.btn-unreserve {
  background-color: var(--edit-color);
  color: var(--edit-text-color);
}
.btn-copy {
  background-color: var(--secondary-color); /* Или любой другой цвет */
  color: var(--secondary-text-color);
}
</style>

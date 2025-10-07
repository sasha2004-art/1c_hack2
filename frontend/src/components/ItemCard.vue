<template>
  <div class="item-card">
    <div v-if="item.thumbnail_url || item.image_url" class="item-image-container">
      <img :src="proxiedImageUrl" alt="Изображение элемента" @click="isLightboxVisible = true">
    </div>

    <div class="item-content">
      <h4 class="item-title">{{ item.title }}</h4>
      <!-- Используем v-html для корректного отображения форматированного текста из Quill -->
      <div v-if="item.description" class="item-description" v-html="item.description"></div>
    </div>

    <div class="item-footer">
      <LikeButton :item="item" />
      <div class="comments-section-container">
        <CommentsSection :item="item" />
      </div>
    </div>

    <!-- 
      ВОТ КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ:
      Блок с кнопками "Изменить" и "Удалить".
      Он показывается только владельцу списка.
      При клике на кнопки мы генерируем (emit) события 'edit' и 'delete'.
    -->
    <div v-if="isOwner" class="owner-actions">
      <button @click="emit('edit', item)" class="btn-edit">Изменить</button>
      <button @click="emit('delete', item.id)" class="btn-delete">Удалить</button>
    </div>

    <!-- Лайтбокс для просмотра полного изображения -->
    <Lightbox
      v-if="isLightboxVisible && item.image_url"
      :image-url="item.image_url"
      @close="isLightboxVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import LikeButton from './LikeButton.vue';
import CommentsSection from './CommentsSection.vue';
import Lightbox from './Lightbox.vue'; // Предполагаем наличие этого компонента

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  isOwner: {
    type: Boolean,
    default: false,
  }
});

// 1. Объявляем, что этот компонент может генерировать события 'edit' и 'delete'.
//    Это ОБЯЗАТЕЛЬНО для правильной работы.
const emit = defineEmits(['edit', 'delete']);

const isLightboxVisible = ref(false);

const proxiedImageUrl = computed(() => {
  const url = props.item.thumbnail_url || props.item.image_url;
  if (!url) return '';
  // Проверяем, не является ли URL уже локальным
  if (url.startsWith('/')) {
    return `http://localhost:8000${url}`;
  }
  // Для внешних ссылок (Unsplash) используем прокси
  return `http://localhost:8000/utils/image-proxy?url=${encodeURIComponent(url)}`;
});
</script>

<style scoped>
.item-card {
  background-color: var(--card-bg-color, white);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: box-shadow 0.3s ease;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.item-image-container {
  width: 100%;
  height: 200px;
  background-color: #f0f0f0;
}

.item-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.item-content {
  padding: 15px;
  flex-grow: 1;
}

.item-title {
  margin: 0 0 10px 0;
  color: var(--text-color);
}

.item-description {
  font-size: 0.9rem;
  opacity: 0.8;
  color: var(--text-color);
  /* Стили для контента из Quill */
  :deep(p) { margin: 0 0 10px; }
  :deep(ul), :deep(ol) { padding-left: 20px; }
}

.item-footer {
  padding: 10px 15px;
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.comments-section-container {
  margin-top: 10px;
}

.owner-actions {
  display: flex;
  gap: 10px;
  padding: 10px 15px;
  background-color: rgba(0,0,0,0.03);
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.btn-edit, .btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-edit {
  background-color: var(--edit-color, #ffc107);
  color: var(--edit-text-color, #212529);
}

.btn-delete {
  background-color: var(--secondary-color, #dc3545);
  color: var(--secondary-text-color, white);
}
</style>
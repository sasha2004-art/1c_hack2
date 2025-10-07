<script setup>
import { ref } from 'vue';
import Lightbox from './Lightbox.vue';
import LikeButton from './LikeButton.vue';
import CommentsSection from './CommentsSection.vue';

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  isOwner: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['edit-item']);

const isLightboxVisible = ref(false);
const showComments = ref(false);

const openLightbox = () => {
  if (props.item.image_url) {
    isLightboxVisible.value = true;
  }
};

const closeLightbox = () => {
  isLightboxVisible.value = false;
};

const handleEditClick = () => {
  emit('edit-item', props.item);
};
</script>

<template>
  <div class="item-card">
    <div v-if="item.thumbnail_url" class="item-image-container" @click="openLightbox">
      <img :src="`http://localhost:8000${item.thumbnail_url}`" :alt="item.title" class="item-image" />
    </div>

    <div class="item-info">
      <h3>{{ item.title }}</h3>
      <div class="item-description" v-html="item.description"></div>
    </div>

    <div class="card-footer">
      <div class="interactions">
        <LikeButton :item="item" />
        <button @click="showComments = !showComments" class="btn-icon" title="Комментарии">
          💬 {{ item.comments.length }}
        </button>
      </div>
      <button v-if="isOwner" @click="handleEditClick" class="btn-edit">Изменить</button>
    </div>

    <CommentsSection v-if="showComments" :item-id="item.id" />

    <Lightbox
      :is-visible="isLightboxVisible"
      :image-url="`http://localhost:8000${item.image_url}`"
      @close="closeLightbox"
    />
  </div>
</template>

<style scoped>
.item-card {
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.item-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.item-image-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
  cursor: pointer;
}
.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.item-image:hover {
  transform: scale(1.05);
}
.item-info {
  padding: 1rem;
  flex-grow: 1;
}
.item-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}
.item-description {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* --- ИСПРАВЛЕНИЕ ЗДЕСЬ --- */
/* Селекторы :deep вынесены из .item-description и записаны как отдельные правила */
.item-description :deep(p) { 
  margin-bottom: 0.5em; 
}
.item-description :deep(a) { 
  color: var(--primary-color); 
}
.item-description :deep(ul), .item-description :deep(ol) { 
  padding-left: 1.5em; 
}
/* --- КОНЕЦ ИСПРАВЛЕНИЯ --- */


.card-footer {
  padding: 0.5rem 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(0,0,0,0.02);
}
.interactions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.btn-edit {
  background-color: var(--edit-color);
  color: var(--edit-text-color);
  border: none;
  padding: 6px 12px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: bold;
}
.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 5px;
  border-radius: 50%;
  line-height: 1;
  transition: background-color 0.2s;
}
.btn-icon:hover {
  background-color: rgba(0,0,0,0.1);
}
</style>

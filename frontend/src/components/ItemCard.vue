<script setup>
import { ref } from 'vue';
import Lightbox from './Lightbox.vue';
import LikeButton from './LikeButton.vue';
import CommentsSection from './CommentsSection.vue';
import GoalProgressBar from './GoalProgressBar.vue';
import LogProgressModal from './LogProgressModal.vue';
import { useListsStore } from '@/store/lists';

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
const listsStore = useListsStore();

const isLightboxVisible = ref(false);
const showComments = ref(false);

const isLogModalOpen = ref(false);
const itemToLog = ref(null);

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

const openLogModal = (item) => {
  itemToLog.value = item;
  isLogModalOpen.value = true;
};

const closeLogModal = () => {
  isLogModalOpen.value = false;
  itemToLog.value = null;
};

const submitLog = async (value) => {
  if (!itemToLog.value || !itemToLog.value.goal_tracker) return;
  try {
    await listsStore.logGoalProgress(itemToLog.value.goal_tracker.id, value);
  } catch (error) {
    console.error("Failed to log progress:", error);
    alert(listsStore.error || 'Не удалось записать прогресс.');
  }
};

const submitHabitChange = async (item, value) => {
  if (!item.goal_tracker) return;
  try {
    await listsStore.logGoalProgress(item.goal_tracker.id, value);
  } catch (error) {
    console.error("Failed to log progress:", error);
    alert(listsStore.error || 'Не удалось записать прогресс.');
  }
};
</script>

<template>
  <div class="item-card" :class="{ 'completed': item.is_completed }">
    <!-- ИЗМЕНЕНИЕ: Новый контейнер .card-body для всего контента с отступами -->
    <div class="card-body">
      <h3>{{ item.title }}</h3>
      
      <!-- Этот контейнер теперь корректно отобразит контент из Quill, включая картинки -->
      <div class="item-description" v-html="item.description"></div>

      <!-- Этот блок остался для поддержки старого поля `thumbnail_url` -->
      <div v-if="item.thumbnail_url" class="item-image-container" @click="openLightbox">
        <img :src="`http://localhost:8000${item.thumbnail_url}`" :alt="item.title" class="item-image" />
      </div>

      <div class="goal-progress-section" v-if="item.goal_tracker && !item.is_completed && isOwner">
        <GoalProgressBar
          :tracker="item.goal_tracker"
          @open-log-modal="openLogModal(item)"
          @log-value-change="value => submitHabitChange(item, value)"
        />
      </div>
      
      <div v-if="item.is_completed" class="goal-completed">
        ✅ Цель достигнута!
      </div>
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

    <!-- Комментарии теперь ВНУТРИ карточки, но ВНЕ .card-body для корректного отображения -->
    <CommentsSection v-if="showComments" :item-id="item.id" :comments="item.comments" class="comments-in-card" />
    
    <Lightbox :is-visible="isLightboxVisible" :image-url="`http://localhost:8000${item.image_url}`" @close="closeLightbox" />
    <LogProgressModal
      :is-open="isLogModalOpen"
      :tracker="itemToLog?.goal_tracker"
      @close="closeLogModal"
      @submit="submitLog"
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

/* ИЗМЕНЕНИЕ: Основной контейнер с отступами */
.card-body {
  padding: 1rem;
  flex-grow: 1;
}

.item-image-container {
  width: 100%;
  overflow: hidden;
  cursor: pointer;
  margin-top: 1rem;
  margin-bottom: 1rem;
}
.item-image {
  width: 100%;
  max-height: 250px;
  object-fit: cover;
  transition: transform 0.3s;
  border-radius: 8px; /* Скругленные углы у картинки */
}
.item-image:hover {
  transform: scale(1.05);
}

.item-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  color: var(--text-color);
}
.item-description {
  font-size: 0.9rem;
  opacity: 0.8;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px; /* Для полосы прокрутки */
  color: var(--text-color);
  /* Эти стили нужны, чтобы текст обтекал картинки, если они маленькие */
  word-wrap: break-word;
}
/* Стили для контента, вставленного через v-html */
.item-description :deep(p) { margin-bottom: 0.5em; }
.item-description :deep(a) { color: var(--primary-color); }
.item-description :deep(ul), .item-description :deep(ol) { padding-left: 1.5em; }
.item-description :deep(img) {
  display: block;
  max-width: 100%;
  height: auto;
  max-height: 250px;
  object-fit: cover;
  border-radius: 8px;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.goal-progress-section {
  margin-top: 1rem;
}

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(0,0,0,0.02); /* Легкий фон для футера */
}
.interactions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.btn-edit {
  background-color: var(--color-warm-amber, #ffc107); /* Цвет как на скриншоте */
  color: var(--text-color, #212529);
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
  font-size: 1rem; /* Уменьшаем иконки */
  padding: 5px;
  border-radius: 50%;
  line-height: 1;
  display: flex;
  align-items: center;
  gap: 4px; /* Расстояние между иконкой и цифрой */
  transition: background-color 0.2s;
  color: var(--text-color);
  opacity: 0.7;
}
.btn-icon:hover {
  background-color: rgba(0,0,0,0.1);
  opacity: 1;
}

.item-card.completed {
  opacity: 0.7;
}
.goal-completed {
  width: 100%;
  text-align: center;
  font-weight: bold;
  color: #28a745;
  padding: 0.75rem;
  margin-top: 1rem;
  background-color: #e8f9ec;
  border-radius: 6px;
}

/* ИЗМЕНЕНИЕ: Стили для секции комментариев внутри карточки */
.comments-in-card {
    padding: 0 1rem 1rem 1rem;
    margin-top: 0;
    border-top: none;
}
</style>
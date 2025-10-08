<script setup>
import { ref } from 'vue';
import Lightbox from './Lightbox.vue';
import LikeButton from './LikeButton.vue';
import CommentsSection from './CommentsSection.vue';
// (Этап 14) Импортируем новые компоненты
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

// (Этап 14) Новое состояние для модального окна записи прогресса
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

// (Этап 14) Новые функции для управления модальным окном
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

// (ИЗМЕНЕНИЕ) Новая функция для прямого вызова без модального окна
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
    <div v-if="item.thumbnail_url" class="item-image-container" @click="openLightbox">
      <img :src="`http://localhost:8000${item.thumbnail_url}`" :alt="item.title" class="item-image" />
    </div>

    <div class="item-info">
      <h3>{{ item.title }}</h3>
      <div class="item-description" v-html="item.description"></div>

      <!-- (ИЗМЕНЕНИЕ) Блок с прогресс-баром теперь здесь, в основной части -->
      <div class="goal-progress-section" v-if="item.goal_tracker">
        <GoalProgressBar
          v-if="!item.is_completed && isOwner"
          :tracker="item.goal_tracker"
          @open-log-modal="openLogModal(item)"
          @log-value-change="value => submitHabitChange(item, value)"
        />
        <div v-else-if="item.is_completed" class="goal-completed">
          ✅ Цель достигнута!
        </div>
      </div>
    </div>

    <!-- (ИЗМЕНЕНИЕ) Футер теперь всегда одинаковый для всех карточек -->
    <div class="card-footer">
      <div class="interactions">
        <LikeButton :item="item" />
        <button @click="showComments = !showComments" class="btn-icon" title="Комментарии">
          💬 {{ item.comments.length }}
        </button>
      </div>
      <button v-if="isOwner" @click="handleEditClick" class="btn-edit">Изменить</button>
    </div>

    <CommentsSection v-if="showComments" :item-id="item.id" :comments="item.comments" />

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
  /* --- ДОБАВЛЕНО СВОЙСТВО --- */
  flex-grow: 1;
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
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px;
}

.item-description :deep(p) { 
  margin-bottom: 0.5em; 
}
.item-description :deep(a) { 
  color: var(--primary-color); 
}
.item-description :deep(ul), .item-description :deep(ol) { 
  padding-left: 1.5em; 
}

.goal-progress-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

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

/* (Этап 14) Стили для целей */
.item-card.completed {
  opacity: 0.7;
  background-color: #f7fff8;
}
.goal-completed {
  width: 100%;
  text-align: center;
  font-weight: bold;
  color: #28a745;
  padding: 0.5rem;
}
</style>
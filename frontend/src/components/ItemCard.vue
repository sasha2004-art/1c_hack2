<script setup>
import { ref, watch } from 'vue';
import Lightbox from './Lightbox.vue';
import LikeButton from './LikeButton.vue';
import CommentsSection from './CommentsSection.vue';
import GoalProgressBar from './GoalProgressBar.vue';
import LogProgressModal from './LogProgressModal.vue';
import { useListsStore } from '@/store/lists';
// НОВОЕ: Импортируем confetti
import confetti from 'canvas-confetti';

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

// НОВОЕ: Следим за изменением статуса is_completed
watch(() => props.item.is_completed, (newValue, oldValue) => {
  // Вызываем конфетти, только если статус изменился с false на true
  if (newValue === true && oldValue === false) {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    });
  }
});

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

// НОВОЕ: Обработчик для кнопки выполнения
const handleToggleComplete = () => {
  listsStore.toggleItemCompletion(props.item.id);
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
    <div class="card-body">
       <!-- НОВЫЙ БЛОК: Кнопка выполнения для простых задач -->
      <button 
        v-if="isOwner && !item.goal_tracker" 
        @click="handleToggleComplete" 
        class="complete-toggle-btn"
        :title="item.is_completed ? 'Вернуть в работу' : 'Отметить выполненным'">
        <span class="checkmark" :class="{ 'checked': item.is_completed }">✓</span>
      </button>

      <h3>{{ item.title }}</h3>
      
      <div class="item-description" v-html="item.description"></div>

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
        ✅ Выполнено!
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
  transition: box-shadow 0.3s, transform 0.3s; /* ИЗМЕНЕНИЕ: Добавили transform */
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  position: relative; /* НОВОЕ: Для позиционирования кнопки */
}
/* ИЗМЕНЕНИЕ: Более выразительный hover */
.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}

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
  border-radius: 8px;
}
.item-image:hover {
  transform: scale(1.05);
}

.item-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  color: var(--text-color);
  padding-right: 40px; /* НОВОЕ: Освобождаем место для кнопки */
  transition: color 0.3s;
}
.item-description {
  font-size: 0.9rem;
  opacity: 0.8;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px;
  color: var(--text-color);
  word-wrap: break-word;
}
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
  background-color: rgba(0,0,0,0.02);
}
.interactions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.btn-edit {
  background-color: var(--color-warm-amber, #ffc107);
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
  font-size: 1rem;
  padding: 5px;
  border-radius: 50%;
  line-height: 1;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: background-color 0.2s;
  color: var(--text-color);
  opacity: 0.7;
}
.btn-icon:hover {
  background-color: rgba(0,0,0,0.1);
  opacity: 1;
}

/* ИЗМЕНЕНИЕ: Стили для выполненной задачи */
.item-card.completed {
  opacity: 0.6;
}
.item-card.completed h3 {
  text-decoration: line-through;
  color: #888;
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

.comments-in-card {
    padding: 0 1rem 1rem 1rem;
    margin-top: 0;
    border-top: none;
}

/* НОВЫЕ СТИЛИ: Кнопка выполнения */
.complete-toggle-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  background-color: var(--card-bg-color);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.complete-toggle-btn:hover {
  border-color: var(--color-soft-green);
  transform: scale(1.1);
}
.checkmark {
  font-size: 20px;
  color: transparent;
  transition: color 0.2s ease;
}
.complete-toggle-btn:hover .checkmark {
  color: var(--color-soft-green);
}
.checkmark.checked {
  color: var(--color-soft-green);
}
.complete-toggle-btn .checkmark.checked {
  color: var(--color-soft-green);
}
.item-card.completed .complete-toggle-btn {
  border-color: var(--color-soft-green);
}
</style>
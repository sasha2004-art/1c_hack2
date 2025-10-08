<template>
  <!-- ИЗМЕНЕНИЕ: Оборачиваем в transition -->
  <transition name="fade">
    <div v-if="isModalOpen" class="modal-backdrop" @click.self="$emit('close')">
      <!-- ИЗМЕНЕНИЕ: Оборачиваем в transition -->
      <transition name="pop">
        <div v-if="isModalOpen" class="modal-content">
          <h2>{{ isEditing ? 'Настройки списка' : 'Создать новый список' }}</h2>
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="title">Название</label>
              <input type="text" id="title" v-model="form.title" required>
            </div>
            <div class="form-group">
              <label for="description">Описание</label>
              <textarea id="description" v-model="form.description"></textarea>
            </div>
            <div class="form-group">
              <label for="list_type">Тип списка</label>
              <select id="list_type" v-model="form.list_type">
                <option value="wishlist">Вишлист</option>
                <option value="todo">Список дел</option>
              </select>
            </div>
            <div class="form-group">
              <label for="privacy_level">Приватность</label>
              <select id="privacy_level" v-model="form.privacy_level">
                <option value="private">Приватный</option>
                <option value="friends_only">Только для друзей</option>
                <option value="public">Публичный</option>
              </select>
            </div>
            
            <ThemeSelector v-model="form.theme_name" />

            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="$emit('close')">Отмена</button>
              <button type="submit" class="btn btn-primary">Сохранить</button>
            </div>
            <div v-if="error" class="error-message">{{ error }}</div>
          </form>
        </div>
      </transition>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch } from 'vue'; // ИЗМЕНЕНИЕ: Добавил watch
import { useListsStore } from '@/store/lists';
import ThemeSelector from './ThemeSelector.vue';

const props = defineProps({
  initialList: {
    type: Object,
    default: null
  },
  isOpen: {
    type: Boolean,
    default: false
  }
});
const emit = defineEmits(['close']);

const listsStore = useListsStore();
const isEditing = !!props.initialList;
const error = ref(null);

// НОВОЕ: Отдельное состояние для видимости, чтобы анимация работала корректно
const isModalOpen = ref(true); 

const form = ref({
  title: props.initialList?.title || '',
  description: props.initialList?.description || '',
  list_type: props.initialList?.list_type || 'wishlist',
  privacy_level: props.initialList?.privacy_level || 'private',
  theme_name: props.initialList?.theme_name || 'default',
});

const handleSubmit = async () => {
  error.value = null;
  try {
    if (isEditing) {
      await listsStore.updateList(props.initialList.id, form.value);
    } else {
      await listsStore.addList(form.value);
    }
    emit('close');
  } catch (e) {
    error.value = e.message || 'Произошла ошибка.';
  }
};

// НОВОЕ: Отслеживаем пропс, чтобы управлять видимостью для анимации
watch(() => props.isOpen, (newVal) => {
    isModalOpen.value = newVal;
}, { immediate: true });
</script>

<style scoped>
/* НОВЫЕ СТИЛИ: Анимация для модального окна */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.pop-enter-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.pop-leave-active {
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.pop-enter-from,
.pop-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: var(--card-bg-color);
  padding: var(--space-xl);
  border-radius: 16px;
  width: 90%;
  max-width: 640px;
  box-shadow: var(--shadow-3);
  color: var(--text-color);
}
h2 {
  margin-top: 0;
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin-bottom: var(--space-lg);
}
.form-group {
  margin-bottom: var(--space-lg);
}
.form-group label {
  display: block;
  margin-bottom: var(--space-sm);
  font-weight: 500;
}
.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 16px;
  height: 44px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-size: 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group textarea {
    height: auto;
    min-height: 120px;
}
.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(155, 135, 245, 0.3);
}

.form-actions {
  margin-top: var(--space-xl);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
}
.error-message {
    color: var(--destructive-color);
    margin-top: var(--space-md);
    text-align: right;
}
</style>
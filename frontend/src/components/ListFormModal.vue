<!-- frontend/src/components/ListFormModal.vue -->
<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-content">
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
            <option value="books">Книги</option>
            <option value="movies">Фильмы</option>
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
          <button type="button" @click="$emit('close')">Отмена</button>
          <button type="submit">Сохранить</button>
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useListsStore } from '@/store/lists';
import ThemeSelector from './ThemeSelector.vue';

const props = defineProps({
  initialList: {
    type: Object,
    default: null
  }
});
const emit = defineEmits(['close']);

const listsStore = useListsStore();
const isEditing = !!props.initialList;
const error = ref(null);

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
</script>

<style scoped>
/* Стили для модального окна (можете адаптировать под свой main.css) */
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
  background-color: var(--card-bg-color, white);
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
h2 {
  margin-top: 0;
  color: var(--text-color);
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}
.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--bg-color);
  color: var(--text-color);
}
.form-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.form-actions button {
    padding: 0.75rem 1.5rem;
    border-radius: 5px;
    border: none;
    cursor: pointer;
}
.form-actions button[type="submit"] {
    background-color: var(--primary-color);
    color: var(--primary-text-color);
}
.form-actions button[type="button"] {
    background-color: #ccc;
}
.error-message {
    color: var(--secondary-color);
    margin-top: 1rem;
}
</style>
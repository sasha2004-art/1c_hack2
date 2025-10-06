<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ formTitle }}</h2>
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
            <option value="wishlist">Wishlist</option>
            <option value="todo">To-Do</option>
            <option value="books">Books</option>
            <option value="movies">Movies</option>
          </select>
        </div>
        <div class="form-group">
          <label for="privacy_level">Уровень приватности</label>
          <select id="privacy_level" v-model="form.privacy_level">
            <option value="private">Приватный</option>
            <option value="public">Публичный</option>
          </select>
        </div>
        <div class="form-actions">
          <button type="button" class="secondary" @click="$emit('close')">Отмена</button>
          <button type="submit">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
  listToEdit: {
    type: Object,
    default: null
  }
});
const emit = defineEmits(['close', 'save']);

const form = ref({
  title: '',
  description: '',
  list_type: 'wishlist',
  privacy_level: 'private'
});

const formTitle = computed(() => props.listToEdit ? 'Редактировать список' : 'Создать новый список');

onMounted(() => {
  if (props.listToEdit) {
    form.value = { ...props.listToEdit };
  }
});

const handleSubmit = () => {
  emit('save', form.value);
};
</script>

<style scoped>
.modal-overlay {
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
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}
.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.form-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>
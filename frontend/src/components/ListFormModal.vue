<template>
  <div class="modal-overlay" v-if="show">
    <!-- ИЗМЕНЕНИЕ: Убран :style="themeStyles", теперь стили наследуются -->
    <div class="modal-content">
      <h3 class="modal-title">{{ formTitle }}</h3>
      <form @submit.prevent="handleSubmit">
        <!-- Название -->
        <div class="form-group">
          <label for="title">Название</label>
          <input id="title" type="text" v-model="formData.title" required>
        </div>
        
        <!-- Описание -->
        <div class="form-group">
          <label for="description">Описание</label>
          <textarea id="description" v-model="formData.description"></textarea>
        </div>

        <!-- Тип списка -->
        <div class="form-group">
          <label for="list_type">Тип списка</label>
          <select id="list_type" v-model="formData.list_type">
            <option v-for="option in listTypeOptions" :key="option.value" :value="option.value">
              {{ option.text }}
            </option>
          </select>
        </div>

        <!-- ИЗМЕНЕНИЕ: Добавлен выбор уровня приватности -->
        <div class="form-group">
          <label for="privacy_level">Уровень приватности</label>
           <select id="privacy_level" v-model="formData.privacy_level">
            <option v-for="option in privacyLevelOptions" :key="option.value" :value="option.value">
              {{ option.text }}
            </option>
          </select>
        </div>

        <!-- Тема -->
        <div class="form-group">
          <label>Тема оформления</label>
          <ThemeSelector v-model="formData.theme_name" />
        </div>

        <!-- Кнопки -->
        <div class="modal-actions">
          <button type="button" @click="close" class="btn btn-cancel">Отмена</button>
          <button type="submit" class="btn btn-primary">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
// ИЗМЕНЕНИЕ: themes больше не нужен для стилизации, но нужен для ThemeSelector
// import { themes } from '../themes.js'; 
import ThemeSelector from './ThemeSelector.vue';

const props = defineProps({
  show: Boolean,
  list: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'save']);

// Переводы для выпадающих списков
const listTypeOptions = [
  { value: 'wishlist', text: 'Список желаний' },
  { value: 'todo', text: 'Список дел' },
  { value: 'books', text: 'Книги' },
  { value: 'movies', text: 'Фильмы' }
];

// ИЗМЕНЕНИЕ: Добавлены переводы для приватности
const privacyLevelOptions = [
    { value: 'private', text: 'Приватный' },
    { value: 'public', text: 'Публичный' }
];

// ИЗМЕНЕНИЕ: Добавлено поле privacy_level
const formData = ref({
  id: null,
  title: '',
  description: '',
  list_type: 'wishlist',
  privacy_level: 'private', // Значение по умолчанию
  theme_name: 'default'
});

const formTitle = computed(() => props.list ? 'Редактировать список' : 'Создать новый список');

// ИЗМЕНЕНИЕ: Убрана вычисляемая переменная themeStyles
// const themeStyles = computed(...)

watch(() => props.list, (newList) => {
  if (newList) {
    // Режим редактирования: копируем все данные
    formData.value = { ...newList };
  } else {
    // Режим создания: сбрасываем до значений по умолчанию
    formData.value = { id: null, title: '', description: '', list_type: 'wishlist', privacy_level: 'private', theme_name: 'default' };
  }
}, { immediate: true });

const handleSubmit = () => {
  emit('save', formData.value);
  close();
};

const close = () => {
  emit('close');
};
</script>

<style scoped>
/* ИЗМЕНЕНИЕ: Все стили теперь используют CSS переменные */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.7); display: flex;
  justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background-color: var(--card-bg-color); /* Фон из темы */
  color: var(--text-color); /* Цвет текста из темы */
  padding: 2.5rem; border-radius: 8px; width: 90%; max-width: 500px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  border: 1px solid var(--border-color);
}
.modal-title {
  color: var(--text-color); margin-top: 0; margin-bottom: 2rem;
  text-align: center; font-size: 1.8rem;
}
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
.form-group input, .form-group textarea, .form-group select {
  width: 100%; padding: 0.8rem; 
  border: 1px solid var(--border-color); /* Граница из темы */
  border-radius: 4px; 
  background-color: var(--bg-color); /* Фон поля ввода из темы */
  color: var(--text-color); /* Цвет текста в поле из темы */
  box-sizing: border-box; font-size: 1rem;
}
.modal-actions {
  display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;
}
.btn {
  padding: 0.7rem 1.5rem; border-radius: 5px; cursor: pointer;
  font-weight: bold; font-size: 1rem; border: 1px solid transparent;
}
.btn-primary {
  background-color: var(--primary-color); color: var(--primary-text-color);
  border-color: var(--primary-color);
}
.btn-cancel {
  background-color: transparent; color: var(--text-color);
  border: 1px solid var(--border-color);
}
</style>
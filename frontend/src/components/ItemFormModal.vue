<!-- --- НАЧАЛО ФАЙЛА: frontend/src/components/ItemFormModal.vue --- -->
<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ formTitle }}</h2>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="title">Название</label>
          <input id="title" v-model="form.title" type="text" required>
        </div>
        <div class="form-group">
          <label for="description">Краткое описание</label>
          <textarea id="description" v-model="form.description"></textarea>
        </div>
        <div class="form-group">
          <label>Детальное описание</label>
          <!-- НОВЫЙ КОМПОНЕНТ: Редактор текста -->
          <QuillEditor
            theme="snow"
            :toolbar="toolbarOptions"
            v-model:content="form.details"
            contentType="html"
          />
        </div>
        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="btn-cancel">Отмена</button>
          <button type="submit" class="btn-save">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
// Импортируем редактор и его стили
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';

const props = defineProps({
  isVisible: Boolean,
  itemToEdit: Object,
});

const emit = defineEmits(['close', 'save']);

const form = ref({});

// Настройки панели инструментов редактора
const toolbarOptions = [
  ['bold', 'italic', 'underline'], // полужирный, курсив, подчеркнутый
  ['link'], // кнопка для вставки ссылки
  [{ 'list': 'ordered'}, { 'list': 'bullet' }], // нумерованный и маркированный списки
  ['clean'] // очистка форматирования
];

watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    if (props.itemToEdit) {
      // Режим редактирования: копируем данные, включая HTML-описание
      form.value = { ...props.itemToEdit };
    } else {
      // Режим создания: обнуляем поля
      form.value = { title: '', description: '', details: '' };
    }
  }
});

const formTitle = computed(() => {
  return props.itemToEdit ? 'Редактировать элемент' : 'Добавить новый элемент';
});

function submitForm() {
  // Теперь не нужно парсить JSON, просто отправляем форму как есть
  const payload = {
    title: form.value.title,
    description: form.value.description,
    details: form.value.details,
  };
  
  emit('save', payload);
}
</script>

<style scoped>
/* Стили для модального окна */
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
  z-index: 100;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 650px; /* Увеличим ширину для редактора */
}
.form-group {
  margin-bottom: 1.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
input, textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}
.btn-save { background-color: #42b983; color: white; }
.btn-cancel { background-color: #6c757d; color: white; }
button { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }

/* Стили для редактора Quill могут потребовать небольшой корректировки */
.form-group .ql-toolbar {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
.form-group .ql-container {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  min-height: 150px; /* Задаем минимальную высоту */
  font-size: 1rem;
}
</style>
<!-- --- КОНЕЦ ФАЙЛА: frontend/src/components/ItemFormModal.vue --- -->
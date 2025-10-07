<template>
  <div class="modal-overlay" v-if="show">
    <div class="modal-content">
      <h3 class="modal-title">{{ formTitle }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title">Название</label>
          <input id="title" type="text" v-model="formData.title" required>
        </div>
        
        <div class="form-group">
          <label>Описание</label>
          <QuillEditor 
            v-model:content="formData.description" 
            contentType="html" 
            theme="snow"
            placeholder="Добавьте форматированный текст, ссылки и детали..."
          />
        </div>

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
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';

const props = defineProps({
  show: Boolean,
  item: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'save']);

const formData = ref({
  id: null,
  title: '',
  description: ''
});

const formTitle = computed(() => props.item ? 'Редактировать элемент' : 'Добавить новый элемент');

watch(() => props.item, (newItem) => {
  if (newItem) {
    formData.value = { id: newItem.id, title: newItem.title || '', description: newItem.description || '' };
  } else {
    formData.value = { id: null, title: '', description: '' };
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
/* Стили скопированы из ListFormModal для консистентности и используют CSS переменные */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.7); display: flex;
  justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
  background-color: var(--card-bg-color); color: var(--text-color);
  padding: 2.5rem; border-radius: 8px; width: 90%; max-width: 600px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3); border: 1px solid var(--border-color);
}
.modal-title {
  color: var(--text-color); margin-top: 0; margin-bottom: 2rem;
  text-align: center; font-size: 1.8rem;
}
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
.form-group input[type="text"] {
  width: 100%; padding: 0.8rem; border: 1px solid var(--border-color);
  border-radius: 4px; background-color: var(--bg-color);
  color: var(--text-color); box-sizing: border-box; font-size: 1rem;
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

/* Стилизация редактора Quill с использованием CSS переменных */
:deep(.ql-toolbar) {
  border-color: var(--border-color) !important;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
:deep(.ql-container) {
  border-color: var(--border-color) !important;
  background-color: var(--bg-color);
  color: var(--text-color);
  min-height: 150px;
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}
:deep(.ql-editor) {
  color: var(--text-color);
}
:deep(.ql-snow .ql-stroke) {
    stroke: var(--text-color);
}
</style>
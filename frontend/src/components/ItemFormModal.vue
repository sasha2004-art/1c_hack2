<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Новый элемент</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title">Название</label>
          <input type="text" id="title" v-model="formData.title" required>
        </div>
        <div class="form-group">
          <label for="description">Описание</label>
          <QuillEditor 
            theme="snow" 
            contentType="html"
            v-model:content="formData.description" 
            placeholder="Подробное описание, ссылки и т.д."
            toolbar="essential"
            />
        </div>
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Отмена</button>
          <button type="submit" class="btn btn-primary">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css';

const emit = defineEmits(['close', 'save']);

const formData = ref({
  title: '',
  description: '',
});

const handleSubmit = () => {
  emit('save', formData.value);
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
  background-color: var(--bg-color, #fff);
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.modal-content h3 {
    margin-top: 0;
    color: var(--text-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--text-color);
}

.form-group input {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 5px;
  background-color: var(--card-bg-color);
  color: var(--text-color);
}

/* Стилизация редактора Quill */
:deep(.ql-toolbar) {
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border-color: var(--border-color) !important;
}
:deep(.ql-container) {
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
    height: 150px;
    border-color: var(--border-color) !important;
    background-color: var(--card-bg-color);
    color: var(--text-color);
}
:deep(.ql-editor) {
    color: var(--text-color);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.btn-primary {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
</style>
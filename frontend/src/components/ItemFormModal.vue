<template>
  <div class="modal-backdrop" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Добавить новый элемент</h2>
        <button @click="closeModal" class="close-button">&times;</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Содержимое</label>
            <!-- Единственное поле ввода - редактор Quill -->
            <QuillEditor 
              v-model:content="content"
              theme="snow"
              toolbar="full"
              contentType="html"
              placeholder="Напишите заголовок (он будет выделен) и описание..."
            />
          </div>
          <div class="form-group">
            <label for="image">Изображение (опционально)</label>
            <input type="file" id="image" accept="image/*" @change="handleFileChange" class="file-input">
          </div>
          <div class="modal-footer">
            <button type="button" @click="closeModal" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-submit">Добавить</button>
          </div>
          <p v-if="error" class="error-message">{{ error }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useListsStore } from '@/store/lists';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';

const props = defineProps({
  listId: {
    type: Number,
    required: true,
  }
});

const emit = defineEmits(['close']);
const store = useListsStore();

// Единое состояние для всего контента
const content = ref('');
const error = ref(null);
const selectedFile = ref(null);

const closeModal = () => {
  emit('close');
};

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

// Функция для парсинга HTML и извлечения заголовка
const parseContent = (htmlContent) => {
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = htmlContent;

  const heading = tempDiv.querySelector('h1, h2, h3, h4, h5, h6');
  let title = '';
  
  if (heading) {
    // Ограничиваем длину извлеченного заголовка
    title = heading.innerText.trim().substring(0, 150);
    heading.parentNode.removeChild(heading);
  } else {
    // Ограничиваем длину заголовка из обычного текста
    title = tempDiv.innerText.trim().substring(0, 150) || '(Без названия)';
  }

  const description = tempDiv.innerHTML.trim();

  if (!title && !description) return null;

  return { title, description };
};


const handleSubmit = async () => {
  error.value = null;
  const parsedData = parseContent(content.value);

  if (!parsedData) {
    error.value = 'Пожалуйста, добавьте содержимое.';
    return;
  }

  try {
    const newItem = await store.addItem(props.listId, parsedData);
    
    // Если файл выбран, загружаем его
    if (selectedFile.value) {
      await store.uploadItemImage(newItem.id, selectedFile.value);
    }
    
    closeModal();
  } catch (e) {
    error.value = store.error || 'Не удалось создать элемент.';
  }
};
</script>

<style scoped>
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
  background-color: var(--bg-color, #fff);
  color: var(--text-color, #333);
  padding: 2rem;
  border-radius: 10px;
  width: 90%;
  max-width: 700px; /* Увеличим ширину для редактора */
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color, #eee);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.modal-header h2 {
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--text-color, #333);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.file-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 4px;
  background-color: var(--card-bg-color, #fff);
  color: var(--text-color, #333);
}

/* Стили для Quill Editor */
.form-group :deep(.ql-editor) {
  min-height: 200px;
  background-color: var(--card-bg-color, #fff);
  color: var(--text-color, #333);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color, #eee);
}

.modal-footer button {
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-submit {
  background-color: var(--primary-color, #007bff);
  color: var(--primary-text-color, #fff);
}

.error-message {
  color: var(--secondary-color, #dc3545);
  margin-top: 1rem;
  text-align: right;
}
</style>
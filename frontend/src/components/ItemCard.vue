<template>
  <div class="item-card">
    <!-- Кнопка удаления теперь позиционируется абсолютно -->
    <button @click="handleDeleteItem" class="btn-delete">Удалить</button>
    
    <div class="card-content">
      <!-- Состояние 1: Отображение контента. Кликабельно для начала редактирования. -->
      <div 
        v-if="!isEditing" 
        @click="startEditing" 
        class="content-display"
      >
        <!-- Отображаем заголовок и описание вместе -->
        <h3 v-if="item.title">{{ item.title }}</h3>
        <div v-html="item.description || (!item.title ? '<p style=\'color: #888;\'>Нажмите, чтобы добавить содержимое...</p>' : '')"></div>
      </div>

      <!-- Состояние 2: Редактирование контента с помощью редактора Quill. -->
      <div v-else class="content-editor">
        <QuillEditor 
          v-model:content="editableContent"
          theme="snow"
          toolbar="full"
          contentType="html"
          placeholder="Напишите заголовок, а затем описание..."
        />
        <div class="editor-actions">
          <button @click="saveChanges" class="btn-save">Сохранить</button>
          <button @click="cancelEditing" class="btn-cancel">Отмена</button>
        </div>
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
  item: {
    type: Object,
    required: true,
  }
});

const store = useListsStore();
const isEditing = ref(false);
// Теперь редактируем весь контент целиком
const editableContent = ref('');

// Функция для парсинга HTML и извлечения заголовка
const parseContent = (htmlContent) => {
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = htmlContent;

  // Ищем первый попавшийся заголовок
  const heading = tempDiv.querySelector('h1, h2, h3, h4, h5, h6');
  let title = props.item.title; // Сохраняем старый заголовок на случай, если новый не найден
  
  if (heading) {
    title = heading.innerText.trim().substring(0, 150);
    // Удаляем заголовок из контента, чтобы он не дублировался в описании
    heading.parentNode.removeChild(heading);
  } else {
    // Если заголовка нет, берем первые 150 символов текста без HTML
    title = tempDiv.innerText.trim().substring(0, 150) || '(Без названия)';
  }

  const description = tempDiv.innerHTML.trim();

  return { title, description };
};


const startEditing = () => {
  // Инициализируем редактор, объединяя заголовок и описание
  const titleHtml = props.item.title ? `<h3>${props.item.title}</h3>` : '';
  editableContent.value = `${titleHtml}${props.item.description || ''}`;
  isEditing.value = true;
};

const cancelEditing = () => {
  isEditing.value = false;
};

const saveChanges = async () => {
  try {
    const { title, description } = parseContent(editableContent.value);
    await store.updateItem(props.item.id, { title, description });
    isEditing.value = false;
  } catch (error) {
    console.error("Не удалось сохранить элемент:", error);
  }
};

const handleDeleteItem = async () => {
  if (confirm(`Вы уверены, что хотите удалить этот элемент?`)) {
    try {
      await store.deleteItem(props.item.id);
    } catch (error) {
      console.error("Не удалось удалить элемент:", error);
    }
  }
};
</script>

<style scoped>
.item-card {
  position: relative; /* Необходимо для позиционирования кнопки удаления */
  background-color: var(--card-bg-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  color: var(--text-color);
}

.btn-delete {
  position: absolute;
  top: 10px;
  right: 10px;
  border: none;
  background-color: var(--secondary-color);
  color: var(--secondary-text-color);
  padding: 0.4rem 0.8rem;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s;
  opacity: 0.5; /* Делаем менее заметной по умолчанию */
}

.item-card:hover .btn-delete {
  opacity: 1; /* Показываем при наведении на карточку */
}

.btn-delete:hover {
  opacity: 0.85;
}

.content-display {
  cursor: pointer;
  min-height: 40px;
  border: 1px solid transparent;
  padding: 5px;
  border-radius: 5px;
  transition: background-color 0.2s, border-color 0.2s;
}
.content-display:hover {
  background-color: rgba(0,0,0,0.03);
  border-color: var(--border-color);
}

/* Стили для контента, отображаемого внутри .content-display */
.content-display :deep(h3) {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
}
.content-display :deep(p:first-child) {
  margin-top: 0;
}
.content-display :deep(p:last-child) {
  margin-bottom: 0;
}

/* НОВЫЙ СТИЛЬ: Масштабирование изображений */
.content-display :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin-top: 0.5rem;
}


.content-editor {
  border: 1px solid var(--border-color);
  border-radius: 5px;
}

.content-editor :deep(.ql-editor) {
    min-height: 150px;
    font-size: 1rem;
    background-color: var(--card-bg-color);
    color: var(--text-color);
}
.content-editor :deep(.ql-toolbar) {
    background-color: #f1f1f1;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 10px;
  background-color: #f1f1f1;
  border-bottom-left-radius: 5px;
  border-bottom-right-radius: 5px;
}

.editor-actions button {
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
}

.btn-save {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}

.btn-cancel {
  background-color: #6c757d;
  color: #ffffff;
}
</style>
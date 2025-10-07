<template>
  <div class="modal-backdrop" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2 :class="{'editing-title': props.initialItem}">{{ props.initialItem ? 'Редактировать элемент' : 'Добавить новый элемент' }}</h2>
        <button @click="closeModal" class="close-button">&times;</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="title">Заголовок</label>
            <input type="text" id="title" v-model="title" placeholder="Введите заголовок элемента">
          </div>
          <div class="form-group">
            <label>Содержимое</label>
            <!-- Единственное поле ввода - редактор Quill -->
            <QuillEditor 
              v-model:content="content"
              theme="snow"
              :toolbar="[
                ['bold', 'italic', 'underline', 'strike'],
                ['image'],
              ]"
              contentType="html"
              placeholder="Напишите заголовок (он будет выделен) и описание..."
            />
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
import { ref, watch, onMounted } from 'vue';
import { useListsStore } from '@/store/lists';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  listId: {
    type: Number,
    required: true,
  },
  itemToEdit: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close']);

const listsStore = useListsStore();
const title = ref('');
const description = ref('');
const errorMessage = ref('');

// Настройки для Quill редактора
const quillOptions = {
  theme: 'snow',
  placeholder: 'Добавьте подробное описание...',
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['link', 'image'], // 1. Возвращаем кнопку 'image' в панель инструментов
      ['clean']
    ]
  }
};


// Отслеживаем изменения в itemToEdit, чтобы заполнять форму при редактировании
watch(() => props.itemToEdit, (newItem) => {
  if (newItem) {
    title.value = newItem.title;
    description.value = newItem.description || '';
  } else {
    // Сбрасываем форму, когда добавляем новый элемент
    title.value = '';
    description.value = '';
  }
});

// 1. Функция для закрытия модального окна
const store = useListsStore();

// Единое состояние для всего контента
const content = ref(props.initialItem?.description || '');
const title = ref(props.initialItem?.title || ''); // Новое состояние для заголовка
const error = ref(null);

const closeModal = () => {
  emit('close');
};

// Функция для парсинга HTML и извлечения заголовка - УДАЛЕНО
// const parseContent = (htmlContent) => {
//   const tempDiv = document.createElement('div');
//   tempDiv.innerHTML = htmlContent;

//   const heading = tempDiv.querySelector('h1, h2, h3, h4, h5, h6');
//   let title = '';
  
//   if (heading) {
//     title = heading.innerText.trim().substring(0, 150);
//     heading.parentNode.removeChild(heading);
//   } else {
//     title = tempDiv.innerText.trim().substring(0, 150) || '(Без названия)';
//   }

//   const description = tempDiv.innerHTML.trim();

//   if (!title && !description) return null;

//   return { title, description };
// };


const handleSubmit = async () => {
  if (!title.value.trim()) {
    errorMessage.value = 'Название не может быть пустым.';
  error.value = null;
  // const parsedData = parseContent(content.value); // Больше не нужно

  if (!title.value.trim() && !content.value.trim()) {
    error.value = 'Пожалуйста, добавьте заголовок или содержимое.';
    return;
  }
  errorMessage.value = '';

  const itemData = {
    title: title.value,
    description: description.value,
  };

  try {
    if (props.itemToEdit) {
      // Обновляем существующий элемент
      await listsStore.updateItem(props.itemToEdit.id, itemData);
    if (props.initialItem) {
      // Обновление существующего элемента
      await store.updateItem(props.initialItem.id, { 
        title: title.value,
        description: content.value,
      });
    } else {
      // Добавляем новый элемент
      await listsStore.addItem(props.listId, itemData);
      // Добавление нового элемента
      await store.addItem(props.listId, {
        title: title.value,
        description: content.value,
      });
    }
    closeModal(); // Закрываем окно после успешной операции
  } catch (error) {
    errorMessage.value = listsStore.error || 'Произошла ошибка.';
  }
};
    
    closeModal();
  } catch (e) {
    console.error('Error during item submission:', e);
    error.value = store.error || 'Не удалось сохранить элемент.';
  }
};

// Убедимся, что контент обновляется, если initialItem изменяется (например, при открытии модального окна для другого элемента)
// watch(() => props.initialItem, (newItem) => {
//   content.value = newItem?.description || '';
// }, { immediate: true });

</script>

<template>
  <!-- 2. v-if управляет видимостью всего компонента -->
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <button class="modal-close" @click="closeModal">&times;</button>
      <h2>{{ itemToEdit ? 'Редактировать желание' : 'Добавить новое желание' }}</h2>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="item-title">Название</label>
          <input
            id="item-title"
            type="text"
            v-model="title"
            placeholder="Например, 'Поездка в горы'"
            required
          />
        </div>

        <div class="form-group">
          <label for="item-description">Описание</label>
          <QuillEditor
            v-model:content="description"
            contentType="html"
            :options="quillOptions"
            style="min-height: 150px; display: flex; flex-direction: column;"
          />
        </div>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="closeModal">Отмена</button>
          <button type="submit" class="btn-primary">
            {{ itemToEdit ? 'Сохранить' : 'Добавить' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

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
  /* 3. Устанавливаем сплошной цвет фона, чтобы перекрыть полупрозрачные темы */
  background-color: #ffffff; 
  color: #333; /* Устанавливаем стандартный цвет текста для лучшей читаемости */
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  position: relative;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 15px;
.modal-body {
  flex-grow: 1; /* Позволяем телу модального окна занимать все доступное пространство */
  overflow-y: auto; /* Добавляем вертикальную прокрутку при переполнении */
  padding-right: 1rem; /* Компенсация для прокрутки, чтобы контент не прилипал к краю */
  margin-right: -1rem; /* Скрываем избыточный отступ для прокрутки */
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

.modal-header h2.editing-title {
  color: var(--primary-color, #007bff); /* Пример стиля: изменить цвет для выделения */
  /* Можно добавить другие стили, например, font-weight или border-bottom */
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--text-color);
  opacity: 0.7;
}
.modal-close:hover {
  opacity: 1;
}

h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #4B0082; /* Пример цвета из вашей темы для заголовка */
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #4B0082;
}

/* Стили для полей ввода заголовка и обычных текстовых полей */
.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 4px;
  background-color: var(--card-bg-color, #fff);
  color: var(--text-color, #333);
  box-sizing: border-box; /* Важно для корректной ширины с padding */
  margin-top: 0.5rem; /* Отступ сверху для лучшей читаемости */
}

.form-group input[type="text"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #D8BFD8;
  border-radius: 4px;
  font-size: 1rem;
  background-color: #f9f9f9;
  color: #333;
}
.form-group input[type="text"]:focus {
  outline: none;
  border-color: #8A2BE2;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
}

.btn-primary {
  background-color: #8A2BE2;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.error-message {
  color: var(--secondary-color);
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid var(--secondary-color);
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  margin-top: 1rem;
}

/* Стили для Quill Editor, чтобы они соответствовали общему виду */
.form-group :deep(.ql-toolbar) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  border-color: #D8BFD8;
}
.form-group :deep(.ql-container) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-color: #D8BFD8;
  flex-grow: 1;
  font-size: 1rem;
}
.form-group :deep(.ql-editor) {
  background-color: #f9f9f9;
  color: #333;
}
</style>
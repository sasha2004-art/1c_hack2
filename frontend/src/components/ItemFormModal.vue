<script setup>
import { ref, watch } from 'vue';
import { useListsStore } from '@/store/lists';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import { apiClient } from '@/store/auth'; // <-- Импортируем apiClient

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

// --- НОВЫЕ ref ДЛЯ ПОДБОРА КАРТИНОК ---
const imageSuggestions = ref([]);
const isSuggestionsLoading = ref(false);
let debounceTimer = null;
const editorRef = ref(null); // Ref для доступа к Quill API

const quillOptions = {
  theme: 'snow',
  placeholder: 'Добавьте подробное описание или вставьте ссылку на картинку...',
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['link', 'image'],
      ['clean']
    ],
    clipboard: {
      matchers: [
        [Node.TEXT_NODE, (node, delta) => {
          const text = node.data;
          const urlRegex = /(https?:\/\/[^\s]+)/i;
          const match = text.match(urlRegex);

          if (match && text.trim() === match[0]) {
            const originalUrl = match[0];
            const proxyUrl = `http://localhost:8000/utils/image-proxy?url=${encodeURIComponent(originalUrl)}`;

            return {
              ops: [{ insert: { image: proxyUrl } }]
            };
          }
          
          return delta;
        }]
      ]
    }
  }
};


watch(() => props.itemToEdit, (newItem) => {
  if (newItem) {
    title.value = newItem.title;
    description.value = newItem.description || '';
  } else {
    title.value = '';
    description.value = '';
  }
  imageSuggestions.value = []; // Очищаем предложения при открытии
});

// --- НОВЫЙ watch ДЛЯ ПОИСКА КАРТИНОК ---
watch(title, (newTitle) => {
  clearTimeout(debounceTimer);
  if (newTitle.trim().length < 3) {
    imageSuggestions.value = [];
    return;
  }
  isSuggestionsLoading.value = true;
  debounceTimer = setTimeout(async () => {
    try {
      const response = await apiClient.get(`/utils/image-suggestions?query=${newTitle}`);
      imageSuggestions.value = response.data;
    } catch (error) {
      console.error("Failed to fetch image suggestions:", error);
      imageSuggestions.value = [];
    } finally {
      isSuggestionsLoading.value = false;
    }
  }, 500); // Задержка в 500 мс
});

// --- НОВАЯ ФУНКЦИЯ ДЛЯ ВЫБОРА КАРТИНКИ ---
const selectImage = (imageUrl) => {
    // Используем наш прокси-сервер для вставки картинки, чтобы избежать проблем с CORS у пользователя
    const proxyUrl = `http://localhost:8000/utils/image-proxy?url=${encodeURIComponent(imageUrl)}`;
    const quill = editorRef.value?.getQuill();
    if (quill) {
        const range = quill.getSelection(true);
        // Вставляем картинку и переводим курсор на новую строку после нее
        quill.insertEmbed(range.index, 'image', proxyUrl, 'user');
        quill.setSelection(range.index + 1);
    }
    imageSuggestions.value = []; // Скрываем предложения после выбора
};


const closeModal = () => {
  emit('close');
};

const handleSubmit = async () => {
  if (!title.value.trim()) {
    errorMessage.value = 'Название не может быть пустым.';
    return;
  }
  errorMessage.value = '';

  const itemData = {
    title: title.value,
    description: description.value,
  };

  try {
    if (props.itemToEdit) {
      await listsStore.updateItem(props.itemToEdit.id, itemData);
    } else {
      await listsStore.addItem(props.listId, itemData);
    }
    closeModal();
  } catch (error) {
    errorMessage.value = listsStore.error || 'Произошла ошибка.';
  }
};
</script>

<template>
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

        <!-- --- НОВЫЙ БЛОК ДЛЯ ПРЕДЛОЖЕНИЙ --- -->
        <div class="suggestions-container" v-if="isSuggestionsLoading || imageSuggestions.length > 0">
            <div v-if="isSuggestionsLoading" class="suggestions-loader">Ищем картинки...</div>
            <div v-else class="image-suggestions-grid">
                <img 
                    v-for="suggestion in imageSuggestions" 
                    :key="suggestion.id" 
                    :src="suggestion.urls.small" 
                    :alt="suggestion.description"
                    @click="selectImage(suggestion.urls.regular)"
                    class="suggestion-image"
                />
            </div>
        </div>
        
        <div class="form-group">
          <label for="item-description">Описание</label>
          <QuillEditor
            ref="editorRef"
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
/* Стили остаются без изменений */
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
  background-color: #ffffff; 
  color: #333;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  position: relative;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  max-height: 95vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-content form {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #333;
  opacity: 0.7;
}
.modal-close:hover {
  opacity: 1;
}

h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #4B0082;
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
  color: #dc3545;
  background-color: rgba(220, 53, 69, 0.1);
  border: 1px solid #dc3545;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  margin-top: 1rem;
}

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

/* --- НОВЫЕ СТИЛИ ДЛЯ ПРЕДЛОЖЕНИЙ --- */
.suggestions-container {
    margin-bottom: 1rem;
    background-color: #f9f9f9;
    border: 1px solid #D8BFD8;
    border-radius: 4px;
    padding: 0.5rem;
}
.suggestions-loader {
    text-align: center;
    color: #888;
    padding: 1rem;
}
.image-suggestions-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
}
.suggestion-image {
    width: 100%;
    height: 100px;
    object-fit: cover;
    border-radius: 4px;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}
.suggestion-image:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
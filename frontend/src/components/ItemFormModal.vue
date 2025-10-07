<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ isEditing ? 'Редактировать элемент' : 'Добавить элемент' }}</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleSave">
          <div class="form-group">
            <label for="item-title">Название</label>
            <input id="item-title" v-model="editableItem.title" type="text" required>
          </div>
          
          <div class="form-group">
            <label for="item-description">Описание (необязательно)</label>
            <!-- Для редактора используется Quill, как указано в package.json -->
            <QuillEditor theme="snow" contentType="html" v-model:content="editableItem.description" />
          </div>

          <div class="form-group">
            <label for="image-search">Поиск изображения</label>
            <input 
              id="image-search" 
              type="text" 
              v-model="imageQuery" 
              @input="debouncedSearchImages"
              placeholder="Введите ключевые слова (например, 'книга')"
            >
          </div>

          <!-- Контейнер для найденных изображений с прокруткой -->
          <div v-if="isSearching || imageSuggestions.length > 0" class="image-selector-container">
            <div v-if="isSearching" class="loader">Загрузка...</div>
            
            <!-- ВОТ КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: этот div теперь имеет скролл -->
            <div v-else class="image-suggestions">
              <img
                v-for="img in imageSuggestions"
                :key="img.id"
                :src="img.urls.thumb"
                :alt="img.alt_description"
                :class="{ selected: editableItem.image_url === img.urls.regular }"
                @click="selectImage(img)"
              />
            </div>
          </div>

          <!-- Предпросмотр выбранного изображения -->
          <div v-if="editableItem.image_url" class="image-preview">
            <label>Выбранное изображение:</label>
            <img :src="proxiedImageUrl" alt="Предпросмотр">
          </div>

        </form>
      </div>
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">Отмена</button>
        <button @click="handleSave" class="btn-primary" :disabled="isLoading">
          {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useListsStore } from '@/store/lists';
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import { apiClient } from '@/store/auth'; // Импортируем apiClient

const props = defineProps({
  item: {
    type: Object,
    default: null,
  },
  listId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(['close', 'saved']);
const listsStore = useListsStore();

const isEditing = computed(() => !!props.item);
const isLoading = ref(false);
const editableItem = ref({
  title: '',
  description: '',
  image_url: null,
  thumbnail_url: null,
});

const imageQuery = ref('');
const imageSuggestions = ref([]);
const isSearching = ref(false);
let debounceTimer = null;

// Используем прокси для изображений с Unsplash, чтобы избежать проблем с CORS
const proxiedImageUrl = computed(() => {
  if (!editableItem.value.image_url) return '';
  // Проверяем, не является ли URL уже локальным
  if (editableItem.value.image_url.startsWith('/')) {
    return `http://localhost:8000${editableItem.value.image_url}`;
  }
  return `http://localhost:8000/utils/image-proxy?url=${encodeURIComponent(editableItem.value.image_url)}`;
});

watch(() => props.item, (newItem) => {
  if (newItem) {
    editableItem.value = { ...newItem };
  } else {
    editableItem.value = { title: '', description: '', image_url: null, thumbnail_url: null };
  }
}, { immediate: true });

async function searchImages() {
  if (imageQuery.value.length < 3) {
    imageSuggestions.value = [];
    return;
  }
  isSearching.value = true;
  imageSuggestions.value = [];
  try {
    // Эта логика может быть вынесена в store, но для простоты оставим здесь
    // Предполагается, что у вас есть эндпоинт для поиска картинок
    const response = await apiClient.get(`/utils/image-suggestions?query=${imageQuery.value}`);
    imageSuggestions.value = response.data;
  } catch (error) {
    console.error("Ошибка при поиске изображений:", error);
  } finally {
    isSearching.value = false;
  }
}

// Функция для отложенного вызова поиска, чтобы не слать запрос на каждую букву
function debouncedSearchImages() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    searchImages();
  }, 500); // задержка в 500 мс
}

function selectImage(img) {
  editableItem.value.image_url = img.urls.regular;
  editableItem.value.thumbnail_url = img.urls.thumb;
}

async function handleSave() {
  isLoading.value = true;
  try {
    if (isEditing.value) {
      await listsStore.updateItem(editableItem.value.id, editableItem.value);
    } else {
      await listsStore.addItem(props.listId, editableItem.value);
    }
    emit('saved');
    emit('close');
  } catch (error) {
    console.error('Ошибка сохранения элемента:', error);
    // Можно показать пользователю сообщение об ошибке
  } finally {
    isLoading.value = false;
  }
}
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
  background: var(--card-bg-color, white);
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  max-height: 90vh; /* Ограничиваем высоту всего модального окна */
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color, #eee);
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  color: var(--text-color);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-color);
}

/* Эта обертка позволяет телу модального окна скроллиться независимо от хедера и футера */
.modal-body {
  overflow-y: auto; /* Главный скролл для всего тела, если оно не помещается */
  padding-right: 10px; /* Чтобы скроллбар не наезжал на контент */
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: var(--text-color);
  font-weight: bold;
}

input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 4px;
  box-sizing: border-box;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border-color, #eee);
  padding-top: 15px;
  margin-top: 20px;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-left: 10px;
}

.btn-primary {
  background-color: var(--primary-color, #007bff);
  color: var(--primary-text-color, white);
}
.btn-primary:disabled {
  background-color: #a0c4e4;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

/* Стили для редактора текста */
:deep(.ql-editor) {
    min-height: 100px;
    background-color: #fff;
    color: #333;
}

/* ======================================= */
/* ====== КЛЮЧЕВЫЕ ИЗМЕНЕНИЯ ЗДЕСЬ ====== */
/* ======================================= */

.image-selector-container {
  border: 1px solid var(--border-color, #ccc);
  border-radius: 4px;
  padding: 10px;
}

.image-suggestions {
  /* 1. Устанавливаем максимальную высоту для блока с картинками */
  max-height: 250px; /* Вы можете подобрать удобное значение */
  
  /* 2. Добавляем автоматическую вертикальную прокрутку */
  overflow-y: auto;
  
  /* 3. Стили для красивого отображения галереи */
  display: flex;
  flex-wrap: wrap;
  gap: 10px; /* Отступы между картинками */
}

.image-suggestions img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  cursor: pointer;
  border-radius: 4px;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.image-suggestions img:hover {
  border-color: var(--primary-color, #007bff);
}

.image-suggestions img.selected {
  border-color: var(--edit-color, #ffc107);
  box-shadow: 0 0 5px var(--edit-color, #ffc107);
}

.image-preview {
  margin-top: 15px;
}

.image-preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
  margin-top: 5px;
}

.loader {
  text-align: center;
  padding: 20px;
  color: var(--text-color);
}
</style>
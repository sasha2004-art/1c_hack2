<script setup>
import { ref, watch } from 'vue';
import { useListsStore } from '@/store/lists';
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import { apiClient } from '@/store/auth';

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  listId: {
    type: Number,
    required: true,
  },
  // ---> ДОБАВЬТЕ ЭТОТ НОВЫЙ PROP <---
  listType: {
    type: String,
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

const isGoal = ref(false);
const goalType = ref('cumulative');
const targetValue = ref(null);
const targetCount = ref(null);
const unitName = ref('');

const imageSuggestions = ref([]);
const isSuggestionsLoading = ref(false);
let debounceTimer = null;
const editorRef = ref(null);

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
  imageSuggestions.value = [];
  if (newItem) {
    title.value = newItem.title;
    description.value = newItem.description || '';
    if (newItem.goal_tracker) {
      isGoal.value = true;
      const tracker = newItem.goal_tracker;
      goalType.value = tracker.goal_type;
      targetValue.value = tracker.target_value;
      targetCount.value = tracker.target_count;
      unitName.value = tracker.unit_name || '';
    } else {
      isGoal.value = false;
      goalType.value = 'cumulative';
      targetValue.value = null;
      targetCount.value = null;
      unitName.value = '';
    }
  } else {
    title.value = '';
    description.value = '';
    isGoal.value = false;
    goalType.value = 'cumulative';
    targetValue.value = null;
    targetCount.value = null;
    unitName.value = '';
  }
});

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
  }, 500);
});

const selectImage = (imageUrl) => {
    const proxyUrl = `http://localhost:8000/utils/image-proxy?url=${encodeURIComponent(imageUrl)}`;
    const quill = editorRef.value?.getQuill();
    if (quill) {
        const range = quill.getSelection(true);
        quill.insertEmbed(range.index, 'image', proxyUrl, 'user');
        quill.setSelection(range.index + 1);
    }
    imageSuggestions.value = [];
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

  const goalSettingsData = {
    goal_type: goalType.value,
    unit_name: unitName.value.trim() || null,
    target_value: goalType.value === 'cumulative' ? parseFloat(targetValue.value) || 0 : null,
    target_count: goalType.value === 'check_in' ? parseInt(targetCount.value, 10) || 0 : null,
  };
  
  try {
    if (props.itemToEdit) {
      await listsStore.updateItem(props.itemToEdit.id, itemData);
      
      if (props.itemToEdit.goal_tracker) {
        await listsStore.updateGoalSettings(props.itemToEdit.goal_tracker.id, goalSettingsData);
      }
    } else {
      if (isGoal.value) {
        itemData.goal_settings = goalSettingsData;
      }
      await listsStore.addItem(props.listId, itemData);
    }
    closeModal();
  } catch (error) {
    errorMessage.value = listsStore.error || 'Произошла ошибка.';
  }
};

const handleDelete = async () => {
  if (!props.itemToEdit) return;

  if (confirm('Вы уверены, что хотите удалить этот элемент? Это действие необратимо.')) {
    try {
      await listsStore.deleteItem(props.itemToEdit.id);
      closeModal();
    } catch (error) {
      errorMessage.value = listsStore.error || 'Не удалось удалить элемент.';
    }
  }
};
</script>

<template>
  <!-- ИЗМЕНЕНИЕ: Оборачиваем в transition -->
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
      <!-- ИЗМЕНЕНИЕ: Оборачиваем в transition -->
      <transition name="pop">
        <div v-if="isOpen" class="modal-content">
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
            
            <div v-if="listType === 'todo'" class="goal-settings-section">
              <div class="form-group-checkbox">
                <input type="checkbox" id="is-goal" v-model="isGoal" :disabled="!!itemToEdit && !!itemToEdit.goal_tracker" />
                <label for="is-goal">Сделать целью с отслеживанием?</label>
              </div>

              <div v-if="isGoal" class="goal-options">
                <div class="form-group">
                  <label>Тип цели</label>
                  <select v-model="goalType">
                    <option value="cumulative">Прогресс (накопить значение)</option>
                    <option value="check_in">Привычка (сделать N раз)</option>
                  </select>
                </div>
                
                <div v-if="goalType === 'cumulative'" class="form-group">
                  <label for="target-value">Целевое значение</label>
                  <input id="target-value" type="number" step="0.1" v-model="targetValue" placeholder="Например: 1000" required />
                </div>

                <div v-if="goalType === 'check_in'" class="form-group">
                  <label for="target-count">Целевое количество раз</label>
                  <input id="target-count" type="number" step="1" v-model="targetCount" placeholder="Например: 30" required />
                </div>

                <div class="form-group">
                  <label for="unit-name">Единица измерения</label>
                  <input id="unit-name" type="text" v-model="unitName" placeholder="Например: страниц, км, раз" />
                </div>
              </div>
            </div>

            <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

            <div class="form-actions">
              <button
                v-if="itemToEdit"
                type="button"
                class="btn-danger"
                @click="handleDelete"
              >
                Удалить
              </button>
              
              <div class="spacer"></div>
              
              <button type="button" class="btn-secondary" @click="closeModal">Отмена</button>
              <button type="submit" class="btn-primary">
                {{ itemToEdit ? 'Сохранить' : 'Добавить' }}
              </button>
            </div>
          </form>
        </div>
      </transition>
    </div>
  </transition>
</template>


<style scoped>
/* НОВЫЕ СТИЛИ: Анимация для модального окна */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.pop-enter-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.pop-leave-active {
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.pop-enter-from,
.pop-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

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

.form-group input[type="text"],
.form-group input[type="number"] { /* ИЗМЕНЕНИЕ: добавил number */
  width: 100%;
  padding: 10px;
  border: 1px solid #D8BFD8;
  border-radius: 4px;
  font-size: 1rem;
  background-color: #f9f9f9;
  color: #333;
  box-sizing: border-box; /* ИЗМЕНЕНИЕ: для корректного рендеринга */
}
.form-group input[type="text"]:focus,
.form-group input[type="number"]:focus { /* ИЗМЕНЕНИЕ: добавил number */
  outline: none;
  border-color: #8A2BE2;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  gap: 1rem;
  margin-top: 1.5rem;
  align-items: center;
}

.spacer {
  flex-grow: 1;
}

.btn-primary, .btn-secondary, .btn-danger {
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
.btn-danger {
  background-color: var(--secondary-color, #dc3545);
  color: var(--secondary-text-color, white);
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

.goal-settings-section {
  border: 1px solid #D8BFD8;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  background-color: #fcfaff;
}
.form-group-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.form-group-checkbox label {
  font-weight: bold;
  margin-bottom: 0;
}
.goal-options {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed #D8BFD8;
}
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #D8BFD8;
  border-radius: 4px;
  background-color: #f9f9f9;
}
</style>
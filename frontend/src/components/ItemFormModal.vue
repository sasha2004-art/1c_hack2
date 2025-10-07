<template>
  <div class="modal-overlay" v-if="show">
    <div class="modal-content">
      <h3 class="modal-title">{{ formTitle }}</h3>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title">Название</label>
          <input id="title" type="text" v-model="formData.title" required>
        </div>
        
        <!-- Поле "Описание" теперь является основным полем для форматированного текста -->
        <div class="form-group">
          <label>Описание</label>
          <QuillEditor 
            v-model:content="formData.description" 
            contentType="html" 
            theme="snow"
            placeholder="Добавьте форматированный текст, ссылки и детали..."
          />
        </div>

        <!-- Блок с полем "Детали" полностью удален -->

        <div class="modal-actions">
          <button type="button" @click="close" class="btn-cancel">Отмена</button>
          <button type="submit" class="btn-save">Сохранить</button>
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

// ИЗМЕНЕНИЕ: Убрали 'details' из состояния формы
const formData = ref({
  id: null,
  title: '',
  description: ''
});

const formTitle = computed(() => props.item ? 'Редактировать элемент' : 'Добавить новый элемент');

// ИЗМЕНЕНИЕ: Убрали 'details' из логики заполнения формы
watch(() => props.item, (newItem) => {
  if (newItem) {
    formData.value = { 
      id: newItem.id,
      title: newItem.title || '',
      description: newItem.description || ''
    };
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
  background-color: #F5F5DC; /* Coffee theme background */
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.modal-title {
  color: #8B4513; /* Coffee theme text */
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #D2B48C;
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #8B4513;
  font-weight: bold;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #D2B48C;
  border-radius: 4px;
  background-color: #FFFDF6;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

button {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  color: white;
}

.btn-save {
  background-color: #A0522D; /* Primary coffee color */
}

.btn-cancel {
  background-color: #DEB887; /* Secondary coffee color */
  color: #8B4513;
}

:deep(.ql-toolbar) {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  border-color: #D2B48C !important;
}
:deep(.ql-container) {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-color: #D2B48C !important;
  background-color: #FFFDF6;
  min-height: 120px;
}
</style>
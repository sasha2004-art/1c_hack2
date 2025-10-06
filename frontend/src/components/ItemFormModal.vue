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
          <label for="description">Описание</label>
          <textarea id="description" v-model="form.description"></textarea>
        </div>
        <div class="form-group">
          <label for="details">Дополнительные данные (JSON)</label>
          <textarea id="details" v-model="detailsAsJson" rows="4"></textarea>
          <small v-if="jsonError" class="json-error">Некорректный формат JSON</small>
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

const props = defineProps({
  isVisible: Boolean,
  itemToEdit: Object,
});

const emit = defineEmits(['close', 'save']);

const form = ref({});
const detailsAsJson = ref('');
const jsonError = ref(false);

watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    jsonError.value = false;
    if (props.itemToEdit) {
      // Режим редактирования
      form.value = { ...props.itemToEdit };
      detailsAsJson.value = props.itemToEdit.details
        ? JSON.stringify(props.itemToEdit.details, null, 2)
        : '';
    } else {
      // Режим создания
      form.value = { title: '', description: '' };
      detailsAsJson.value = '';
    }
  }
});

const formTitle = computed(() => {
  return props.itemToEdit ? 'Редактировать элемент' : 'Добавить новый элемент';
});

function submitForm() {
  let detailsObject = null;
  jsonError.value = false;

  if (detailsAsJson.value.trim()) {
    try {
      detailsObject = JSON.parse(detailsAsJson.value);
    } catch (e) {
      jsonError.value = true;
      return; // Остановить отправку, если JSON невалиден
    }
  }

  const payload = {
    title: form.value.title,
    description: form.value.description,
    details: detailsObject,
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
  max-width: 500px;
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
}
.btn-save { background-color: #42b983; color: white; }
.btn-cancel { background-color: #6c757d; color: white; }
button { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; }
.json-error { color: red; font-size: 0.8rem; }
</style>
<!-- --- КОНЕЦ ФАЙЛА: frontend/src/components/ItemFormModal.vue --- -->
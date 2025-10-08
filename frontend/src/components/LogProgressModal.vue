<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h4>Записать прогресс</h4>
      <p v-if="tracker">Цель: <strong>{{ tracker.unit_name || 'раз' }}</strong></p>
      <div class="form-group">
        <input
          type="number"
          v-model.number="valueToAdd"
          placeholder="Например: 25.5"
          step="0.1"
          min="0"
          ref="inputRef"
        />
      </div>
      <div class="form-actions">
        <button @click="$emit('close')" class="btn-secondary">Отмена</button>
        <button @click="handleSubmit" :disabled="!isValid" class="btn-primary">Записать</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  tracker: Object,
});

const emit = defineEmits(['close', 'submit']);

const valueToAdd = ref(null);
const inputRef = ref(null);

const isValid = computed(() => typeof valueToAdd.value === 'number' && valueToAdd.value > 0);

const handleSubmit = () => {
  if (isValid.value) {
    emit('submit', valueToAdd.value);
    emit('close');
  }
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    valueToAdd.value = null;
    // Фокусируемся на инпуте при открытии
    nextTick(() => {
      inputRef.value?.focus();
    });
  }
});
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
  z-index: 1010; /* Выше чем другие модалки */
}
.modal-content {
  background: #fff;
  color: #333;
  padding: 1.5rem;
  border-radius: 8px;
  width: 90%;
  max-width: 350px;
}
h4 {
  margin-top: 0;
  text-align: center;
}
.form-group input {
  width: 100%;
  padding: 10px;
  font-size: 1.2rem;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
}
.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
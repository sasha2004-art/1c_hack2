<template>
  <div class="theme-selector">
    <button
      v-for="(theme, key) in themes"
      :key="key"
      type="button"
      class="theme-button"
      :class="{ 'selected': modelValue === key }"
      :style="getThemePreviewStyles(theme)"
      @click="selectTheme(key)"
    >
      {{ theme.name }}
      <span v-if="modelValue === key" class="checkmark">✓</span>
    </button>
  </div>
</template>

<script setup>
import { themes } from '../themes.js';

defineProps({
  modelValue: String
});

const emit = defineEmits(['update:modelValue']);

const selectTheme = (themeKey) => {
  emit('update:modelValue', themeKey);
};

// Функция для стилизации кнопок-превью
const getThemePreviewStyles = (theme) => {
  return {
    backgroundColor: theme.styles['--card-bg-color'],
    color: theme.styles['--text-color'],
    borderColor: theme.styles['--primary-color']
  };
};
</script>

<style scoped>
.theme-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
}

.theme-button {
  padding: 1rem 0.5rem;
  border: 2px solid #ccc;
  border-radius: 5px;
  cursor: pointer;
  text-align: center;
  font-weight: bold;
  position: relative;
  transition: all 0.2s ease;
}

.theme-button.selected {
  border-width: 3px;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.checkmark {
  position: absolute;
  top: 5px;
  right: 8px;
  font-size: 1.2rem;
  color: var(--border-color);
}
</style>
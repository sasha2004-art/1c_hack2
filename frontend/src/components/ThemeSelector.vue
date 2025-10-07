<template>
  <div class="theme-selector">
    <label>Тема оформления</label>
    <div class="theme-options">
      <div
        v-for="(theme, key) in themes"
        :key="key"
        class="theme-option"
        :class="{ 'selected': modelValue === key }"
        :style="{ backgroundColor: theme.styles['--bg-color'] }"
        @click="selectTheme(key)"
      >
        <span class="theme-name" :style="{ color: theme.styles['--text-color'] }">{{ theme.name }}</span>
        <div v-if="modelValue === key" class="checkmark">✔</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { themes } from '../themes.js';

defineProps({
  modelValue: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue']);

function selectTheme(themeKey) {
  emit('update:modelValue', themeKey);
}
</script>

<style scoped>
.theme-selector {
  margin-bottom: 1rem;
}
.theme-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 0.5rem;
}
.theme-option {
  padding: 10px;
  border-radius: 5px;
  border: 2px solid #ccc;
  cursor: pointer;
  text-align: center;
  position: relative;
  transition: transform 0.2s, border-color 0.2s;
}
.theme-option:hover {
  transform: scale(1.05);
}
.theme-option.selected {
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}
.theme-name {
  font-size: 0.9em;
  font-weight: bold;
}
.checkmark {
  position: absolute;
  top: 5px;
  right: 5px;
  color: #007bff;
  font-weight: bold;
}
</style>
<template>
  <div class="list-card" :style="cardStyle">
    <div class="card-content" @click="navigateToList">
      <h3 class="card-title">{{ list.title }}</h3>
      <p class="card-description">{{ list.description || 'Нет описания' }}</p>
    </div>
    <div class="card-footer">
      <div class="tags">
        <span class="tag tag-type">{{ list.list_type }}</span>
        <span class="tag tag-privacy">{{ list.privacy_level }}</span>
      </div>
      <div class="card-actions">
        <button class="btn-card btn-edit" @click="$emit('edit', list)">✏️</button>
        <button class="btn-card btn-delete" @click="$emit('delete', list.id)">🗑️</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { themes } from '../themes.js';

const props = defineProps({
  list: {
    type: Object,
    required: true
  }
});

defineEmits(['edit', 'delete']);

const router = useRouter();

// Вычисляемое свойство для применения стилей темы к карточке
const cardStyle = computed(() => {
  const themeName = props.list.theme_name || 'default';
  const theme = themes[themeName] || themes.default;
  return theme.styles;
});

function navigateToList() {
  router.push({ name: 'ListView', params: { id: props.list.id } });
}
</script>

<style scoped>
.list-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  /* Применяем переменные из темы */
  background-color: var(--card-bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.list-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.card-content {
  padding: 1.5rem;
  cursor: pointer;
}

.card-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: bold;
}

.card-description {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
  height: 40px; /* Ограничение высоты для единообразия */
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background-color: rgba(0, 0, 0, 0.03); /* Легкий фон для футера */
  border-top: 1px solid var(--border-color);
}

.tags {
  display: flex;
  gap: 8px;
  font-size: 0.75rem;
}

.tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.tag-type {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  opacity: 0.7;
}

.tag-privacy {
  background-color: #6c757d; /* Нейтральный цвет для приватности */
  color: white;
  opacity: 0.7;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.btn-card {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 5px;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}
.btn-card:hover {
  background-color: rgba(0, 0, 0, 0.1);
}
</style>
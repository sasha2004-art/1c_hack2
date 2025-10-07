<template>
  <div class="item-card">
    <div class="item-header">
      <h3>{{ item.title }}</h3>
      <div class="item-actions">
        <button @click="$emit('edit', item)" class="btn btn-edit">Редактировать</button>
        <button @click="$emit('delete', item.id)" class="btn btn-delete">Удалить</button>
      </div>
    </div>
    <div class="item-content" v-if="item.description" v-html="item.description"></div>
    <div class="item-meta" v-if="item.created_at">
      <small>Создано: {{ formatDate(item.created_at) }}</small>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  item: {
    type: Object,
    required: true
  }
});

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>

<style scoped>
.item-card {
  background-color: var(--card-bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s;
}

.item-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

h3 {
  margin: 0;
  color: var(--text-color);
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.8;
}

/* ИЗМЕНЕНИЕ: Кнопки теперь используют переменные темы */
.btn-edit {
  background-color: var(--edit-color);
  color: var(--edit-text-color);
}

.btn-delete {
  background-color: var(--delete-color);
  color: var(--delete-text-color);
}

.item-content {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.item-meta {
  opacity: 0.7;
  font-size: 0.85rem;
}
</style>
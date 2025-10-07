<template>
  <div class="item-card">
    <div class="card-header">
      <h4 class="item-title">{{ item.title }}</h4>
      <div class="card-actions">
        <button @click="$emit('edit', item)" class="btn-edit">Редактировать</button>
        <button @click="$emit('delete', item.id)" class="btn-delete">Удалить</button>
      </div>
    </div>
    
    <!-- Отображение отформатированного описания. Оно теперь главное. -->
    <div v-if="item.description" class="item-content ql-editor-display" v-html="item.description"></div>
    
    <!-- Блок для отображения деталей полностью удален -->
  </div>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true
  }
});

defineEmits(['edit', 'delete']);
</script>

<style scoped>
.item-card {
  background-color: rgba(255, 253, 246, 0.85); /* Coffee card background */
  border: 1px solid #D2B48C;
  border-radius: 6px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  color: #8B4513;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #D2B48C;
  padding-bottom: 1rem;
}

/* Добавляем margin, если есть контент ниже */
.card-header:not(:only-child) {
    margin-bottom: 1rem;
}

.item-title {
  margin: 0;
  font-size: 1.25rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-edit {
  background-color: #DEB887;
  color: #8B4513;
}

.btn-delete {
  background-color: #800000;
  color: white;
}

/* Общие стили для контента, чтобы он выглядел как в редакторе */
.ql-editor-display {
  font-size: 1rem;
  line-height: 1.6;
}

.ql-editor-display:deep(a) {
  color: #A0522D;
  text-decoration: underline;
}

.ql-editor-display:deep(p) {
  margin: 0 0 1rem;
}

.ql-editor-display:deep(ul),
.ql-editor-display:deep(ol) {
  padding-left: 1.5rem;
}

.ql-editor-display:deep(*:last-child) {
    margin-bottom: 0;
}
</style>
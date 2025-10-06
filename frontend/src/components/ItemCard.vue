<!-- --- НАЧАЛО ФАЙЛА: frontend/src/components/ItemCard.vue --- -->
<template>
  <div class="item-card">
    <h3>{{ item.title }}</h3>
    <p v-if="item.description">{{ item.description }}</p>

    <div v-if="item.details && Object.keys(item.details).length" class="item-details">
      <strong>Дополнительно:</strong>
      <pre>{{ JSON.stringify(item.details, null, 2) }}</pre>
    </div>

    <div class="card-actions">
      <button @click="$emit('edit', item)" class="btn-edit">Редактировать</button>
      <button @click="$emit('delete', item.id)" class="btn-delete">Удалить</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true,
  }
});

defineEmits(['edit', 'delete']);
</script>

<style scoped>
.item-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}
.item-card h3 {
  margin-top: 0;
}
.item-details {
  margin-top: 1rem;
  background-color: #f5f5f5;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  white-space: pre-wrap; /* чтобы json красиво переносился */
  word-break: break-all;
}
.card-actions {
  margin-top: auto; /* прижимает кнопки к низу */
  padding-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.btn-edit, .btn-delete {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-edit {
  background-color: #ffc107;
}
.btn-delete {
  background-color: #dc3545;
  color: white;
}
</style>
<!-- --- КОНЕЦ ФАЙЛА: frontend/src/components/ItemCard.vue --- -->
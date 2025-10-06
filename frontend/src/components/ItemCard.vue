<!-- --- НАЧАЛО ФАЙЛА: frontend/src/components/ItemCard.vue --- -->
<template>
  <div class="item-card">
    <h3>{{ item.title }}</h3>
    <p v-if="item.description">{{ item.description }}</p>
    
    <!-- ИЗМЕНЕНИЕ: Отображаем отформатированный текст с помощью v-html -->
    <div v-if="item.details" class="item-details ql-editor" v-html="item.details"></div>
    
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
  background: white;
}
.item-card h3 {
  margin-top: 0;
}
.item-details {
  margin-top: 1rem;
  padding: 0;
  font-size: 1rem;
  /* Сбрасываем стили, чтобы они наследовались от Quill */
  line-height: 1.5;
}
.card-actions {
  margin-top: auto;
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

/* 
  Мы добавляем класс ql-editor к нашему блоку v-html.
  Это позволяет нам использовать готовые стили Quill для списков, ссылок и т.д.,
  чтобы отображение в карточке соответствовало тому, что было в редакторе.
*/
.item-details.ql-editor {
  padding: 0; /* Убираем отступы по умолчанию */
}
</style>

<!-- Добавляем глобальные стили, чтобы v-html корректно отображал контент Quill -->
<style>
.item-details.ql-editor a {
  color: #007bff;
  text-decoration: underline;
}
.item-details.ql-editor ul, .item-details.ql-editor ol {
  padding-left: 1.5em;
}
.item-details.ql-editor h1, .item-details.ql-editor h2, .item-details.ql-editor h3 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}
</style>
<!-- --- КОНЕЦ ФАЙЛА: frontend/src/components/ItemCard.vue --- -->
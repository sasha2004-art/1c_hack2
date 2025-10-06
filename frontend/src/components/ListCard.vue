<!-- --- НАЧАЛО ФАЙЛА: frontend/src/components/ListCard.vue --- -->
<template>
  <router-link :to="{ name: 'ListView', params: { id: list.id } }" class="list-card-link">
    <div class="list-card">
      <h3>{{ list.title }}</h3>
      <p>{{ list.description || 'Нет описания' }}</p>
      <div class="card-footer">
        <span class="tag">{{ list.list_type }}</span>
        <span class="privacy-level">{{ list.privacy_level }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  list: {
    type: Object,
    required: true,
  }
});
</script>

<style scoped>
.list-card-link {
  text-decoration: none;
  color: inherit;
}
.list-card {
  border: 1px solid #eee;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%; /* Чтобы все карточки были одной высоты */
  display: flex;
  flex-direction: column;
}
.list-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.card-footer {
  margin-top: auto; /* Прижимает футер к низу */
  padding-top: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #666;
}
.tag {
  background-color: #e7f3ff;
  padding: 3px 8px;
  border-radius: 12px;
}
</style>
<!-- --- КОНЕЦ ФАЙЛА: frontend/src/components/ListCard.vue --- -->
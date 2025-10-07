<template>
  <nav class="pagination">
    <button 
      @click="goToPage(currentPage - 1)" 
      :disabled="currentPage === 1"
      class="pagination-button"
    >
      Предыдущая
    </button>
    <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
    <button 
      @click="goToPage(currentPage + 1)" 
      :disabled="currentPage === totalPages"
      class="pagination-button"
    >
      Следующая
    </button>
  </nav>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalItems: { type: Number, required: true },
  itemsPerPage: { type: Number, default: 10 }
});

const emit = defineEmits(['page-change']);

const totalPages = computed(() => Math.ceil(props.totalItems / props.itemsPerPage));

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    emit('page-change', page);
  }
};
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.pagination-button {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: var(--primary-color-dark);
}

.pagination-button:disabled {
  background-color: var(--button-disabled-bg);
  color: var(--button-disabled-text);
  cursor: not-allowed;
}

.page-info {
  color: var(--text-color);
  font-weight: bold;
}
</style>

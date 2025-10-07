<template>
  <div class="home-container">
    <header class="home-header">
      <h1>Мои списки</h1>
      <button class="btn btn-primary" @click="openCreateModal">Создать список</button>
    </header>

    <div v-if="listsStore.isLoading">Загрузка списков...</div>
    <div v-else-if="listsStore.error" class="error-message">{{ listsStore.error }}</div>
    
    <div v-else-if="listsStore.lists.length > 0" class="lists-grid">
      <ListCard 
        v-for="list in listsStore.lists" 
        :key="list.id" 
        :list="list"
        @edit="openListForEdit"
        @delete="confirmDelete"
      />
    </div>
    <div v-else class="no-lists-message">
      <p>У вас пока нет ни одного списка. Начните с создания нового!</p>
    </div>

    <!-- Модальное окно для создания/редактирования -->
    <ListFormModal 
      v-if="isModalOpen"
      :list-to-edit="listToEdit"
      @close="closeModal"
      @save="handleSaveList"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useListsStore } from '../store/lists';
import ListCard from '../components/ListCard.vue';
import ListFormModal from '../components/ListFormModal.vue';

const listsStore = useListsStore();
const isModalOpen = ref(false);
const listToEdit = ref(null);

onMounted(() => {
  listsStore.fetchLists();
});

const openCreateModal = () => {
  listToEdit.value = null;
  isModalOpen.value = true;
};

const openListForEdit = (list) => {
  listToEdit.value = { ...list };
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  listToEdit.value = null;
};

const handleSaveList = async (listData) => {
  if (listToEdit.value) {
    // Редактирование
    await listsStore.updateList(listToEdit.value.id, listData);
  } else {
    // Создание
    await listsStore.addList(listData);
  }
  if (!listsStore.error) {
    closeModal();
  }
};

const confirmDelete = (listId) => {
    if (window.confirm("Вы уверены, что хотите удалить этот список?")) {
        listsStore.deleteList(listId);
    }
}
</script>

<style scoped>
/* Используем переменные из темы по умолчанию, которые будут унаследованы от App.vue или body */
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color, #dee2e6); /* Добавляем fallback */
}

.home-header h1 {
  font-size: 2.5rem;
  color: var(--text-color, #333);
}

.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.no-lists-message {
  text-align: center;
  padding: 3rem;
  background-color: var(--card-bg-color, #fff);
  border-radius: 8px;
  border: 1px solid var(--border-color, #dee2e6);
}

/* Стили для кнопок, которые мы определили ранее */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn:hover {
  opacity: 0.85;
}
.btn-primary {
  background-color: var(--primary-color, #007bff);
  color: var(--primary-text-color, #fff);
}
</style>

<template>
  <div class="home-dashboard">
    <div class="dashboard-header">
      <h1>Мои списки</h1>
      <button @click="openCreateModal">Создать список</button>
    </div>

    <div v-if="listsStore.isLoading" class="loader">Загрузка...</div>
    <div v-else-if="listsStore.error" class="error-message">{{ listsStore.error }}</div>
    
    <div v-else-if="listsStore.lists.length === 0" class="no-lists">
        <p>У вас пока нет списков. Нажмите "Создать список", чтобы добавить первый!</p>
    </div>

    <div v-else class="lists-grid">
      <ListCard 
        v-for="list in listsStore.lists" 
        :key="list.id" 
        :list="list"
        @edit="openListForEdit"
        @delete="confirmDelete"
      />
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
.home-dashboard {
  width: 100%;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.no-lists, .error-message, .loader {
    text-align: center;
    margin-top: 4rem;
    color: #888;
}
</style>

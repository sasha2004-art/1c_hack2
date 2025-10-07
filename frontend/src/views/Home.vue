<!-- frontend/src/views/Home.vue -->
<template>
  <div class="home-container">
    <div class="home-header">
      <h1>Мои списки</h1>
      <button @click="openListModal(null)">Создать список</button>
    </div>

    <div v-if="isLoading" class="loading-spinner">Загрузка...</div>
    <div v-else-if="lists.length === 0" class="no-lists-message">
      У вас пока нет списков. Нажмите "Создать список", чтобы начать!
    </div>
    
    <div v-else class="lists-container">
      <ListCard 
        v-for="list in lists" 
        :key="list.id" 
        :list="list"
        @edit="openListModal(list)"
        @delete="handleDeleteList(list.id)"
      />
    </div>

    <!-- Модальное окно для создания/редактирования списка -->
    <ListFormModal 
      v-if="isListModalVisible" 
      :initial-list="editingList"
      @close="closeListModal"
      @list-updated="listsStore.fetchLists"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useListsStore } from '@/store/lists';
import { storeToRefs } from 'pinia';
import ListCard from '@/components/ListCard.vue';
import ListFormModal from '@/components/ListFormModal.vue';

const listsStore = useListsStore();
const { lists, isLoading } = storeToRefs(listsStore);

// --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
// Устанавливаем значение по умолчанию в `false`
const isListModalVisible = ref(false); 
const editingList = ref(null);

const openListModal = (list = null) => {
  editingList.value = list;
  isListModalVisible.value = true;
};

const closeListModal = () => {
  isListModalVisible.value = false;
  editingList.value = null;
  listsStore.fetchLists(); // Добавляем вызов для обновления списков
};

const handleDeleteList = async (listId) => {
    if(confirm('Вы уверены, что хотите удалить этот список со всеми элементами?')) {
        await listsStore.deleteList(listId);
    }
}

onMounted(() => {
  listsStore.fetchLists();
});
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.home-header h1 {
  margin: 0;
  color: var(--text-color);
}
.home-header button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: var(--primary-color);
  color: var(--primary-text-color);
}
.lists-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.loading-spinner, .no-lists-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.5rem;
  color: #888;
}
</style>

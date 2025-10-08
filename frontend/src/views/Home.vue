<template>
  <div class="home-container">
    <div class="home-header">
      <h1>Мои списки</h1>
      <button @click="openListModal(null)" class="btn btn-primary">Создать список</button>
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
        @share="openShareModal(list)"
      />
    </div>

    <ListFormModal 
      v-if="isListModalVisible" 
      :initial-list="editingList"
      :is-open="isListModalVisible"
      @close="closeListModal"
      @list-updated="listsStore.fetchLists"
    />
    <ShareModal 
      :is-open="isShareModalVisible" 
      :list="listToShare" 
      @close="closeShareModal" 
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useListsStore } from '@/store/lists';
import { storeToRefs } from 'pinia';
import ListCard from '@/components/ListCard.vue';
import ListFormModal from '@/components/ListFormModal.vue';
import ShareModal from '@/components/ShareModal.vue';

const listsStore = useListsStore();
const { lists, isLoading } = storeToRefs(listsStore);

const isListModalVisible = ref(false); 
const editingList = ref(null);

const isShareModalVisible = ref(false);
const listToShare = ref(null);

const openListModal = (list = null) => {
  editingList.value = list;
  isListModalVisible.value = true;
};

const closeListModal = () => {
  isListModalVisible.value = false;
  editingList.value = null;
  listsStore.fetchLists();
};

const openShareModal = (list) => {
  listToShare.value = list;
  isShareModalVisible.value = true;
};

const closeShareModal = () => {
  isShareModalVisible.value = false;
  listToShare.value = null;
};

const handleDeleteList = async (listId) => {
    if(confirm('Вы уверены, что хотите удалить этот список со всеми элементами?')) {
        try {
            await listsStore.deleteList(listId);
            listsStore.fetchLists();
        } catch (error) {
            console.error('Ошибка при удалении списка:', error);
            alert('Не удалось удалить список. Пожалуйста, попробуйте еще раз.');
        }
    }
}

onMounted(() => {
  listsStore.fetchLists();
});
</script>

<style scoped>
.home-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
}
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  padding-top: var(--space-lg);
}
.home-header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--text-color);
}
.lists-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-lg);
}
.loading-spinner, .no-lists-message {
  text-align: center;
  padding: var(--space-2xl);
  font-size: 18px;
  color: #6c757d;
  grid-column: 1 / -1; /* Span all columns */
}
</style>

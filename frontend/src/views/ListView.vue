<template>
  <div class="list-view-container">
    <div v-if="isLoading" class="loading">Загрузка списка...</div>
    <div v-else-if="currentList" class="list-content">
      <header class="list-header">
        <h1>{{ currentList.title }}</h1>
        <p>{{ currentList.description }}</p>
        <button @click="showItemModal = true; editingItem = null;">
          Добавить элемент
        </button>
      </header>

      <div class="items-grid">
        <ItemCard
          v-for="item in currentList.items"
          :key="item.id"
          :item="item"
          @edit="handleEditItem"
          @delete="handleDeleteItem"
        />
      </div>
      <div v-if="!currentList.items.length" class="no-items">
        В этом списке пока нет элементов.
      </div>
    </div>
    <div v-else class="not-found">
      Список не найден или у вас нет к нему доступа.
    </div>

    <ItemFormModal
      v-if="showItemModal"
      :list-id="currentList.id"
      :item-to-edit="editingItem"
      @close="showItemModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useListsStore } from '@/store/lists';
import ItemCard from '@/components/ItemCard.vue';
import ItemFormModal from '@/components/ItemFormModal.vue';

const route = useRoute();
const listsStore = useListsStore();
const { currentList, isLoading } = storeToRefs(listsStore);

const showItemModal = ref(false);
const editingItem = ref(null);

const handleEditItem = (item) => {
  editingItem.value = item;
  showItemModal.value = true;
};

const handleDeleteItem = async (itemId) => {
  if (confirm('Вы уверены, что хотите удалить этот элемент?')) {
    await listsStore.deleteItem(itemId);
  }
};

onMounted(() => {
  const listId = Number(route.params.id);
  listsStore.fetchListById(listId);
});
</script>

<style scoped>
.list-view-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1rem;
}
.list-header {
  text-align: center;
  margin-bottom: 2rem;
}
.list-header h1 {
    color: var(--text-color);
}
.list-header p {
    color: var(--text-color);
    opacity: 0.8;
}
.list-header button {
    margin-top: 1rem;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    cursor: pointer;
    background-color: var(--primary-color);
    color: var(--primary-text-color);
    border: none;
    border-radius: 5px;
}
.items-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.loading, .not-found, .no-items {
  text-align: center;
  font-size: 1.2rem;
  color: #888;
  margin-top: 3rem;
}
</style>
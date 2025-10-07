<template>
  <!-- ИЗМЕНЕНИЕ: Класс list-view-container теперь не имеет жестко заданного фона -->
  <div class="list-view-container" v-if="!listsStore.isLoading">
    <div v-if="listsStore.currentList" class="list-content">
      <div class="list-header">
        <h1>{{ listsStore.currentList.title }}</h1>
        <button @click="openAddItemModal" class="btn btn-primary">Добавить элемент</button>
      </div>
      <p class="list-description" v-if="listsStore.currentList.description">{{ listsStore.currentList.description }}</p>

      <div class="items-container">
        <p v-if="!listsStore.currentList.items.length">В этом списке пока нет элементов.</p>
        <ItemCard 
          v-for="item in listsStore.currentList.items" 
          :key="item.id"
          :item="item"
          @edit="openEditItemModal"
          @delete="handleDeleteItem"
        />
      </div>
    </div>
    <div v-else class="error-message">
      <p>{{ listsStore.error || 'Список не найден или не удалось его загрузить.' }}</p>
      <router-link to="/">Вернуться на главную</router-link>
    </div>

    <ItemFormModal
      :show="isModalVisible"
      :item="currentItem"
      @close="closeModal"
      @save="handleSaveItem"
    />
  </div>
  <div v-else class="loading-spinner">
    <p>Загрузка списка...</p>
  </div>
</template>

<script setup>
// Скриптовая часть остается без изменений
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '../store/lists';
import ItemCard from '../components/ItemCard.vue';
import ItemFormModal from '../components/ItemFormModal.vue';

const route = useRoute();
const listsStore = useListsStore();
const isModalVisible = ref(false);
const currentItem = ref(null);
const listId = computed(() => parseInt(route.params.id));

onMounted(() => {
  listsStore.fetchListById(listId.value);
});

const openAddItemModal = () => { currentItem.value = null; isModalVisible.value = true; };
const openEditItemModal = (item) => { currentItem.value = item; isModalVisible.value = true; };
const closeModal = () => { isModalVisible.value = false; currentItem.value = null; };
const handleSaveItem = async (itemData) => {
  try {
    if (itemData.id) { await listsStore.updateItem(itemData.id, itemData); } 
    else { await listsStore.addItem(listId.value, itemData); }
  } catch (error) { console.error("Ошибка при сохранении элемента:", error); }
};
const handleDeleteItem = async (itemId) => {
  if (confirm('Вы уверены, что хотите удалить этот элемент?')) {
    try { await listsStore.deleteItem(itemId); }
    catch (error) { console.error("Ошибка при удалении элемента:", error); }
  }
};
</script>

<style scoped>
.list-view-container {
  max-width: 900px;
  margin: 2rem auto;
}

/* ИЗМЕНЕНИЕ: Основной блок контента теперь использует переменные темы */
.list-content {
  padding: 2.5rem;
  background-color: var(--card-bg-color); /* Фон из темы */
  color: var(--text-color); /* Текст из темы */
  border: 1px solid var(--border-color); /* Граница из темы */
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

h1 { margin: 0; }

.list-description {
  opacity: 0.9;
  margin-bottom: 2rem;
}

.items-container {
  margin-top: 2rem;
}

.loading-spinner, .error-message {
  text-align: center;
  margin-top: 4rem;
  font-size: 1.2rem;
}

.error-message a {
  color: var(--primary-color);
}
</style>
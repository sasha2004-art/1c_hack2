<template>
  <div class="list-view-container" v-if="!listsStore.isLoading">
    <div v-if="listsStore.currentList" class="list-content">
      <div class="list-header">
        <h1>{{ listsStore.currentList.title }}</h1>
        <button @click="openAddItemModal" class="btn-primary">Добавить элемент</button>
      </div>
      <p v-if="listsStore.currentList.description">{{ listsStore.currentList.description }}</p>

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

    <!-- Модальное окно для создания/редактирования -->
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
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '../store/lists';
import ItemCard from '../components/ItemCard.vue';
import ItemFormModal from '../components/ItemFormModal.vue';

const route = useRoute();
const listsStore = useListsStore();

const isModalVisible = ref(false);
const currentItem = ref(null);

// Получаем ID списка из URL
const listId = computed(() => parseInt(route.params.id));

// Загружаем данные списка при монтировании компонента
onMounted(() => {
  listsStore.fetchListById(listId.value);
});

// --- Логика управления модальным окном ---
const openAddItemModal = () => {
  currentItem.value = null; // Устанавливаем в null для создания нового элемента
  isModalVisible.value = true;
};

const openEditItemModal = (item) => {
  currentItem.value = item; // Передаем данные существующего элемента
  isModalVisible.value = true;
};

const closeModal = () => {
  isModalVisible.value = false;
  currentItem.value = null;
};

// --- ИСПРАВЛЕННАЯ ЛОГИКА СОХРАНЕНИЯ ---
const handleSaveItem = async (itemData) => {
  try {
    // Если у элемента есть ID, значит, мы его редактируем
    if (itemData.id) {
      await listsStore.updateItem(itemData.id, itemData);
    } 
    // Если ID нет (он равен null), значит, мы создаем новый элемент
    else {
      await listsStore.addItem(listId.value, itemData);
    }
  } catch (error) {
    console.error("Ошибка при сохранении элемента:", error);
    // Здесь можно показать уведомление пользователю
  }
};

// --- Логика удаления ---
const handleDeleteItem = async (itemId) => {
  if (confirm('Вы уверены, что хотите удалить этот элемент?')) {
    try {
      await listsStore.deleteItem(itemId);
    } catch (error) {
      console.error("Ошибка при удалении элемента:", error);
    }
  }
};
</script>

<style scoped>
.list-view-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--card-bg-color, #fff);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  color: var(--text-color, #333);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid var(--border-color, #dee2e6);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

h1 {
  margin: 0;
  color: var(--text-color);
}

.btn-primary {
  background-color: var(--primary-color, #007bff);
  color: var(--primary-text-color, #fff);
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
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
  color: var(--primary-color, #007bff);
}
</style>
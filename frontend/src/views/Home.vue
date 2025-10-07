<template>
  <div class="home-container">
    <div class="home-header">
      <h2>Мои списки</h2>
      <button @click="openAddModal" class="btn btn-primary">Создать список</button>
    </div>

    <div v-if="listsStore.isLoading" class="loading-message">Загрузка списков...</div>
    <div v-else-if="listsStore.error" class="error-message">{{ listsStore.error }}</div>
    
    <div v-else-if="lists.length" class="lists-grid">
      <!-- ИЗМЕНЕНИЕ: Добавлены обработчики событий @edit и @delete -->
      <ListCard 
        v-for="list in lists" 
        :key="list.id" 
        :list="list"
        @edit="openEditModal"
        @delete="handleDeleteList"
      />
    </div>

    <div v-else class="no-lists-message">
      <p>У вас пока нет ни одного списка. Нажмите "Создать список", чтобы начать!</p>
    </div>

    <ListFormModal 
      :show="isModalVisible" 
      :list="currentList" 
      @close="closeModal" 
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useListsStore } from '../store/lists';
import ListCard from '../components/ListCard.vue';
import ListFormModal from '../components/ListFormModal.vue';

const listsStore = useListsStore();
const lists = computed(() => listsStore.lists);

const isModalVisible = ref(false);
const currentList = ref(null);

onMounted(() => {
  listsStore.fetchLists();
});

// --- ИЗМЕНЕНИЕ: Функции для обработки событий от карточек ---

// Открывает модальное окно для создания
const openAddModal = () => {
  currentList.value = null;
  isModalVisible.value = true;
};

// Открывает модальное окно для редактирования, передавая данные списка
const openEditModal = (list) => {
  currentList.value = list;
  isModalVisible.value = true;
};

// Обрабатывает удаление списка
const handleDeleteList = async (listId) => {
  if (confirm('Вы уверены, что хотите удалить этот список?')) {
    try {
      await listsStore.deleteList(listId);
    } catch (error) {
      console.error("Не удалось удалить список:", error);
      // Можно показать уведомление об ошибке
    }
  }
};

// --- Конец изменений ---

const closeModal = () => {
  isModalVisible.value = false;
};

const handleSave = async (listData) => {
  try {
    if (listData.id) {
      // Обновляем существующий список
      await listsStore.updateList(listData.id, listData);
    } else {
      // Создаем новый список
      await listsStore.addList(listData);
    }
    closeModal(); // Закрываем окно после успешного сохранения
  } catch (error) {
    console.error("Не удалось сохранить список:", error);
  }
};
</script>

<style scoped>
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
}
h2 {
  margin: 0;
  font-size: 2rem;
}
.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}
.loading-message, .error-message, .no-lists-message {
  text-align: center;
  margin-top: 4rem;
  font-size: 1.2rem;
  color: #6c757d;
}
</style>

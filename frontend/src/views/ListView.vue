<template>
  <!-- Состояние 1: Показываем индикатор загрузки -->
  <div v-if="listStore.isLoading" class="status-indicator">
    <p>Загрузка списка...</p>
  </div>

  <!-- Состояние 2: Показываем ошибку, если она есть -->
  <div v-else-if="listStore.error" class="status-indicator error">
     <p>{{ listStore.error }}</p>
  </div>

  <!-- Состояние 3: Список успешно загружен, показываем контент -->
  <div v-else-if="listStore.currentList" class="list-view-container">
    <header class="list-header">
      <h1>{{ listStore.currentList.title }}</h1>
      <p v-if="listStore.currentList.description">{{ listStore.currentList.description }}</p>
      <button @click="isModalVisible = true" class="add-item-btn">Добавить элемент</button>
    </header>

    <main class="items-grid">
      <div v-if="listStore.currentList.items.length > 0">
        <ItemCard
          v-for="item in listStore.currentList.items"
          :key="item.id"
          :item="item"
        />
      </div>
      <div v-else class="no-items-placeholder">
        <p>В этом списке пока нет элементов. Нажмите "Добавить элемент", чтобы создать первый.</p>
      </div>
    </main>

    <!-- Модальное окно для добавления нового элемента.
         Оно корректно получает ID списка и обрабатывает закрытие. -->
    <ItemFormModal
      v-if="isModalVisible"
      :list-id="listStore.currentList.id"
      @close="isModalVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
import ItemCard from '@/components/ItemCard.vue';
import ItemFormModal from '@/components/ItemFormModal.vue';

const route = useRoute();
const listStore = useListsStore();
const isModalVisible = ref(false);

onMounted(() => {
  const listId = Number(route.params.id);
  if (listId) {
    listStore.fetchListById(listId);
  }
});

// Очищаем данные при уходе со страницы, чтобы не показывать старый список при переходе на новый
onUnmounted(() => {
  listStore.currentList = null;
  listStore.error = null;
});
</script>

<style scoped>
.list-view-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  color: var(--text-color);
}

.list-header {
  text-align: center;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
}

.list-header h1 {
  font-size: 2.8rem;
  margin-bottom: 0.5rem;
}

.list-header p {
  font-size: 1.1rem;
  color: var(--text-color-secondary, #6c757d);
  max-width: 600px;
  margin: 0 auto 1.5rem auto;
}

.add-item-btn {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  border: none;
  padding: 0.8rem 1.8rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.add-item-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.no-items-placeholder {
  text-align: center;
  padding: 4rem;
  background-color: var(--card-bg-color);
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  color: var(--text-color-secondary, #6c757d);
}

.status-indicator {
  text-align: center;
  padding: 5rem;
  color: var(--text-color);
  font-size: 1.2rem;
}

.status-indicator.error {
  color: var(--secondary-color, red);
}
</style>
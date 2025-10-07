<template>
  <div class="list-view-container">
    <div v-if="listsStore.isLoading" class="loading">Загрузка...</div>
    <div v-else-if="listsStore.error" class="error">{{ listsStore.error }}</div>
    <div v-else-if="listsStore.currentList" class="list-details">
      <div class="list-header">
        <h1>{{ listsStore.currentList.title }}</h1>
        <p>{{ listsStore.currentList.description }}</p>
      </div>

      <!-- Показываем кнопку добавления только владельцу -->
      <div class="actions" v-if="isOwner">
        <button @click="openAddItemModal" class="btn-primary">Добавить желание</button>
      </div>

      <div v-if="listsStore.currentList.items.length > 0" class="items-grid">
        <ItemCard
          v-for="item in listsStore.currentList.items"
          :key="item.id"
          :item="item"
          :is-owner="isOwner"
          @edit-item="openEditItemModal(item)"
        />
      </div>
      <div v-else class="empty-state">
        <p>В этом списке пока нет желаний. Пора добавить первое!</p>
      </div>
    </div>
    <div v-else>
      <p>Список не найден.</p>
    </div>

    <ItemFormModal
      :is-open="isItemModalOpen"
      :list-id="parseInt(listId)"
      :item-to-edit="currentItemForEdit"
      @close="handleItemFormClose"
    />
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth'; // 1. Импортируем auth store
import ItemCard from '@/components/ItemCard.vue';
import ItemFormModal from '@/components/ItemFormModal.vue';
import { themes } from '@/themes.js';

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore(); // 2. Получаем экземпляр auth store

const listId = route.params.id;

const isItemModalOpen = ref(false);
const currentItemForEdit = ref(null);

// 3. Создаем вычисляемое свойство для определения владельца
const isOwner = computed(() => {
  if (!authStore.user || !listsStore.currentList) return false;
  return authStore.user.id === listsStore.currentList.owner_id;
});


const currentTheme = computed(() => {
  const themeName = listsStore.currentList?.theme_name || 'default';
  return themes[themeName] || themes.default;
});

const applyTheme = (theme) => {
  const root = document.documentElement;
  for (const [key, value] of Object.entries(theme.styles)) {
    root.style.setProperty(key, value);
  }
};

const openAddItemModal = () => {
  currentItemForEdit.value = null;
  isItemModalOpen.value = true;
};

const openEditItemModal = (item) => {
  currentItemForEdit.value = item;
  isItemModalOpen.value = true;
};

const handleItemFormClose = () => {
  isItemModalOpen.value = false;
  currentItemForEdit.value = null;
};

onMounted(async () => {
  await listsStore.fetchListById(listId);
  if (listsStore.currentList) {
    applyTheme(currentTheme.value);
  }
});

// Сброс стилей при уходе со страницы
import { onBeforeUnmount } from 'vue';
onBeforeUnmount(() => {
  applyTheme(themes.default);
});
</script>

<style scoped>
.list-view-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  color: var(--text-color);
}

.list-header {
  text-align: center;
  margin-bottom: 2rem;
}

.list-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.list-header p {
  font-size: 1.2rem;
  color: var(--text-color);
  opacity: 0.8;
}

.actions {
  text-align: center;
  margin-bottom: 2rem;
}

.btn-primary {
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  opacity: 0.9;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  background-color: var(--card-bg-color);
}
.loading, .error {
  text-align: center;
  font-size: 1.2rem;
  padding: 2rem;
}
</style>
<!-- frontend/src/views/ListView.vue -->
<template>
  <div class="list-view-container" v-if="currentList">
    <div class="list-header">
      <div class="list-info">
        <h1>{{ currentList.title }}</h1>
        <p v-if="currentList.description">{{ currentList.description }}</p>
      </div>
      <!-- --- ИСПРАВЛЕНИЕ ЗДЕСЬ --- -->
      <div v-if="isOwner" class="list-actions">
        <button @click="openItemModal(null)">Добавить элемент</button>
        <!-- Кнопка заменена на иконку с подсказкой -->
        <button @click="openSettingsModal" class="icon-button settings-button" title="Настройки списка">
          ⚙️
        </button>
      </div>
    </div>
    
    <div v-if="!currentList.items || currentList.items.length === 0" class="no-items-message">
      В этом списке пока нет элементов.
    </div>

    <div class="items-grid" v-else>
      <ItemCard
        v-for="item in currentList.items"
        :key="item.id"
        :item="item"
        :is-owner="isOwner"
        :is-logged-in="isLoggedIn"
        :is-wishlist="isWishlist"
        :is-public="isPublic"
        @edit="openItemModal(item)"
        @delete="handleDeleteItem(item.id)"
        @open-lightbox="openLightbox"
        @reserve="handleReserveItem"
        @unreserve="handleUnreserveItem"
        :id="`item-${item.id}`"
      />
    </div>

    <ItemFormModal 
      v-if="isItemModalVisible" 
      :initial-item="editingItem"
      :list-id="currentList.id"
      @close="closeItemModal" 
    />

    <ListFormModal 
      v-if="isSettingsModalVisible" 
      :initial-list="currentList"
      @close="closeSettingsModal"
    />

    <Lightbox 
      :visible="isLightboxVisible" 
      :image-url="selectedImageUrl" 
      @close="isLightboxVisible = false" 
    />

  </div>
  <div v-else-if="isLoading" class="loading-spinner">Загрузка списка...</div>
  <div v-else class="error-message">{{ error }}</div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth'; // <-- ИМПОРТИРУЕМ AUTH STORE
import { storeToRefs } from 'pinia';
import ItemCard from '@/components/ItemCard.vue';
import ItemFormModal from '@/components/ItemFormModal.vue';
import ListFormModal from '@/components/ListFormModal.vue';
import Lightbox from '@/components/Lightbox.vue';

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
});

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore(); // <-- СОЗДАЕМ ЭКЗЕМПЛЯР
const { currentList, isLoading, error } = storeToRefs(listsStore);

// --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ №3: Логика определения владельца ---
const isOwner = computed(() => {
  // Используем optional chaining (?.) на случай, если данные еще не загрузились
  if (!authStore.user || !currentList.value) {
    return false;
  }
  // Сравниваем ID залогиненного пользователя с ID владельца списка
  return authStore.user.id === currentList.value.owner_id;
});

const isLoggedIn = computed(() => !!authStore.user);

const isWishlist = computed(() => currentList.value?.is_wishlist || false);

const isPublic = computed(() => route.path.startsWith('/public'));

const isItemModalVisible = ref(false);
const isSettingsModalVisible = ref(false);
const editingItem = ref(null);
const isLightboxVisible = ref(false);
const selectedImageUrl = ref('');

const openItemModal = (item) => {
  editingItem.value = item;
  isItemModalVisible.value = true;
};

const closeItemModal = () => {
  isItemModalVisible.value = false;
  editingItem.value = null;
};

const openSettingsModal = () => {
    isSettingsModalVisible.value = true;
};

const closeSettingsModal = () => {
    isSettingsModalVisible.value = false;
};

const handleDeleteItem = async (itemId) => {
  if (confirm('Вы уверены, что хотите удалить этот элемент?')) {
    await listsStore.deleteItem(itemId);
  }
};

const handleReserveItem = async (itemId) => {
  await listsStore.reserveItem(itemId, isPublic.value ? props.id : null);
};

const handleUnreserveItem = async (itemId) => {
  await listsStore.unreserveItem(itemId, isPublic.value ? props.id : null);
};

const openLightbox = (imageUrl) => {
  const backendUrl = 'http://localhost:8000';
  selectedImageUrl.value = `${backendUrl}${imageUrl}`;
  isLightboxVisible.value = true;
};

const scrollToAndHighlightItem = async (hash) => {
    if (!hash || !hash.startsWith('#item-')) return;
    
    await nextTick();
    
    const itemId = hash.substring(1);
    const element = document.getElementById(itemId);

    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        element.classList.add('highlight');
        
        setTimeout(() => {
            element.classList.remove('highlight');
        }, 3000);
    }
};

onMounted(async () => {
  if (isPublic.value) {
    await listsStore.fetchPublicListByKey(props.id);
  } else {
    await listsStore.fetchListById(Number(props.id));
  }
  scrollToAndHighlightItem(route.hash);
});

watch(() => route.hash, (newHash) => {
    scrollToAndHighlightItem(newHash);
});
</script>

<style scoped>
.list-view-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.list-info h1 {
  margin: 0;
  color: var(--text-color);
}
.list-info p {
  margin: 0.5rem 0 0;
  color: var(--text-color);
  opacity: 0.8;
}
.list-actions {
  display: flex;
  gap: 1rem;
  align-items: center; /* Выравниваем иконку и кнопку */
}
/* Стили для обычной кнопки */
.list-actions button:not(.icon-button) {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    background-color: var(--primary-color);
    color: var(--primary-text-color);
}

/* --- ИСПРАВЛЕНИЕ ЗДЕСЬ: Стили для кнопки-иконки --- */
.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.settings-button {
  font-size: 1.75rem; /* Размер иконки */
  color: var(--text-color);
  opacity: 0.7;
  transition: opacity 0.2s;
}
.settings-button:hover {
  opacity: 1;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.no-items-message {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #888;
  background-color: var(--card-bg-color);
  border-radius: 8px;
}
.loading-spinner, .error-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.5rem;
}

.items-grid :deep(.highlight) {
  transition: box-shadow 0.5s ease-in-out, border-color 0.5s ease-in-out;
  box-shadow: 0 0 15px 5px var(--edit-color, gold);
  border-color: var(--edit-color, gold) !important;
}
</style>
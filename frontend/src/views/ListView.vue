<!-- frontend/src/views/ListView.vue -->
<template>
  <div class="list-view-container" v-if="currentList">
    <div class="list-header">
      <div class="list-info">
        <h1>{{ currentList.title }}</h1>
        <p v-if="currentList.description">{{ currentList.description }}</p>
      </div>
      <!-- --- ИСПРАВЛЕНИЕ ЗДЕСЬ --- -->
      <div class="list-actions">
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
        :list-owner-id="currentList.owner_id"
        :is-public="false"
        @edit="openItemModal(item)"
        @delete="handleDeleteItem(item.id)"
        @open-lightbox="openLightbox"
        @copy-item="openCopyModal"
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

  <!-- Этап 10: Модалка выбора списка для копирования -->
  <div v-if="isCopyModalVisible" class="modal-overlay" @click.self="closeCopyModal">
    <div class="modal-content">
      <h3>Скопировать желание в...</h3>
      <p v-if="copyError" class="error-message">{{ copyError }}</p>
      <select v-model="selectedListId" class="form-select">
        <option disabled value="">Выберите ваш список</option>
        <option v-for="l in listsStore.lists" :key="l.id" :value="l.id">{{ l.title }}</option>
      </select>
      <div class="modal-actions">
        <button @click="closeCopyModal" class="btn btn-secondary">Отмена</button>
        <button @click="handleCopyConfirm" class="btn btn-primary" :disabled="!selectedListId">Подтвердить</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
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
const { currentList, isLoading, error } = storeToRefs(listsStore);

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
  await listsStore.fetchListById(Number(props.id));
  scrollToAndHighlightItem(route.hash);
});

watch(() => route.hash, (newHash) => {
    scrollToAndHighlightItem(newHash);
});

// Этап 10: состояние модалки копирования
const isCopyModalVisible = ref(false);
const itemToCopyId = ref(null);
const selectedListId = ref('');
const copyError = ref('');

// Дополнительно загружаем свои списки (для выпадающего списка)
onMounted(async () => {
  await listsStore.fetchLists();
});

// Методы модалки копирования
const openCopyModal = (itemId) => {
  itemToCopyId.value = itemId;
  selectedListId.value = '';
  copyError.value = '';
  isCopyModalVisible.value = true;
};

const closeCopyModal = () => {
  isCopyModalVisible.value = false;
  itemToCopyId.value = null;
  selectedListId.value = '';
};

const handleCopyConfirm = async () => {
  if (!selectedListId.value || !itemToCopyId.value) return;
  try {
    await listsStore.copyItem(itemToCopyId.value, Number(selectedListId.value));
    alert('Желание успешно скопировано!');
    closeCopyModal();
  } catch (e) {
    copyError.value = listsStore.error || 'Не удалось скопировать элемент';
  }
};
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

/* Этап 10: стили модалки копирования */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: var(--card-bg-color);
  color: var(--text-color);
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}
.form-select {
  width: 100%;
  padding: 0.5rem;
  margin-top: 1rem;
  margin-bottom: 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--bg-color);
  color: var(--text-color);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
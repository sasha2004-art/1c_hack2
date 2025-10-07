<template>
  <div class="list-view-container" :style="themeStyles">
    <div v-if="isLoading" class="loader">Загрузка...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="list" class="list-content">
      <header class="list-header">
        <h1>{{ list.title }}</h1>
        <p class="list-description">{{ list.description }}</p>
        <p v-if="isPublicView && list.owner" class="owner-info">
          Автор: 
          <router-link :to="{ name: 'UserProfile', params: { userId: list.owner.id } }">
            {{ list.owner.name }}
          </router-link>
        </p>
      </header>

      <!-- (НОВЫЙ КОД) Кнопка для добавления элемента -->
      <div class="actions-toolbar">
        <button v-if="isOwner" @click="isModalOpen = true" class="btn-add-item">
          Добавить элемент
        </button>
      </div>

      <div class="items-grid">
        <ItemCard
          v-for="item in list.items"
          :key="item.id"
          :item="item"
          :list-type="list.list_type"
          :is-owner="isOwner"
          :is-public-view="isPublicView"
          :is-logged-in="isLoggedIn"
          @reserve="handleReserve"
          @unreserve="handleUnreserve"
        />
      </div>

       <div v-if="list.items.length === 0" class="empty-list">
        <p>В этом списке пока нет элементов.</p>
      </div>
    </div>
    
    <!-- (НОВЫЙ КОД) Модальное окно -->
    <ItemFormModal 
      v-if="isModalOpen"
      @close="isModalOpen = false"
      @save="handleSaveItem"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth';
import { storeToRefs } from 'pinia';
import ItemCard from '@/components/ItemCard.vue';
import { themes } from '@/themes.js';
import ItemFormModal from '@/components/ItemFormModal.vue'; // (НОВЫЙ КОД) Импорт модального окна

const props = defineProps({
  id: String,
  publicKey: String,
});

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore();

const { currentList: list, isLoading, error } = storeToRefs(listsStore);
const { user, token } = storeToRefs(authStore);

// (НОВЫЙ КОД) Состояние для модального окна
const isModalOpen = ref(false);

const isPublicView = computed(() => !!props.publicKey);
const isLoggedIn = computed(() => !!token.value);
const isOwner = computed(() => {
  if (!user.value || !list.value) return false;
  // В публичном виде list.owner вложен, в приватном - owner_id
  return isPublicView.value 
    ? list.value.owner?.id === user.value.id 
    : list.value.owner_id === user.value.id;
});

const themeStyles = computed(() => {
  if (list.value && themes[list.value.theme_name]) {
    return themes[list.value.theme_name].styles;
  }
  return themes.default.styles;
});

const loadList = async () => {
  if (isPublicView.value) {
    await listsStore.fetchPublicListByKey(props.publicKey);
  } else {
    await listsStore.fetchListById(props.id);
  }
};

onMounted(loadList);

watch(() => route.params, (newParams, oldParams) => {
    if (newParams.id !== oldParams.id || newParams.publicKey !== oldParams.publicKey) {
        loadList();
    }
}, { immediate: false });


const handleReserve = async (itemId) => {
    try {
        await listsStore.reserveItem(itemId, props.publicKey);
    } catch (e) {
        alert(e.message || 'Ошибка бронирования');
    }
}

const handleUnreserve = async (itemId) => {
    try {
        await listsStore.unreserveItem(itemId, props.publicKey);
    } catch (e) {
        alert(e.message || 'Ошибка снятия брони');
    }
}

// (НОВЫЙ КОД) Обработчик сохранения из модального окна
const handleSaveItem = async (itemData) => {
  try {
    await listsStore.addItem(list.value.id, itemData);
    isModalOpen.value = false; // Закрываем модальное окно после успешного добавления
  } catch (e) {
    alert(e.message || 'Не удалось добавить элемент');
  }
};
</script>

<style scoped>
.list-view-container {
  min-height: 100vh;
  padding: 2rem;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: var(--font-family);
  transition: all 0.3s ease;
}

.list-content {
  max-width: 1200px;
  margin: 0 auto;
}

.list-header {
  text-align: center;
  margin-bottom: 1rem; /* Уменьшаем отступ */
  background: var(--card-bg-color);
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
}

.list-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.list-description {
  font-size: 1.1rem;
  opacity: 0.8;
}

.owner-info {
  margin-top: 1rem;
}

.owner-info a {
  color: var(--primary-color);
  font-weight: bold;
  text-decoration: none;
}

/* (НОВЫЙ КОД) Стили для панели с кнопкой */
.actions-toolbar {
  display: flex;
  justify-content: center;
  margin-bottom: 2.5rem;
}

.btn-add-item {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  background-color: var(--primary-color);
  color: var(--primary-text-color);
  transition: opacity 0.2s;
}
.btn-add-item:hover {
    opacity: 0.9;
}


.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.loader, .error-message, .empty-list {
  text-align: center;
  font-size: 1.2rem;
  padding: 3rem;
}

.error-message {
  color: var(--secondary-color);
}
</style>
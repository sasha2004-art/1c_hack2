<template>
  <div v-if="isLoading && !currentList" class="loading-state">
    Загрузка списка...
  </div>

  <div v-else-if="listsStore.error" class="error-state">
    Ошибка: {{ listsStore.error }}
  </div>

  <div v-else-if="currentList" class="list-view-container" :style="customStyles">
    
    <div class="list-header">
      <h1>{{ currentList.title }}</h1>
      <p v-if="currentList.description">{{ currentList.description }}</p>
      <div class="list-meta">
        <span class="badge">{{ currentList.list_type.toUpperCase() }}</span>
        <span class="badge">{{ currentList.privacy_level.toUpperCase() }}</span>
        <span class="badge">Владелец: {{ currentList.owner_id === authStore.user.id ? 'Вы' : 'Другой пользователь' }}</span>
      </div>

      <!-- Кнопки управления (только для владельца) -->
      <div v-if="isOwner" class="owner-controls">
        <button @click="openNewItemModal" class="primary-btn">
            <i class="fas fa-plus"></i> Добавить элемент
        </button>
        <button @click="openEditListModal" class="edit-btn">
             <i class="fas fa-edit"></i> Редактировать список
        </button>
        <button @click="handleDeleteList" class="delete-btn">
             <i class="fas fa-trash"></i> Удалить
        </button>
      </div>
      
    </div>

    <!-- Область списка элементов -->
    <div class="list-items">
      <p v-if="currentList.items.length === 0">В этом списке пока нет элементов.</p>
      <ItemCard
        v-for="item in currentList.items"
        :key="item.id"
        :item="item"
        :listType="currentList.list_type"
        :isOwner="isOwner"
        :listOwnerId="currentList.owner_id" 
        @edit-item="openEditItemModal"
        @delete-item="handleDeleteItem"
        @reserve-item="handleReserve"
        @unreserve-item="handleUnreserve"
      />
    </div>

    <!-- Модальное окно для списка -->
    <ListFormModal
      v-if="showListModal"
      :isVisible="showListModal"
      :isEditing="isEditingList"
      :initialList="currentList"
      @close="showListModal = false"
      @submitted="handleFormSubmitted"
    />

    <!-- Модальное окно для элемента -->
    <ItemFormModal
      v-if="showItemModal"
      :isVisible="showItemModal"
      :listId="listId"
      :listType="currentList.list_type"
      :initialItem="itemToEdit"
      @close="showItemModal = false"
      @submitted="handleFormSubmitted"
    />

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth';
import ItemCard from '@/components/ItemCard.vue';
import ListFormModal from '@/components/ListFormModal.vue';
import ItemFormModal from '@/components/ItemFormModal.vue';
import ThemeSelector from '@/components/ThemeSelector.vue';
import { themes } from '@/themes'; // Импортируем темы

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore();

const listId = computed(() => parseInt(route.params.id));
const currentList = computed(() => listsStore.currentList);
const isLoading = computed(() => listsStore.isLoading);

// Состояние модальных окон
const showListModal = ref(false);
const showItemModal = ref(false);
const itemToEdit = ref(null);
const isEditingList = ref(false);

const isOwner = computed(() => {
    // Проверяем, является ли текущий пользователь владельцем списка
    return currentList.value?.owner_id === authStore.user.id;
});

// Применение темы
const customStyles = computed(() => {
    if (currentList.value) {
        const theme = themes[currentList.value.theme_name] || themes.default;
        const styles = { ...theme.styles };

        // Если есть background_url (хотя в текущей модели его нет,
        // эта логика останется для потенциального будущего)
        // if (currentList.value.background_url) {
        //     styles['--bg-image'] = `url(${currentList.value.background_url})`;
        // }

        return styles;
    }
    return {};
});

onMounted(async () => {
    await listsStore.fetchListById(listId.value);
    
    // Если пользователь - не владелец, но имеет доступ (например, друг), 
    // нам нужно знать его бронирования для отображения статуса "Забронировать"
    if (authStore.user && !isOwner.value && currentList.value.list_type === 'wishlist') {
         listsStore.fetchUserReservations();
    }
});

// Логика управления списком
function openEditListModal() {
    if (isOwner.value) {
        isEditingList.value = true;
        showListModal.value = true;
    }
}

async function handleDeleteList() {
    if (confirm('Вы уверены, что хотите удалить этот список? Это действие необратимо.')) {
        try {
            await listsStore.deleteList(listId.value);
            // После удаления списка перенаправляем на главную
            router.push({ name: 'Home' });
        } catch (e) {
            console.error(e);
        }
    }
}

// Логика управления элементами
function openNewItemModal() {
    if (isOwner.value) {
        itemToEdit.value = null; // Создание нового
        showItemModal.value = true;
    }
}

function openEditItemModal(item) {
    if (isOwner.value) {
        itemToEdit.value = item; // Редактирование существующего
        showItemModal.value = true;
    }
}

async function handleDeleteItem(itemId) {
    if (confirm('Удалить этот элемент?')) {
        await listsStore.deleteItem(itemId);
    }
}

// Перезагрузка после сохранения формы
async function handleFormSubmitted() {
    showListModal.value = false;
    showItemModal.value = false;
    await listsStore.fetchListById(listId.value);
}

// Обработка бронирования (для друзей, которые могут видеть список)
async function handleReserve(itemId) {
    await listsStore.reserveItem(itemId);
}

async function handleUnreserve(itemId) {
    await listsStore.unreserveItem(itemId);
}


</script>

<style scoped>
/* Стили из main.css */
/* ... (стили для .list-view-container, .list-header, .owner-controls и т.д.) ... */
.list-view-container {
    padding: 20px;
    transition: all 0.5s ease;
    min-height: 100vh;
    /* Применяем кастомные свойства */
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: var(--font-family);
    background-image: var(--bg-image);
    background-size: cover;
    background-attachment: fixed;
}
.list-header h1 {
    color: var(--primary-color);
}

.list-meta {
    margin: 10px 0;
}

.list-items {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-top: 20px;
}

.owner-controls {
    display: flex;
    gap: 10px;
    margin-top: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid var(--border-color);
}

.badge {
    display: inline-block;
    padding: 4px 8px;
    background-color: var(--card-bg-color);
    border: 1px solid var(--border-color);
    color: var(--text-color);
    border-radius: 4px;
    font-size: 0.8em;
    margin-right: 5px;
}
</style>
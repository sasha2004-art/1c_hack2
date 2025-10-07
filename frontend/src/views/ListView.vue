<template>
  <div v-if="isLoading" class="loader">Загрузка списка...</div>
  <div v-else-if="error" class="error-message">{{ error }}</div>
  
  <div v-else-if="list" class="list-view-container" :style="themeStyles">
    <div class="list-header">
      <div>
        <h1>{{ list.title }}</h1>
        <p v-if="list.description">{{ list.description }}</p>
      </div>
      <!-- ВОТ КНОПКА, КОТОРАЯ ТЕПЕРЬ ОТКРЫВАЕТ ОКНО -->
      <button @click="openAddItemModal" class="btn-primary">Добавить желание</button>
    </div>

    <div class="items-grid">
      <ItemCard 
        v-for="item in list.items" 
        :key="item.id" 
        :item="item" 
        :is-owner="isOwner"
        @edit="openEditItemModal(item)"
        @delete="handleDeleteItem(item.id)"
      />
    </div>

    <div v-if="list.items.length === 0" class="empty-list-message">
      В этом списке пока нет ни одного элемента.
    </div>
  </div>

  <!-- 
    КЛЮЧЕВОЕ ИЗМЕНЕНИЕ:
    Модальное окно теперь обернуто в v-if.
    Оно появится только когда isItemFormModalVisible станет true.
    Мы также передаем ему item для редактирования и слушаем его события.
  -->
  <ItemFormModal
    v-if="isItemFormModalVisible"
    :list-id="listId"
    :item="currentItemToEdit"
    @close="closeItemFormModal"
    @saved="handleItemSaved"
  />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth';
import ItemCard from '@/components/ItemCard.vue';
import ItemFormModal from '@/components/ItemFormModal.vue'; // Импортируем модальное окно
import { themes } from '@/themes.js';

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore();

// Получаем ID списка из URL
const listId = computed(() => parseInt(route.params.id, 10));

// --- ЭТО ГЛАВНАЯ ЧАСТЬ ИСПРАВЛЕНИЯ ---
// 1. Создаем переменную для управления видимостью окна. Изначально false.
const isItemFormModalVisible = ref(false);
const currentItemToEdit = ref(null); // Для передачи данных при редактировании

// 2. Функции для открытия и закрытия окна
function openAddItemModal() {
  currentItemToEdit.value = null; // Сбрасываем, т.к. добавляем новый элемент
  isItemFormModalVisible.value = true;
}

function openEditItemModal(item) {
  currentItemToEdit.value = item; // Запоминаем, какой элемент редактируем
  isItemFormModalVisible.value = true;
}

function closeItemFormModal() {
  isItemFormModalVisible.value = false;
}

// Функция, которая вызывается после успешного сохранения элемента
async function handleItemSaved() {
  // Перезагружаем данные списка, чтобы увидеть изменения
  await listsStore.fetchListById(listId.value);
}
// --- КОНЕЦ ГЛАВНОЙ ЧАСТИ ИСПРАВЛЕНИЯ ---


const list = computed(() => listsStore.currentList);
const isLoading = computed(() => listsStore.isLoading);
const error = computed(() => listsStore.error);

const isOwner = computed(() => {
  if (!list.value || !authStore.user) return false;
  return list.value.owner_id === authStore.user.id;
});

const themeStyles = computed(() => {
  if (list.value && themes[list.value.theme_name]) {
    return themes[list.value.theme_name].styles;
  }
  return themes.default.styles;
});

async function handleDeleteItem(itemId) {
  if (confirm('Вы уверены, что хотите удалить этот элемент?')) {
    try {
      await listsStore.deleteItem(itemId);
    } catch (e) {
      console.error('Ошибка при удалении элемента:', e);
      // Можно показать уведомление об ошибке
    }
  }
}

onMounted(() => {
  listsStore.fetchListById(listId.value);
});
</script>

<style scoped>
.list-view-container {
  padding: 20px;
  background-color: var(--bg-color);
  min-height: 100vh;
  color: var(--text-color);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.list-header h1 {
  margin: 0;
}

.list-header p {
  margin-top: 5px;
  opacity: 0.8;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.empty-list-message {
  text-align: center;
  margin-top: 50px;
  font-size: 1.2rem;
  color: var(--text-color);
  opacity: 0.7;
}

.loader, .error-message {
  text-align: center;
  padding: 50px;
  font-size: 1.5rem;
}

.btn-primary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: var(--primary-color, #007bff);
  color: var(--primary-text-color, white);
  font-size: 1rem;
}
</style>
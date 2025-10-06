<!-- --- НАЧАЛО ФАЙЛА: frontend/src/views/ListView.vue --- -->
<template>
  <div class="list-view-container">
    <div v-if="isLoading">Загрузка...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="list">
      <div class="list-header">
        <h1>{{ list.title }}</h1>
        <p>{{ list.description }}</p>
        <div class="header-actions">
          <button @click="openAddItemModal" class="btn-add">Добавить элемент</button>
          <button @click="openEditListModal" class="btn-edit">Редактировать список</button>
        </div>
        <div class="header-actions-bottom">
          <button @click="handleDeleteList" class="btn-delete">Удалить список</button>
        </div>
      </div>

      <div v-if="list.items && list.items.length > 0" class="items-grid">
        <ItemCard
          v-for="item in list.items"
          :key="item.id"
          :item="item"
          @edit="openEditItemModal"
          @delete="handleDeleteItem"
        />
      </div>
      <div v-else class="no-items-message">
        <p>В этом списке пока нет элементов. Самое время добавить первый!</p>
      </div>
    </div>
  </div>

  <ItemFormModal
    :is-visible="isModalVisible"
    :item-to-edit="itemToEdit"
    @close="closeModal"
    @save="handleSaveItem"
  />
  <ListFormModal
    :list-to-edit="list"
    :can-change-privacy="canChangePrivacy"
    v-if="isListModalVisible"
    @close="closeListModal"
    @save="handleSaveList"
  />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useListsStore } from '../store/lists';
import { storeToRefs } from 'pinia';
import ItemCard from '../components/ItemCard.vue';
import ItemFormModal from '../components/ItemFormModal.vue';
import ListFormModal from '../components/ListFormModal.vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const props = defineProps({
  id: {
    type: String,
    required: true,
  }
});

const listsStore = useListsStore();
const { currentList: list, isLoading, error } = storeToRefs(listsStore);
const authStore = useAuthStore();

const isModalVisible = ref(false);
const itemToEdit = ref(null);
const router = useRouter();
const isListModalVisible = ref(false);
const canChangePrivacy = ref(true);

onMounted(() => {
  listsStore.fetchListById(props.id);
});

watch([list, () => authStore.user], () => {
  canChangePrivacy.value = !!(list.value && authStore.user && list.value.owner_id === authStore.user.id);
});

function openAddItemModal() {
  itemToEdit.value = null;
  isModalVisible.value = true;
}

function openEditItemModal(item) {
  itemToEdit.value = item;
  isModalVisible.value = true;
}

function closeModal() {
  isModalVisible.value = false;
  itemToEdit.value = null;
}

function openEditListModal() {
  isListModalVisible.value = true;
}

function closeListModal() {
  isListModalVisible.value = false;
}

async function handleSaveList(listData) {
  if (!list.value) return;
  try {
    await listsStore.updateList(list.value.id, listData);
    // обновить локально
    await listsStore.fetchListById(list.value.id);
    closeListModal();
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось сохранить изменения списка.');
  }
}

async function handleSaveItem(itemData) {
  try {
    if (itemToEdit.value) {
      // Редактирование
      await listsStore.updateItem(itemToEdit.value.id, itemData);
    } else {
      // Создание
      await listsStore.addItem(list.value.id, itemData);
    }
    closeModal();
  } catch (e) {
    // Ошибка будет обработана и показана в модальном окне
  }
}

async function handleDeleteItem(itemId) {
  if (confirm('Вы уверены, что хотите удалить этот элемент?')) {
    await listsStore.deleteItem(itemId);
  }
}

async function handleDeleteList() {
  if (!list.value) return;
  if (!confirm('Вы уверены, что хотите полностью удалить этот список? Это действие не обратимо.')) return;
  try {
    await listsStore.deleteList(list.value.id);
    router.push({ name: 'Home' });
  } catch (e) {
    alert(e.response?.data?.detail || 'Не удалось удалить список.');
  }
}
</script>

<style scoped>
.list-view-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}
.list-header {
  text-align: center;
  margin-bottom: 2rem;
}
.list-header h1 {
  margin-bottom: 0.5rem;
}
.btn-add {
  margin-top: 1rem;
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  margin-right: 1rem;
}

.btn-delete {
  margin-top: 1rem;
  padding: 10px 20px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-edit {
  margin-top: 1rem;
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  margin-right: 1rem;
}
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
.header-actions-bottom {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}
.no-items-message {
  text-align: center;
  margin-top: 3rem;
  color: #666;
}
.error-message {
  color: red;
  text-align: center;
}
</style>
<!-- --- КОНЕЦ ФАЙЛА: frontend/src/views/ListView.vue --- -->
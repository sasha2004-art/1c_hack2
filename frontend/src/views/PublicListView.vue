<template>
  <div class="list-view-container public-view">
    <div v-if="isLoading" class="loading">Загрузка списка...</div>
    <div v-else-if="currentList" class="list-content">
      <header class="list-header">
        <h1>{{ currentList.title }}</h1>
        <p>{{ currentList.description }}</p>
      </header>

      <div class="items-grid">
        <ItemCard
          v-for="item in currentList.items"
          :key="item.id"
          :item="item"
          :is-guest="!token"
          :is-reservable="isReservable"
          :is-reserved="item.is_reserved"
          :is-my-reservation="myReservationIds.has(item.id)"
          @reserve="handleReserve"
          @unreserve="handleUnreserve"
        />
      </div>
       <div v-if="!currentList.items.length" class="no-items">
        В этом списке пока нет элементов.
      </div>
    </div>
    <div v-else class="not-found">
      <p>😕</p>
      Список не найден, или он является приватным.
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, onBeforeMount } from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useListsStore } from '@/store/lists';
import { useAuthStore } from '@/store/auth';
import ItemCard from '@/components/ItemCard.vue';
import router from '@/router';

const route = useRoute();
const listsStore = useListsStore();
const authStore = useAuthStore();

const { currentList, isLoading, userReservations } = storeToRefs(listsStore);
// Получаем токен из auth store
const { token } = storeToRefs(authStore);

const isReservable = computed(() => {
  return currentList.value?.list_type === 'wishlist';
});

const myReservationIds = computed(() => {
    return new Set(userReservations.value.map(r => r.item.id));
});

const handleReserve = async (itemId) => {
  if (!token.value) {
    alert('Пожалуйста, войдите или зарегистрируйтесь, чтобы бронировать желания.');
    router.push('/login');
    return;
  }
  try {
    await listsStore.reserveItem(itemId, route.params.publicKey);
  } catch (error) {
    alert(listsStore.error);
  }
};

const handleUnreserve = async (itemId) => {
   try {
    await listsStore.unreserveItem(itemId, route.params.publicKey);
  } catch (error)
{
    alert(listsStore.error);
  }
};

onBeforeMount(() => {
    if (token.value) {
        listsStore.fetchUserReservations();
    }
});

onMounted(() => {
  listsStore.fetchPublicListByKey(route.params.publicKey);
});
</script>

<style scoped>
.public-view {
}
.list-view-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 1rem;
}
.list-header {
  text-align: center;
  margin-bottom: 2rem;
}
.list-header h1, .list-header p {
    color: var(--text-color);
}
.items-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.loading, .not-found, .no-items {
  text-align: center;
  font-size: 1.2rem;
  color: #888;
  margin-top: 3rem;
}
.not-found p {
    font-size: 3rem;
    margin: 0;
}
</style>
